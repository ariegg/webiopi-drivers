#   Copyright 2015-2016 Andreas Riegg - t-h-i-n-x.net
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
#   1.0    2015-08-28    Initial release.
#   1.1    2015-09-01    inH2O added, readRaw splitted, diagnostic condition
#                        detection added, transfer count matrix value bugfix.
#   1.2    2015-09-07    Driver filename changed. Bugfix and simplifications.
#                        ABP... series chips added.
#   1.3    2016-08-18    Added @api annotations.
#   1.4    2016-08-26    Added bus selection.
#
#   Config parameters
#
#   - slave         8 bit       Value of the I2C slave address for the I2C
#                               versions of the chips. Defaults to 0x28.
#
#   - chip          0, 1        Value of the chip enable (CE) pin/port for
#                               the SPI versions of the chips. Defaults to 0.
#                               Connect this signal to the SS pin.
#
#   - unit          'Pa','bar','psi','inH2O' (for HSC... and SSC... series)
#                   'Pa','bar','psi',        (for ABP... series)

#                               Unit type value of the sensor pressure range.
#                               Defaults to 'Pa'.
#
#   - pmin          float       Minimum value of the sensor pressure range
#                               as float. Only values in the supported units
#                               are allowed, so for e.g. -16 kPa use -16000.0
#                               Defaults to 0.0
#
#   - pmax          float       Maximum value of the sensor pressure range
#                               as float. Only values in the supported units
#                               are allowed, so for e.g. 600 mbar use 0.6
#                               Defaults to 100000.0 (1000 kPa).
#
#   - transfer      'A','B','C','F'  (for HSC... and SSC... series)
#                   'A','D','S','T'  (for ABP... series)

#                               String value of the sensor transfer function.
#                               See chip spec for details.
#                               Defaults to 'A' (10% to 90%).
#
#   - altitude      int         Integer value of the topological height of
#                               the sensor. This allows to calculate a good
#                               approximation of the absolute pressure at sea
#                               level. Makes only sense for the gauge version
#                               of the chips. Defaults to 0.
#
#   - external      string      This is the name of another temperature sensor
#                               within WebIOPi that measures outside temperature.
#                               Using the external temperature instead of the
#                               local (typically inside) temperature improves
#                               the value of the sea level pressure approximation.
#                               Makes only sense for the gauge version of the
#                               chips. Defaults to None.
#
#   - bus           String      Name of the I2C or SPI bus to use.
#
#   Usage remarks
#
#   - This driver supports ALL HSC...,  SSC... and ABP... series of the chips.
#     Versions with analog output are NOT supported by this driver.
#
#   - This driver has 8 concrete chip classes that have to be used:
#     = The classes with an '...I' at the end are for the I2C versions.
#     = The classes with an '...S' at the end are for the SPI versions.
#     = The classes with '...XSC...' in their name are for the HSC... and
#       SSC... series.
#     = The classes with '...ABP...' in their name are for the ABP... series.
#     = The classes with an '...P.' in their name map only pressure values.
#     = The classes with an '...PT.' in their name map pressure and temperature
#       values.
#
#   - The final selection of the concrete chip subversions is achieved
#     by using the appropriate config file parameters.
#
#   - A sample config file entry for chip "HSC SANN 150PA 2F5" would be:
#     myhsc1 = HONXSCPTI unit:psi pmax:150.0 transfer:F
#
#   - A sample config file entry for chip "ABP DNNN 060MD SA3" would be:
#     myhsc2 = HONABPPS unit:bar pmin:-0.06 pmax:0.06
#
#   Implementation remarks
#
#   - This driver has been coded using the chip spec. Due to lack of sample
#     chips this driver has been tested with simulated I2C and SPI calls.
#
#   - Due to the immense variability of possible chips of the HSC...,
#     SSC... and ABP... series it was not possible to test it with every
#     variant of the chips.
#
#   - The SPI protocol of the Honeywell chips is unidirectional and this
#     could be incompatible with the SPI library call used by this driver.
#     Due to lack of sample SPI chips this has not been tested so far.
#
#   - The ABP chips with the sleep function are not supported as the wakeup
#     is initiated by a 0 byte read command and this could not be tested.
#
#   - According to the chip spec, for I2C the minimum frequency is 100 kHz
#     and the maximum is 400 kHz. For SPI, these values are 50 kHz and 800 kHz.
#

