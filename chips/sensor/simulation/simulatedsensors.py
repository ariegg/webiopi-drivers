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
#   1.4    2017-01-16    File renamed to simulatedsensor.py. Added two different
#                        possibilities for randomization (uniform and gauss distribution)
#
#   Config parameters
#
#   - lower         Float       Lower bound of the simulated sensor values (uniform distribution).
#                               
#   - upper         Float       Upper bound of the simulated sensor values (uniform distribution).
#                               
#   - mean          Float       Means value of the simulated sensor values (gauss distribution).
#
#   - variance      Float       Variance value of the simulated sensor values (gauss distribution).
#
#   - gauss         Boolean     Flag to use uniform or gauss distribution random values. Default is
#                               "no" (use uniform duistribution values).
#
#   - digits        Integer     Number of rounding digits of generated random values.
#                               
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
#     distribution within a lower and upper bound or to have a gauss distribution with a means
#     and variance value.
#   - Depending on the "gauss" flag only the lower/upper or only the means/variance
#     parameters are used. The opposite pairs are ignored.
#   - For triple value (channel) sensors (e.g. Color) the first 4 paramerters are also tripled
#     and can be set independent for each value channel.
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
from webiopi.utils.types import toint, str2bool
from random import Random

#---------- Single value sensors ----------

class SimulatedSingleSensor():
    def __init__(self, lower=0, upper=100, mean=50, variance=1, gauss="no", digits=2, name="UNKNOWN"):
        self._lower = float(lower)
        self._upper = float(upper)
        self._mean = float(mean)
        self._variance = float(variance)
        self._gauss = str2bool(gauss)
        self._digits = toint(digits)
        self._name = name
        self._r = Random()

    def __str__(self):
        if self._gauss:
            return "%s (gauss: mean=%.3f, variance=%.3f, digits=%d)" % (self._name, self._mean, self._variance, self._digits)
        else:
            return "%s (uniform: lower=%.3f, upper=%.3f, digits=%d)" % (self._name, self._lower, self._upper, self._digits)

    def __getNextSimulatedValue__(self):
        if self._gauss:
            return round(self._r.gauss(self._mean, self._variance), self._digits)
        else:
            return round(self._r.uniform(self._lower, self._upper), self._digits)


class PRESSURE(Pressure, SimulatedSingleSensor):
    def __init__(self, altitude=0, external=None, lower=0, upper=100000, mean=1000, variance=10, gauss="no", digits=1):
        Pressure.__init__(self, altitude, external)
        SimulatedSingleSensor.__init__(self, lower, upper, mean, variance, gauss, digits, "PRESSURE")

    def __getPascal__(self):
        return self.__getNextSimulatedValue__()

class TEMPERATURE(Temperature, SimulatedSingleSensor):
    def __init__(self, lower=0, upper=100, mean=20, variance=1, gauss="no", digits=2):
        SimulatedSingleSensor.__init__(self, lower, upper, mean, variance, gauss, digits, "TEMPERATURE")
        
    def __getKelvin__(self):
        return self.Celsius2Kelvin()

    def __getCelsius__(self):
        return self.__getNextSimulatedValue__()

    def __getFahrenheit__(self):
        return self.Celsius2Fahrenheit()

class LUMINOSITY(Luminosity, SimulatedSingleSensor):
    def __init__(self, lower=0, upper=100000, mean=10000, variance=100, gauss="no", digits=0):
        SimulatedSingleSensor.__init__(self, lower, upper, mean, variance, gauss, digits, "LUMINOSITY")

    def __getLux__(self):
        return self.__getNextSimulatedValue__()

class DISTANCE(Distance, SimulatedSingleSensor):
    def __init__(self, lower=0, upper=1000, mean=100, variance=10, gauss="no", digits=1):
        SimulatedSingleSensor.__init__(self, lower, upper, mean, variance, gauss, digits, "DISTANCE")

    def __getMillimeter__(self):
        return self.__getNextSimulatedValue__()

class HUMIDITY(Humidity, SimulatedSingleSensor):
    def __init__(self, lower=0, upper=1, mean=10000, variance=100, gauss="no", digits=2):
        SimulatedSingleSensor.__init__(self, lower, upper, mean, variance, gauss, digits, "HUMIDITY")

    def __getHumidity__(self):
        return self.__getNextSimulatedValue__()

class CURRENT(Current, SimulatedSingleSensor):
    def __init__(self, lower=0, upper=1000, mean=1, variance=0.1, gauss="no", digits=1):
        SimulatedSingleSensor.__init__(self, lower, upper, mean, variance, gauss, digits, "CURRENT")

    def __getMilliampere__(self):
        return self.__getNextSimulatedValue__()

