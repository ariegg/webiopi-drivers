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
#   1.0    2017-01-26    Initial release.
#
#   Config parameters
#
#   - distribution  String      Name of the random distribution that is choosen. Valid values
#                               are most of the random distributions that the Python base library
#                               provides: "gauss", "normal", "lognorm", "expo", "beta", "gamma",
#                               "weibull" and "pareto". Default is "gauss".
#
#   - digits        Integer     Number of rounding digits of generated random values.
#
#   - mu/mu.        Float       Mu (means) value of the simulated sensor values for
#                               gauss, normal and lognorm distribution.
#
#   - sigma/sigma.  Float       Sigma (variance) value of the simulated sensor values for
#                               gauss, normal and lognorm distribution.
#
#   - lambd/lambd.  Float       Lambd value of the simulated sensor values (expo distribution).
#
#   - alpha/alpha.  Float       Alpha value of the simulated sensor values for
#                               beta, gamma, weibull and pareto distribution.
#
#   - beta/beta.    Float       Beta value of the simulated sensor values for
#                               beta, gamma and weibull distribution.
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
#   - For each sensor object you can choose to have the simulated random values to have a
#     distribution of your choice. This provides some statistical flexibility if needed for
#     a specific situation.
#   - For triple value (channel) sensors (e.g. Color) the disribution paramerters are also tripled
#     and can be set independent for each value channel.
#
#
#   Implementation remarks
#
#   - This driver is implemented based on the standard random module of Python and uses the
#     special distibutions this module provides.
#   - For simplicity, the simulated sensor class/device names are just the upper case versions of
#     the underlying sensor abstractions prefixed with a "V" (e.g. Temperature -> VTEMPERATURE).
#     If it is sufficient to have a simple uniform distribution of the values use the corresponding
#     device/class names without the prefix "V" instead.
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

class VariableSimulatedSingleSensor():
    def __init__(self, distribution="gauss", digits=2, name="UNKNOWN", **kwparams):
        self._distribution = distribution
        self._digits = toint(digits)
        self._name = name
        self._r = Random()
        if distribution == "gauss" or distribution == "normal" or distribution == "lognorm":
            if "mu" in kwparams:
                self._mu = float(kwparams["mu"])
            else:
                self._mu = 0
            if "sigma" in kwparams:
                self._sigma = float(kwparams["sigma"])
            else:
                self._sigma = 1
        elif distribution == "expo":
            if "lambd" in kwparams:
                self._lambd = float(kwparams["lambd"])
            else:
                self._lambd = 1
        elif distribution == "beta" or distribution == "gamma" or distribution == "weibull":
            if "alpha" in kwparams:
                self._alpha = float(kwparams["alpha"])
            else:
                self._alpha = 1
            if "beta" in kwparams:
                self._beta = float(kwparams["beta"])
            else:
                self._beta = 1
        elif distribution == "pareto":
            if "alpha" in kwparams:
                self._alpha = float(kwparams["alpha"])
            else:
                self._alpha = 1
        else:
            raise ValueError("Unknown distribution submitted")

    def __str__(self):
        if self._distribution == "gauss" or self._distribution == "normal" or self._distribution == "lognorm":
            return "%s (%s: mu=%.3f sigma=%.3f digits=%d)" % \
                   (self._name, self._distribution, self._mu, self._sigma, self._digits)
        elif self._distribution == "expo":
            return "%s (expo: lambd=%.3f digits=%d)" % (self._name, self._lambd, self._digits)
        elif self._distribution == "beta" or self._distribution == "gamma" or self._distribution == "weibull":
            return "%s (%s: alpha=%.3f beta=%.3f digits=%d)" % \
                   (self._name, self._distribution, self._alpha, self._beta, self._digits)
        elif self._distribution == "pareto":
            return "%s (pareto: alpha=%.3f digits=%d)" % (self._name, self._alpha, self._digits)

    def __getNextSimulatedValue__(self):
        if self._distribution == "gauss":
            return round(self._r.gauss(self._mu, self._sigma), self._digits)
        elif self._distribution == "normal":
            return round(self._r.normalvariate(self._mu, self._sigma), self._digits)
        elif self._distribution == "lognorm":
            return round(self._r.lognormvariate(self._mu, self._sigma), self._digits)
        elif self._distribution == "expo":
            return round(self._r.expovariate(self._lambd), self._digits)
        elif self._distribution == "beta":
            return round(self._r.betavariate(self._alpha, self._beta), self._digits)
        elif self._distribution == "gamma":
            return round(self._r.gammavariate(self._alpha, self._beta), self._digits)
        elif self._distribution == "weibull":
            return round(self._r.weibullvariate(self._alpha, self._beta), self._digits)
        elif self._distribution == "pareto":
            return round(self._r.paretovariate(self._alpha), self._digits)


