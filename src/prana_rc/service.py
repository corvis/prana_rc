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
import datetime
import logging
from asyncio import AbstractEventLoop, Lock

import bleak
from typing import Dict, List, Union, Optional

from prana_rc import utils
from prana_rc.entity import PranaState, PranaDeviceInfo, Speed


class PranaDeviceManager(object):
    PRANA_DEVICE_NAME_PREFIXES = ["PRNAQaq", "PRANA"]

    def __init__(self, iface: str = "hci0", loop: Optional[AbstractEventLoop] = None) -> None:
        self.__ble_interface = iface
        self.__loop = loop
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__managed_devices: Dict["str", PranaDevice] = {}
        self.__lock = Lock()

    @classmethod
    def __is_prana_device(cls, dev: "bleak.backends.device.BLEDevice"):
        return dev.name and len(list(filter(dev.name.startswith, cls.PRANA_DEVICE_NAME_PREFIXES))) > 0

    @classmethod
    def __prana_dev_name_2_name(cls, dev_name: str):
        name = dev_name
        if dev_name:
            for prefix in cls.PRANA_DEVICE_NAME_PREFIXES:
                if dev_name.startswith(prefix):
                    name = dev_name.replace(prefix, "", 1)
                    break
        return name.strip()

    @classmethod
    def __addr_for_target(cls, target: Union[str, PranaDeviceInfo]) -> str:
        if isinstance(target, PranaDeviceInfo):
            address = target.address
        elif isinstance(target, str):
            address = target
        else:
            raise ValueError("Device must be specified either by mac address or by PranaDeviceInfo instance")
        return address

    async def discover(self, timeout: int = 5) -> List[PranaDeviceInfo]:
        """
        Listens to devices advertisement for TIMEOUT seconds and returns the list of discovered devices
        :param timeout: time to wait for devices in seconds
        :return: list of discovered devices
        """
        async with self.__lock:
            discovered_devs = await bleak.discover(timeout)
        return list(
            map(
                lambda dev: PranaDeviceInfo(
                    address=dev.address,
                    bt_device_name=(dev.name or "").strip(),
                    name=self.__prana_dev_name_2_name(dev.name),
                    rssi=dev.rssi,
                ),
                filter(PranaDeviceManager.__is_prana_device, discovered_devs),
            )
        )

    async def connect(self, target: Union[str, PranaDeviceInfo], timeout: float = 5, attempts=1) -> "PranaDevice":
        address = self.__addr_for_target(target)
        device = self.__managed_devices.get(address, None)
        if device is None:  # If not found in managed devices list
            device = PranaDevice(address, self.__loop, self.__ble_interface)
            self.__managed_devices[address] = device
        # if not await device.is_connected():
        attempts_left = attempts
        while attempts_left > 0:
            current_attempt = (attempts - attempts_left) + 1
            try:
                await device.connect(timeout)
                return device
            except Exception as e:
                if attempts == 1:
                    raise e
                self.__logger.warning("Connection failed. Attempt #{} Re-connecting...".format(current_attempt))
                attempts_left -= 1
                await asyncio.sleep(0.5)
        raise RuntimeError("Connection to device {} failed after {} attempts".format(address, attempts))

    async def disconnect_all(self):
        for dev in self.__managed_devices.values():
            await dev.disconnect()