class VOLTAGE(Voltage, SimulatedSingleSensor):
    def __init__(self, lower=0, upper=10, mean=10, variance=1, gauss="no", digits=2):
        SimulatedSingleSensor.__init__(self, lower, upper, mean, variance, gauss, digits, "VOLTAGE")

    def __getVolt__(self):
        return self.__getNextSimulatedValue__()

class POWER(Power, SimulatedSingleSensor):
    def __init__(self, lower=0, upper=10, mean=5, variance=1, gauss="no", digits=2):
        SimulatedSingleSensor.__init__(self, lower, upper, mean, variance, gauss, digits, "POWER")

    def __getWatt__(self):
        return self.__getNextSimulatedValue__()


#---------- Triple value sensors ----------

class SimulatedTripleSensor():
    def __init__(self, lowerx=0, upperx=100, lowery=0, uppery=100, lowerz=0, upperz=100,
                 meanx=50, variancex=1, meany=50, variancey=1, meanz=50, variancez=1,
                 gauss="no", digits=2, name="UNKNOWN"):
        self._lowerx = float(lowerx)
        self._upperx = float(upperx)
        self._lowery = float(lowery)
        self._uppery = float(uppery)
        self._lowerz = float(lowerz)
        self._upperz = float(upperz)
        self._meanx = float(meanx)
        self._variancex = float(variancex)
        self._meany = float(meany)
        self._variancey = float(variancey)
        self._meanz = float(meanz)
        self._variancez = float(variancez)
        self._gauss = str2bool(gauss)
        self._digits = toint(digits)
        self._name = name
        self._rx = Random()
        self._ry = Random()
        self._ry.jumpahead(1000000)
        self._rz = Random()
        self._rz.jumpahead(1000000000000)

    def __str__(self):
        if self._gauss:
            return "%s (gauss: mx=%.3f, vx=%.3f, my=%.3f, vy=%.3f, mz=%.3f, vz=%.3f, digits=%d)" %  \
                (self._name, self._meanx, self._variancex, self._meany, self._variancey, self._meanz, self._variancez, self._digits)
        else:
            return "%s (uniform: lx=%.3f, ux=%.3f, ly=%.3f, uy=%.3f, lz=%.3f, uz=%.3f, digits=%d)" % \
                (self._name, self._lowerx, self._upperx, self._lowery, self._uppery, self._lowerz, self._upperz, self._digits)

    def __getNextSimulatedValueX__(self):
        if self._gauss:
            return round(self._rx.gauss(self._meanx, self._variancex), self._digits)
        else:
            return round(self._rx.uniform(self._lowerx, self._upperx), self._digits)

    def __getNextSimulatedValueY__(self):
        if self._gauss:
            return round(self._ry.gauss(self._meany, self._variancey), self._digits)
        else:
            return round(self._ry.uniform(self._lowery, self._uppery), self._digits)

    def __getNextSimulatedValueZ__(self):
        if self._gauss:
            return round(self._rz.gauss(self._meanz, self._variancez), self._digits)
        else:
            return round(self._rz.uniform(self._lowerz, self._upperz), self._digits)

class COLOR(Color, SimulatedTripleSensor):
    def __init__(self, lowerr=0x00, upperr=0xFF, lowerg=0x00, upperg=0xFF, lowerb=0x00, upperb=0xFF,
                 meanr=0x7F, variancer=10, meang=0x7F, varianceg=10, meanb=0x7F, varianceb=10,
                 gauss="no"):
        lowerr = toint(lowerr) & 0xFF
        upperr = toint(upperr) & 0xFF
        lowerg = toint(lowerg) & 0xFF
        upperg = toint(upperg) & 0xFF
        lowerb = toint(lowerb) & 0xFF
        upperb = toint(upperb) & 0xFF
        meanr  = toint(meanr)  & 0xFF
        meang  = toint(meang)  & 0xFF
        meanb  = toint(meanb)  & 0xFF
        digits = 0
        
        SimulatedTripleSensor.__init__(self, lowerr, upperr, lowerg, upperg, lowerb, upperb,
                                       meanr, variancer, meang, varianceg, meanb, varianceb,
                                       gauss, digits, "COLOR")

    def __getRGB__(self):
        red = int(self.__getNextSimulatedValueX__())
        green = int(self.__getNextSimulatedValueY__())
        blue = int(self.__getNextSimulatedValueZ__())
        return red, green, blue

    def __getRGB16bpp__(self):
        red, green, blue = self.__getRGB__()
        return red*256, green*256, blue*256

