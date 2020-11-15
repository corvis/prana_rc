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
from asyncio import CancelledError

from sizzlews.server.tornado import (
    bootstrap_torando_rpc_application,
)

from prana_rc.cli_utils import CliExtension, CLI
from prana_rc.contrib.api.handler import PranaRCApiHandler
from prana_rc.service import PranaDeviceManager


class HttpServerCLIExtension(CliExtension):
    COMMAND_NAME = "http-server"
    COMMAND_DESCRIPTION = "Run HTTP server which exposes functionality via RPC interface"

    @classmethod
    def setup_parser(cls, parser: argparse.ArgumentParser):
        parser.add_argument(
            "-p",
            "--port",
            dest="http_port",
            action="store",
            required=False,
            type=int,
            default=8881,
            help="Port to bind http server.",
        )
        parser.add_argument(
            "-r",
            "--path",
            dest="http_path",
            action="store",
            required=False,
            type=str,
            default="/",
            help="Http path to bind rpc endpoint. E.g. /rpc will mount rpc server to "
            "http://localhost:<port>/rpc endpoint. If nothing is rpc will be mounted to the root. ",
        )

    async def handle(self, args: argparse.Namespace):
        CLI.print_info("Prana RC: Starting in HTTP server mode")
        device_manager = PranaDeviceManager(iface=args.iface)
        prana_api = PranaRCApiHandler(device_manager, asyncio.get_event_loop())
        bootstrap_torando_rpc_application(prana_api, args.http_port, args.http_path)
        CLI.print_info("HTTP: Listening on http://0.0.0.0:{}{}".format(args.http_port, args.http_path))
        try:
            while True:
                await asyncio.sleep(5)
        except CancelledError:
            CLI.print_info("Received shutdown signal. Closing connections...")
            await device_manager.disconnect_all()
            CLI.print_info("Connections closed")
