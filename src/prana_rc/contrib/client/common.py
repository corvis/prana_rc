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

import abc
import json

from sizzlews.client.common import SizzleWsAsyncClient
from typing import List

from prana_rc import utils
from prana_rc.contrib.api import (
    PranaRCAsyncFacade,
    SetStateDTO,
    DEFAULT_TIMEOUT,
    DEFAULT_ATTEMPTS,
    PranaStateDTO,
    PranaDeviceInfoDTO,
)


class PranaRCAsyncClient(SizzleWsAsyncClient, PranaRCAsyncFacade, metaclass=abc.ABCMeta):
    async def discover(self, timeout=DEFAULT_TIMEOUT) -> List[PranaDeviceInfoDTO]:
        # TODO: set expected response time. Requires ws-sizzle update to support lists
        return utils.safe_cast(
            List[PranaDeviceInfoDTO], await self.async_invoke("prana.discover", timeout, expected_response_type=None)
        )

    async def get_state(self, address: str, timeout=DEFAULT_TIMEOUT, attempts=DEFAULT_ATTEMPTS) -> PranaStateDTO:
        return utils.safe_cast(
            PranaStateDTO,
            await self.async_invoke(
                "prana.get_state", address, timeout, attempts, expected_response_type=PranaStateDTO
            ),
        )

    async def set_state(
        self,
        address: str,
        state: SetStateDTO,
        timeout=DEFAULT_TIMEOUT,
        attempts=DEFAULT_ATTEMPTS,
    ) -> PranaStateDTO:
        return utils.safe_cast(
            PranaStateDTO,
            await self.async_invoke(
                "prana.set_state", address, json.loads(state.json()), timeout, expected_response_type=PranaStateDTO
            ),
        )
