#   Copyright 2016 Andreas Riegg - t-h-i-n-x.net
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
#   1.0    2016/08/25    Initial release
#
#   Config parameters
#
#   - time          Float       Integration time of the chip in ms. Valid values
#                               are in the range 2.4 to 614.4 ms. Default is 38.4
#                               ms which represents a 14 bit resolution.
#   - gain          Integer     Gain value of the chip. Valid values are from
#                               (1, 4, 16 , 60). Default is 16.
#   - relative      Boolean     Calculate the RGB result relative to the current
#                               brightness of the highest RGB channel.
#                               Default is "Yes".
#   - auto          Boolean     Adjust the gain automatically depending on the
#                               current saturation of the highest RGB channel.
#                               default is "No".
#   - bus           String      Name of the I2C bus
#
#   Usage remarks
#
#   - Slave address defaults to 0x29 or 0x39 depending on chip sub-version.
#   - If you encounter overexposure/saturation (getting RGB like #FFFFFF or very
#     close to this) try to reduce gain/and or change time or try the auto
#     feature.
#
#   Implementation remarks
#
#   - This driver is implemented based on the specs from ams (formerly TAOS).
#   - When using the relative mode this driver enlightens the RGB values
#     based on the value of the highest RGB channel. This makes the colors better
#     viewable for human eyes when detecting darker colors or in darker
#     environments. If you want to have the original raw values set relative to "No".
#   - This driver has an auto gain feature that can help to adjust the gain
#     based on the saturation of the highest RGB channel. Using this may bring
#     the clear channel to saturation before the RGB channels. Use auto="Yes" to
#     activate this feature, but it will not help in every situation so its default
#     is set to "No".
#   - The driver scales the 16 bit raw values (being measured depending on the time
#     parameter between 10 bits and 16 bits) using the max_count to a normalized
#     scale from 0 to 65535 (full 16 bit).
#   - The chip spec does not clearly indicate how to calculate the correct lux value
#     based on the clear channel. For this an asumption how to estimate this has been
#     made. In order to get better values use a dedicated light sensor instead.
#   - This driver has a simple white balance feature. If requested, it adjusts the
#     measured RGB values to be equal to #FFFFFF for the light situation when the
#     set white command is sent. White balance can be reset by calling the set
#     to neutral feature.
#   - This driver does currently not support the wait and the interrupt functions
#     of the chip.
#

from webiopi.utils.logger import debug
from webiopi.decorators.rest import request, response, api
from webiopi.utils.types import toint, str2bool
from webiopi.devices.i2c import I2C
from webiopi.devices.sensor import Color, Luminosity


#---------- Abstract class for the TCS3472. chip variants ----------

class TCS3472X(I2C, Color, Luminosity):
    VAL_COMMAND         = 0x80
    VAL_AUTOINCREMENT   = 1 << 5

    REG_ENABLE          = 0x00 | VAL_COMMAND
    REG_RGBC_TIMING     = 0x01 | VAL_COMMAND
   #REG_WAIT_TIME       = 0x03 | VAL_COMMAND
   #REG_CONFIGURATION   = 0x0D | VAL_COMMAND
    REG_CONTROL         = 0x0F | VAL_COMMAND
   #REG_STATUS          = 0x13 | VAL_COMMAND
    REG_CLEARDATA_START = 0x14 | VAL_COMMAND | VAL_AUTOINCREMENT
    REG_RGBDATA_START   = 0x16 | VAL_COMMAND | VAL_AUTOINCREMENT

    VAL_PWON            = 0x03
    VAL_PWOFF           = 0x00

    VAL_MIN_ATIME       = 0x00
    VAL_MAX_ATIME       = 0xFF
    VAL_MIN_TIME        = 2.4
    VAL_MAX_TIME        = 614.4
    VAL_MAX_COUNT_BASE  = 1024
    VAL_MAX_COUNT_MAX   = 65535

    VAL_GAIN_01         = 0b00000000
    VAL_GAIN_04         = 0b00000001
    VAL_GAIN_16         = 0b00000010
    VAL_GAIN_60         = 0b00000011

#---------- Class initialisation ----------

    def __init__(self, slave, time, gain, relative, auto, name, bus):
        I2C.__init__(self, toint(slave), bus)
        self._max_count = self.VAL_MAX_COUNT_BASE
        self._red_scale = 1.0
        self._green_scale = 1.0
        self._blue_scale = 1.0
        self.name = name
        self.wake()
        self.setRelative(str2bool(relative))
        self.setAuto(str2bool(auto))
        self.setTime(float(time))
        self.setGain(toint(gain))

#---------- Abstraction framework contracts ----------

    def __str__(self):
        return "%s(slave=0x%02X, dev=%s)" % (self.name, self.slave, self.device())

    def __family__(self):
        return [Color.__family__(self), Luminosity.__family__(self)]


