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

**DISCLAIMER: This library is under active development now. There are no any stable release yet, so please do not 
use it in your installation unless you are developer who would like to contribute into module**

Python library and CLI to manage Prana recuperators (https://prana.org.ua/) via BLE interface.
It provides access to the device API and provides functionality similar to functionality of the official mobile 
application with some limitations (see limitation section below).

**ATTENTION**: Manufacturer doesn't provide any technical documentation describing protocol and also officially doesn't 
provide an ability to interact with the devices programmatically. This library is based on reverse engineering of the 
closed proprietary protocol. Used it on your own risk.

**Features:**

* Read current prana state
* Control everything which could be managed via official app with a few exceptions (see limitations section)
* Discover not connected devices around
* Client-server architecture (allows distributed setup)
* CLI interface available for quick tinkering

## Installation & Usage

### Server component

The easiest way is to use pip. In order to install the recent version with HTTP API support run:

```
pip install prana-rc[server-tornado]
```

If you prefer dockerized setup you could run it like this:

​```
docker run --volume /run/dbus/system_bus_socket:/run/dbus/system_bus_socket  --restart=unless-stopped prana-rc:0.3.5
​```

By default it will run `http-server` command, however you could run any cli commend by addign extra arguments to the end. For example to run discover you could use:

```
docker run --rm --volume /run/dbus/system_bus_socket:/run/dbus/system_bus_socket corvis/prana-rc:0.3.5 discover
```

### Client 

You could use any http client to query the server. The underlying is JSON-RPCv2. The interface is defined here. 

If you are looking for programmatic access from the python code you might consider python API client. It has minimal dependencies and could be installed from the pip. 

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

This approach is recommended as it brings some significant benefits over the embedding prana_rc into own code base:

* **Stability**. Prana RC uses bluetooth library which relies on low level OS APIs. Theoretically it might be a stability risk for your application. In case you use prana server in case of crash it will not affect your application. If you use Dockerized version it is easy to configure automatic restart.
* **Coverage**. Bluetooth works stable on a relatively small distance (5-10m with no obstacles) this means your server should be located close to the device. Often it is hard\impossible as you have a number of prana devices in different locations so the solution would be to setup a few intermidiate nodes (e.g. some microcomputers like Raspberry Pi) with server component and connect them to the central control unit via API.
* **Easy integration**. There is no lock on particular technology so the library could be used in conjunction with any tech stack.

# Hardware

Device running this software must be equipped with bluetooth 4.0+ module so it support BLE. 
This module relies on [Bleak](https://github.com/hbldh/bleak) library so there is a chance it might work on 
Win, Mac and Linux. However it was tested only on:

* Linux (x64): Fedora, Debian
* Raspbery PI: Raspbian
* Mac: Catalina 

Most likely it is compatible with Prana 150,200G, and Eco Energy series (with limited feature set). 
But confirmed list of models which were verified to work fine is below:

* Prana 150

Please, create an ticket if you tested it with other device model so we could extend the list.

# Limitations

* Using device password is not supported
* Reading information form built-in sensors (for Eco Energy series) is not supported

# Credits
* Dmitry Berezovsky, author
* [Bleak](https://github.com/hbldh/bleak), bluetooth client library

# Disclaimer
This module is licensed under GPL v3. This means you are free to use in non-commercial projects.

The GPL license clearly explains that there is no warranty for this free software. Please see the included LICENSE file for details.

````
