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
#   1.4    2017-01-16    File renamed to simulatedsensors.py. Added two different
#                        possibilities for randomization (uniform and gauss distribution)
#   1.5    2017-01-26    Reduced to basic possibility for randomization (uniform distribution)
#                        and moved other distribution possibilities to another file
#                        "variablesimulatedsensors.py" with variable distribution settings.
#
#   Config parameters
#
#   - lower/lower.  Float       Lower bound of the simulated sensor values (uniform distribution).
#
#   - upper/upper.  Float       Upper bound of the simulated sensor values (uniform distribution).
#
#   - digits        Integer     Number of rounding digits of generated random values.
#
#
#   Usage remarks
#
#   - You can use all devices here just like ordinary devices by e.g. using them in the
#     config file.
#   - As pure artificial devices they have no hardware dependency at all. For that reason
#     no bus parameter is necessary.
#   - You can use these devices to do some testing prior to having the real physical sensors
#     available to e.g. create some user interface in advance.
#   - You can use these devices also to check the correctness of some REST API calls that use
#     the sensor values.
#   - For each sensor object you can choose to have the simulated random values to have a uniform
#     distribution within a lower and upper bound.
#   - For triple value (channel) sensors (e.g. Color) the first 2 paramerters are also tripled
#     and can be set independent for each value channel.
#
#
#   Implementation remarks
#
#   - This driver is implemented based on the standard random module of Python.
#   - For simplicity, the simulated sensor class/device names are just the upper case versions of
#     the underlying sensor abstractions (e.g. Temperature -> TEMPERATURE).
#   - Each single value sensor instance gets its own Random object for high independence of the values.
#   - Each triple value sensor instance gets its own three individual Random objects and two of them
#     use additionally different "jumpahead" for high independence of the three values.
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
from random import Random


#---------- Single value sensors ----------

class SimulatedSingleSensor():
    def __init__(self, lower=0, upper=100, digits=2, name="UNKNOWN"):
        self._lower = float(lower)
        self._upper = float(upper)
        self._digits = toint(digits)
        self._name = name
        self._r = Random()

    def __str__(self):
        return "%s (lower=%.3f upper=%.3f digits=%d)" % (self._name, self._lower, self._upper, self._digits)

    def __getNextSimulatedValue__(self):
        return round(self._r.uniform(self._lower, self._upper), self._digits)


class PRESSURE(Pressure, SimulatedSingleSensor):
    def __init__(self, altitude=0, external=None, lower=0, upper=100000, digits=1):
        Pressure.__init__(self, altitude, external)
        SimulatedSingleSensor.__init__(self, lower, upper, digits, "PRESSURE")

    def __getPascal__(self):
        return self.__getNextSimulatedValue__()

class TEMPERATURE(Temperature, SimulatedSingleSensor):
    def __init__(self, lower=0, upper=100, digits=2):
        SimulatedSingleSensor.__init__(self, lower, upper, digits, "TEMPERATURE")

    def __getKelvin__(self):
        return self.Celsius2Kelvin()

    def __getCelsius__(self):
        return self.__getNextSimulatedValue__()

    def __getFahrenheit__(self):
        return self.Celsius2Fahrenheit()

class LUMINOSITY(Luminosity, SimulatedSingleSensor):
    def __init__(self, lower=0, upper=100000, digits=0):
        SimulatedSingleSensor.__init__(self, lower, upper, digits, "LUMINOSITY")

    def __getLux__(self):
        return self.__getNextSimulatedValue__()

class DISTANCE(Distance, SimulatedSingleSensor):
    def __init__(self, lower=0, upper=1000, digits=1):
        SimulatedSingleSensor.__init__(self, lower, upper, digits, "DISTANCE")

    def __getMillimeter__(self):
        return self.__getNextSimulatedValue__()

