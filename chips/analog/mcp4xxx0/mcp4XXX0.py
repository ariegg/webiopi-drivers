#   Copyright 2017 Andreas Riegg - t-h-i-n-x.net
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#   Changelog
#
#   1.0    2017-02-06    Initial release.
#
#   Config parameters
#
#   - chip         Integer   Value of the SPI CS address. Default is 0.
#   - speed        Integer   Value of the SPI clock frequency. Default is 10 MHz.
#   - vref         Float     Value of the analog reference voltage. Inherited
#                            from Analog abstraction. Can be used for voltage selection
#                            when the chips are used in potentiometer mode.
#   - channelCount Integer   The overall number of channels when wired in
#                            daisy chain (DC) configuration. Odd numbers are supported,
#                            in this case the last chip should be a single channel
#                            chip version. Assumes that all chips listen to one common
#                            chip select (CS) signal.
#   - bus          String    Name of the SPI bus.
#
#   Usage remarks
#
#   - You can set the speed but not every SPI bus implementation allows to select
#     an individual speed per chip or support every requested frequency.
#     In this case the parameter will be ignored (by the SPI bus driver).
#
#   Implementation remarks
#
#   - As the SPI interface of all chips is write-only and does not allow to
#     to read back the register values, those are cached in the driver to still
#     allow reading them.
#
#   - For that reason a reading of previous set values of the chips is not possible.
#     In order to assure a consistent value actively set all channels to a defined 
#     value at device startup if you want.
#

from webiopi.decorators.rest import request, response, api
from webiopi.utils.types import toint
from webiopi.devices.spi import SPI
from webiopi.devices.analog import DAC


class MCP4XXX0(DAC, SPI):

    WRITE_TO_POT_VALUE = 0b01 << 4
    SHUTDOWN_POT_VALUE = 0b10 << 4


#---------- Abstraction framework contracts ----------

    def __str__(self):
        return "%s(chip=%d)" %  (self.name, self.chip)


class MCP42XX0MULTI(MCP4XXX0):

#---------- Class initialisation ----------

    def __init__(self, chip, speed, vref, channelCount, name, bus):
        SPI.__init__(self, toint(chip), 0, 8, toint(speed), bus)
        DAC.__init__(self, channelCount, 8, float(vref))
        self.name = name
        self.values = [0x80 for i in range(channelCount)]

#---------- ADC abstraction related methods ----------

    def __analogRead__(self, channel, diff=False):
        return self.values[channel]

#---------- DAC abstraction related methods ----------

    def __analogWrite__(self, channel, value):
        self.__write__(channel, value, self.WRITE_TO_POT_VALUE)

#---------- Device methods that implement features including additional REST mappings ----------
        
    @api("Device", 3, "feature", "driver")
    @request("POST", "run/shutdown/%(channel)d")
    @response("%s")
    def shutdown(self, channel):
        self.checkAnalogChannel(channel)
        self.__shutdown__(channel)
        return "Channel %d shut down." % channel

    def __shutdown__(self, channel):
        self.__write__(channel, 0x00, self.SHUTDOWN_POT_VALUE)

#---------- Helper methods ----------

    def __write__(self, channel, value, command):
        d = bytearray(2)
        d[0] = command | (channel + 1)
        d[1] = value & 0xFF
        self.writeBytes(d)
        self.values[channel] = value


class MCP4XDC(MCP42XX0MULTI):

#---------- Class initialisation ----------

    def __init__(self, chip=0, speed=10000000, vref=5.0, channelCount=1, bus=None):
        MCP42XX0MULTI.__init__(self, chip, speed, vref, toint(channelCount), "MCP4XDC", bus)

#---------- Abstraction framework contracts ----------

    def __str__(self):
        return "%s(chip=%d channelCount=%d)" %  (self.name, self.chip, self.analogCount())

#---------- DAC abstraction related methods ----------

    def __analogWrite__(self, channel, value):
        self.__chainWrite__(channel, value, self.WRITE_TO_POT_VALUE)

#---------- Device methods that implement features ----------

    def __shutdown__(self, channel):
        self.__chainWrite__(channel, 0x00, self.SHUTDOWN_POT_VALUE)

#---------- Helper methods ----------
        
    def __chainWrite__(self, channel, value, command):
        channelCount = self.analogCount()
        byteCount = ((channelCount / 2) + (channelCount % 2)) * 2
        index = channel / 2 * 2
        d = bytearray(byteCount)
        # Fill array in inverse byte order (value -> command)
        d[index] = value & 0xFF
        d[index + 1] = command | ((channel % 2) + 1)
        # Reverse array
        data = bytearray(d[::-1])
        self.writeBytes(data)
        self.values[channel] = value
        

class MCP42010(MCP42XX0MULTI):

#---------- Class initialisation ----------

    def __init__(self, chip=0, speed=10000000, vref=5.0, bus=None):
        MCP42XX0MULTI.__init__(self, chip, speed, vref, 2, "MCP42010", bus)


class MCP42050(MCP42XX0MULTI):

#---------- Class initialisation ----------

    def __init__(self, chip=0, speed=10000000, vref=5.0, bus=None):
        MCP42XX0MULTI.__init__(self, chip, speed, vref, 2, "MCP42050", bus)


class MCP42100(MCP42XX0MULTI):

#---------- Class initialisation ----------

    def __init__(self, chip=0, speed=10000000, vref=5.0, bus=None):
        MCP42XX0MULTI.__init__(self, chip, speed, vref, 2, "MCP42100", bus)



class MCP42XX0SINGLE(MCP4XXX0):

#---------- Class initialisation ----------

    def __init__(self, chip, speed, vref, name, bus):
        SPI.__init__(self, toint(chip), 0, 8, toint(speed), bus)
        DAC.__init__(self, 1, 8, float(vref))
        self.name = name
        self.value = 0x80

#---------- ADC abstraction related methods ----------

    def __analogRead__(self, channel, diff=False):
        return self.value

#---------- DAC abstraction related methods ----------

    def __analogWrite__(self, channel, value):
        self.__write__(value, self.WRITE_TO_POT_VALUE)

#---------- Device methods that implement features including additional REST mappings ----------
        
    @api("Device", 3, "feature", "driver")
    @request("POST", "run/shutdown")
    @response("%s")
    def shutdown(self):
        self.__shutdown__()
        return "Channel shut down."

    def __shutdown__(self):
        self.__write__(0x00, self.SHUTDOWN_POT_VALUE)

#---------- Helper methods ----------

    def __write__(self, value, command):
        d = bytearray(2)
        d[0] = command | 0b1
        d[1] = value
        self.writeBytes(d)
        self.value = value


class MCP41010(MCP42XX0SINGLE):

#---------- Class initialisation ----------

    def __init__(self, chip=0, speed=10000000, vref=5.0, bus=None):
        MCP42XX0SINGLE.__init__(self, chip, speed, vref, "MCP41010", bus)


class MCP41050(MCP42XX0SINGLE):

#---------- Class initialisation ----------

    def __init__(self, chip=0, speed=10000000, vref=5.0, bus=None):
        MCP42XX0SINGLE.__init__(self, chip, speed, vref, "MCP41050", bus)


class MCP41100(MCP42XX0SINGLE):

#---------- Class initialisation ----------

    def __init__(self, chip=0, speed=10000000, vref=5.0, bus=None):
        MCP42XX0SINGLE.__init__(self, chip, speed, vref, "MCP41100", bus)


