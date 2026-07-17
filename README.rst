Introduction to the DS1302 Real Time Clock (RTC) Library
========================================================


.. image:: https://readthedocs.org/projects/circuitpython-ds1302/badge/?version=latest
    :target: https://circuitpython-ds1302.readthedocs.io/
    :alt: Documentation Status



.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/Elfking29/CircuitPython_DS1302/workflows/Build%20CI/badge.svg
    :target: https://github.com/Elfking29/CircuitPython_DS1302/actions
    :alt: Build Status


.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Code Style: Ruff

The DS1302 is a small battery-backed real time clock (RTC) that allows your microcontroller project to keep track of time even if it is reprogrammed, or if the power is lost. This is perfect for clocks, datalogging, timers, etc. The DS1302 also features a trickle charger for the battery so you never need to change batteries.

The DS1302 is simple and inexpensive but not a high precision device. It may lose or gain up to two seconds a day. In addition, it communicates over a custom serial protocol. For a high-precision, temperature compensated, alternative, please check out the `DS3231 precision RTC <https://www.adafruit.com/products/5188>`_, which communicates over I2C.


Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.

Installing from PyPI
=====================
.. note:: This library is not available on PyPI yet. Install documentation is included
   as a standard element. Stay tuned for PyPI availability!

.. todo:: Remove the above note if PyPI version is/will be available at time of release.

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/circuitpython-ds1302/>`_.
To install for current user:

.. code-block:: shell

    pip3 install circuitpython-ds1302

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install circuitpython-ds1302

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .venv
    source .env/bin/activate
    pip3 install circuitpython-ds1302

Installing to a Connected CircuitPython Device with Circup
==========================================================

Make sure that you have ``circup`` installed in your Python environment.
Install it with the following command if necessary:

.. code-block:: shell

    pip3 install circup

With ``circup`` installed and your CircuitPython device connected use the
following command to install:

.. code-block:: shell

    circup install ds1302

Or the following command to update an existing version:

.. code-block:: shell

    circup update

Usage Example
=============

Basics
------

Of course, you must import the library to use it:

.. code:: python3

    import time
    import board
    import ds1302

The DS1302 requires three pins: Reset, I/O, and Clock. These can be any 3 pins as long as they support digital output (and in the case of I/O, digital input):

.. code:: python3

    import board
    reset_pin = board.GP13
    io_pin = board.GP14
    clock_pin = board.GP15

Now, you can use these pins to instantiate the RTC object:

.. code:: python3

    rtc = ds1302.DS1302(reset_pin, io_pin, clock_pin)

To set the time, you need to set ``datetime`` to a `time.struct_time` object:

.. code:: python

    rtc.datetime = time.struct_time((2026,7,16,23,38,0,3,194,-1))

After the RTC is set, you retrieve the time by reading the `datetime`
attribute and access the standard attributes of a struct_time such as ``tm_year``,
``tm_hour`` and ``tm_min``.

.. code:: python3

    t = rtc.datetime
    print(t)
    print(t.tm_hour, t.tm_min)


Documentation
=============
API documentation for this library can be found on `Read the Docs <https://circuitpython-ds1302.readthedocs.io/>`_.

For information on building library documentation, please check out
`this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/Elfking29/CircuitPython_DS1302/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
