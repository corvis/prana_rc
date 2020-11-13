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

from prana_rc.entity import Speed, Mode


class SetStateDTO(pydantic.BaseModel):
    speed: Speed = None
    mode: Mode = None
    winter_mode: bool = None
    heating: bool = None


class PranaDeviceInfoDTO(pydantic.BaseModel):
    address: str = None
    bt_device_name: str = None
    name: str = None
    rssi: int = None


class PranaStateDTO(pydantic.BaseModel):
    speed_locked: int = None
    speed_in: int = None
    speed_out: int = None
    night_mode: bool = None
    auto_mode: bool = None
    flows_locked: bool = None
    is_on: bool = None
    mini_heating_enabled: bool = None
    winter_mode_enabled: bool = None
    is_input_fan_on: bool = None
    is_output_fan_on: bool = None
    timestamp: datetime.datetime = None