from webiopi.utils.types import toint
from webiopi.devices.i2c import I2C
from webiopi.devices.spi import SPI
from webiopi.devices.sensor import Temperature, Pressure
from webiopi.decorators.rest import request, response, api


#---------- Abstract class for the HSC... and SSC... chip variants ----------

class HONXSC():

#---------- Class initialisation ----------

    def __init__(self):

        self.TRANSFER = {'A':{'min':1638,'max':14745},
                         'B':{'min': 819,'max':15563},
                         'C':{'min': 819,'max':13925},
                         'F':{'min': 655,'max':15400}}

        self.UNIT =     ['Pa','bar','psi','inH2O']


#---------- Abstract class for the ABP... chip variants ----------

class HONABP():

#---------- Class initialisation ----------

    def __init__(self):

        self.TRANSFER = {'A':{'min':1638,'max':14745},
                         'D':{'min':1638,'max':14745},
                         'S':{'min':1638,'max':14745},
                         'T':{'min':1638,'max':14745}}

        self.UNIT =     ['Pa','bar','psi']


#---------- Abstract class for the I2C chip variants ----------

class HONI2C(I2C):

#---------- Class initialisation ----------

    def __init__(self, slave, bus):
        I2C.__init__(self, toint(slave), bus)

#---------- Local helpers ----------

    def readRawFull(self):
        return self.readBytes(4)

    def readRawShort(self):
        return self.readBytes(2)


#---------- Abstract class for the SPI chip variants ----------

class HONSPI(SPI):

#---------- Class initialisation ----------

    def __init__(self, chip, mode, bits, speed, bus):
        SPI.__init__(self, chip, mode, bits, speed, bus)

#---------- Local helpers ----------

    def readRawFull(self):
        data = bytearray(4)
        return self.xfer(data)

    def readRawShort(self):
        data = bytearray(2)
        return self.xfer(data)


#---------- Abstract class that maps only pressure ----------

class HONXXXP(Pressure):

#---------- Constants and definitons ----------

    MS_BYTEMASK = 0b00111111
    FAULT_FLAGS = 0b11

    TRANSFER = {}
    UNIT =     []

#---------- Class initialisation ----------

    def __init__(self, unit, pmin, pmax, transfer, altitude, external):
        Pressure.__init__(self, altitude, external)
        self.pmin = float(pmin)
        self.pmax = float(pmax)

        if not unit in self.UNIT:
            raise ValueError("unit value \'%s\' out of range %s" % (unit, self.UNIT))
        self.unit = unit

        if not transfer in self.TRANSFER:
            raise ValueError("transfer value \'%s\' out of range %s" % (transfer, sorted(self.TRANSFER.keys())))
        self.transfer = transfer

#---------- Abstraction framework contracts ----------

    def __family__(self):
        return [Pressure.__family__(self)]

#---------- Pressure abstraction related methods ----------

    def __getPascal__(self):
        rawPressure = self.__getRawPressure__()
        if self.unit == 'Pa':
            return rawPressure
        elif self.unit == 'bar':
            return self.Bar2Pascal(rawPressure)
        elif self.unit == 'psi':
            return self.Psi2Pascal(rawPressure)
        elif self.unit == 'inH2O':
            return self.InH2O2Pascal(rawPressure)

#---------- Local helpers ----------

    def __getRawPressure__(self):
        rawdata = self.readRawShort()
        self.__checkDiagnosticCondition__(rawdata[0])

        pressureOutput = ((rawdata[0] & self.MS_BYTEMASK) << 8) + rawdata[1]
        outputMin = self.TRANSFER[self.transfer]['min']
        outputMax = self.TRANSFER[self.transfer]['max']
        return ((pressureOutput - outputMin) * (self.pmax - self.pmin) / (outputMax - outputMin)) + self.pmin

    def __checkDiagnosticCondition__(self, rawByte):
        if (rawByte & ~self.MS_BYTEMASK) >> 6 == self.FAULT_FLAGS:
            raise ValueError("hardware fault: sensor has detected a diagnostic condition")

