# Prana RC

![Prana device picture](https://github.com/corvis/prana_rc/blob/development/media/cover-picture.jpg?raw=true "Prana device picture")

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


## Installation

Install regular server component with Http API:

```
pip install prana-rc[server-tornado]
```

If you prefer dockerized setup you could run it like this:

```
docker run --rm prana-rc:latest -d  --network=host --restart=unless-stopped	
```

For more details [see readme](https://github.com/corvis/prana_rc).

# Disclaimer
This module is licensed under GPL v3. This means you are free to use in non-commercial projects.

The GPL license clearly explains that there is no warranty for this free software. Please see the included LICENSE file for details.