class VPRESSURE(Pressure, VariableSimulatedSingleSensor):
    def __init__(self, altitude=0, external=None, distribution="gauss", digits=2, **kwparams):
        Pressure.__init__(self, altitude, external)
        VariableSimulatedSingleSensor.__init__(self, distribution, digits, name="VPRESSURE", **kwparams)

    def __getPascal__(self):
        return self.__getNextSimulatedValue__()

class VTEMPERATURE(Temperature, VariableSimulatedSingleSensor):
    def __init__(self, distribution="gauss", digits=2, **kwparams):
        VariableSimulatedSingleSensor.__init__(self, distribution, digits, name="VTEMPERATURE", **kwparams)

    def __getKelvin__(self):
        return self.Celsius2Kelvin()

    def __getCelsius__(self):
        return self.__getNextSimulatedValue__()

    def __getFahrenheit__(self):
        return self.Celsius2Fahrenheit()

class VLUMINOSITY(Luminosity, VariableSimulatedSingleSensor):
    def __init__(self, distribution="gauss", digits=2, **kwparams):
        VariableSimulatedSingleSensor.__init__(self, distribution, digits, name="VLUMINOSITY", **kwparams)

    def __getLux__(self):
        return self.__getNextSimulatedValue__()

class VDISTANCE(Distance, VariableSimulatedSingleSensor):
    def __init__(self, distribution="gauss", digits=2, **kwparams):
        VariableSimulatedSingleSensor.__init__(self, distribution, digits, name="VDISTANCE", **kwparams)

    def __getMillimeter__(self):
        return self.__getNextSimulatedValue__()

class VHUMIDITY(Humidity, VariableSimulatedSingleSensor):
    def __init__(self, distribution="gauss", digits=2, **kwparams):
        VariableSimulatedSingleSensor.__init__(self, distribution, digits, name="VHUMIDITY", **kwparams)

    def __getHumidity__(self):
        return self.__getNextSimulatedValue__()

class VCURRENT(Current, VariableSimulatedSingleSensor):
    def __init__(self, distribution="gauss", digits=2, **kwparams):
        VariableSimulatedSingleSensor.__init__(self, distribution, digits, name="VCURRENT", **kwparams)

    def __getMilliampere__(self):
        return self.__getNextSimulatedValue__()

class VVOLTAGE(Voltage, VariableSimulatedSingleSensor):
    def __init__(self, distribution="gauss", digits=2, **kwparams):
        VariableSimulatedSingleSensor.__init__(self, distribution, digits, name="VVOLTAGE", **kwparams)

    def __getVolt__(self):
        return self.__getNextSimulatedValue__()

class VPOWER(Power, VariableSimulatedSingleSensor):
    def __init__(self, distribution="gauss", digits=2, **kwparams):
        VariableSimulatedSingleSensor.__init__(self, distribution, digits, name="VPOWER", **kwparams)

    def __getWatt__(self):
        return self.__getNextSimulatedValue__()


#---------- Triple value sensors ----------

