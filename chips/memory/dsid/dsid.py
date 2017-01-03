#   Copyright 2014-2016 Andreas Riegg - t-h-i-n-x.net
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
#   1.0    2014-11-12    Initial release.
#   1.1    2016-08-11    Added @api annotations and bus selection.
#
#   Config parameters
#
#   - bus           String      Name of the I2C bus to use.
#   
#   Usage remarks
#
#   - Slave address is fixed to 0x50
#   - Chip has just 8 bytes of unique factory-lasered ROM memory being
#     1 byte family code (0x70), 6 byte serial number, 1 byte CRC-8 of first 7 bytes
#
#   Implementation remarks
#
#   - This driver is implemented just to be able to read the 8 id bytes
#

from webiopi.decorators.rest import request, response, api
from webiopi.devices.i2c import I2C
from webiopi.devices.memory import Memory


class DS28CM00(I2C, Memory):

#---------- Class initialisation ----------

    def __init__(self, bus=None):
        I2C.__init__(self, 0x50, bus)
        Memory.__init__(self, 8)

#---------- Abstraction framework contracts ----------
            
    def __str__(self):
        return "DS28CM00(slave=0x%02X, dev=%s)" % (self.slave, self.device())

    def __family__(self):
        #return "Id" -> todo: add abstraction for Id, use Memory until then
        return "Memory"


#---------- Memory abstraction related methods ----------

    def __readMemoryByte__(self, address):
        return self.readRegister(address)

#---------- Digital serial number convenience method ----------

    @api("Id", source="driver")
    @request("GET", "id")
    @response("%s")
    def serialNumber(self):
    # ignore crc byte
        data = self.readMemoryBytes()
        family = data[0]
        sn = data[1] | data[2]<<8 | data[3]<<16 | data[4]<<24 | data[5]<<32 | data[6]<<40
        return "%02x-%012x" % (family, sn)

    @api("Id", 3, source="driver")
    @request("GET", "id/raw")
    @response("%s")
    def serialNumberRaw(self):
    # ignore crc byte
        data = self.readMemoryBytes()
        val = data[0] | data[1]<<8 | data[2]<<16 | data[3]<<24 | data[4]<<32 | data[5]<<40 | data[6]<<48
        return "0x%014x" % val


