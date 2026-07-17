# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2026 Avery Ramsey
#
# SPDX-License-Identifier: Unlicense

import board

import ds1302

# Set up the three interface pins
ce_pin = board.GP13
io_pin = board.GP14
ck_pin = board.GP15

# Instantiate the RTC
rtc = ds1302.DS1302(ce_pin, io_pin, ck_pin)

# Clear the user-accessible RAM
rtc.clear_ram()

# Write value 29 to RAM address 5
number = 29
rtc.write_ram_single(5, number)

# Read address 5 and print the value
data = rtc.read_ram_single(5)
print("Single value:", data)

# Checks whether the returned value is equal to 29
print("Match:", data == number)

# Write values of 1 to 10 addresses 16 to 25
array = bytearray([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
rtc.write_ram(16, array)

# Read addresses 16 to 25 and print the values
data_array = rtc.read_ram(16, 10)
print("Block Values:")
for value in data_array:
    print(value)

# Check whether data_array is equal to the original array
print("Match:", data_array == array)