#---------- Additional REST mappings to support 'psi', 'bar' and 'inH2O' units ----------
# This code could go up to __init__() to extend Pressure abstraction

    @api("Pressure", source="driver")
    @request("GET", "sensor/pressure/psi")
    @response("%.4f")
    def getPsi(self):
        return self.Pascal2Psi(self.__getPascal__())

    @api("Pressure", source="driver")
    @request("GET", "sensor/pressure/bar")
    @response("%.4f")
    def getBar(self):
        return self.Pascal2Bar(self.__getPascal__())

    @api("Pressure", source="driver")
    @request("GET", "sensor/pressure/inh2o")
    @response("%.4f")
    def getInH2O(self):
        return self.Pascal2InH2O(self.__getPascal__())

#---------- Additional conversion methods to support 'psi', 'bar' and 'inH2O' units ----------
# This code could go up to __init__() to extend Pressure abstraction

    def Pascal2Psi(self, value=None):
        if value == None:
            value = self.getPascal()
        return value * 0.000145037738

    def Psi2Pascal(self, value=None):
        if value == None:
            value = self.getPsi()
        return value * 6894.75729

    def Pascal2Bar(self, value=None):
        if value == None:
            value = self.getPascal()
        return value * 0.00001

    def Bar2Pascal(self, value=None):
        if value == None:
            value = self.getBar()
        return value * 100000.0

    def Pascal2InH2O(self, value=None):
        if value == None:
            value = self.getPascal()
        return value * 0.004014631332

    def InH2O2Pascal(self, value=None):
        if value == None:
            value = self.getInH2O()
        return value * 249.088875


#---------- Abstract class that maps pressure and temperature ----------

class HONXXXPT(HONXXXP, Temperature):

#---------- Class initialisation ----------

    def __init__(self, unit, pmin, pmax, transfer, altitude, external):
        HONXXXP.__init__(self, unit, pmin, pmax, transfer, altitude, external)


#---------- Abstraction framework contracts ----------

    def __family__(self):
        return [Pressure.__family__(self), Temperature.__family__(self)]

#---------- Temperature abstraction related methods ----------

    def __getCelsius__(self):
        rawdata = self.readRawFull()
        self.__checkDiagnosticCondition__(rawdata[0])

        temperatureOutput = (rawdata[2] << 3) + (rawdata[3] >> 5)
        return (temperatureOutput * 200.0 / 2047.0) - 50

    def __getKelvin__(self):
        return self.Celsius2Kelvin()

    def __getFahrenheit__(self):
        return self.Celsius2Fahrenheit()


#---------- Device classes for the I2C chip variants ----------
#---------- HSC... and SSC... chip variants

class HONXSCPI(HONXXXP, HONI2C, HONXSC):

#---------- Class initialisation ----------

    def __init__(self, slave=0x28, unit='Pa', pmin=0.0, pmax=100000.0, transfer='A', altitude=0, external=None, bus=None):
        HONXSC.__init__(self)
        HONI2C.__init__(self, toint(slave), bus)
        HONXXXP.__init__(self, unit, pmin, pmax, transfer, altitude, external)

#---------- Abstraction framework contracts ----------

    def __str__(self):
        return ("HONXSCPI(slave=0x%02X,dev=%s,unit=%s,pmin=%.4f,pmax=%.4f,transfer=%s)" %
                        (self.slave, self.device(), self.unit, self.pmin, self.pmax, self.transfer))


class HONXSCPTI(HONXXXPT, HONI2C, HONXSC):

#---------- Class initialisation ----------

    def __init__(self, slave=0x28, unit='Pa', pmin=0.0, pmax=100000.0, transfer='A', altitude=0, external=None, bus=None):
        HONXSC.__init__(self)
        HONI2C.__init__(self, toint(slave), bus)
        HONXXXPT.__init__(self, unit, pmin, pmax, transfer, altitude, external)

#---------- Abstraction framework contracts ----------

    def __str__(self):
        return ("HONXSCPTI(slave=0x%02X,dev=%s,unit=%s,pmin=%.4f,pmax=%.4f,transfer=%s)" %
                        (self.slave, self.device(), self.unit, self.pmin, self.pmax, self.transfer))

#---------- ABP... chip variants

class HONABPPI(HONXXXP, HONI2C, HONABP):

#---------- Class initialisation ----------

    def __init__(self, slave=0x28, unit='Pa', pmin=0.0, pmax=100000.0, transfer='A', altitude=0, external=None, bus=None):
        HONABP.__init__(self)
        HONI2C.__init__(self, toint(slave), bus)
        HONXXXP.__init__(self, unit, pmin, pmax, transfer, altitude, external)

