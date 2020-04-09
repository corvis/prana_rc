#    Prana RC
#    Copyright (C) 2020 Dmitry Berezovsky
#    
#    prana is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#    
#    prana is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import sys
import traceback
from asyncio import AbstractEventLoop

from prana_rc.service import PranaDeviceManager


class CLI:
    verbose_mode = False

    @classmethod
    def print_data(cls, msg: str):
        print(msg)

    @classmethod
    def print_info(cls, msg: str):
        print(msg, file=sys.stderr)

    @classmethod
    def print_error(cls, exception):
        print(" -> ERROR: " + str(exception), file=sys.stderr)
        if cls.verbose_mode:
            print('--------------')
            traceback.print_exc(file=sys.stderr)

    @classmethod
    def print_debug(cls, string_to_print):
        if cls.verbose_mode:
            print('[DEBUG] ' + string_to_print, file=sys.stderr)


class CliExtension(object):
    """
    Allows to extend CLI interface
    """
    COMMAND_NAME = None
    COMMAND_DESCRIPTION = None

    def __init__(self, parser: argparse.ArgumentParser, device_manager: PranaDeviceManager, loop: AbstractEventLoop):
        super().__init__()
        self.parser = parser
        self.__devce_manager = device_manager
        self.__loop = loop

    @property
    def device_manager(self) -> PranaDeviceManager:
        return self.__devce_manager

    @property
    def loop(self):
        return self.__loop

    @classmethod
    def setup_parser(cls, parser: argparse.ArgumentParser):
        pass

    def handle(self, args):
        raise NotImplementedError()


def register_global_arguments(parser: argparse.ArgumentParser):
    parser.add_argument("-v", "--verbose", dest="verbose", action='store_true', required=False,
                        help="If set more verbose output will used",
                        default=False)
    parser.add_argument("-i", "--iface", dest="iface", action='store_true', required=False,
                        help="Bluetooth interface to be used",
                        default='hci0')