class PranaDevice(object):
    CONTROL_SERVICE_UUID = "0000baba-0000-1000-8000-00805f9b34fb"
    CONTROL_RW_CHARACTERISTIC_UUID = "0000cccc-0000-1000-8000-00805f9b34fb"
    STATE_MSG_PREFIX = b"\xbe\xef"

    class Cmd:
        ENABLE_HIGH_SPEED = bytearray([0xBE, 0xEF, 0x04, 0x07])
        ENABLE_NIGHT_MODE = bytearray([0xBE, 0xEF, 0x04, 0x06])
        TOGGLE_FLOW_LOCK = bytearray([0xBE, 0xEF, 0x04, 0x09])
        TOGGLE_HEATING = bytearray([0xBE, 0xEF, 0x04, 0x05])
        TOGGLE_WINTER_MODE = bytearray([0xBE, 0xEF, 0x04, 0x16])

        SPEED_UP = bytearray([0xBE, 0xEF, 0x04, 0x0C])
        SPEED_DOWN = bytearray([0xBE, 0xEF, 0x04, 0x0B])
        SPEED_IN_UP = bytearray([0xBE, 0xEF, 0x04, 0x0E])
        SPEED_IN_DOWN = bytearray([0xBE, 0xEF, 0x04, 0x0F])
        SPEED_OUT_UP = bytearray([0xBE, 0xEF, 0x04, 0x11])
        SPEED_OUT_DOWN = bytearray([0xBE, 0xEF, 0x04, 0x12])

        FLOW_IN_OFF = bytearray([0xBE, 0xEF, 0x04, 0x0D])
        FLOW_OUT_OFF = bytearray([0xBE, 0xEF, 0x04, 0x10])

        STOP = bytearray([0xBE, 0xEF, 0x04, 0x01])
        READ_STATE = bytearray([0xBE, 0xEF, 0x05, 0x01, 0x00, 0x00, 0x00, 0x00, 0x5A])
        READ_DEVICE_DETAILS = bytearray([0xBE, 0xEF, 0x05, 0x02, 0x00, 0x00, 0x00, 0x00, 0x5A])

    def __init__(
        self,
        target: Union[str, PranaDeviceInfo],
        loop: Optional[AbstractEventLoop] = None,
        iface: str = "hci0",
    ) -> None:
        self.__address = None
        if isinstance(target, PranaDeviceInfo):
            self.__address = target.address
        elif isinstance(target, str):
            self.__address = target
        else:
            raise ValueError(
                "PranaDevice constructor error: Target must be eithermac address or PranaDeviceInfo instance"
            )
        self.__client = bleak.BleakClient(self.__address, device=iface)
        self.__has_connect_attempts = False
        self.__notification_bytes: Optional[bytearray] = None
        self.__state: Optional[PranaState] = None
        self.__read_state_event: Optional[asyncio.Event] = None
        self.__lock = Lock()
        self.__logger = logging.getLogger(self.__class__.__name__)

    async def __verify_connected(self):
        if not await self.is_connected():
            raise RuntimeError("Illegal state: device must be connected before running any commands")

    def notification_handler(self, sender, data):
        """Simple notification handler which prints the data received."""
        self.__notification_bytes = data
        # Notify waiters
        if self.__read_state_event is not None:
            self.__read_state_event.set()

    async def connect(self, timeout: float = 2):
        async with self.__lock:
            if not await self.is_connected():
                await self.__client.connect(timeout=timeout)
                self.__has_connect_attempts = True
                await self.__client.start_notify(self.CONTROL_RW_CHARACTERISTIC_UUID, self.notification_handler)
                # TODO: shall we subscribe for disconnect callback and change status?
                # TODO: Verify prana service exists to ensure it is prana device

    async def disconnect(self):
        async with self.__lock:
            await self.__client.disconnect()

    async def is_connected(self):
        if not self.__has_connect_attempts:
            return False
        try:
            return await self.__client.is_connected()
        except Exception:
            self.__logger.error("Is Connected: Failed to verify connection status")
            return False

    async def _send_command(self, command: bytearray, expect_reply=False):
        async with self.__lock:
            # Invalidate state
            self.__state = None
            await self.__client.write_gatt_char(self.CONTROL_RW_CHARACTERISTIC_UUID, command, response=expect_reply)
            if expect_reply:
                self.__read_state_event = asyncio.Event()
                await asyncio.wait_for(self.__wait_for_read_event(), timeout=1)
                return self.__notification_bytes
            # await asyncio.sleep(0.6)
            # result = await self.__client.read_gatt_char(self.CONTROL_RW_CHARACTERISTIC_UUID, use_cached=False)
            # if expect_reply:
            #     return result

    async def set_high_speed(self):
        await self.__verify_connected()
        await self._send_command(self.Cmd.ENABLE_HIGH_SPEED)

    async def speed_up(self):
        await self.__verify_connected()
        await self._send_command(self.Cmd.SPEED_UP)

    async def speed_down(self):
        await self.__verify_connected()
        await self._send_command(self.Cmd.SPEED_DOWN)

    async def set_low_speed(self):
        await self.__verify_connected()
        await self._send_command(self.Cmd.ENABLE_NIGHT_MODE)

    async def set_night_mode(self):
        await self.__verify_connected()
        await self._send_command(self.Cmd.ENABLE_NIGHT_MODE)

    async def set_normal_speed(self):
        await self.set_speed(Speed.SPEED_3)

    async def set_speed(self, speed: Speed):
        if speed == Speed.LOW:
            await self.set_low_speed()
        elif speed == Speed.HIGH:
            await self.set_high_speed()
        elif speed == Speed.OFF:
            await self.turn_off()
        else:
            # Other speeds couldn't be set with one single command
            direction_up = speed.value <= 5
            if direction_up:
                await self.set_low_speed()
                counter = Speed.LOW.value
                while counter != speed.value:
                    await self.speed_up()
                    counter += 1
            else:
                await self.set_high_speed()
                counter = Speed.HIGH.value
                while counter != speed.value:
                    await self.speed_down()
                    counter -= 1

    async def set_heating(self, enable: bool):
        state = await self.read_state()
        if state.mini_heating_enabled != enable:
            await self._send_command(self.Cmd.TOGGLE_HEATING)

    async def set_winter_mode(self, enable: bool):
        state = await self.read_state()
        if state.winter_mode_enabled != enable:
            await self._send_command(self.Cmd.TOGGLE_WINTER_MODE)

    async def turn_off(self):
        await self.__verify_connected()
        await self._send_command(self.Cmd.STOP)

    async def turn_on(self, speed=Speed.SPEED_3):
        await self.set_speed(speed)

    def __parse_state(self, data: bytearray) -> Optional[PranaState]:
        if not data[:2] == self.STATE_MSG_PREFIX:
            return None
        s = PranaState()
        s.timestamp = datetime.datetime.now()
        s.speed_locked = int(data[26] / 10)
        s.speed_in = int(data[30] / 10)
        s.speed_out = int(data[34] / 10)
        s.auto_mode = bool(data[20])
        s.night_mode = bool(data[16])
        s.flows_locked = bool(data[22])
        s.is_on = bool(data[10])
        s.mini_heating_enabled = bool(data[14])
        s.winter_mode_enabled = bool(data[42])
        s.is_input_fan_on = bool(data[28])
        s.is_output_fan_on = bool(data[32])
        return s

    async def read_state(self, force_read: bool = False) -> PranaState:
        """
        Read state from the devcie and return it as an object
        :param force_read: If set, cached state will be ignored and read command to the device will be generated
        :return:
        """
        await self.__verify_connected()
        state_bin = await self._send_command(self.Cmd.READ_STATE, expect_reply=True)
        state = self.__parse_state(state_bin)
        if state is not None:
            self.__state = state
        return utils.none_throws(state)

    async def __wait_for_read_event(self):
        if self.__read_state_event is not None:
            await self.__read_state_event.wait()

    def __has_relevant_state(self) -> bool:
        return not (
            self.__state is None
            or (datetime.datetime.now() - utils.none_throws(self.__state.timestamp)).total_seconds() > 60
        )
