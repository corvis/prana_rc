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

from asyncio.events import AbstractEventLoop

from jsonrpc import Dispatcher
from pydantic import validate_arguments
from sizzlews.server.annotation import rpc_method
from sizzlews.server.common import MethodDiscoveryMixin, SizzleWSHandler
from typing import List, Optional

from prana_rc import utils
from prana_rc.contrib.api import (
    PranaRCAsyncFacade,
    DEFAULT_TIMEOUT,
    DEFAULT_ATTEMPTS,
    SetStateDTO,
    PranaStateDTO,
    PranaDeviceInfoDTO,
)
from prana_rc.entity import Mode, PranaDeviceInfo, PranaState
from prana_rc.service import PranaDeviceManager, PranaDevice


class ToDTO(object):
    @classmethod
    def prana_device_info(cls, obj: Optional[PranaDeviceInfo]) -> Optional[PranaDeviceInfoDTO]:
        if obj is None:
            return None
        return PranaDeviceInfoDTO(
            address=obj.address,
            bt_device_name=obj.bt_device_name,
            name=obj.name,
            rssi=obj.rssi,
        )

    @classmethod
    def prana_state(cls, obj: Optional[PranaState]) -> Optional[PranaStateDTO]:
        if obj is None:
            return None
        return PranaStateDTO.parse_obj(obj.to_dict())


class PranaRCApiHandler(MethodDiscoveryMixin, SizzleWSHandler, PranaRCAsyncFacade):
    METHOD_PREFXIX = "prana."

    def __init__(
        self,
        device_manager: PranaDeviceManager,
        loop: AbstractEventLoop,
        dispatcher: Dispatcher = None,
        expose_version_api=True,
        expose_ping_api=True,
    ) -> None:
        super().__init__(dispatcher, expose_version_api, expose_ping_api)
        self.__device_manager = device_manager
        # self.__devices_pool = {}  # type: Dict[str, PranaDevice]
        self.__loop = loop

    async def get_connected_prana_device(
        self, device_addr: str, timeout=DEFAULT_TIMEOUT, attempts=DEFAULT_ATTEMPTS
    ) -> PranaDevice:
        prana_device = await self.__device_manager.connect(device_addr, timeout, attempts)
        return prana_device

    @rpc_method
    async def discover(self, timeout=4) -> List[PranaDeviceInfoDTO]:
        res = await self.__device_manager.discover(timeout)
        return [utils.none_throws(ToDTO.prana_device_info(d)) for d in res]

    @rpc_method
    async def get_state(self, address: str, timeout=DEFAULT_TIMEOUT, attempts=DEFAULT_ATTEMPTS) -> PranaStateDTO:
        prana_device = await self.get_connected_prana_device(address, timeout, attempts)
        state = await prana_device.read_state()
        return utils.none_throws(ToDTO.prana_state(state))

    @rpc_method
    @validate_arguments
    async def set_state(
        self,
        address: str,
        state: SetStateDTO,
        timeout=DEFAULT_TIMEOUT,
        attempts=DEFAULT_ATTEMPTS,
    ) -> PranaStateDTO:
        features = [state.speed, state.mode, state.winter_mode, state.heating]
        if all(v is None for v in features):
            raise ValueError("At least one parameter must be set. Check your arguments.")
        prana_device = await self.get_connected_prana_device(address, timeout, attempts)
        if state.speed is not None:
            await prana_device.set_speed(state.speed)
        if state.heating is not None:
            await prana_device.set_heating(state.heating)
        if state.winter_mode is not None:
            await prana_device.set_winter_mode(state.winter_mode)
        if state.mode is not None:
            if state.mode == Mode.NIGHT:
                await prana_device.set_night_mode()
            elif state.mode == Mode.NORMAL:
                await prana_device.set_normal_speed()
            elif state.mode == Mode.HIGH:
                await prana_device.set_high_speed()
        new_state = await prana_device.read_state()
        return utils.none_throws(ToDTO.prana_state(new_state))
