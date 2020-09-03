from asyncio import AbstractEventLoop

from jsonrpc import Dispatcher
from sizzlews.server.annotation import rpc_method
from sizzlews.server.common import MethodDiscoveryMixin, SizzleWSHandler
from typing import List, Dict

from prana_rc.contrib.api.dto import SetStateDTO
from prana_rc.entity import PranaDeviceInfo, ToApiDict
from prana_rc.service import PranaDeviceManager, PranaDevice

DEFAULT_TIMEOUT = 5
DEFAULT_ATTEMPTS = 5


class PranaRCApiHandler(MethodDiscoveryMixin, SizzleWSHandler):
    METHOD_PREFXIX = "prana."

    def __init__(self, device_manager: PranaDeviceManager, loop: AbstractEventLoop, dispatcher: Dispatcher = None,
                 expose_version_api=True,
                 expose_ping_api=True) -> None:
        super().__init__(dispatcher, expose_version_api, expose_ping_api)
        self.__device_manager = device_manager
        self.__devices_pool = {}  # type: Dict[str, PranaDevice]
        self.__loop = loop

    # TODO: Locks!

    async def get_connected_prana_device(self, device_addr: str, timeout=DEFAULT_TIMEOUT,
                                         attempts=DEFAULT_ATTEMPTS) -> PranaDevice:
        prana_device = self.__devices_pool.get(device_addr, None)  # type: PranaDevice
        if prana_device is None:
            prana_device = await self.__device_manager.connect(device_addr, timeout, attempts)
            self.__devices_pool[device_addr] = prana_device
        if prana_device.is_connected():
            return prana_device
        else:
            try:
                prana_device.connect(timeout)
            except:
                # TODO: logger - connection seems to be already dead. Reconnecting
                del self.__devices_pool[device_addr]
                return await self.get_connected_prana_device(device_addr, timeout, attempts)
        return prana_device

    @rpc_method
    async def discover(self, timeout=4) -> List[dict]:
        res = await self.__device_manager.discover(timeout)
        return [ToApiDict.prana_device_info(d) for d in res]

    @rpc_method
    async def get_state(self, address: str, timeout=DEFAULT_TIMEOUT, attempts=DEFAULT_ATTEMPTS) -> dict:
        prana_device = await self.get_connected_prana_device(address, timeout, attempts)
        state = await prana_device.read_state()
        state.timestamp = None  # TODO: Fix JSON converter to serialize datetime correctly
        return ToApiDict.prana_state(state)

    @rpc_method
    async def set_state(self, address: str, state: dict, timeout=DEFAULT_TIMEOUT, attempts=DEFAULT_ATTEMPTS) -> dict:
        state = SetStateDTO(**state)
        features = [state.speed, state.mode, state.winter_mode, state.heating]
        if all(v is None for v in features):
            raise ValueError("At least one parameter must be set. Check your arguments.")
        prana_device = await self.get_connected_prana_device(address, timeout, attempts)
        if state.speed is not None:
            await prana_device.set_speed(state.speed)

        # TODO: Apply the rest

        state = await prana_device.read_state()
        return ToApiDict.prana_state(state)
