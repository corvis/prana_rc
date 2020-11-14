![Prana device picture](https://github.com/corvis/prana_rc/blob/master/prana_pic.jpg?raw=true "Prana device picture")

<h2 align="center">Prana RC </h2>

[![License: GPLv3](https://img.shields.io/pypi/l/prana-rc?style=for-the-badge)](https://pypi.org/project/prana-rc/)
[![Python Versions](https://img.shields.io/pypi/pyversions/prana-rc?style=for-the-badge)](https://pypi.org/project/prana-rc/)
[![Code style: black](https://img.shields.io/badge/Code%20Style-black-black?style=for-the-badge)](https://github.com/psf/black) 
[![PyPy Downloads](https://img.shields.io/pypi/dm/prana_rc?style=for-the-badge)](https://pypi.org/project/prana-rc/) 
[![Last Commit](https://img.shields.io/github/last-commit/corvis/prana_rc?style=for-the-badge)](https://github.com/corvis/prana_rc/) 
[![Last Release](https://img.shields.io/github/release-date/corvis/prana_rc?style=for-the-badge)](https://github.com/corvis/prana_rc/releases)


**DISCLAIMER: This library is under active development now. There are no any stable release yet, so please do not 
use it in your installation unless you are developer who would like to contribute into module**

Python library and CLI to manage Prana recuperators (https://prana.org.ua/) via BLE interface.
It provides access to the device API and provides functionality similar to functionality of the official mobile 
application with some limitations (see limitation section below).

**ATTENTION**: Manufacturer doesn't provide any technical documentation describing protocol and also officially doesn't 
provide an ability to interact with the devices programmatically. This library is based on reverse engineering of the 
closed proprietary protocol. Used it on your own risk.

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
Dmitry Berezovsky

# Disclaimer
This module is licensed under GPL v3. This means you are free to use in non-commercial projects.

The GPL license clearly explains that there is no warranty for this free software. Please see the included LICENSE file for details.
