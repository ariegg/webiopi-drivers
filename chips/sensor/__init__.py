#   Copyright 2012-2017 Eric Ptak - trouch.com
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
#   Changelog
#
#   1.0    2016-04-30    Initial release based on WebIOPi 0.7.22
#   1.1    2016-08-12    Added @api annotations and /* state routes
#                        Bugfix, inch calculation was wrong /0.254 -> /25.4
#   1.2    2016-08-22    Added TCS3472X color sensors.
#   1.3    2016-09-26    Added all SENSORS class.
#   1.4    2016-12-12    Added Current, Voltage and Power abstractions.
#   1.5    2017-01-10    Added Acceleration abstractions.
#   1.6    2017-01-12    Added Velocity abstractions.
#   1.7    2017-01-16    Reflect driver file rename to simulatedsensors.py.
#   1.8    2017-02-06    Added alternative drivers lookup.
#

from webiopi.utils.types import toint
from webiopi.utils.types import M_JSON
from webiopi.utils.drivers import driverDetector
from webiopi.devices.instance import deviceInstance
from webiopi.decorators.rest import request, response, api # Modified

class Pressure():
    def __init__(self, altitude=0, external=None):
        self.altitude = toint(altitude)
        if isinstance(external, str):
            self.external = deviceInstance(external)
        else:
            self.external = external

        if self.external != None and not isinstance(self.external, Temperature):
            raise Exception("external must be a Temperature sensor")

    def __family__(self):
        return "Pressure"

    def __getPascal__(self):
        raise NotImplementedError

    def __getPascalAtSea__(self):
        raise NotImplementedError

    @api("Pressure", 0)
    @request("GET", "sensor/pressure/*")
    @response(contentType=M_JSON)
    def pressureWildcard(self):
        values = {}
        pressure = self.__getPascal__()
        values["Pa"] = pressure
        values["hPa"] = "%.2f" % (pressure / 100.0)
        return values

    @api("Pressure", 0)
    @request("GET", "sensor/pressure/sea/*")
    @response(contentType=M_JSON)
    def pressureWildcardSea(self):
        values = {}
        pressureAtSea = self.getPascalAtSea()
        values["Pa"] = pressureAtSea
        values["hPa"] = "%.02f" % (pressureAtSea / 100.0)
        return values

    @api("Pressure")
    @request("GET", "sensor/pressure/pa")
    @response("%d")
    def getPascal(self):
        return self.__getPascal__()

    @api("Pressure")
    @request("GET", "sensor/pressure/hpa")
    @response("%.2f")
    def getHectoPascal(self):
        return float(self.__getPascal__()) / 100.0

    @api("Pressure")
    @request("GET", "sensor/pressure/sea/pa")
    @response("%d")
    def getPascalAtSea(self):
        pressure = self.__getPascal__()
        if self.external != None:
            k = self.external.getKelvin()
            if k != 0:
                return float(pressure) / (1.0 / (1.0 + 0.0065 / k * self.altitude)**5.255)
        return float(pressure) / (1.0 - self.altitude / 44330.0)**5.255

    @api("Pressure")
    @request("GET", "sensor/pressure/sea/hpa")
    @response("%.2f")
    def getHectoPascalAtSea(self):
        return self.getPascalAtSea() / 100.0

class Temperature():
    def __family__(self):
        return "Temperature"

    def __getKelvin__(self):
        raise NotImplementedError

    def __getCelsius__(self):
        raise NotImplementedError

    def __getFahrenheit__(self):
        raise NotImplementedError

    def Kelvin2Celsius(self, value=None):
        if value == None:
            value = self.getKelvin()
        return value - 273.15

    def Kelvin2Fahrenheit(self, value=None):
        if value == None:
            value = self.getKelvin()
        return value * 1.8 - 459.67

    def Celsius2Kelvin(self, value=None):
        if value == None:
            value = self.getCelsius()
        return value + 273.15

    def Celsius2Fahrenheit(self, value=None):
        if value == None:
            value = self.getCelsius()
        return value * 1.8 + 32

    def Fahrenheit2Kelvin(self, value=None):
        if value == None:
            value = self.getFahrenheit()
        return (value - 459.67) / 1.8

    def Fahrenheit2Celsius(self, value=None):
        if value == None:
            value = self.getFahrenheit()
        return (value - 32) / 1.8

    @api("Temperature", 0)
    @request("GET", "sensor/temperature/*")
    @response(contentType=M_JSON)
    def temperatureWildcard(self):
        values = {}
        temperature = self.__getCelsius__()
        values["C"] = "%.2f" % temperature
        values["K"] = "%.2f" % self.Celsius2Kelvin(temperature)
        values["F"] = "%.2f" % self.Celsius2Fahrenheit(temperature)
        return values

    @api("Temperature")
    @request("GET", "sensor/temperature/k")
    @response("%.02f")
    def getKelvin(self):
        return self.__getKelvin__()

    @api("Temperature")
    @request("GET", "sensor/temperature/c")
    @response("%.02f")
    def getCelsius(self):
        return self.__getCelsius__()

    @api("Temperature")
    @request("GET", "sensor/temperature/f")
    @response("%.02f")
    def getFahrenheit(self):
        return self.__getFahrenheit__()

