#   Copyright 2012-2016 Eric Ptak - trouch.com
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
#   1.0    2016-03-03    Initial release based on WebIOPi 0.7.22
#   1.1    2016-06-28    Added support for bus selection.
#

from webiopi.utils.types import toint, signInteger
from webiopi.devices.i2c import I2C
from webiopi.devices.sensor import Temperature
from webiopi.devices.analog.helper import AnalogSensor

class TMP36(Temperature, AnalogSensor):
    def __init__(self, adc, channel):
        AnalogSensor.__init__(self, adc, channel)
        
    def __str__(self):
        return "TMP36(ADC=%s/%s)" % (self.adcname, self.channel)
        
    def __getKelvin__(self):
        return self.Celsius2Kelvin()

    def __getCelsius__(self):
        return (self.readVolt()*1000 - 500) / 10
    
    def __getFahrenheit__(self):
        return self.Celsius2Fahrenheit()


class TMP102(I2C, Temperature):
    def __init__(self, slave=0x48, bus=None):
        I2C.__init__(self, toint(slave), bus)
        
    def __str__(self):
        return "TMP102(slave=0x%02X, dev=%s)" % (self.slave, self.device())

    def __getKelvin__(self):
        return self.Celsius2Kelvin()

    def __getCelsius__(self):
        d = self.readBytes(2)
        count = ((d[0] << 4) | (d[1] >> 4)) & 0xFFF
        return signInteger(count, 12)*0.0625
    
    def __getFahrenheit__(self):
        return self.Celsius2Fahrenheit()

class TMP75(TMP102):
    def __init__(self, slave=0x48, resolution=12, bus=None):
        TMP102.__init__(self, slave, bus)
        resolution = toint(resolution)
        if not resolution in range(9,13):
            raise ValueError("%dbits resolution out of range [%d..%d]bits" % (resolution, 9, 12))
        self.resolution = resolution
        
        config  = self.readRegister(0x01)
        config &= ~0x60
        config |= (self.resolution - 9) << 5
        self.writeRegister(0x01, config)
        self.readRegisters(0x00, 2)

    def __str__(self):
        return "TMP75(slave=0x%02X, dev=%s, resolution=%d-bits)" % (self.slave, self.device(), self.resolution)

        
class TMP275(TMP75):
    def __init__(self, slave=0x48, resolution=12, bus=None):
        TMP75.__init__(self, slave, resolution, bus)

    def __str__(self):
        return "TMP275(slave=0x%02X, dev=%s, resolution=%d-bits)" % (self.slave, self.device(), self.resolution)
        