#---------- Color abstraction related methods ----------

    def __getRGB__(self):
        # Expected result: tuple r,g,b all values integer between 0 and 255
        r16, g16, b16 = self.__getRGB16bpp__()
        return (r16/256, g16/256, b16/256)

    def __getRGB16bpp__(self):
        # Expected result: tuple r,g,b all values integer between 0 and 65535
        rgb_bytes  = self.readRegisters(self.REG_RGBDATA_START, 6)
        red_word   = (rgb_bytes[1] << 8 | rgb_bytes[0]) * self._red_scale
        green_word = (rgb_bytes[3] << 8 | rgb_bytes[2]) * self._green_scale
        blue_word  = (rgb_bytes[5] << 8 | rgb_bytes[4]) * self._blue_scale

        counting_scale = self.__calculateCountingScale__()
        brightness = self.__calculateRelativeBrightnessRGB__(red_word, green_word, blue_word)
        debug("%s: raw_red=%d, raw_green=%d, raw_blue=%d, counting scale=%.2f, relative brightness=%.2f" %
              (self.__str__(), red_word, green_word, blue_word, counting_scale, brightness))

        if self._relative and brightness > 0:
            brightness_factor = brightness
        else:
            brightness_factor = 1.0
        red16 = int(round(red_word * counting_scale / brightness_factor))
        if red16   > self.VAL_MAX_COUNT_MAX:
            red16   = self.VAL_MAX_COUNT_MAX
        green16 = int(round(green_word * counting_scale / brightness_factor))
        if green16 > self.VAL_MAX_COUNT_MAX:
            green16 = self.VAL_MAX_COUNT_MAX
        blue16 = int(round(blue_word * counting_scale / brightness_factor))
        if blue16  > self.VAL_MAX_COUNT_MAX:
            blue16  = self.VAL_MAX_COUNT_MAX

        if self._auto:
            if brightness > 0.9:
                self.__reduceGain__()
            elif brightness < 0.1:
                self.__enlargeGain__()

        return (red16, green16, blue16)

#---------- Color helper methods ----------

    def __calculateCountingScale__(self):
        return self.VAL_MAX_COUNT_MAX / float(self._max_count)

    def __calculateRelativeBrightnessRGB__(self, red_count, green_count, blue_count):
        brightness = max(red_count, green_count, blue_count) / float(self._max_count)
        if brightness > 1.0:
            return 1.0
        else:
            return brightness

    def __reduceGain__(self):
        if self._gain == 1:
            return
        if self._gain == 60:
            new_gain = 16
        else:
            new_gain = self._gain / 4
        self.__setGain__(new_gain)

    def __enlargeGain__(self):
        if self._gain == 60:
            return
        if self._gain == 16:
            new_gain = 60
        else:
            new_gain = self._gain * 4
        self.__setGain__(new_gain)

#---------- Luminosity abstraction related methods ----------

    def __getLux__(self):
        clear_bytes  = self.readRegisters(self.REG_CLEARDATA_START, 2)
        clear_word   = clear_bytes[1] << 8 | clear_bytes[0]
        debug("%s: raw_clear=%d" % (self.__str__(), clear_word))
        return self.__calculateLux__(clear_word)

    def __calculateLux__(self, clear_value):
        # Value from chip spec: 16 counts per lux when time = 24 ms and gain = 16
        return clear_value * 24.0 / self._time / self._gain


#---------- Device methods that implement features including additional REST mappings ----------

    @api("Device", 3, "feature", "driver")
    @request("POST", "run/wake")
    @response("%s")
    def wake(self):
        self.__wake__()
        return "Chip is waken up."

    def __wake__(self):
        self.writeRegister(self.REG_ENABLE, self.VAL_PWON)

    @api("Device", 3, "feature", "driver")
    @request("POST", "run/sleep")
    @response("%s")
    def sleep(self):
        self.__sleep__()
        return "Chip sent to sleep."

    def __sleep__(self):
        self.writeRegister(self.REG_ENABLE, self.VAL_PWOFF)

    @api("Device", 3, "feature", "driver")
    @request("POST", "run/setwhite")
    @response("%s")
    def setWhite(self):
        self.__setWhite__()
        return "Current color output set to white."

    def __setWhite__(self):
        rgb_bytes  = self.readRegisters(self.REG_RGBDATA_START, 6)
        red_word   = rgb_bytes[1] << 8 | rgb_bytes[0]
        green_word = rgb_bytes[3] << 8 | rgb_bytes[2]
        blue_word  = rgb_bytes[5] << 8 | rgb_bytes[4]

        lowest = min(red_word, green_word, blue_word)
        self._red_scale   = float(lowest) / red_word
        self._green_scale = float(lowest) / green_word
        self._blue_scale  = float(lowest) / blue_word
        debug("%s: setwhite red_scale=%.2f, green_scale=%.2f, blue_scale=%.2f" % (self.__str__(), self._red_scale, self._green_scale, self._blue_scale))

    @api("Device", 3, "feature", "driver")
    @request("POST", "run/setneutral")
    @response("%s")
    def setNeutral(self):
        self.__setNeutral__()
        return "Color output set to neutral."

    def __setNeutral__(self):
        self._red_scale   = 1.0
        self._green_scale = 1.0
        self._blue_scale  = 1.0
        debug("%s: setneutral red_scale=%.2f, green_scale=%.2f, blue_scale=%.2f" % (self.__str__(), self._red_scale, self._green_scale, self._blue_scale))


