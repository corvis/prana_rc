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
import asyncio
import json
import sys
import traceback
from asyncio import AbstractEventLoop, CancelledError
from enum import Enum

from typing import Optional

from prana_rc.entity import Speed, PranaState
from prana_rc.service import PranaDeviceManager


class OutputFormat(Enum):
    TEXT = "text"
    JSON = "json"

    def __str__(self):
        return self.value


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
            print("--------------")
            traceback.print_exc(file=sys.stderr)

    @classmethod
    def print_debug(cls, string_to_print):
        if cls.verbose_mode:
            print("[DEBUG] " + string_to_print, file=sys.stderr)

    @classmethod
    def print_state(cls, state: PranaState, output_format: OutputFormat = OutputFormat.TEXT):
        if output_format == OutputFormat.TEXT:
            cls.print_data(str(state))
        elif output_format == OutputFormat.JSON:
            state_dict = state.to_dict()
            state_dict["timestamp"] = None  # Todo: Implement proper datetime converter
            cls.print_data(json.dumps(state_dict))

    @classmethod
    def print_version(cls, version_obj: dict, output_format: OutputFormat = OutputFormat.TEXT):
        if output_format == OutputFormat.TEXT:
            cls.print_data(str(version_obj.get("version")))
        elif output_format == OutputFormat.JSON:
            cls.print_data(json.dumps(version_obj))


class CliExtension(object):
    """
    Allows to extend CLI interface
    """

    COMMAND_NAME: Optional[str] = None
    COMMAND_DESCRIPTION: Optional[str] = None

    def __init__(
        self,
        parser: argparse.ArgumentParser,
        device_manager: PranaDeviceManager,
        loop: AbstractEventLoop,
    ):
        super().__init__()
        self.parser = parser
        self.__devce_manager = device_manager
        self.__loop = loop

    @staticmethod
    def _ensure_device_arg(args):
        if args.device is None:
            raise ValueError("Device is not set. Please check --device option.")

    async def connect_to_device(self, args):
        self._ensure_device_arg(args)
        CLI.print_info("Connecting to {}...".format(args.device))
        attempts_left = 10
        attempt_number = 1
        while attempts_left > 0:
            try:
                device = await self.device_manager.connect(args.device, args.timeout, attempts=1)
                CLI.print_info("   Connected")
                return device
            except CancelledError as e:
                CLI.print_info("Connect to device routine interrupted")
                raise e
            except Exception as e:
                attempts_left -= 1
                attempt_number += 1
                CLI.print_error(e)
                CLI.print_info("Reconnecting... Attempt #{}".format(attempt_number))
                await asyncio.sleep(1)
        raise RuntimeError("Unable to connect after {} attempts".format(attempt_number - 1))

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
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        required=False,
        help="If set more verbose output will used",
        default=False,
    )
    parser.add_argument(
        "-i",
        "--iface",
        dest="iface",
        action="store",
        required=False,
        type=str,
        help="Bluetooth interface to be used",
        default="hci0",
    )
    parser.add_argument(
        "-d",
        "--device",
        dest="device",
        action="store",
        required=False,
        type=str,
        help="Mac address of the prana device to connect to device. Required for the most of commands",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        dest="timeout",
        action="store",
        required=False,
        type=int,
        help="Time in seconds to wait for device",
        default=3,
    )
    parser.add_argument(
        "-f",
        "--format",
        dest="format",
        action="store",
        required=False,
        type=OutputFormat,
        choices=list(OutputFormat),
        default=OutputFormat.TEXT,
        help="Output format, e.g. text, json, etc.",
    )


def parse_bool_val(v: str) -> bool:
    if isinstance(v, bool):
        return v
    if v.lower() in ("on", "yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("off", "no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


def parse_speed_str(v: str) -> Speed:
    return Speed.from_str(v)