class Luminosity():
    def __family__(self):
        return "Luminosity"

    def __getLux__(self):
        raise NotImplementedError

    @api("Luminosity", 0)
    @request("GET", "sensor/luminosity/*")
    @response(contentType=M_JSON)
    def luminosityWildcard(self):
        values = {}
        luminosity = self.__getLux__()
        values["lux"] = "%.2f" % luminosity
        return values

    @api("Luminosity")
    @request("GET", "sensor/luminosity/lux")
    @response("%.02f")
    def getLux(self):
        return self.__getLux__()

class Distance():
    def __family__(self):
        return "Distance"

    def __getMillimeter__(self):
        raise NotImplementedError

    @api("Distance", 0)
    @request("GET", "sensor/distance/*")
    @response(contentType=M_JSON)
    def distanceWildcard(self):
        values = {}
        distance = self.__getMillimeter__()
        values["mm"] = "%.2f" % distance
        values["cm"] = "%.2f" % (distance / 10)
        values["m"]  = "%.2f" % (distance / 1000)
        values["in"] = "%.2f" % (distance / 25.4)
        values["ft"] = "%.2f" % (distance / 25.4 / 12)
        values["yd"] = "%.2f" % (distance / 25.4 / 36)
        return values

    @api("Distance")
    @request("GET", "sensor/distance/mm")
    @response("%.02f")
    def getMillimeter(self):
        return self.__getMillimeter__()

    @api("Distance")
    @request("GET", "sensor/distance/cm")
    @response("%.02f")
    def getCentimeter(self):
        return self.getMillimeter() / 10

    @api("Distance")
    @request("GET", "sensor/distance/m")
    @response("%.02f")
    def getMeter(self):
        return self.getMillimeter() / 1000

    @api("Distance")
    @request("GET", "sensor/distance/in")
    @response("%.02f")
    def getInch(self):
        return self.getMillimeter() / 25.4

    @api("Distance")
    @request("GET", "sensor/distance/ft")
    @response("%.02f")
    def getFoot(self):
        return self.getInch() / 12

    @api("Distance")
    @request("GET", "sensor/distance/yd")
    @response("%.02f")
    def getYard(self):
        return self.getInch() / 36

class Humidity():
    def __family__(self):
        return "Humidity"

    def __getHumidity__(self):
        raise NotImplementedError

    @api("Humidity", 0)
    @request("GET", "sensor/humidity/*")
    @response(contentType=M_JSON)
    def humidityWildcard(self):
        values = {}
        humidity = self.__getHumidity__()
        values["float"]   = "%f" % humidity
        values["percent"] = "%d" % (humidity * 100)
        return values

    @api("Humidity")
    @request("GET", "sensor/humidity/float")
    @response("%f")
    def getHumidity(self):
        return self.__getHumidity__()

    @api("Humidity")
    @request("GET", "sensor/humidity/percent")
    @response("%d")
    def getHumidityPercent(self):
        return self.__getHumidity__() * 100

