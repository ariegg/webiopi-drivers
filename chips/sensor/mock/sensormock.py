#   Copyright 2016-2017 Andreas Riegg - t-h-i-n-x.net
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
#   1.3    2017-01-10    Added ACCELERATION and VELOCITY classes.
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
from webiopi.devices.sensor import Acceleration
from webiopi.devices.sensor import LinearAcceleration
from webiopi.devices.sensor import AngularAcceleration
from webiopi.devices.sensor import Velocity
from webiopi.devices.sensor import LinearVelocity
from webiopi.devices.sensor import AngularVelocity
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

#---

class LINEARVELOCITY(LinearVelocity):
    def __init__(self, xlower=0, xupper=10, ylower=0, yupper=10, zlower=0, zupper=10, digits=3):
        self.xlower = toint(xlower)
        self.xupper = toint(xupper)
        self.ylower = toint(ylower)
        self.yupper = toint(yupper)
        self.zlower = toint(zlower)
        self.zupper = toint(zupper)
        self.digits = toint(digits)

    def __str__(self):
        return "LINEARVELOCITY"

    def __getMeterPerSecondX__(self):
        return round(random.uniform(self.xlower, self.xupper), self.digits)

    def __getMeterPerSecondY__(self):
        return round(random.uniform(self.ylower, self.yupper), self.digits)

    def __getMeterPerSecondZ__(self):
        return round(random.uniform(self.zlower, self.zupper), self.digits)


class ANGULARVELOCITY(AngularVelocity):
    def __init__(self, xlower=-100, xupper=100, ylower=-100, yupper=100, zlower=-100, zupper=100, digits=3):
        self.xlower = toint(xlower)
        self.xupper = toint(xupper)
        self.ylower = toint(ylower)
        self.yupper = toint(yupper)
        self.zlower = toint(zlower)
        self.zupper = toint(zupper)
        self.digits = toint(digits)

    def __str__(self):
        return "ANGULARVELOCITY"

    def __getRadianPerSecondX__(self):
        return round(random.uniform(self.xlower, self.xupper), self.digits)

    def __getRadianPerSecondY__(self):
        return round(random.uniform(self.ylower, self.yupper), self.digits)

    def __getRadianPerSecondZ__(self):
        return round(random.uniform(self.zlower, self.zupper), self.digits)

class VELOCITY(Velocity):
    def __init__(self, linlower=0, linupper=10, anglower=-100, angupper=100, digits=3):
        self._linear =  LINEARVELOCITY(linlower, linupper, linlower, linupper, linlower, linupper, digits)
        self._angular = ANGULARVELOCITY(anglower, angupper, anglower, angupper, anglower, angupper, digits)

    def __str__(self):
        return "VELOCITY"

    def __getMeterPerSecondX__(self):
        return self._linear.__getMeterPerSecondX__()
        
    def __getMeterPerSecondY__(self):
        return self._linear.__getMeterPerSecondY__()
        
    def __getMeterPerSecondZ__(self):
        return self._linear.__getMeterPerSecondZ__()

    def __getRadianPerSecondX__(self):
        return self._angular.__getRadianPerSecondX__()

    def __getRadianPerSecondY__(self):
        return self._angular.__getRadianPerSecondY__()

    def __getRadianPerSecondZ__(self):
        return self._angular.__getRadianPerSecondZ__()


#---
    
class LINEARACCELERATION(LinearAcceleration):
    def __init__(self, xlower=-10, xupper=10, ylower=-10, yupper=10, zlower=-10, zupper=10, digits=3):
        self.xlower = toint(xlower)
        self.xupper = toint(xupper)
        self.ylower = toint(ylower)
        self.yupper = toint(yupper)
        self.zlower = toint(zlower)
        self.zupper = toint(zupper)
        self.digits = toint(digits)

    def __str__(self):
        return "LINEARACCELERATION"

    def __getMeterPerSquareSecondX__(self):
        return round(random.uniform(self.xlower, self.xupper), self.digits)

    def __getMeterPerSquareSecondY__(self):
        return round(random.uniform(self.ylower, self.yupper), self.digits)

    def __getMeterPerSquareSecondZ__(self):
        return round(random.uniform(self.zlower, self.zupper), self.digits)

    def __getGravityX__(self):
        return self.__getMeterPerSquareSecondX__() / self.StandardGravity()

    def __getGravityY__(self):
        return self.__getMeterPerSquareSecondY__() / self.StandardGravity()

    def __getGravityZ__(self):
        return self.__getMeterPerSquareSecondZ__() / self.StandardGravity() + 1

class ANGULARACCELERATION(AngularAcceleration):
    def __init__(self, xlower=-100, xupper=100, ylower=-100, yupper=100, zlower=-100, zupper=100, digits=3):
        self.xlower = toint(xlower)
        self.xupper = toint(xupper)
        self.ylower = toint(ylower)
        self.yupper = toint(yupper)
        self.zlower = toint(zlower)
        self.zupper = toint(zupper)
        self.digits = toint(digits)

    def __str__(self):
        return "ANGULARACCELERATION"

    def __getRadianPerSquareSecondX__(self):
        return round(random.uniform(self.xlower, self.xupper), self.digits)

    def __getRadianPerSquareSecondY__(self):
        return round(random.uniform(self.ylower, self.yupper), self.digits)

    def __getRadianPerSquareSecondZ__(self):
        return round(random.uniform(self.zlower, self.zupper), self.digits)

class ACCELERATION(Acceleration):
    def __init__(self, linlower=-10, linupper=10, anglower=-100, angupper=100, digits=3):
        self._linear =  LINEARACCELERATION(linlower, linupper, linlower, linupper, linlower, linupper, digits)
        self._angular = ANGULARACCELERATION(anglower, angupper, anglower, angupper, anglower, angupper, digits)

    def __str__(self):
        return "ACCELERATION"

    def __getMeterPerSquareSecondX__(self):
        return self._linear.__getMeterPerSquareSecondX__()
        
    def __getMeterPerSquareSecondY__(self):
        return self._linear.__getMeterPerSquareSecondY__()
        
    def __getMeterPerSquareSecondZ__(self):
        return self._linear.__getMeterPerSquareSecondZ__()
       
    def __getGravityX__(self):
        return self._linear.__getGravityX__()
        
    def __getGravityY__(self):
        return self._linear.__getGravityY__()

    def __getGravityZ__(self):
        return self._linear.__getGravityZ__()


    def __getRadianPerSquareSecondX__(self):
        return self._angular.__getRadianPerSquareSecondX__()

    def __getRadianPerSquareSecondY__(self):
        return self._angular.__getRadianPerSquareSecondY__()

    def __getRadianPerSquareSecondZ__(self):
        return self._angular.__getRadianPerSquareSecondZ__()


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



