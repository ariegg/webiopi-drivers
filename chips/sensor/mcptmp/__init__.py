#   Copyright 2012-2016 Eric Ptak - trouch.com
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
#   1.0    2016-04-30    Initial release based on WebIOPi 0.7.22
#   1.1    2016-08-12    Added @api annotations and /* state routes
#                        Bugfix, inch calculation was wrong /0.254 -> /25.4
#   1.2    2016-08-22    Added TCS3472X color sensors.
#   1.3    2016-09-26    Added all SENSORS class.
#   1.4    2016-12-12    Added Current, Voltage and Power abstractions.
#

from webiopi.utils.types import toint
from webiopi.utils.types import M_JSON
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
        values["pa"] = pressure
        values["hpa"] = "%.02f" % (pressure / 100.0)
        return values

    @api("Pressure", 0)
    @request("GET", "sensor/pressure/sea/*")
    @response(contentType=M_JSON)
    def pressureWildcardSea(self):
        values = {}
        pressureAtSea = self.getPascalAtSea()
        values["pa"] = pressureAtSea
        values["hpa"] = "%.02f" % (pressureAtSea / 100.0)
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
        values["c"] = "%.02f" % temperature
        values["k"] = "%.02f" % self.Celsius2Kelvin(temperature)
        values["f"] = "%.02f" % self.Celsius2Fahrenheit(temperature)
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
        values["lux"] = "%.02f" % luminosity
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
        values["mm"] = "%.02f" % distance
        values["cm"] = "%.02f" % (distance / 10)
        values["m"]  = "%.02f" % (distance / 1000)
        values["in"] = "%.02f" % (distance / 25.4)
        values["ft"] = "%.02f" % (distance / 25.4 / 12)
        values["yd"] = "%.02f" % (distance / 25.4 / 36)
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
        values["k"]     = "%d"    % self.RGB16bpp2Kelvin(rgb16bpp_values)
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
        values["k"]     = "%d"    % self.RGB16bpp2Kelvin(rgb16bpp_values)
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
        values["mA"] = "%.03f" % current
        values["A"]  = "%.03f" % (current * 1000)
        return values

    @api("Current")
    @request("GET", "sensor/current/mA")
    @response("%.03f")
    def getMilliampere(self):
        return self.__getMilliampere__()

    @api("Current")
    @request("GET", "sensor/current/A")
    @response("%.03f")
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
        values["V"]  = "%.03f" % voltage
        values["mV"] = "%.03f" % (voltage / 1000)
        return values

    @api("Voltage")
    @request("GET", "sensor/voltage/V")
    @response("%.03f")
    def getVolt(self):
        return self.__getVolt__()

    @api("Voltage")
    @request("GET", "sensor/voltage/mV")
    @response("%.03f")
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
        values["kW"] = "%.03f" % (power * 1000)
        values["W"]  = "%.03f" % power
        values["mW"] = "%.03f" % (power / 1000)
        return values

    @api("Power")
    @request("GET", "sensor/power/kW")
    @response("%.03f")
    def getKilowatt(self):
        return self.__getWatt__() / 1000

    @api("Power")
    @request("GET", "sensor/power/W")
    @response("%.03f")
    def getWatt(self):
        return self.__getWatt__()

    @api("Power")
    @request("GET", "sensor/power/mW")
    @response("%.03f")
    def getMilliwatt(self):
        return self.__getWatt__() * 1000


DRIVERS = {}
DRIVERS["bmp085"] = ["BMP085", "BMP180"]
DRIVERS["onewiretemp"] = ["DS1822", "DS1825", "DS18B20", "DS18S20", "DS28EA00"]
DRIVERS["tmpXXX"] = ["TMP36", "TMP75", "TMP102", "TMP275"]
DRIVERS["tslXXXX"] = ["TSL2561", "TSL2561CS", "TSL2561T", "TSL4531", "TSL45311", "TSL45313", "TSL45315", "TSL45317"]
DRIVERS["tcs3472X"] = ["TCS34721", "TCS34723", "TCS34725", "TCS34727"]
DRIVERS["vcnl4000"] = ["VCNL4000"]
DRIVERS["hytXXX"] = ["HYT221"]
DRIVERS["honXXXpressure"] = ["HONXSCPI", "HONXSCPTI", "HONXSCPS", "HONXSCPTS", "HONABPPI", "HONABPPTI", "HONABPPS", "HONABPPTS"]
DRIVERS["mcptmp"] = ["MCP9808"]
DRIVERS["ina219"] = ["INA219"]
DRIVERS["sensormock"] = ["PRESSURE", "TEMPERATURE", "LUMINOSITY", "DISTANCE", "HUMIDITY", "COLOR", "CURRENT", "VOLTAGE", "POWER", "SENSORS"]