class Color():
    def __family__(self):
        return "Color"

    def __getRGB__(self):
        # Expected result: tuple r,g,b all values integer between 0 and 255
        raise NotImplementedError

    def __getRGB16bpp__(self):
        # Expected result: tuple r,g,b all values integer between 0 and 65535
        raise NotImplementedError

    def RGB16bpp2Kelvin(self, rgb16bpp_values=None):
        # This calculation is based on the tech note from ams (formerly TAOS)
        # Maybe this code should go to the TAOS drivers
        # Keep in mind: This conversion makes only sense to colors near to white!

        if rgb16bpp_values == None:
            r, g, b = self.__getRGB16bpp__()
        else:
            r, g, b = rgb16bpp_values

        # X = (-0.14282 * r) + (1.54924 * g) + (-0.95641 * b)
        # Y = (-0.32466 * r) + (1.57837 * g) + (-0.73191 * b)
        # Z = (-0.68202 * r) + (0.77073 * g) + ( 0.56332 * b)
        # x = X /(X+Y+Z)
        # y = Y /(X+Y+Z)
        # n = (x - 0.3320) / (0.1858 - y)

        n = ((0.23881 * r) + (0.25499 * g) + (-0.58291 * b)) / ((0.11109 * r) + (-0.85406 * g) +(0.52289 * b))
        cct = 449 * n**3 + 3525 * n**2 + 6823.3 * n + 5520.33

        return int(round(cct))


    @api("Color", 0)
    @request("GET", "sensor/color/*")
    @response(contentType=M_JSON)
    def colorWildcard(self):
        values = {}
        rgb16bpp_values = self.__getRGB16bpp__()
        r16, g16, b16 = rgb16bpp_values
        r = int(round(r16 / 256))
        g = int(round(g16 / 256))
        b = int(round(b16 / 256))
        values["hex"]   = "#%02X%02X%02X" % (r, g, b)
        values["red"]   = "%d" % r
        values["green"] = "%d" % g
        values["blue"]  = "%d" % b
        values["K"]     = "%d"    % self.RGB16bpp2Kelvin(rgb16bpp_values)
        return values

    @api("Color", 1)
    @request("GET", "sensor/color/16bpp/*")
    @response(contentType=M_JSON)
    def colorWildcard16bpp(self):
        values = {}
        rgb16bpp_values = self.__getRGB16bpp__()
        r16, g16, b16 = rgb16bpp_values
        values["red"]   = "%d" % r16
        values["green"] = "%d" % g16
        values["blue"]  = "%d" % b16
        values["K"]     = "%d"    % self.RGB16bpp2Kelvin(rgb16bpp_values)
        return values

    @api("Color")
    @request("GET", "sensor/color/rgb")
    @response("%s")
    def getRGB(self):
        r, g, b = self.__getRGB__()
        return "%s,%s,%s" % (r, g, b)

    @api("Color")
    @request("GET", "sensor/color/rgb/hex")
    @response("%s")
    def getRGBHex(self):
        r, g, b = self.__getRGB__()
        return "#%02X%02X%02X" % (r, g, b)

    @api("Color")
    @request("GET", "sensor/color/red")
    @response("%d")
    def getRed(self):
        r, g, b = self.__getRGB__()
        return r

    @api("Color")
    @request("GET", "sensor/color/green")
    @response("%d")
    def getGreen(self):
        r, g, b = self.__getRGB__()
        return g

    @api("Color")
    @request("GET", "sensor/color/blue")
    @response("%d")
    def getBlue(self):
        r, g, b = self.__getRGB__()
        return b

    @api("Color", 3)
    @request("GET", "sensor/color/rgb/16bpp")
    @response("%s")
    def getRGB16bpp(self):
        r, g, b = self.__getRGB16bpp__()
        return "%s,%s,%s" % (r, g, b)

    @api("Color")
    @request("GET", "sensor/color/k")
    @response("%d")
    def getKelvin(self):
        return self.RGB16bpp2Kelvin()

class Current():
    def __family__(self):
        return "Current"

    def __getMilliampere__(self):
        raise NotImplementedError

    @api("Current", 0)
    @request("GET", "sensor/current/*")
    @response(contentType=M_JSON)
    def currentWildcard(self):
        values = {}
        current = self.__getMilliampere__()
        values["mA"] = "%.3f" % current
        values["A"]  = "%.3f" % (current * 1000)
        return values

    @api("Current")
    @request("GET", "sensor/current/mA")
    @response("%.3f")
    def getMilliampere(self):
        return self.__getMilliampere__()

    @api("Current")
    @request("GET", "sensor/current/A")
    @response("%.3f")
    def getAmpere(self):
        return self.__getMilliampere__() * 1000