class HUMIDITY(Humidity, SimulatedSingleSensor):
    def __init__(self, lower=0, upper=1, digits=2):
        SimulatedSingleSensor.__init__(self, lower, upper, digits, "HUMIDITY")

    def __getHumidity__(self):
        return self.__getNextSimulatedValue__()

class CURRENT(Current, SimulatedSingleSensor):
    def __init__(self, lower=0, upper=1000, digits=1):
        SimulatedSingleSensor.__init__(self, lower, upper, digits, "CURRENT")

    def __getMilliampere__(self):
        return self.__getNextSimulatedValue__()

class VOLTAGE(Voltage, SimulatedSingleSensor):
    def __init__(self, lower=0, upper=10, digits=2):
        SimulatedSingleSensor.__init__(self, lower, upper, digits, "VOLTAGE")

    def __getVolt__(self):
        return self.__getNextSimulatedValue__()

class POWER(Power, SimulatedSingleSensor):
    def __init__(self, lower=0, upper=10, digits=2):
        SimulatedSingleSensor.__init__(self, lower, upper, digits, "POWER")

    def __getWatt__(self):
        return self.__getNextSimulatedValue__()


#---------- Triple value sensors ----------

class SimulatedTripleSensor():
    def __init__(self, lowerx=0, upperx=100, lowery=0, uppery=100, lowerz=0, upperz=100, digits=2, name="UNKNOWN"):
        self._lowerx = float(lowerx)
        self._upperx = float(upperx)
        self._lowery = float(lowery)
        self._uppery = float(uppery)
        self._lowerz = float(lowerz)
        self._upperz = float(upperz)
        self._digits = toint(digits)
        self._name = name
        self._rx = Random()
        self._ry = Random()
        self._ry.jumpahead(1000000)
        self._rz = Random()
        self._rz.jumpahead(1000000000000)

    def __str__(self):
        return "%s (lx=%.3f ux=%.3f ly=%.3f uy=%.3f lz=%.3f uz=%.3f digits=%d)" % \
                (self._name,
                 self._lowerx, self._upperx, self._lowery, self._uppery, self._lowerz, self._upperz,
                 self._digits)

    def __getNextSimulatedValueX__(self):
        return round(self._rx.uniform(self._lowerx, self._upperx), self._digits)

    def __getNextSimulatedValueY__(self):
        return round(self._ry.uniform(self._lowery, self._uppery), self._digits)

    def __getNextSimulatedValueZ__(self):
        return round(self._rz.uniform(self._lowerz, self._upperz), self._digits)

class COLOR(Color, SimulatedTripleSensor):
    def __init__(self, lowerr=0x00, upperr=0xFF, lowerg=0x00, upperg=0xFF, lowerb=0x00, upperb=0xFF):
        lowerr = toint(lowerr) & 0xFF
        upperr = toint(upperr) & 0xFF
        lowerg = toint(lowerg) & 0xFF
        upperg = toint(upperg) & 0xFF
        lowerb = toint(lowerb) & 0xFF
        upperb = toint(upperb) & 0xFF
        digits = 0
        SimulatedTripleSensor.__init__(self, lowerr, upperr, lowerg, upperg, lowerb, upperb,
                                       digits, "COLOR")

    def __str__(self):
        return "%s (lred=0x%02X ured=0x%02X lgreen=0x%02X ugreen=0x%02X lblue=0x%02X ublue=0x%02X)" % \
                (self._name, self._lowerx, self._upperx, self._lowery, self._uppery, self._lowerz, self._upperz)

    def __getRGB__(self):
        red = abs(int(self.__getNextSimulatedValueX__()))
        green = abs(int(self.__getNextSimulatedValueY__()))
        blue = abs(int(self.__getNextSimulatedValueZ__()))
        return red, green, blue

    def __getRGB16bpp__(self):
        red, green, blue = self.__getRGB__()
        return red*256, green*256, blue*256

