# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2022 ladyada for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_pcf8574`
================================================================================

Python library for PCF8574 GPIO expander


* Author(s): ladyada

Implementation Notes
--------------------

**Hardware:**

* `Adafruit PCF8574 GPIO Expander <https://www.adafruit.com/product/5545>`

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads
* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice

"""

try:
    # This is only needed for typing
    import busio  # pylint: disable=unused-import
except ImportError:
    pass


from adafruit_bus_device.i2c_device import I2CDevice
from micropython import const
import digitalio

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_PCF8574.git"


PCF8574_I2CADDR_DEFAULT: int = const(0x20)  # Default I2C address

class PCF8574:
    """
    Interface library for PCF8574 GPIO expanders
    :param ~busio.I2C i2c_bus: The I2C bus the PCF8574 is connected to.
    :param int address: The I2C device address. Default is :const:`0x20`
    """

    def __init__(
        self, i2c_bus: busio.I2C, address: int = PCF8574_I2CADDR_DEFAULT
    ) -> None:
        self.i2c_device = I2CDevice(i2c_bus, address)
        self._writebuf = bytearray(1)
        self._readbuf = bytearray(1)

    def get_pin(self, pin):
        """Convenience function to create an instance of the DigitalInOut class
        pointing at the specified pin of this PCF8574 device.
        :param int pin: pin to use for digital IO, 0 to 7
        """
        assert 0 <= pin <= 7
        return DigitalInOut(pin, self)

    def write_gpio(self, val):
        self._writebuf[0] = val & 0xFF
        with self.i2c_device as i2c:
            i2c.write(self._writebuf)

    def read_gpio(self):
        with self.i2c_device as i2c:
            i2c.readinto(self._readbuf)
        return self._readbuf[0]

"""
`digital_inout`
====================================================
Digital input/output of the MCP230xx.
* Author(s): Tony DiCola
"""

# Internal helpers to simplify setting and getting a bit inside an integer.
def _get_bit(val, bit):
    return val & (1 << bit) > 0


def _enable_bit(val, bit):
    return val | (1 << bit)


def _clear_bit(val, bit):
    return val & ~(1 << bit)


class DigitalInOut:
    """Digital input/output of the PCF8574.  The interface is exactly the
    same as the digitalio.DigitalInOut class, however:
      * PCF8574 does not support pull-down resistors
      * PCF8574 does not actually have a sourcing transistor, instead there's
      an internal pullup
    Exceptions will be thrown when attempting to set unsupported pull
    configurations.
    """

    def __init__(self, pin_number, pcf):
        """Specify the pin number of the PCF8574 0..7, and instance."""
        self._pin = pin_number
        self._pcf = pcf

    # kwargs in switch functions below are _necessary_ for compatibility
    # with DigitalInout class (which allows specifying pull, etc. which
    # is unused by this class).  Do not remove them, instead turn off pylint
    # in this case.
    # pylint: disable=unused-argument
    def switch_to_output(self, value=False, **kwargs):
        """Switch the pin state to a digital output with the provided starting
        value (True/False for high or low, default is False/low).
        """
        self.direction = digitalio.Direction.OUTPUT
        self.value = value

    def switch_to_input(self, pull=None, **kwargs):
        """Switch the pin state to a digital input with the provided starting
        pull-up resistor state (optional, no pull-up by default) and input polarity.  Note that
        pull-down resistors are NOT supported!
        """
        self.direction = digitalio.Direction.INPUT
        self.pull = pull

    # pylint: enable=unused-argument

    @property
    def value(self):
        """The value of the pin, either True for high or False for
        low.  Note you must configure as an output or input appropriately
        before reading and writing this value.
        """
        return _get_bit(self._aw.inputs, self._pin)

    @value.setter
    def value(self, val):
        if val:
            self._aw.outputs = _enable_bit(self._aw.outputs, self._pin)
        else:
            self._aw.outputs = _clear_bit(self._aw.outputs, self._pin)

    @property
    def direction(self):
        """The direction of the pin, either True for an input or
        False for an output.
        """
        if _get_bit(self._aw.direction, self._pin):
            return digitalio.Direction.INPUT
        return digitalio.Direction.OUTPUT

    @direction.setter
    def direction(self, val):
        if val == digitalio.Direction.INPUT:
            self._aw.directions = _clear_bit(self._aw.directions, self._pin)

        elif val == digitalio.Direction.OUTPUT:
            self._aw.directions = _enable_bit(self._aw.directions, self._pin)
        else:
            raise ValueError("Expected INPUT or OUTPUT direction!")

    @property
    def pull(self):
        """
        Pull-down resistors are NOT supported!
        """
        raise NotImplementedError("Pull-down resistors not supported.")

    @pull.setter
    def pull(self, val):  # pylint: disable=no-self-use
        if val is not None:
            raise NotImplementedError("Pull-up/pull-down resistors not supported.")