class Voltage():
    def __family__(self):
        return "Voltage"

    def __getVolt__(self):
        raise NotImplementedError

    @api("Voltage", 0)
    @request("GET", "sensor/voltage/*")
    @response(contentType=M_JSON)
    def voltageWildcard(self):
        values = {}
        voltage = self.__getVolt__()
        values["V"]  = "%.3f" % voltage
        values["mV"] = "%.3f" % (voltage / 1000)
        return values

    @api("Voltage")
    @request("GET", "sensor/voltage/V")
    @response("%.3f")
    def getVolt(self):
        return self.__getVolt__()

    @api("Voltage")
    @request("GET", "sensor/voltage/mV")
    @response("%.3f")
    def getMillivolt(self):
        return self.__getVolt__() / 1000

class Power():
    def __family__(self):
        return "Power"

    def __getWatt__(self):
        raise NotImplementedError

    @api("Power", 0)
    @request("GET", "sensor/power/*")
    @response(contentType=M_JSON)
    def powerWildcard(self):
        values = {}
        power = self.__getWatt__()
        values["kW"] = "%.3f" % (power * 1000)
        values["W"]  = "%.3f" % power
        values["mW"] = "%.3f" % (power / 1000)
        return values

    @api("Power")
    @request("GET", "sensor/power/kW")
    @response("%.3f")
    def getKilowatt(self):
        return self.__getWatt__() / 1000

    @api("Power")
    @request("GET", "sensor/power/W")
    @response("%.3f")
    def getWatt(self):
        return self.__getWatt__()

    @api("Power")
    @request("GET", "sensor/power/mW")
    @response("%.3f")
    def getMilliwatt(self):
        return self.__getWatt__() * 1000


class LinearVelocity():

    def __family__(self):
        return "LinearVelocity"

    def __getMeterPerSecondX__(self):
        raise NotImplementedError

    def __getMeterPerSecondY__(self):
        raise NotImplementedError

    def __getMeterPerSecondZ__(self):
        raise NotImplementedError

    def MeterPerSecond2KmPerHour(self, value=0):
        return value * 3.6

    def KmPerHour2MeterPerSecond(self, value=0):
        return value / 3.6

    @api("LinearVelocity", 0)
    @request("GET", "sensor/velocity/linear/*")
    @response(contentType=M_JSON)
    def linearVelocityWildcard(self):
        values = {}
        x = self.getMeterPerSecondX()
        y = self.getMeterPerSecondY()
        z = self.getMeterPerSecondZ()
        values["x.m/s"] = "%.3f" % x
        values["y.m/s"] = "%.3f" % y
        values["z.m/s"] = "%.3f" % z
        return values

    @api("LinearVelocity", 0)
    @request("GET", "sensor/velocity/speed/*")
    @response(contentType=M_JSON)
    def speedWildcard(self):
        values = {}
        x = self.MeterPerSecond2KmPerHour(self.getMeterPerSecondX())
        y = self.MeterPerSecond2KmPerHour(self.getMeterPerSecondY())
        z = self.MeterPerSecond2KmPerHour(self.getMeterPerSecondZ())
        values["x.km/h"] = "%.3f" % x
        values["y.km/h"] = "%.3f" % y
        values["z.km/h"] = "%.3f" % z
        return values

    @request("GET", "sensor/velocity/linear/x/m_s")
    @response("%.3f")
    def getMeterPerSecondX(self):
        return self.__getMeterPerSecondX__()

    @request("GET", "sensor/velocity/linear/y/m_s")
    @response("%.3f")
    def getMeterPerSecondY(self):
        return self.__getMeterPerSecondY__()

    @request("GET", "sensor/velocity/linear/z/m_s")
    @response("%.3f")
    def getMeterPerSecondZ(self):
        return self.__getMeterPerSecondZ__()

