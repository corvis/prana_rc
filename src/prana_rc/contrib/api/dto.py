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

import datetime

import pydantic
from typing import Optional

from prana_rc.entity import Speed, Mode


class SetStateDTO(pydantic.BaseModel):
    speed: Optional[Speed] = None
    mode: Optional[Mode] = None
    winter_mode: Optional[bool] = None
    heating: Optional[bool] = None


class PranaDeviceInfoDTO(pydantic.BaseModel):
    address: Optional[str] = None
    bt_device_name: Optional[str] = None
    name: Optional[str] = None
    rssi: Optional[int] = None


class PranaStateDTO(pydantic.BaseModel):
    speed_locked: Optional[int] = None
    speed_in: Optional[int] = None
    speed_out: Optional[int] = None
    night_mode: Optional[bool] = None
    auto_mode: Optional[bool] = None
    flows_locked: Optional[bool] = None
    is_on: Optional[bool] = None
    mini_heating_enabled: Optional[bool] = None
    winter_mode_enabled: Optional[bool] = None
    is_input_fan_on: Optional[bool] = None
    is_output_fan_on: Optional[bool] = None
    timestamp: Optional[datetime.datetime] = None
