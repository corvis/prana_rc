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

import asyncio

from sizzlews.server.tornado import (
    bootstrap_torando_rpc_application,
)

from prana_rc.cli_utils import CliExtension, CLI
from prana_rc.contrib.api.handler import PranaRCApiHandler
from prana_rc.service import PranaDeviceManager


class HttpServerCLIExtension(CliExtension):
    COMMAND_NAME = "http-server"
    COMMAND_DESCRIPTION = "Run HTTP server which exposes functionality via RPC interface"

    async def handle(self, args):
        CLI.print_info("HTTP SERVER!")
        device_manager = PranaDeviceManager(iface=args.iface)
        prana_api = PranaRCApiHandler(device_manager, asyncio.get_event_loop())
        # app = tornado.web.Application([
        #     ('/', TornadoHttpSizzleWSHandler, dict(api_handler=prana_api))
        # ])
        # app.listen(8888)
        bootstrap_torando_rpc_application(prana_api, 8888, "/")
        while True:
            await asyncio.sleep(5)