class AngularVelocity():

    def PI(self):
        return 3.141592653589793

    def __family__(self):
        return "AngularVelocity"

    def __getRadianPerSecondX__(self):
        raise NotImplementedError

    def __getRadianPerSecondY__(self):
        raise NotImplementedError

    def __getRadianPerSecondZ__(self):
        raise NotImplementedError

    def RadianPerSecond2DegreePerSecond(self, value=0):
        return value / self.PI() * 180

    def DegreePerSecond2RadianPerSecond(self, value=0):
        return value * self.PI() / 180

    def RadianPerSecond2Hertz(self, value=0):
        return value / self.PI() / 2

    def Hertz2RadianPerSecond(self, value=0):
        return value * self.PI() * 2


    @api("AngularVelocity", 0)
    @request("GET", "sensor/velocity/angular/*")
    @response(contentType=M_JSON)
    def angularVelocityWildcard(self):
        values = {}
        x = self.getRadianPerSecondX()
        y = self.getRadianPerSecondY()
        z = self.getRadianPerSecondZ()
        values["x.rad/s"] = "%.3f" % x
        values["y.rad/s"] = "%.3f" % y
        values["z.rad/s"] = "%.3f" % z
        return values

    @api("AngularVelocity", 0)
    @request("GET", "sensor/velocity/rotation/*")
    @response(contentType=M_JSON)
    def rotationWildcard(self):
        values = {}
        x = self.RadianPerSecond2Hertz(self.getRadianPerSecondX())
        y = self.RadianPerSecond2Hertz(self.getRadianPerSecondY())
        z = self.RadianPerSecond2Hertz(self.getRadianPerSecondZ())
        values["x.Hz"] = "%.3f" % x
        values["y.Hz"] = "%.3f" % y
        values["z.Hz"] = "%.3f" % z
        return values


    @request("GET", "sensor/velocity/angular/x/rad_s")
    @response("%.3f")
    def getRadianPerSecondX(self):
        return self.__getRadianPerSecondX__()

    @request("GET", "sensor/velocity/angular/y/rad_s")
    @response("%.3f")
    def getRadianPerSecondY(self):
        return self.__getRadianPerSecondY__()

    @request("GET", "sensor/velocity/angular/z/rad_s")
    @response("%.3f")
    def getRadianPerSecondZ(self):
        return self.__getRadianPerSecondZ__()

class Velocity(LinearVelocity, AngularVelocity):

    def __family__(self):
        return [LinearVelocity.__family__(self), AngularVelocity.__family__(self)]

class LinearAcceleration():

    def StandardGravity(self):
        return 9.80665

    def __family__(self):
        return "LinearAcceleration"

    def __getMeterPerSquareSecondX__(self):
        raise NotImplementedError

    def __getMeterPerSquareSecondY__(self):
        raise NotImplementedError

    def __getMeterPerSquareSecondZ__(self):
        raise NotImplementedError

    def __getGravityX__(self):
        raise NotImplementedError

    def __getGravityY__(self):
        raise NotImplementedError

    def __getGravityZ__(self):
        raise NotImplementedError

    def MeterPerSquareSecond2Gravity(self, value=0):
        return value / self.StandardGravity()

    def Gravity2MeterPerSquareSecond(self, value=0):
        return value * self.StandardGravity()

    @api("LinearAcceleration", 0)
    @request("GET", "sensor/acceleration/linear/*")
    @response(contentType=M_JSON)
    def linearAccelerationWildcard(self):
        values = {}
        x = self.getMeterPerSquareSecondX()
        y = self.getMeterPerSquareSecondY()
        z = self.getMeterPerSquareSecondZ()
        values["x.m/s2"] = "%.3f" % x
        values["y.m/s2"] = "%.3f" % y
        values["z.m/s2"] = "%.3f" % z
        return values

    @api("LinearAcceleration", 0)
    @request("GET", "sensor/acceleration/gravity/*")
    @response(contentType=M_JSON)
    def gravityAccelerationWildcard(self):
        values = {}
        x = self.getGravityX()
        y = self.getGravityY()
        z = self.getGravityZ()
        values["x.g"] = "%.3f" % x
        values["y.g"] = "%.3f" % y
        values["z.g"] = "%.3f" % z
        return values

    @request("GET", "sensor/acceleration/linear/x/m_s2")
    @response("%.3f")
    def getMeterPerSquareSecondX(self):
        return self.__getMeterPerSquareSecondX__()

    @request("GET", "sensor/acceleration/linear/y/m_s2")
    @response("%.3f")
    def getMeterPerSquareSecondY(self):
        return self.__getMeterPerSquareSecondY__()

    @request("GET", "sensor/acceleration/linear/z/m_s2")
    @response("%.3f")
    def getMeterPerSquareSecondZ(self):
        return self.__getMeterPerSquareSecondZ__()

    @request("GET", "sensor/acceleration/gravity/x/g")
    @response("%.3f")
    def getGravityX(self):
        return self.__getGravityX__()

    @request("GET", "sensor/acceleration/gravity/y/g")
    @response("%.3f")
    def getGravityY(self):
        return self.__getGravityY__()

    @request("GET", "sensor/acceleration/gravity/z/g")
    @response("%.3f")
    def getGravityZ(self):
        return self.__getGravityZ__()

    @request("GET", "sensor/acceleration/gravity/x/mg")
    @response("%.3f")
    def getMilliGravityX(self):
        return float(self.__getGravityX__()) * 1000.0

    @request("GET", "sensor/acceleration/gravity/y/mg")
    @response("%.3f")
    def getMilliGravityY(self):
        return float(self.__getGravityY__()) * 1000.0

    @request("GET", "sensor/acceleration/gravity/z/mg")
    @response("%.3f")
    def getMilliGravityZ(self):
        return float(self.__getGravityZ__()) * 1000.0