#---------- Device methods that implement chip configuration settings including additional REST mappings ----------

    @api("Device", 3, "configuration", "driver")
    @request("POST", "configure/time/%(time)f")
    @response("%.1f")
    def setTime(self, time):
        self.__setTime__(time)
        return self.__getTime__()

    @api("Device", 3, "configuration", "driver")
    @request("GET", "configure/time")
    @response("%.1f")
    def getTime(self):
        return self.__getTime__()

    def __setTime__(self, time):
        if time < self.VAL_MIN_TIME or time > self.VAL_MAX_TIME:
            raise ValueError("Parameter time:%.1f out of allowed range [%.1f .. %.1f]" % (time, self.VAL_MIN_TIME, self.VAL_MAX_TIME))
        atime = int(round(256 - (time / self.VAL_MIN_TIME)))
        if atime < self.VAL_MIN_ATIME:
            atime = self.VAL_MIN_ATIME
        if atime > self.VAL_MAX_ATIME:
            atime = self.VAL_MAX_ATIME
        self.writeRegister(self.REG_RGBC_TIMING, atime)
        self._time = (256 - atime) * self.VAL_MIN_TIME
        self._max_count = (256 - atime) * self.VAL_MAX_COUNT_BASE
        if self._max_count > self.VAL_MAX_COUNT_MAX:
            self._max_count = self.VAL_MAX_COUNT_MAX
        debug("%s: requested time=%.1f, set time=%.1f, max count=%d" % (self.__str__(), time, self._time, self._max_count))

    def __getTime__(self):
        atime = self.readRegister(self.REG_RGBC_TIMING) & 0xFF
        self._time = (256 - atime) * self.VAL_MIN_TIME
        return self._time

    @api("Device", 3, "configuration", "driver")
    @request("POST", "configure/gain/%(gain)d")
    @response("%d")
    def setGain(self, gain):
        self.__setGain__(gain)
        return self.__getGain__()

    @api("Device", 3, "configuration", "driver")
    @request("GET", "configure/gain")
    @response("%d")
    def getGain(self):
        return self.__getGain__()

    def __setGain__(self, gain):
        if gain not in (1, 4, 16, 60):
            raise ValueError("Parameter gain:%d not one of the allowed values (1, 4, 16, 60)" % gain)
        self._gain = gain
        if gain   ==  1:
            bits_gain =  self.VAL_GAIN_01
        elif gain ==  4:
            bits_gain =  self.VAL_GAIN_04
        elif gain == 16:
            bits_gain =  self.VAL_GAIN_16
        elif gain == 60:
            bits_gain =  self.VAL_GAIN_60
        self.writeRegister(self.REG_CONTROL, bits_gain & 0xFF)
        debug("%s: set gain=%d" % (self.__str__(), gain))

    def __getGain__(self):
        bits_gain = self.readRegister(self.REG_CONTROL) & 0xFF
        if bits_gain   == self.VAL_GAIN_01:
            self._gain =  1
        elif bits_gain == self.VAL_GAIN_04:
            self._gain =  4
        elif bits_gain == self.VAL_GAIN_16:
            self._gain = 16
        elif bits_gain == self.VAL_GAIN_60:
            self._gain = 60
        return self._gain

    @api("Device", 3, "configuration", "driver")
    @request("POST", "configure/relative/%(relative)b")
    @response("%s")
    def setRelative(self, relative):
        self._relative = relative
        debug("%s: set relative=%s" % (self.__str__(), relative))
        return relative

    @api("Device", 3, "configuration", "driver")
    @request("GET", "configure/relative")
    @response("%s")
    def getRelative(self):
        return self._relative

    @api("Device", 3, "configuration", "driver")
    @request("POST", "configure/auto/%(auto)b")
    @response("%s")
    def setAuto(self, auto):
        self._auto = auto
        debug("%s: set auto=%s" % (self.__str__(), auto))
        return auto

    @api("Device", 3, "configuration", "driver")
    @request("GET", "configure/auto")
    @response("%s")
    def getAuto(self):
        return self._auto


#---------- Device classes for the TCS3472. chip variants ----------

class TCS34721(TCS3472X):
    def __init__(self, time=38.4, gain=16, relative="Yes", auto="No", bus=None):
        TCS3472X.__init__(self, 0x39, time, gain, relative, auto, "TCS34721", bus)

class TCS34723(TCS3472X):
    def __init__(self, time=38.4, gain=16, relative="Yes", auto="No", bus=None):
        TCS3472X.__init__(self, 0x39, time, gain, relative, auto, "TCS34723", bus)

class TCS34725(TCS3472X):
    def __init__(self, time=38.4, gain=16, relative="Yes", auto="No", bus=None):
        TCS3472X.__init__(self, 0x29, time, gain, relative, auto, "TCS34725", bus)

class TCS34727(TCS3472X):
    def __init__(self, time=38.4, gain=16, relative="Yes", auto="No", bus=None):
        TCS3472X.__init__(self, 0x29, time, gain, relative, auto, "TCS34727", bus)

