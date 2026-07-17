# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2026 Avery Ramsey
#
# SPDX-License-Identifier: MIT
"""
`ds1302`
================================================================================

CircuitPython driver for the Maxim Integrated / Analog Devices DS1302 Real Time Clock.


* Author(s): Avery Ramsey

Implementation Notes
--------------------

**Hardware:**

.. todo:: Add links to any specific hardware product page(s), or category page(s).
  Use unordered list & hyperlink rST inline format: "* `Link Text <url>`_"

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

"""

# imports

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/Elfking29/CircuitPython_DS1302.git"

from time import struct_time

import board
import digitalio
from micropython import const

_DIODE_1 = const(0x04)
_DIODE_2 = const(0x08)
_RESISTOR_2 = const(0x01)
_RESISTOR_4 = const(0x02)
_RESISTOR_8 = const(0x03)
try:
    import typing

    from microcontroller import Pin
except ImportError:
    pass


class DS1302:
    """DS1302 real-time clock"""

    def __init__(self, ce_pin: Pin, io_pin: Pin, ck_pin: Pin) -> None:
        """
        Create a DS1302 RTC

        :param microcontroller.Pin ce_pin: Chip Enable Pin
        :param microcontroller.Pin io_pin: I/O Pin
        :param microcontroller.Pin ck_pin: Clock Pin
        """

        self.__rs = digitalio.DigitalInOut(ce_pin)
        self.__io = digitalio.DigitalInOut(io_pin)
        self.__ck = digitalio.DigitalInOut(ck_pin)
        self.__rs.direction = digitalio.Direction.OUTPUT
        self.__io.direction = digitalio.Direction.OUTPUT
        self.__ck.direction = digitalio.Direction.OUTPUT
        self.__rs.value = 0
        self.__io.value = 0
        self.__ck.value = 0
        self.__buffer = bytearray(31)
        self.clock_enable = True

    @property
    def datetime(self) -> struct_time:
        """
        Current date and time from the RTC as a :class:`time.struct_time`.

        :return: Current date and time.
        :rtype: time.struct_time
        """

        data = [0, 0, 0, 0, 0, 0, 0]
        data[0] = self.__read(0xBF)
        for i in range(6):
            data[i + 1] = self.__read(0)
        self.__rs.value = 0
        second = self.bcdtodec(data[0] & ~(0x80))
        minute = self.bcdtodec(data[1] & ~(0x80))
        raw_hour = self.bcdtodec(data[2] & ~(0x80 | 0x40 | 0x20))
        pm = bool(data[2] & 0x20)
        if raw_hour == 12:
            hour = 12 if pm else 0
        else:
            hour = raw_hour + (12 if pm else 0)
        date = self.bcdtodec(data[3] & ~(0x80 | 0x40))
        month = self.bcdtodec(data[4] & ~(0x80 | 0x40 | 0x20))
        weekday = self.bcdtodec(data[5] & ~(0x80 | 0x40 | 0x20 | 0x10 | 0x08)) - 1
        year = 2000 + self.bcdtodec(data[6])
        mdays = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
        yday = mdays[month - 1] + date
        if ((year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)) and month > 2:
            yday += 1
        return struct_time((year, month, date, hour, minute, second, weekday, yday, -1))

    @datetime.setter
    def datetime(self, t: struct_time) -> None:
        """
        Set the current date and time.

        :param time.struct_time value: New date and time.
        """

        if not isinstance(t, struct_time):
            raise TypeError(f"Expected struct_time, got {type(t).__name__}.")
        data = [0, 0, 0, 0, 0, 0, 0]
        data[0] = (self.__read_reg(0x81) & 0x80) | (self.dectobcd(self.clamp(t.tm_sec, 0, 59)))
        data[1] = self.dectobcd(self.clamp(t.tm_min, 0, 59))
        if self.__read_reg(0x85) & 0x08:
            th = self.clamp(t.tm_hour, 0, 23) % 12
            th = th if th != 0 else 12
            data[2] = self.dectobcd(th) | 0x80
            if self.clamp(t.tm_hour, 0, 23) < 12:
                data[2] &= ~0x20
            else:
                data[2] |= 0x20
        else:
            data[2] = self.dectobcd(self.clamp(t.tm_hour, 0, 23)) & ~0x80
        data[3] = self.dectobcd(self.clamp(t.tm_mday, 1, 31))
        data[4] = self.dectobcd(self.clamp(t.tm_mon, 1, 12))
        data[5] = self.dectobcd(self.clamp(t.tm_wday + 1, 1, 7))
        data[6] = self.dectobcd(self.clamp(t.tm_year % 100, 0, 99))
        self.__setwp(False)
        self.__write(0xBE, data[0])
        for i in range(6):
            self.__write(0, data[i + 1])
        self.__setwp(True)

    @property
    def clock_enable(self) -> bool:
        return not bool(self.__read_reg(0x81) & 0x80)

    @clock_enable.setter
    def clock_enable(self, enable: bool) -> None:
        second = self.__read_reg(0x81)
        self.__write_reg(0x80, second & ~0x80 if enable else second | 0x80)

    @property
    def is_12_hour(self) -> bool:
        return bool(self.__read_reg(0x85) & 0x80)

    @is_12_hour.setter
    def is_12_hour(self, enable_12_hour: bool) -> None:
        hreg = self.__read_reg(0x85)
        if hreg & 0x80:
            hour = 12 * (hreg & 0x20) // 32 + self.bcdtodec(hreg & ~(0x80 | 0x40 | 0x20))
        else:
            hour = self.bcdtodec(hreg & ~(0x80 | 0x40))
        if enable_12_hour:
            th = self.clamp(hour, 0, 23) % 12
            th = th if th != 0 else 12
            data = self.dectobcd(th) | 0x80
            if self.clamp(hour, 0, 23) < 12:
                data &= ~0x20
            else:
                data |= 0x20
        else:
            data = self.dectobcd(self.clamp(hour, 0, 23)) & ~0x80
        self.__write_reg(0x84, data)

    @property
    def trickle_enable(self) -> bool:
        return self.__read_reg(0x91) & (0x80 | 0x40 | 0x20 | 0x10) == (0x80 | 0x20)

    @trickle_enable.setter
    def trickle_enable(self, enable: bool) -> None:
        if enable:
            self.__write_reg(
                0x90, self.__read_reg(0x91) & ~(0x80 | 0x40 | 0x20 | 0x10) | (0x80 | 0x20)
            )
        else:
            self.__write_reg(
                0x90, self.__read_reg(0x91) & ~(0x80 | 0x40 | 0x20 | 0x10) | (0x40 | 0x10)
            )

    @property
    def trickle_diode(self) -> int:
        return self.__read_reg(0x91) & (0x08 | 0x04)

    @trickle_diode.setter
    def trickle_diode(self, diode: int) -> None:
        if diode in {_DIODE_1, _DIODE_2}:
            self.__write_reg(0x90, self.__read_reg(0x91) & ~(0x04 | 0x08) | (diode))
        else:
            raise ValueError(f"Diode value {diode} is not {_DIODE_1} or {_DIODE_2}.")

    @property
    def trickle_resistor(self) -> int:
        return self.__read_reg(0x91) & (0x02 | 0x01)

    @trickle_resistor.setter
    def trickle_resistor(self, resistor: int) -> None:
        if resistor in {_RESISTOR_2, _RESISTOR_4, _RESISTOR_8}:
            self.__write_reg(0x90, self.__read_reg(0x91) & ~(0x01 | 0x02) | (resistor))
        else:
            raise ValueError(
                f"Resistor value {resistor} is not {_RESISTOR_2}, {_RESISTOR_4}, or {_RESISTOR_8}."
            )

    @staticmethod
    def bcdtodec(num: int) -> int:
        return ((num >> 4) * 10) + (num & 0x0F)

    @staticmethod
    def dectobcd(num: int) -> int:
        return ((num // 10) << 4) | (num % 10)

    @staticmethod
    def clamp(v: int, a: int, b: int) -> int:
        n, x = (a, b) if a < b else (b, a)
        return max(n, min(x, v))

    def __rwset(self, rw: bool) -> None:
        if not rw:  # Read
            self.__io.direction = digitalio.Direction.INPUT
        else:  # Write
            self.__io.direction = digitalio.Direction.OUTPUT

    def __setwp(self, wp: bool) -> None:
        self.__rs.value = 0
        self.__write(0x8E, 0x00 if not wp else 0x80)
        self.__rs.value = 0

    def __write(self, addr: int, val: int) -> None:
        if addr != 0:  # addr=0 cannot be the first read() call in a chain
            self.__rwset(True)
            self.__rs.value = 1
            for _ in range(8):
                self.__io.value = addr & 1
                self.__ck.value = 1
                self.__ck.value = 0
                addr >>= 1
        for _ in range(8):
            self.__io.value = val & 1
            self.__ck.value = 1
            self.__ck.value = 0
            val >>= 1

    def __read(self, addr: int) -> int:
        if addr != 0:  # addr=0 cannot be the first read() call in a chain
            self.__rwset(True)
            self.__rs.value = 1
            for _ in range(8):
                self.__io.value = addr & 1
                self.__ck.value = 1
                self.__ck.value = 0
                addr >>= 1
        data = 0
        self.__rwset(False)
        for i in range(8):
            if self.__io.value:
                data |= 1 << i
            self.__ck.value = 1
            self.__ck.value = 0
        return data

    def __read_reg(self, addr: int) -> int:
        data = self.__read(addr)
        self.__rs.value = 0
        return data

    def __write_reg(self, addr: int, val: int) -> None:
        self.__setwp(False)
        self.__write(addr, val)
        self.__setwp(True)

    def clear_ram(self) -> None:
        self.write_ram(0, bytes(31))

    def read_ram(self, offset: int, length: int = 1) -> bytearray:
        if not 0 <= offset <= 30:
            raise ValueError("Starting offset must be between 0 and 30, inclusive.")
        if offset + length > 31:
            raise IndexError(f"Read range {offset + length} exceeds RAM boundary")
        if offset == 0:
            self.__buffer[0] = self.__read(0xFF)
        else:
            self.__read(0xFF)
        for i in range(1, offset + length):
            if i < offset:
                self.__read(0)
            else:
                self.__buffer[i - offset] = self.__read(0)
        self.__rs.value = 0
        return self.__buffer[:length]

    def read_ram_single(self, offset: int) -> int:
        if not 0 <= offset <= 30:
            raise ValueError("Offset must be between 0 and 30, inclusive.")
        return self.__read_reg(0xC1 + offset * 2)

    def write_ram(self, offset: int, data: ReadableBuffer) -> None:
        if len(data) == 0:
            return
        if not 0 <= offset <= 30:
            raise ValueError("Starting offset must be between 0 and 30, inclusive.")
        if offset + len(data) > 31:
            raise IndexError(f"Write range {offset + len(data)} exceeds RAM boundary")
        for value in data:
            if not 0x00 <= value <= 0xFF:
                raise ValueError("All data values must be between 0 and 255")
        self.__setwp(False)
        if offset == 0:
            self.__write(0xFE, data[0])
            for i in range(1, len(data)):
                self.__write(0, data[i])
            self.__rs.value = 0
        else:
            for i in range(len(data)):
                self.__write(0xC0 + 2 * (offset + i), data[i])
        self.__setwp(True)

    def write_ram_single(self, offset: int, data: int) -> None:
        if not 0 <= offset <= 30:
            raise ValueError("Offset must be between 0 and 30, inclusive.")
        if not 0x00 <= data <= 0xFF:
            raise ValueError("Data must be between 0 and 255, inclusive.")
        self.__write_reg(0xC0 + offset * 2, data)
