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
#   1.0    2016-06-30    Initial release.
#
#   Implementation and usage remarks
#
#   Version for UART simulation using an internal string object.
#   Writing appends the new string to the existing string.
#   Reading consumes (reduces) the existing string.
#

from webiopi.devices.bus import Bus, UART_Bus
from webiopi.utils.logger import debug, info

class UART_MOCK(UART_Bus):
    def __init__(self, dev="uart", baudrate=None):
        Bus.__init__(self, "UART", "mock:%s" % dev, None)
        self.string = ""

        debug("Mapped UART bus device - %s" % self.__str__())
        
    def __str__(self):
        return "UART_MOCK"
    
#---------- Bus abstraction methods reimplementation ----------

    def open(self):
        debug("Opening UART bus device - %s" % self.__str__())
    
    def close(self):
        debug("Closing UART bus device - %s" % self.__str__())

#---------- UART abstraction communication methods redirected to reading/writing a string ----------
    
    def readString(self):
        if len(self.string) > 0:
            string = self.string
            self.string = ""
            return string
        return ""
    
    def writeString(self, string):
        self.string += string

    def available(self):
        return len(self.string)