class VariableSimulatedTripleSensor():
    def __init__(self, distribution="gauss", digits=2, name="UNKNOWN", **kwparams):
        self._distribution = distribution
        self._digits = toint(digits)
        self._name = name
        self._rx = Random()
        self._ry = Random()
        self._ry.jumpahead(1000000)
        self._rz = Random()
        self._rz.jumpahead(1000000000000)

        if distribution == "gauss" or distribution == "normal" or distribution == "lognorm":
            if "mux" in kwparams:
                self._mux = float(kwparams["mux"])
            else:
                self._mux = 0
            if "sigmax" in kwparams:
                self._sigmax = float(kwparams["sigmax"])
            else:
                self._sigmax = 1
            if "muy" in kwparams:
                self._muy = float(kwparams["muy"])
            else:
                self._muy = 0
            if "sigmay" in kwparams:
                self._sigmay = float(kwparams["sigmay"])
            else:
                self._sigmay = 1
            if "muz" in kwparams:
                self._muz = float(kwparams["muz"])
            else:
                self._muz = 0
            if "sigmaz" in kwparams:
                self._sigmaz = float(kwparams["sigmaz"])
            else:
                self._sigmaz = 1
        elif distribution == "expo":
            if "lambdx" in kwparams:
                self._lambdx = float(kwparams["lambdx"])
            else:
                self._lambdx = 1
            if "lambdy" in kwparams:
                self._lambdy = float(kwparams["lambdy"])
            else:
                self._lambdy = 1
            if "lambdz" in kwparams:
                self._lambdz = float(kwparams["lambdz"])
            else:
                self._lambdx = 1
        elif distribution == "beta" or distribution == "gamma" or distribution == "weibull":
            if "alphax" in kwparams:
                self._alphax = float(kwparams["alphax"])
            else:
                self._alphax = 1
            if "betax" in kwparams:
                self._betax = float(kwparams["betax"])
            else:
                self._betax = 1
            if "alphay" in kwparams:
                self._alphay = float(kwparams["alphay"])
            else:
                self._alphay = 1
            if "betay" in kwparams:
                self._betay = float(kwparams["betay"])
            else:
                self._betay = 1
            if "alphaz" in kwparams:
                self._alphaz = float(kwparams["alphaz"])
            else:
                self._alphaz = 1
            if "betaz" in kwparams:
                self._betaz = float(kwparams["betaz"])
            else:
                self._betaz = 1
        elif distribution == "pareto":
            if "alphax" in kwparams:
                self._alphax = float(kwparams["alphax"])
            else:
                self._alphax = 1
            if "alphay" in kwparams:
                self._alphay = float(kwparams["alphay"])
            else:
                self._alphay = 1
            if "alphaz" in kwparams:
                self._alphaz = float(kwparams["alphaz"])
            else:
                self._alphaz = 1
        else:
            raise ValueError("Unknown distribution submitted")

    def __str__(self):
        if self._distribution == "gauss" or self._distribution == "normal" or self._distribution == "lognorm":
            return "%s (%s: mx=%.3f sx=%.3f my=%.3f sy=%.3f mz=%.3f sz=%.3f digits=%d)" % \
                (self._name, self._distribution,
                 self._mux, self._sigmax, self._muy, self._sigmay, self._muz, self._sigmaz,
                 self._digits)
        elif self._distribution == "expo":
            return "%s (expo: lambdx=%.3f lambdy=%.3f lambdz=%.3f digits=%d)" % \
                (self._name, self._lambdx, self._lambdy, self._lambdz, self._digits)
        elif self._distribution == "beta" or self._distribution == "gamma" or self._distribution == "weibull":
            return "%s (%s: ax=%.3f bx=%.3f ay=%.3f by=%.3f az=%.3f bz=%.3f digits=%d)" % \
                (self._name, self._distribution,
                 self._alphax, self._betax, self._alphay, self._betay, self._alphaz, self._betaz,
                 self._digits)
        elif self._distribution == "pareto":
            return "%s (pareto: ax=%.3f ay=%.3f az=%.3f digits=%d)" % \
                (self._name, self._alphax, self._alphay, self._alphaz, self._digits)

    def __getNextSimulatedValueX__(self):
        if self._distribution == "gauss":
            return round(self._rx.gauss(self._mux, self._sigmax), self._digits)
        elif self._distribution == "normal":
            return round(self._rx.normalvariate(self._mux, self._sigmax), self._digits)
        elif self._distribution == "lognorm":
            return round(self._rx.lognormvariate(self._mux, self._sigmax), self._digits)
        elif self._distribution == "expo":
            return round(self._rx.expovariate(self._lambdx), self._digits)
        elif self._distribution == "beta":
            return round(self._rx.betavariate(self._alphax, self._betax), self._digits)
        elif self._distribution == "gamma":
            return round(self._rx.gammavariate(self._alphax, self._betax), self._digits)
        elif self._distribution == "weibull":
            return round(self._rx.weibullvariate(self._alphax, self._betax), self._digits)
        elif self._distribution == "pareto":
            return round(self._rx.paretovariate(self._alphax), self._digits)

    def __getNextSimulatedValueY__(self):
        if self._distribution == "gauss":
            return round(self._ry.gauss(self._muy, self._sigmay), self._digits)
        elif self._distribution == "normal":
            return round(self._ry.normalvariate(self._muy, self._sigmay), self._digits)
        elif self._distribution == "lognorm":
            return round(self._ry.lognormvariate(self._muy, self._sigmay), self._digits)
        elif self._distribution == "expo":
            return round(self._ry.expovariate(self._lambdy), self._digits)
        elif self._distribution == "beta":
            return round(self._ry.betavariate(self._alphay, self._betay), self._digits)
        elif self._distribution == "gamma":
            return round(self._ry.gammavariate(self._alphay, self._betay), self._digits)
        elif self._distribution == "weibull":
            return round(self._ry.weibullvariate(self._alphay, self._betay), self._digits)
        elif self._distribution == "pareto":
            return round(self._ry.paretovariate(self._alphay), self._digits)

    def __getNextSimulatedValueZ__(self):
        if self._distribution == "gauss":
            return round(self._rz.gauss(self._muz, self._sigmaz), self._digits)
        elif self._distribution == "normal":
            return round(self._rz.normalvariate(self._muz, self._sigmaz), self._digits)
        elif self._distribution == "lognorm":
            return round(self._rz.lognormvariate(self._muz, self._sigmaz), self._digits)
        elif self._distribution == "expo":
            return round(self._rz.expovariate(self._lambdz), self._digits)
        elif self._distribution == "beta":
            return round(self._rz.betavariate(self._alphaz, self._betaz), self._digits)
        elif self._distribution == "gamma":
            return round(self._rz.gammavariate(self._alphaz, self._betaz), self._digits)
        elif self._distribution == "weibull":
            return round(self._rz.weibullvariate(self._alphaz, self._betaz), self._digits)
        elif self._distribution == "pareto":
            return round(self._rz.paretovariate(self._alphaz), self._digits)

