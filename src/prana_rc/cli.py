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
import logging
from typing import Type

from prana_rc.cli_utils import CliExtension, register_global_arguments, CLI
from prana_rc.service import PranaDeviceManager

supplementary_parser = argparse.ArgumentParser(add_help=False)
register_global_arguments(supplementary_parser)

parser = argparse.ArgumentParser(prog='prana', add_help=True,
                                 description='CLI interface to manage Prana recuperators via BLE',
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog="""
--------------------------------------------------------------
Prana RC CLI Copyright (C) 2020 Dmitry Berezovsky
This program comes with ABSOLUTELY NO WARRANTY;
This is free software, and you are welcome to redistribute it
under certain conditions;
--------------------------------------------------------------
"""
                                 )
register_global_arguments(parser)
command_parser = parser.add_subparsers(title="command",
                                       dest="cmd", required=True,
                                       description='Use \"<command> -h\" to get information '
                                                   'about particular command')


# =========== AVAILABLE COMMANDS =====================

class DiscoveryCLIExtension(CliExtension):
    COMMAND_NAME = 'discover'
    COMMAND_DESCRIPTION = 'Run discovery process to find available Prana devices nearby'

    @classmethod
    def setup_parser(cls, parser: argparse.ArgumentParser):
        parser.add_argument("-t", "--timeout", dest="timeout", action='store_true', required=False,
                            help="Time in seconds to wait for devices",
                            default=5)

    async def handle(self, args):
        CLI.print_info("Starting discovery (timeout {}s)...".format(args.timeout))
        devs = await self.device_manager.discover()
        if len(devs) == 0:
            CLI.print_info("No devices found")
        else:
            for dev in devs:
                CLI.print_info(
                    "{} [{}] (identity: {}, rssi: {})".format(dev.name, dev.address, dev.bt_device_name, dev.rssi))


# =========== END OF COMMAND DEFINITIONS ==============

def read_global_args():
    known, unknown = supplementary_parser.parse_known_args()
    return known


def configure_subparser_for_cli_extension(ext: Type[CliExtension], parser: argparse.ArgumentParser,
                                          device_manager: PranaDeviceManager, loop: asyncio.AbstractEventLoop):
    ext.setup_parser(parser)
    ext_instance = ext(parser, device_manager, loop)
    parser.set_defaults(handler=ext_instance)


def run_cli():
    # logging.basicConfig(level=logging.ERROR)
    root_commands = (DiscoveryCLIExtension,)
    global_args = read_global_args()
    CLI.verbose_mode = global_args.verbose

    loop = asyncio.get_event_loop()
    device_manager = PranaDeviceManager(iface=global_args.iface)

    # Process root commands
    for cmd in root_commands:
        cmd_subparser = command_parser.add_parser(cmd.COMMAND_NAME, help=cmd.COMMAND_DESCRIPTION)
        configure_subparser_for_cli_extension(cmd, cmd_subparser, device_manager, loop)

    args = parser.parse_args()
    if hasattr(args, "handler"):
        loop.run_until_complete(asyncio.ensure_future(args.handler.handle(args)))


if __name__ == "__main__":
    run_cli()
