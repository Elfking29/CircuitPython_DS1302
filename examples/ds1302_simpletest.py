# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2026 Avery Ramsey
#
# SPDX-License-Identifier: Unlicense

import time

import board

import ds1302

# Set up three pins
reset_pin = board.GP13
io_pin = board.GP14
clock_pin = board.GP15

# Instantiate the RTC
rtc = ds1302.DS1302(reset_pin, io_pin, clock_pin)

# Lookup table for names of days (nicer printing).
days = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")

if False:  # change to True if you want to set the time!
    #                     year, mon, date, hour, min, sec, wday, yday, isdst
    t = time.struct_time((2026, 7, 16, 12, 38, 0, 3, -1, -1))
    # you must set year, mon, date, hour, min, sec and weekday
    # isdst can be set but we don't do anything with it at this time
    # setting yearday doesn't do anything, but getting it will calculate it from the date
    print("Setting time to:", t)  # uncomment for debugging
    rtc.datetime = t
    print()

# Main loop:
while True:
    t = rtc.datetime
    # print(t)     # uncomment for debugging
    print(f"The date is {days[int(t.tm_wday)]} {t.tm_mday}/{t.tm_mon}/{t.tm_year}")
    print(f"The time is {t.tm_hour}:{t.tm_min:02}:{t.tm_sec:02}")
    time.sleep(1)  # wait a second
