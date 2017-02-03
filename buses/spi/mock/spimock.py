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
#   1.0    2015-09-09    Initial release.
#
#   1.1    2016-06-22    Added support for bus selection.
#                        Added separate memory for SI and SO.
#
#   1.2    2016-06-30    Stream like function:
#                        - writing shifts into memory
#                        - reading shifts outof memory (and nulls out)
#   1.3    2016-08-29    Bugfix concat error for writeBytes.
#                        Make all results consistent to be bytearrays.
#
#   Implementation and usage remarks
#
#   Version for SPI simulation using Memory class.
#   The devicename for the mock memory instance is derived from the value
#   of dev.
#   Separate memory devices are used for SI (slave in) and SO (slave out).
#   The resulting memory device names are "<dev>_si" e.g. "spidev0.1_si" for
#   <dev> being "spidev0.1" and SI as well as "spimock_so" for <dev>
#   being "spimock" and SO. <dev> ist just a name and has no other meaning.
#
#   IMPORTANT: The memory devices that provide the SPI mock memory have to
#   be defined before the SPI device that uses the bus simulation device in
#   the config file. Also make sure that the memory devices have at least
#   enough bytes to fulfill the longest singular read and write (or xfer)
#   requests.
#

import webiopi
from webiopi.devices.bus import Bus, SPI_Bus
from webiopi.utils.logger import debug, info

class SPI_MOCK(SPI_Bus):
    def __init__(self, dev="", chip=0, mode=0, bits=8, speed=0):
        Bus.__init__(self, "SPI", "mock:%s" % dev)        

        mockMemoryNameSI = "%s_si" % dev
        self._memorySI = webiopi.deviceInstance(mockMemoryNameSI)
        self._hasMockSI = self._memorySI != None

        mockMemoryNameSO = "%s_so" % dev
        self._memorySO = webiopi.deviceInstance(mockMemoryNameSO)
        self._hasMockSO = self._memorySO != None
        
        debug("Mapped SPI bus device - %s" % self.__str__())
   
    def __str__(self):
        return "SPI_MOCK(dev=%s)" % self.device

#---------- Bus abstraction methods reimplementation ----------

    def open(self):
        debug("Opening SPI bus device - %s" % self.__str__())
    
    def close(self):
        debug("Closing SPI bus device - %s" % self.__str__())

#---------- SPI abstraction communication methods redirected to reading/writing simulation memory ----------
    
    def readBytes(self, size=1):
        if self._hasMockSO:
            currentBytes = self._memorySO.readMemoryBytes()
            result = currentBytes[:size]
            remaining = currentBytes[size:]
            newBytes = bytearray(remaining) + bytearray(size)
            self._memorySO.writeMemoryBytes(0, newBytes)
            return bytearray(result)
        else:
            return bytearray(size)

    def writeBytes(self, data):
        if self._hasMockSI:
            slots = self._memorySI.byteCount()
            currentBytes = self._memorySI.readMemoryBytes()
            allBytes = bytearray(data) + bytearray(currentBytes)
            self._memorySI.writeMemoryBytes(0, allBytes[:slots])
        
    def xfer(self, txbuff=None):
        length = len(txbuff)
        self.writeBytes(txbuff)
        return self.readBytes(length)
        
