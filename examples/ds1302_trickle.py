# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2026 Avery Ramsey
#
# SPDX-License-Identifier: Unlicense

# WARNING:
# Only enable the trickle charger when using a rechargeable backup
# power source and an appropriate charging configuration.
# Incorrect use may damage the backup battery or power source.
# See page 7 of the DS1302 datasheet for details:
# https://www.analog.com/media/en/technical-documentation/data-sheets/ds1302.pdf

import board

import ds1302

# Set up the three interface pins
ce_pin = board.GP13
io_pin = board.GP14
ck_pin = board.GP15

# Instantiate the RTC
rtc = ds1302.DS1302(ce_pin, io_pin, ck_pin)

# Use one diode in the trickle charger
rtc.trickle_diode = ds1302.TRICKLE_DIODE_1

# Set the trickle charger resistance to 4kΩ
rtc.trickle_resistor = ds1302.TRICKLE_RESISTOR_4

# Enable the trickle charger
rtc.trickle_enable = True
