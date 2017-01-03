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
#   1.0    2016-04-01    Initial release.
#   1.1    2016-06-22    Added support for bus selection.
#


from webiopi.utils.types import toint, signInteger
from webiopi.devices.i2c import I2C
from webiopi.devices.sensor import Temperature

class MCP9808(I2C, Temperature):
    def __init__(self, slave=0x18, resolution=12, bus=None):
        I2C.__init__(self, toint(slave), bus)

        resolution = toint(resolution)
        if not resolution in range(9,13):
            raise ValueError("%dbits resolution out of range [%d..%d]bits" % (resolution, 9, 12))
        self.resolution = resolution
        self.writeRegister(0x08, (resolution - 9))
        
    def __str__(self):
        return "MCP9808(slave=0x%02X, dev=%s)" % (self.slave, self.device())
        
    def __getKelvin__(self):
        return self.Celsius2Kelvin()

    def __getCelsius__(self):
        d = self.readRegisters(0x05, 2)
        count = ((d[0] << 8) | d[1]) & 0x1FFF
        return signInteger(count, 13)*0.0625
    
    def __getFahrenheit__(self):
        return self.Celsius2Fahrenheit()

