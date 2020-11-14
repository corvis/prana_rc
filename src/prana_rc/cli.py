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
import importlib
import inspect
import pkgutil
import signal
from asyncio import CancelledError

from typing import Type, List

import prana_rc.__version__
from prana_rc.cli_utils import (
    CliExtension,
    register_global_arguments,
    CLI,
    parse_bool_val,
    parse_speed_str,
)
from prana_rc.entity import Mode
from prana_rc.service import PranaDeviceManager

PRANA_RC_VERSION = prana_rc.__version__.__version__
SHUTDOWN_SIGNALS = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)

supplementary_parser = argparse.ArgumentParser(add_help=False)
register_global_arguments(supplementary_parser)

parser = argparse.ArgumentParser(
    prog="prana",
    add_help=True,
    description="CLI interface to manage Prana recuperators via BLE",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Version: {version}
--------------------------------------------------------------
Prana RC CLI Copyright (C) 2020 Dmitry Berezovsky
This program comes with ABSOLUTELY NO WARRANTY;
This is free software, and you are welcome to redistribute it
under certain conditions;
--------------------------------------------------------------
""".format(
        version=PRANA_RC_VERSION
    ),
)
register_global_arguments(parser)
command_parser = parser.add_subparsers(
    title="command",
    dest="cmd",
    description='Use "<command> -h" to get information ' "about particular command",
)


# =========== AVAILABLE COMMANDS =====================


class DiscoveryCLIExtension(CliExtension):
    COMMAND_NAME = "discover"
    COMMAND_DESCRIPTION = "Run discovery process to find available Prana devices nearby"

    async def handle(self, args):
        CLI.print_info("Starting discovery (timeout {}s)...".format(args.timeout))
        devs = await self.device_manager.discover()
        if len(devs) == 0:
            CLI.print_info("No devices found")
        else:
            for dev in devs:
                CLI.print_info(
                    "{} [{}] (identity: {}, rssi: {})".format(dev.name, dev.address, dev.bt_device_name, dev.rssi)
                )


class VersionCLIExtension(CliExtension):
    COMMAND_NAME = "version"
    COMMAND_DESCRIPTION = "Print version and exit"

    async def handle(self, args):
        version_obj = dict(version=PRANA_RC_VERSION)
        CLI.print_version(version_obj, args.format)


class ReadStateCLIExtension(CliExtension):
    COMMAND_NAME = "status"
    COMMAND_DESCRIPTION = "Read state of the device and print back to terminal"

    async def handle(self, args):
        device = await self.connect_to_device(args)
        state = await device.read_state()
        CLI.print_state(state, args.format)


class SetCLIExtension(CliExtension):
    COMMAND_NAME = "set"
    COMMAND_DESCRIPTION = "Set speed"

    @classmethod
    def setup_parser(cls, parser: argparse.ArgumentParser):
        parser.add_argument(
            "-s",
            "--speed",
            dest="speed",
            action="store",
            required=False,
            type=parse_speed_str,
            help="Speed to set. Could be one of: 0-10, off, high, low",
        )
        parser.add_argument(
            "-m",
            "--mode",
            dest="mode",
            action="store",
            required=False,
            type=Mode,
            help="Mode to set. Could be normal, night or high",
        )
        parser.add_argument(
            "-w",
            "--winter-mode",
            dest="winter_mode",
            action="store",
            required=False,
            type=parse_bool_val,
            help="Enable or disable winter mode (de-icing)",
        )
        parser.add_argument(
            "-q",
            "--heating",
            dest="heating",
            action="store",
            required=False,
            type=parse_bool_val,
            help="Enable or disable heating (mini-heating function in device manual)",
        )

    async def handle(self, args: argparse.Namespace):
        features = [args.speed, args.mode, args.winter_mode, args.heating]
        if all(v is None for v in features):
            raise ValueError("At least one parameter must be set. Check your arguments.")
        device = await self.connect_to_device(args)
        if args.speed is not None:
            CLI.print_info("Setting speed to {}...".format(args.speed.value))
            await device.set_speed(args.speed)
        if args.heating is not None:
            CLI.print_info("Setting heating to {}...".format(args.heating))
            await device.set_heating(args.heating)
        if args.winter_mode is not None:
            CLI.print_info("Setting winter-mode to {}...".format(args.winter_mode))
            await device.set_winter_mode(args.winter_mode)
        if args.mode is not None:
            CLI.print_info("Setting mode to {}...".format(args.mode))
            if args.mode == Mode.NIGHT:
                await device.set_night_mode()
            elif args.mode == Mode.NORMAL:
                await device.set_normal_speed()
            elif args.mode == Mode.HIGH:
                await device.set_high_speed()

        # At the end let's print the new state
        state = await device.read_state()
        CLI.print_info("Recent device status:")
        CLI.print_state(state, args.format)


# =========== END OF COMMAND DEFINITIONS ==============


def read_global_args():
    known, unknown = supplementary_parser.parse_known_args()
    return known


def configure_subparser_for_cli_extension(
    ext: Type[CliExtension],
    parser: argparse.ArgumentParser,
    device_manager: PranaDeviceManager,
    loop: asyncio.AbstractEventLoop,
):
    ext.setup_parser(parser)
    ext_instance = ext(parser, device_manager, loop)
    parser.set_defaults(handler=ext_instance)


async def handle_wrapper(device_manager: PranaDeviceManager, args):
    try:
        await args.handler.handle(args)
    except CancelledError:
        pass
    except Exception as e:
        CLI.print_error(e)


async def on_shutdown(signal, loop, device_manager: PranaDeviceManager):
    CLI.print_error(f"Received exit signal {signal.name}...")
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks)
    await device_manager.disconnect_all()

    # loop.stop()


def discover_cli_extensions(target_package_name: str) -> List[Type]:
    extensions = []
    target_package = importlib.import_module(target_package_name)
    for loader, pkg_name, is_pkg in pkgutil.walk_packages(target_package.__path__):  # type: ignore
        # Check if we've got a valid extension package
        if is_pkg:
            full_name = ".".join((target_package.__name__, pkg_name))
            try:
                candidate_pkg = importlib.import_module(full_name)
                if hasattr(candidate_pkg, "is_available"):
                    if not candidate_pkg.is_available():  # type: ignore
                        continue  # Package is not supported
                    cli_module = importlib.import_module(".cli", full_name)
                    found_extensions = inspect.getmembers(
                        cli_module,
                        lambda member: inspect.isclass(member)
                        and member.__name__ != CliExtension.__name__
                        and issubclass(member, CliExtension),
                    )
                    extensions += [cls for name, cls in found_extensions]
            except ImportError:
                pass
    return extensions


def run_cli():
    # logging.basicConfig(level=logging.ERROR)
    root_commands = [
        DiscoveryCLIExtension,
        SetCLIExtension,
        ReadStateCLIExtension,
        VersionCLIExtension,
    ]
    # Extra commands
    root_commands += discover_cli_extensions("prana_rc.contrib")
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
        # Register on shutdown callback
        for s in SHUTDOWN_SIGNALS:
            loop.add_signal_handler(s, lambda s=s: asyncio.create_task(on_shutdown(s, loop, device_manager)))
        # Run main login
        try:
            loop.run_until_complete(asyncio.ensure_future(handle_wrapper(device_manager, args)))
        except KeyboardInterrupt:
            CLI.print_error("Process interrupted. Closing connections.")


if __name__ == "__main__":
    run_cli()