class AngularAcceleration():

    def __family__(self):
        return "AngularAcceleration"

    def __getRadianPerSquareSecondX__(self):
        raise NotImplementedError

    def __getRadianPerSquareSecondY__(self):
        raise NotImplementedError

    def __getRadianPerSquareSecondZ__(self):
        raise NotImplementedError

    @api("AngularAcceleration", 0)
    @request("GET", "sensor/acceleration/angular/*")
    @response(contentType=M_JSON)
    def angularAccelerationWildcard(self):
        values = {}
        x = self.getRadianPerSquareSecondX()
        y = self.getRadianPerSquareSecondY()
        z = self.getRadianPerSquareSecondZ()
        values["x.rad/s2"] = "%.3f" % x
        values["y.rad/s2"] = "%.3f" % y
        values["z.rad/s2"] = "%.3f" % z
        return values

    @request("GET", "sensor/acceleration/angular/x/rad_s2")
    @response("%.3f")
    def getRadianPerSquareSecondX(self):
        return self.__getRadianPerSquareSecondX__()

    @request("GET", "sensor/acceleration/angular/y/rad_s2")
    @response("%.3f")
    def getRadianPerSquareSecondY(self):
        return self.__getRadianPerSquareSecondY__()

    @request("GET", "sensor/acceleration/angular/z/rad_s2")
    @response("%.3f")
    def getRadianPerSquareSecondZ(self):
        return self.__getRadianPerSquareSecondZ__()

class Acceleration(LinearAcceleration, AngularAcceleration):

    def __family__(self):
        return [LinearAcceleration.__family__(self), AngularAcceleration.__family__(self)]


DRIVERS = {}
DRIVERS["bmp085"] = ["BMP085", "BMP180"]
DRIVERS["onewiretemp"] = ["DS1822", "DS1825", "DS18B20", "DS18S20", "DS28EA00"]
DRIVERS["tmpXXX"] = ["TMP36", "TMP75", "TMP102", "TMP275"]
DRIVERS["tslXXXX"] = ["TSL2561", "TSL2561CS", "TSL2561T", "TSL4531", "TSL45311", "TSL45313", "TSL45315", "TSL45317"]
DRIVERS["vcnl4000"] = ["VCNL4000"]
DRIVERS["hytXXX"] = ["HYT221"]
##DRIVERS["tcs3472X"] = ["TCS34721", "TCS34723", "TCS34725", "TCS34727"]
##DRIVERS["honXXXpressure"] = ["HONXSCPI", "HONXSCPTI", "HONXSCPS", "HONXSCPTS", "HONABPPI", "HONABPPTI", "HONABPPS", "HONABPPTS"]
##DRIVERS["mcptmp"] = ["MCP9808"]
##DRIVERS["ina219"] = ["INA219"]
##DRIVERS["lis3dh"] = ["LIS3DH"]
##DRIVERS["simulatedsensors"] = ["PRESSURE", "TEMPERATURE", "LUMINOSITY", "DISTANCE", "HUMIDITY",
##                         "COLOR", "CURRENT", "VOLTAGE", "POWER",
##                         "LINEARVELOCITY", "ANGULARVELOCITY", "VELOCITY",
##                         "LINEARACCELERATION", "ANGULARACCELERATION", "ACCELERATION",
##                         "SENSORS"]
##DRIVERS["variablesimulatedsensors"] = ["VPRESSURE", "VTEMPERATURE", "VLUMINOSITY", "VDISTANCE", "VHUMIDITY",
##                         "VCOLOR", "VCURRENT", "VVOLTAGE", "VPOWER",
##                         "VLINEARVELOCITY", "VANGULARVELOCITY",
##                         "VLINEARACCELERATION", "VANGULARACCELERATION",
##                         "VSENSORS"]

driverDetector(__file__, DRIVERS)

