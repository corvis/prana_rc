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

from typing import NamedTuple


class PranaDeviceInfo(NamedTuple):
    address: str
    bt_device_name: str
    name: str
    rssi: int


class PranaState(object):

    def __init__(self) -> None:
        self.speed_locked: int = None
        self.speed_in: int = None
        self.speed_out: int = None
        self.night_mode: bool = None
        self.auto_mode: bool = None
        self.flows_locked: bool = None
        self.is_on: bool = None
        self.mini_heating_enabled: bool = None
        self.winter_mode_enabled: bool = None
        self.is_input_fan_on: bool = None
        self.is_output_fan_on: bool = None

    @property
    def speed(self):
        if not self.is_on:
            return 0
        return self.speed_locked if self.flows_locked else int((self.speed_in + self.speed_out) / 2)

    def __repr__(self):
        return "Prana state: {}, Speed: {}, Winter Mode: {}, Heating: {}, Flows locked: {}".format(
            'RUNNING' if self.is_on else 'IDLE',
            self.speed, self.winter_mode_enabled, self.mini_heating_enabled, self.flows_locked
        )