class LINEARVELOCITY(LinearVelocity, SimulatedTripleSensor):
    def __init__(self, lowerx=0, upperx=10, lowery=0, uppery=10, lowerz=0, upperz=10,
                 meanx=10, variancex=1, meany=10, variancey=1, meanz=10, variancez=1,
                 gauss="no", digits=3):
        SimulatedTripleSensor.__init__(self, lowerx, upperx, lowery, uppery, lowerz, upperz,
                                       meanx, variancex, meany, variancey, meanz, variancez,
                                       gauss, digits, "LINEARVELOCITY")

    def __getMeterPerSecondX__(self):
        return self.__getNextSimulatedValueX__()
    
    def __getMeterPerSecondY__(self):
        return self.__getNextSimulatedValueY__()

    def __getMeterPerSecondZ__(self):
        return self.__getNextSimulatedValueZ__()


class ANGULARVELOCITY(AngularVelocity, SimulatedTripleSensor):
    def __init__(self, lowerx=-100, upperx=100, lowery=-100, uppery=100, lowerz=-100, upperz=100,
                 meanx=0, variancex=1, meany=0, variancey=1, meanz=0, variancez=1,
                 gauss="no", digits=3):
        SimulatedTripleSensor.__init__(self, lowerx, upperx, lowery, uppery, lowerz, upperz,
                                       meanx, variancex, meany, variancey, meanz, variancez,
                                       gauss, digits, "ANGULARVELOCITY")

    def __getRadianPerSecondX__(self):
        return self.__getNextSimulatedValueX__()

    def __getRadianPerSecondY__(self):
        return self.__getNextSimulatedValueX__()

    def __getRadianPerSecondZ__(self):
        return self.__getNextSimulatedValueX__()

    
class LINEARACCELERATION(LinearAcceleration, SimulatedTripleSensor):
    def __init__(self, lowerx=-10, upperx=10, lowery=-10, uppery=10, lowerz=-10, upperz=10,
                 meanx=10, variancex=1, meany=10, variancey=1, meanz=10, variancez=1,
                 gauss="no", digits=3):
        SimulatedTripleSensor.__init__(self, lowerx, upperx, lowery, uppery, lowerz, upperz,
                                       meanx, variancex, meany, variancey, meanz, variancez,
                                       gauss, digits, "LINEARACCELERATION")

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
    def __init__(self, lowerx=-100, upperx=100, lowery=-100, uppery=100, lowerz=-100, upperz=100,
                 meanx=0, variancex=1, meany=0, variancey=1, meanz=0, variancez=1,
                 gauss="no", digits=3):
        SimulatedTripleSensor.__init__(self, lowerx, upperx, lowery, uppery, lowerz, upperz,
                                       meanx, variancex, meany, variancey, meanz, variancez,
                                       gauss, digits, "ANGULARACCELERATION")

    def __getRadianPerSquareSecondX__(self):
        return self.__getNextSimulatedValueX__()

    def __getRadianPerSquareSecondY__(self):
        return self.__getNextSimulatedValueY__()

    def __getRadianPerSquareSecondZ__(self):
        return self.__getNextSimulatedValueZ__()


#---------- Multiple category sensors ----------

class SENSORS(Pressure, Temperature, Luminosity, Distance, Humidity, Color, Current, Voltage, Power):
    def __init__(self, gauss="no"):
        self._pressure    = PRESSURE(gauss=gauss)
        self._temperature = TEMPERATURE(gauss=gauss)
        self._luminosity  = LUMINOSITY(gauss=gauss)
        self._distance    = DISTANCE(gauss=gauss)
        self._humidity    = HUMIDITY(gauss=gauss)
        self._color       = COLOR(gauss=gauss)
        self._current     = CURRENT(gauss=gauss)
        self._voltage     = VOLTAGE(gauss=gauss)
        self._power       = POWER(gauss=gauss)

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
    def __init__(self, linlower=0, linupper=10, anglower=-100, angupper=100,
                 linmean=10, linvariance=1, angmean=0, angvariance=1,
                 gauss="no", digits=3):
        self._linear =  LINEARVELOCITY(linlower, linupper, linlower, linupper, linlower, linupper,
                                       linmean, linvariance, linmean, linvariance, linmean, linvariance,
                                       gauss, digits)
        self._angular = ANGULARVELOCITY(anglower, angupper, anglower, angupper, anglower, angupper,
                                        angmean, angvariance, angmean, angvariance, angmean, angvariance,
                                        gauss, digits)
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

    def __init__(self, linlower=-10, linupper=10, anglower=-100, angupper=100,
                 linmean=0, linvariance=1, angmean=0, angvariance=1,
                 gauss="no", digits=3):
        self._linear =  LINEARACCELERATION(linlower, linupper, linlower, linupper, linlower, linupper,
                                           linmean, linvariance, linmean, linvariance, linmean, linvariance,
                                           gauss, digits)
        self._angular = ANGULARACCELERATION(anglower, angupper, anglower, angupper, anglower, angupper,
                                            angmean, angvariance, angmean, angvariance, angmean, angvariance,
                                            gauss, digits)
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


