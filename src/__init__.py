# -*- coding: utf-8 -*-

"""Top level package for Prana RC."""


__author__ = "Dmitry Berezovsky"
__email__ = ""

import logging
import os
import sys
import cli

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())
_logger.setLevel(logging.DEBUG)
if bool(os.environ.get("PRANA_LOGGING", False)):
    FORMAT = "%(asctime)-15s %(name)-8s %(levelname)s: %(message)s"
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(fmt=FORMAT))
    _logger.addHandler(handler)


if __name__ == "__main__":
    cli.run_cli()