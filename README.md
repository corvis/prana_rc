![Prana device picture](https://github.com/corvis/prana_rc/blob/development/media/cover-picture.jpg?raw=true "Prana device picture")

<h2 align="center">Prana RC </h2>

<p align="center">
  <a href="https://pypi.org/project/prana-rc/"><img src="https://img.shields.io/pypi/l/prana-rc?style=for-the-badge" title="License: GPLv3"/></a> 
  <a href="https://pypi.org/project/prana-rc/"><img src="https://img.shields.io/pypi/pyversions/prana-rc?style=for-the-badge" title="Python Versions"/></a> 
  <a href="https://github.com/psf/black/"><img src="https://img.shields.io/badge/Code%20Style-black-black?style=for-the-badge" title="Code style: black"/></a> 
  <a href="https://pypi.org/project/prana-rc/"><img src="https://img.shields.io/pypi/v/prana-rc?style=for-the-badge" title="PyPy Version"/></a> 
  <a href="https://pypi.org/project/prana-rc/"><img src="https://img.shields.io/pypi/dm/prana_rc?style=for-the-badge" title="PyPy Downloads"/></a> 
  <br>
  <a href="https://github.com/corvis/prana_rc/actions?query=workflow%3A%22Sanity+Check"><img src="https://img.shields.io/github/workflow/status/corvis/prana_rc/Sanity%20Check?style=for-the-badge" title="Build Status"/></a> 
  <a href="https://app.codacy.com/gh/corvis/prana_rc/dashboard"><img src="https://img.shields.io/codacy/grade/7aa38cc5c1b14aa9ab06ee8af45d5cff?style=for-the-badge&_nocahe=1" title="Codacy Grade"/></a> 
  <a href="https://github.com/corvis/prana_rc/"><img src="https://img.shields.io/github/last-commit/corvis/prana_rc?style=for-the-badge" title="Last Commit"/></a> 
  <a href="https://github.com/corvis/prana_rc/releases/"><img src="https://img.shields.io/github/release-date/corvis/prana_rc?style=for-the-badge" title="Last Release"/></a> 
</p>

Python library and CLI to manage Prana recuperators (https://prana.org.ua/) via BLE interface.
It provides access to the device API and provides functionality similar to the functionality of the official mobile 
application with some limitations (see limitation section below).

**ATTENTION**: The manufacturer doesn't provide any technical documentation describing the protocol and also officially doesn't provide an ability to interact with the devices programmatically. This library is based on reverse engineering of the closed proprietary protocol. Use it at your own risk.

**Features:**

* Read current prana state
* Control everything which could be managed via an official app with a few exceptions (see [limitations](#limitations) section)
* Discover not connected devices around
* Client-server architecture (allows distributed setup)
* CLI interface available for quick tinkering

## Installation & Usage

### Server component

#### Prerequisites

For Linux hosts:

* Make sure you have Bluez component installed. E.g. on debian based systems you can use `sudo apt-get install bluez`

#### Installation

The easiest way is to use pip. To install the recent version with HTTP API support run:

```
pip install prana-rc[server-tornado]
```

If you prefer dockerized setup you could run it like this:

```
docker run --volume /run/dbus/system_bus_socket:/run/dbus/system_bus_socket -p 8881:8881 --restart=unless-stopped corvis/prana-rc:latest
```

By default it will run `http-server` command, however you could run any cli commend by addign extra arguments to the 
end. For example to run discover you could use:

```
docker run --rm --volume /run/dbus/system_bus_socket:/run/dbus/system_bus_socket corvis/prana-rc:latest discover
```

**NOTE**: It is highly recommended to use the fixed version instead of `latest` to avoid unintended upgrades.

#### API

API is based on [JSON RPC 2.0](https://www.jsonrpc.org/specification) standard. The server exposes one single endpoint 
for handling rpc requests, any other requests will be declined. 

According to json rpc specification, the request must be a POST HTTP request with `Content-Type` set 
to `application/json` and the body containing json of the following structure:

```json
{
  "jsonrpc": "2.0", 
  "method": "METHOD_NAME", 
  "id": 1,
  "params": [] 
}
```

Where params might be omitted if the method doesn't require any arguments. Params also could be an object if you prefer keyword arguments instead of positional args. `id` is a unique identifier of the request (relevant for async APIs), 
it should be generated by the client and it will be returned back with the response.
It is important to include `id` and `jsonrpc` fields into the request otherwise. 

The table below describes the exposed API methods:

##### Discover

Discovers available Prana devices nearby.

**Important**: It will discover __only__ those devices which are not connected to any client (either mobile app, 
prana_rc or any other).

**Method name**: `prana.discover`

###### Params 

| Name                  | Type        | Required | Description                                                         |
| --------------------- | ----------- |-------   | ------------------------------------------------------------------- |
| timeout               | int         | no       | Time in seconds to wait for the device's announcement. <br> Default: 4s. |

**Example**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "prana.discover",
  "params": {}
}
```

Shell command

```bash
curl \
  -X POST \
  -H "Accept: application/json" \
  http://YOUR_IP:8881/ \
  -d '{ "jsonrpc": "2.0", "id": 1, "method": "prana.discover" }'
```

###### Result 

```json
{
   "result":[
      {
         "address":"00:A0:50:99:52:D2",
         "bt_device_name":"PRNAQaqBEDROOM",
         "name":"BEDROOM",
         "rssi":-87
      }
   ],
   "id":1,
   "jsonrpc":"2.0"
}
```

##### Get State

**Method name**: `prana.get_state`

###### Params 

| Name                  | Type        | Required | Description                                                         |
| --------------------- | ----------- |-------   | ------------------------------------------------------------------- |
| address               | string      | yes      | Mac address of the device to communicate with. Could be obtained from `prana.discover` query result  |
| timeout               | int         | no       | Time in seconds to wait for successful command execution. <br> Default: 5s. |
| attempts              | int         | no       | Number of connection attempts to make before the failure <br> Default: 5. |

**Example**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "prana.get_state",
  "params": {"address": "XX:XX:XX:XX:XX:XX"}
}
```

Shell command

```bash
curl \
  -X POST \
  -H "Accept: application/json" \
  http://YOUR_IP:8881/ \
  -d '{ "jsonrpc": "2.0", "id": 1, "method": "prana.get_state", "params": {"address": "XX:XX:XX:XX:XX:XX"} }'
```


###### Result 

Returns PranaState object.
For baseline prana series (e.g.model 150, 200G) with no any sensors on board:

```json
{
   "result":{
      "speed_locked":4,
      "speed_in":4,
      "speed_out":4,
      "night_mode":false,
      "auto_mode":false,
      "flows_locked":true,
      "is_on":false,
      "mini_heating_enabled":false,
      "winter_mode_enabled":false,
      "is_input_fan_on":false,
      "is_output_fan_on":false,
      "sensors": null,
      "timestamp":"2020-11-18T23:14:45.313515"
   },
   "id":1,
   "jsonrpc":"2.0"
}
```

For models with embedded sensors (e.g. Eco Life, Eco energy series):

```json
{
   "result":{
      "speed_locked":4,
      "speed_in":4,
      "speed_out":4,
      "night_mode":false,
      "auto_mode":false,
      "flows_locked":true,
      "is_on":false,
      "mini_heating_enabled":false,
      "winter_mode_enabled":false,
      "is_input_fan_on":false,
      "is_output_fan_on":false,
      "sensors": {
        "temperature_in": 12.3,
        "temperature_out": 9.6,
        "humidity": 41,
        "pressure": 1010
      },
      "timestamp":"2020-11-18T23:14:45.313515"
   },
   "id":1,
   "jsonrpc":"2.0"
}
```

##### Set State

**Method name**: `prana.set_state`

###### Params 

| Name                  | Type        | Required | Description                                                         |
| --------------------- | ----------- |-------   | ------------------------------------------------------------------- |
| address               | string      | yes      | Mac address of the device to communicate with. Could be obtained from `prana.discover` query result  |
| state                 | object      | yes      | State to set for the device. The structure is listed below              |
| timeout               | int         | no       | Time in seconds to wait for successful command execution. <br> Default: 4s. |
| attempts              | int         | no       | Number of connection attempts to make before the failure <br> Default: 5. |

**Example**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "prana.set_state",
  "params": {"address": "XX:XX:XX:XX:XX:XX", "state": {"speed": 1}}
}
```

Shell command

```bash
curl \
  -X POST \
  -H "Accept: application/json" \
  http://YOUR_IP:8881/ \
  -d '{ "jsonrpc": "2.0", "id": 1, "method": "prana.set_state", "params": {"address": "XX:XX:XX:XX:XX:XX", "state": {"speed": 1}} }'
```

###### Result 

Returns the PranaState object. See [Get State](#get-state) method for more details on the object structure.

```json
{
   "result":{
      "speed_locked":4,
      "speed_in":4,
      "speed_out":4,
      "night_mode":false,
      "auto_mode":false,
      "flows_locked":true,
      "is_on":false,
      "mini_heating_enabled":false,
      "winter_mode_enabled":false,
      "is_input_fan_on":false,
      "is_output_fan_on":false,
      "timestamp":"2020-11-18T23:14:45.313515"
   },
   "id":1,
   "jsonrpc":"2.0"
}
```

### Client 

You could use any HTTP client to query the server. The underlying is JSON-RPCv2. The interface is defined here. 

If you are looking for programmatic access from the python code you might consider the python API client. It has minimal 
dependencies and could be installed from the pip. 

#### AIOHTTP Client

If your project is based on asyncio the recommended way is to use [aiohttp](https://docs.aiohttp.org/en/stable/) based client:

​```
pip install prana-rc.client[aiohttp]
​```

Here is the basic usage example:

​```python
TBD
​```

## Architecture

The library could be used either directly in a python project or it could act as a server which maintains bluetooth connection with Prana device and exposes HTTP interface to the clients. See diagram below:

<p align="center">
    <img title="Prana RC Architecture" src="https://github.com/corvis/prana_rc/blob/development/media/prana_rc-architecture.png?raw=true" />
</p>

This approach is recommended as it brings some significant benefits over the embedding prana_rc into its own codebase:

* **Stability**. Prana RC uses bluetooth library which relies on low-level OS APIs. Theoretically, it might be a stability risk for your application. In case you use the prana server in case of a crash, it will not affect your application. If you use the Dockerized version it is easy to configure automatic restart.
* **Coverage**. Bluetooth works stable on a relatively small distance (5-10m with no obstacles) this means your server should be located close to the device. Often it is hard\impossible as you have a number of prana devices in different locations so the solution would be to set up a few intermediate nodes (e.g. some microcomputers like Raspberry Pi) with server components and connect them to the central control unit via API.
* **Easy integration**. There is no lock on particular technology so the library could be used in conjunction with any tech stack.

# Hardware

The device running this software must be equipped with a bluetooth 4.0+ module so it supports BLE. 
This module relies on [Bleak](https://github.com/hbldh/bleak) library so there is a chance it might work on 
Win, Mac, and Linux. However, it was tested only on:

* Linux (x64): Fedora, Debian
* Raspbery PI: Raspbian
* Mac: Catalina 

Most likely it is compatible with Prana 150,200G, and Eco Energy series (with a limited feature set). 
But the confirmed list of models which were verified to work fine is below:

* Prana 150
* Prana 160 (italian market)

Please, create a ticket if you tested it with another device model so we could extend the list.

# Limitations

* Using device password is not supported
* Reading information form built-in sensors (for Eco Energy series) is limited. 
At the moment VOC and CO2 sensors are not supported.
* Changing brightness is not supported

# Credits
* Dmitry Berezovsky, author
* [Bleak](https://github.com/hbldh/bleak), bluetooth client library
* Contributors:
    * [@francesco-re-1107](https://github.com/francesco-re-1107), eco-energy series support

# Disclaimer
This module is licensed under GPL v3. This means you are free to use in non-commercial projects.

The GPL license clearly explains that there is no warranty for this free software. Please see the included LICENSE file for details.
