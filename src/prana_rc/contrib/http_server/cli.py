import asyncio

import tornado
from sizzlews.server.tornado import bootstrap_torando_rpc_application, TornadoHttpSizzleWSHandler

from prana_rc.cli_utils import CliExtension, CLI
from prana_rc.contrib.api import PranaRCApiHandler
from prana_rc.service import PranaDeviceManager


class HttpServerCLIExtension(CliExtension):
    COMMAND_NAME = 'http-server'
    COMMAND_DESCRIPTION = 'Run HTTP server which exposes functionality via RPC interface'

    async def handle(self, args):
        CLI.print_info("HTTP SERVER!")
        device_manager = PranaDeviceManager(iface=args.iface)
        prana_api = PranaRCApiHandler(device_manager, asyncio.get_event_loop())
        # app = tornado.web.Application([
        #     ('/', TornadoHttpSizzleWSHandler, dict(api_handler=prana_api))
        # ])
        # app.listen(8888)
        bootstrap_torando_rpc_application(prana_api, 8888, '/')
        while True:
            await asyncio.sleep(5)
