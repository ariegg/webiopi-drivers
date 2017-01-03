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
#   ----------------------------------------------------------------------------
#
#   Changelog
#
#   1.0    2016-07-28    Initial release.
#   1.1    2016-08-12    Fixed Color 16bpp bug.
#   1.2    2016-09-26    Added all SENSORS class.
#   1.3    2016-12-12    Added CURRENT, VOLTAGE and POWER classes.
#

from webiopi.devices.sensor import Pressure
from webiopi.devices.sensor import Temperature
from webiopi.devices.sensor import Luminosity
from webiopi.devices.sensor import Distance
from webiopi.devices.sensor import Humidity
from webiopi.devices.sensor import Color
from webiopi.devices.sensor import Current
from webiopi.devices.sensor import Voltage
from webiopi.devices.sensor import Power
from webiopi.utils.types import toint
import random


class PRESSURE(Pressure):
    def __init__(self, altitude=0, external=None, lower=0, upper=100000):
        Pressure.__init__(self, altitude, external)
        self.lower = toint(lower)
        self.upper = toint(upper)

    def __str__(self):
        return "PRESSURE"

    def __getPascal__(self):
        return round(random.uniform(self.lower, self.upper), 0)

class TEMPERATURE(Temperature):
    def __init__(self, lower=0, upper=100, digits=1):
        self.lower = toint(lower)
        self.upper = toint(upper)
        self.digits = toint(digits)

    def __str__(self):
        return "TEMPERATURE"

    def __getKelvin__(self):
        return self.Celsius2Kelvin()

    def __getCelsius__(self):
        return round(random.uniform(self.lower, self.upper), self.digits)

    def __getFahrenheit__(self):
        return self.Celsius2Fahrenheit()

class LUMINOSITY(Luminosity):
    def __init__(self, lower=0, upper=100000, digits=0):
        self.lower = toint(lower)
        self.upper = toint(upper)
        self.digits = toint(digits)

    def __str__(self):
        return "LUMINOSITY"

    def __getLux__(self):
        return round(random.uniform(self.lower, self.upper), self.digits)

class DISTANCE(Distance):
    def __init__(self, lower=0, upper=1000, digits=1):
        self.lower = toint(lower)
        self.upper = toint(upper)
        self.digits = toint(digits)

    def __str__(self):
        return "DISTANCE"

    def __getMillimeter__(self):
        return round(random.uniform(self.lower, self.upper), self.digits)

class HUMIDITY(Humidity):
    def __init__(self, lower=0, upper=1, digits=2):
        self.lower = toint(lower)
        self.upper = toint(upper)
        self.digits = toint(digits)

    def __str__(self):
        return "HUMIDITY"

    def __getHumidity__(self):
        return round(random.uniform(self.lower, self.upper), self.digits)

class COLOR(Color):
    def __init__(self, rlower=0x00, rupper=0xFF, glower=0x00, gupper=0xFF, blower=0x00, bupper=0xFF):
        self.rlower = toint(rlower) & 0xFF
        self.rupper = toint(rupper) & 0xFF
        self.glower = toint(glower) & 0xFF
        self.gupper = toint(gupper) & 0xFF
        self.blower = toint(blower) & 0xFF
        self.bupper = toint(bupper) & 0xFF

    def __str__(self):
        return "COLOR"

    def __getRGB__(self):
        red = random.randint(self.rlower, self.rupper)
        green = random.randint(self.glower, self.gupper)
        blue = random.randint(self.blower, self.bupper)
        return red, green, blue

    def __getRGB16bpp__(self):
        red, green, blue = self.__getRGB__()
        return red*256, green*256, blue*256

class CURRENT(Current):
    def __init__(self, lower=0, upper=1000, digits=1):
        self.lower = toint(lower)
        self.upper = toint(upper)
        self.digits = toint(digits)

    def __str__(self):
        return "CURRENT"

    def __getMilliampere__(self):
        return round(random.uniform(self.lower, self.upper), self.digits)

class VOLTAGE(Voltage):
    def __init__(self, lower=0, upper=10, digits=2):
        self.lower = toint(lower)
        self.upper = toint(upper)
        self.digits = toint(digits)

    def __str__(self):
        return "VOLTAGE"

    def __getVolt__(self):
        return round(random.uniform(self.lower, self.upper), self.digits)

class POWER(Power):
    def __init__(self, lower=0, upper=10, digits=2):
        self.lower = toint(lower)
        self.upper = toint(upper)
        self.digits = toint(digits)

    def __str__(self):
        return "POWER"

    def __getWatt__(self):
        return round(random.uniform(self.lower, self.upper), self.digits)


class SENSORS(Pressure, Temperature, Luminosity, Distance, Humidity, Color, Current, Voltage, Power):
    def __init__(self):
        self._pressure    = PRESSURE()
        self._temperature = TEMPERATURE()
        self._luminosity  = LUMINOSITY()
        self._distance    = DISTANCE()
        self._humidity    = HUMIDITY()
        self._color       = COLOR()
        self._current     = CURRENT()
        self._voltage     = VOLTAGE()
        self._power       = POWER()

    def __str__(self):
        return "SENSORS"

    def __family__(self):
        return [
            Pressure.__family__(self),
            Temperature.__family__(self),
            Luminosity.__family__(self),
            Distance.__family__(self),
            Humidity.__family__(self),
            Color.__family__(self),
            Current.__family__(self),
            Voltage.__family__(self),
            Power.__family__(self)
            ]

    def __getPascal__(self):
        return self._pressure.__getPascal__()

    def __getKelvin__(self):
        return self._temperature.__getKelvin__()

    def __getCelsius__(self):
        return self._temperature.__getCelsius__()

    def __getFahrenheit__(self):
        return self._temperature.__getFahrenheit__()

    def __getLux__(self):
        return self._luminosity.__getLux__()

    def __getMillimeter__(self):
        return self._distance.__getMillimeter__()

    def __getHumidity__(self):
        return self._humidity.__getHumidity__()

    def __getRGB__(self):
        return self._color.__getRGB__()

    def __getRGB16bpp__(self):
        return self._color.__getRGB16bpp__()

    def __getMilliampere__(self):
        return self._current.__getMilliampere__()

    def __getVolt__(self):
        return self._voltage.__getVolt__()

    def __getWatt__(self):
        return self._power.__getWatt__()