#---------- Abstraction framework contracts ----------

    def __str__(self):
        return ("HONABPPI(slave=0x%02X,dev=%s,unit=%s,pmin=%.4f,pmax=%.4f,transfer=%s)" %
                        (self.slave, self.device(), self.unit, self.pmin, self.pmax, self.transfer))


class HONABPPTI(HONXXXPT, HONI2C, HONABP):

#---------- Class initialisation ----------

    def __init__(self, slave=0x28, unit='Pa', pmin=0.0, pmax=100000.0, transfer='A', altitude=0, external=None, bus=None):
        HONABP.__init__(self)
        HONI2C.__init__(self, toint(slave), bus)
        HONXXXPT.__init__(self, unit, pmin, pmax, transfer, altitude, external)

#---------- Abstraction framework contracts ----------

    def __str__(self):
        return ("HONABPPTI(slave=0x%02X,dev=%s,unit=%s,pmin=%.4f,pmax=%.4f,transfer=%s)" %
                        (self.slave, self.device(), self.unit, self.pmin, self.pmax, self.transfer))


#---------- Device classes for the SPI chip variants ----------
#---------- HSC... and SSC... chip variants

class HONXSCPS(HONXXXP, HONSPI, HONXSC):

#---------- Class initialisation ----------

    def __init__(self, chip=0, unit='Pa', pmin=0.0, pmax=100000.0, transfer='A', altitude=0, external=None, bus=None):
        HONXSC.__init__(self)
        HONSPI.__init__(self, toint(chip), 0, 8, 800000, bus)
        HONXXXP.__init__(self, unit, pmin, pmax, transfer, altitude, external)

#---------- Abstraction framework contracts ----------

    def __str__(self):
        return ("HONXSCPS(chip=%d,dev=%s,unit=%s,pmin=%.4f,pmax=%.4f,transfer=%s)" %
                    (self.chip, self.device(), self.unit, self.pmin, self.pmax, self.transfer))


class HONXSCPTS(HONXXXPT, HONSPI, HONXSC):

#---------- Class initialisation ----------

    def __init__(self, chip=0, unit='Pa', pmin=0.0, pmax=100000.0, transfer='A', altitude=0, external=None, bus=None):
        HONXSC.__init__(self)
        HONSPI.__init__(self, toint(chip), 0, 8, 800000, bus)
        HONXXXPT.__init__(self, unit, pmin, pmax, transfer, altitude, external)

#---------- Abstraction framework contracts ----------

    def __str__(self):
        return ("HONXSCPTS(chip=%d,dev=%s,unit=%s,pmin=%.4f,pmax=%.4f,transfer=%s)" %
                    (self.chip, self.device(), self.unit, self.pmin, self.pmax, self.transfer))

#---------- ABP... chip variants

class HONABPPS(HONXXXP, HONSPI, HONABP):

#---------- Class initialisation ----------

    def __init__(self, chip=0, unit='Pa', pmin=0.0, pmax=100000.0, transfer='A', altitude=0, external=None, bus=None):
        HONABP.__init__(self)
        HONSPI.__init__(self, toint(chip), 0, 8, 800000, bus)
        HONXXXP.__init__(self, unit, pmin, pmax, transfer, altitude, external)

#---------- Abstraction framework contracts ----------

    def __str__(self):
        return ("HONABPPS(chip=%d,dev=%s,unit=%s,pmin=%.4f,pmax=%.4f,transfer=%s)" %
                    (self.chip, self.device(), self.unit, self.pmin, self.pmax, self.transfer))


class HONABPPTS(HONXXXPT, HONSPI, HONABP):

#---------- Class initialisation ----------

    def __init__(self, chip=0, unit='Pa', pmin=0.0, pmax=100000.0, transfer='A', altitude=0, external=None, bus=None):
        HONABP.__init__(self)
        HONSPI.__init__(self, toint(chip), 0, 8, 800000, bus)
        HONXXXPT.__init__(self, unit, pmin, pmax, transfer, altitude, external)

#---------- Abstraction framework contracts ----------

    def __str__(self):
        return ("HONABPPTS(chip=%d,dev=%s,unit=%s,pmin=%.4f,pmax=%.4f,transfer=%s)" %
                    (self.chip, self.device(), self.unit, self.pmin, self.pmax, self.transfer))

