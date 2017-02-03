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
#   ----------------------------------------------------------------------------
#
#   Changelog
#
#   1.0    2015-10-09    Initial release.
#   1.1    2016-06-22    Added support for bus selection.
#   1.2    2016-07-28    Added compatibility with slave address detect feature from WebIOPi 0.7.22
#   1.3    2016-08-29    Make all results consistent to be bytearrays.
#
#   Implementation and usage remarks
#
#   Version for I2C simulation using Memory class.
#   The devicename for the mock memory instance is derived from the value
#   of dev. <dev> ist just a name and has no other meaning.
#
#   IMPORTANT: The memory device that provides the I2C mock memory has to
#   be defined before the I2C device that uses the bus simulation device in
#   the config file. Also make sure that the memory device has at least
#   enough bytes to allow accessing the highest register address used for
#   requests.
#

import webiopi
from webiopi.devices.bus import Bus, I2C_Bus
from webiopi.utils.logger import debug, info


class I2C_MOCK(I2C_Bus):
    def __init__(self, dev="", slave=0x00):
        Bus.__init__(self, "I2C", "mock:%s" % dev)
        I2C_Bus.__init__(self, slave)
        
        mockMemoryName = "%s" % dev
        self._memory = webiopi.deviceInstance(mockMemoryName)
        self._hasMock = self._memory != None
        
        debug("Mapped I2C bus device - %s" % self.__str__())


    def __str__(self):
        return "%s (dev=%s)" % (self.__class__.__name__, self.device)

#---------- Bus abstraction methods reimplementation ----------
    
    def open(self):
        debug("Opening I2C bus device - %s" % self.__str__())

    def close(self):
        debug("Closing I2C bus device - %s" % self.__str__())
        I2C_Bus.close(self)        

#---------- I2C abstraction communication methods redirected to reading/writing simulation memory ----------
    
    def readBytes(self, size=1):
        if self._hasMock:
            return bytearray(self._memory.readMemoryBytes(0, size))
        else:
            return bytearray(size)

    def writeBytes(self, data):
        if self._hasMock:
            self._memory.writeMemoryBytes(0, bytearray(data))

    def readRegister(self, addr):
        if self._hasMock:
            return self._memory.readMemoryByte(addr)
        else:
            return 0

    def readRegisters(self, addr, count):
        if self._hasMock:
            return bytearray(self._memory.readMemoryBytes(addr, addr + count))
        else:
            return bytearray(count)

    def writeRegister(self, addr, byte):
        if self._hasMock:
            self._memory.writeMemoryByte(addr, byte)

    def writeRegisters(self, addr, buff):
        if self._hasMock:
            self._memory.writeMemoryBytes(addr, buff)
