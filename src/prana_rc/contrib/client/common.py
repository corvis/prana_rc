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

from sizzlews.client.common import SizzleWsAsyncClient
from typing import List

from prana_rc.contrib.api import (
    PranaRCAsyncFacade,
    SetStateDTO,
    DEFAULT_TIMEOUT,
    DEFAULT_ATTEMPTS,
    PranaStateDTO,
    PranaDeviceInfoDTO,
)


class PranaRCAsyncClient(SizzleWsAsyncClient, PranaRCAsyncFacade):
    async def discover(self, timeout=DEFAULT_TIMEOUT) -> List[PranaDeviceInfoDTO]:
        return await self.async_invoke("prana.discover", timeout)

    async def get_state(self, address: str, timeout=DEFAULT_TIMEOUT, attempts=DEFAULT_ATTEMPTS) -> PranaStateDTO:
        return await self.async_invoke("prana.get_state", address, timeout, attempts)

    async def set_state(
        self,
        address: str,
        state: SetStateDTO,
        timeout=DEFAULT_TIMEOUT,
        attempts=DEFAULT_ATTEMPTS,
    ) -> PranaStateDTO:
        return await self.async_invoke("prana.set_state", address, state.dict(), timeout)