class LINEARVELOCITY(LinearVelocity, SimulatedTripleSensor):
    def __init__(self, lowerx=0, upperx=10, lowery=0, uppery=10, lowerz=0, upperz=10, digits=3):
        SimulatedTripleSensor.__init__(self, lowerx, upperx, lowery, uppery, lowerz, upperz,
                                       digits, "LINEARVELOCITY")

    def __getMeterPerSecondX__(self):
        return self.__getNextSimulatedValueX__()

    def __getMeterPerSecondY__(self):
        return self.__getNextSimulatedValueY__()

    def __getMeterPerSecondZ__(self):
        return self.__getNextSimulatedValueZ__()


class ANGULARVELOCITY(AngularVelocity, SimulatedTripleSensor):
    def __init__(self, lowerx=-100, upperx=100, lowery=-100, uppery=100, lowerz=-100, upperz=100, digits=3):
        SimulatedTripleSensor.__init__(self, lowerx, upperx, lowery, uppery, lowerz, upperz,
                                       digits, "ANGULARVELOCITY")

    def __getRadianPerSecondX__(self):
        return self.__getNextSimulatedValueX__()

    def __getRadianPerSecondY__(self):
        return self.__getNextSimulatedValueY__()

    def __getRadianPerSecondZ__(self):
        return self.__getNextSimulatedValueZ__()


class LINEARACCELERATION(LinearAcceleration, SimulatedTripleSensor):
    def __init__(self, lowerx=-10, upperx=10, lowery=-10, uppery=10, lowerz=-10, upperz=10, digits=3):
        SimulatedTripleSensor.__init__(self, lowerx, upperx, lowery, uppery, lowerz, upperz,
                                       digits, "LINEARACCELERATION")

    def __getMeterPerSquareSecondX__(self):
        return self.__getNextSimulatedValueX__()

    def __getMeterPerSquareSecondY__(self):
        return self.__getNextSimulatedValueY__()

    def __getMeterPerSquareSecondZ__(self):
        return self.__getNextSimulatedValueZ__()

    def __getGravityX__(self):
        return self.__getMeterPerSquareSecondX__() / self.StandardGravity()

    def __getGravityY__(self):
        return self.__getMeterPerSquareSecondY__() / self.StandardGravity()

    def __getGravityZ__(self):
        return self.__getMeterPerSquareSecondZ__() / self.StandardGravity() + 1


class ANGULARACCELERATION(AngularAcceleration, SimulatedTripleSensor):
    def __init__(self, lowerx=-100, upperx=100, lowery=-100, uppery=100, lowerz=-100, upperz=100, digits=3):
        SimulatedTripleSensor.__init__(self, lowerx, upperx, lowery, uppery, lowerz, upperz,
                                       digits, "ANGULARACCELERATION")

    def __getRadianPerSquareSecondX__(self):
        return self.__getNextSimulatedValueX__()

    def __getRadianPerSquareSecondY__(self):
        return self.__getNextSimulatedValueY__()

    def __getRadianPerSquareSecondZ__(self):
        return self.__getNextSimulatedValueZ__()


#---------- Multiple category sensors ----------

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


class VELOCITY(Velocity):
    def __init__(self, linlower=0, linupper=10, anglower=-100, angupper=100, digits=3):
        self._linear =  LINEARVELOCITY(linlower, linupper, linlower, linupper, linlower, linupper, digits)
        self._angular = ANGULARVELOCITY(anglower, angupper, anglower, angupper, anglower, angupper, digits)

    def __str__(self):
        return "VELOCITY (%s --- %s)" % (self._linear.__str__(), self._angular.__str__())

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


class ACCELERATION(Acceleration):
    def __init__(self, linlower=-10, linupper=10, anglower=-100, angupper=100, digits=3):
        self._linear =  LINEARACCELERATION(linlower, linupper, linlower, linupper, linlower, linupper, digits)
        self._angular = ANGULARACCELERATION(anglower, angupper, anglower, angupper, anglower, angupper, digits)

    def __str__(self):
        return "ACCELERATION (%s --- %s)" % (self._linear.__str__(), self._angular.__str__())

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