class VCOLOR(Color, VariableSimulatedTripleSensor):
    def __init__(self, distribution="gauss", **kwparams):
        for key in kwparams.keys():
            kwparams[key] = int(float(kwparams[key])) & 0xFF
        VariableSimulatedTripleSensor.__init__(self, distribution, digits=0, name="VCOLOR", **kwparams)

    def __getRGB__(self):
        red = abs(int(self.__getNextSimulatedValueX__())) & 0xFF
        green = abs(int(self.__getNextSimulatedValueY__())) & 0xFF
        blue = abs(int(self.__getNextSimulatedValueZ__())) & 0xFF
        return red, green, blue

    def __getRGB16bpp__(self):
        red, green, blue = self.__getRGB__()
        return red*256, green*256, blue*256

class VLINEARVELOCITY(LinearVelocity, VariableSimulatedTripleSensor):
    def __init__(self, distribution="gauss", digits=2, **kwparams):
        VariableSimulatedTripleSensor.__init__(self, distribution, digits, name="VLINEARVELOCITY", **kwparams)

    def __getMeterPerSecondX__(self):
        return self.__getNextSimulatedValueX__()

    def __getMeterPerSecondY__(self):
        return self.__getNextSimulatedValueY__()

    def __getMeterPerSecondZ__(self):
        return self.__getNextSimulatedValueZ__()


class VANGULARVELOCITY(AngularVelocity, VariableSimulatedTripleSensor):
    def __init__(self, distribution="gauss", digits=2, **kwparams):
        VariableSimulatedTripleSensor.__init__(self, distribution, digits, name="VANGULARVELOCITY", **kwparams)

    def __getRadianPerSecondX__(self):
        return self.__getNextSimulatedValueX__()

    def __getRadianPerSecondY__(self):
        return self.__getNextSimulatedValueY__()

    def __getRadianPerSecondZ__(self):
        return self.__getNextSimulatedValueZ__()


class VLINEARACCELERATION(LinearAcceleration, VariableSimulatedTripleSensor):
    def __init__(self, distribution="gauss", digits=2, **kwparams):
        VariableSimulatedTripleSensor.__init__(self, distribution, digits, name="VLINEARACCELERATION", **kwparams)

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


class VANGULARACCELERATION(AngularAcceleration, VariableSimulatedTripleSensor):
    def __init__(self, distribution="gauss", digits=2, **kwparams):
        VariableSimulatedTripleSensor.__init__(self, distribution, digits, name="VANGULARACCELERATION", **kwparams)

    def __getRadianPerSquareSecondX__(self):
        return self.__getNextSimulatedValueX__()

    def __getRadianPerSquareSecondY__(self):
        return self.__getNextSimulatedValueY__()

    def __getRadianPerSquareSecondZ__(self):
        return self.__getNextSimulatedValueZ__()


#---------- Multiple category sensors ----------

class VSENSORS(Pressure, Temperature, Luminosity, Distance, Humidity, Color, Current, Voltage, Power):
    def __init__(self):
        self._vpressure    = VPRESSURE()
        self._vtemperature = VTEMPERATURE()
        self._vluminosity  = VLUMINOSITY()
        self._vdistance    = VDISTANCE()
        self._vhumidity    = VHUMIDITY()
        self._vcolor       = VCOLOR()
        self._vcurrent     = VCURRENT()
        self._vvoltage     = VVOLTAGE()
        self._vpower       = VPOWER()

    def __str__(self):
        return "VSENSORS"

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
        return self._vpressure.__getPascal__()

    def __getKelvin__(self):
        return self._vtemperature.__getKelvin__()

    def __getCelsius__(self):
        return self._vtemperature.__getCelsius__()

    def __getFahrenheit__(self):
        return self._vtemperature.__getFahrenheit__()

    def __getLux__(self):
        return self._vluminosity.__getLux__()

    def __getMillimeter__(self):
        return self._vdistance.__getMillimeter__()

    def __getHumidity__(self):
        return self._vhumidity.__getHumidity__()

    def __getRGB__(self):
        return self._vcolor.__getRGB__()

    def __getRGB16bpp__(self):
        return self._vcolor.__getRGB16bpp__()

    def __getMilliampere__(self):
        return self._vcurrent.__getMilliampere__()

    def __getVolt__(self):
        return self._vvoltage.__getVolt__()

    def __getWatt__(self):
        return self._vpower.__getWatt__()

