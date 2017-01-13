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
#   1.0    2016-07-29    Initial release.
#

from webiopi.devices.digital import GPIOPort
from webiopi.utils.types import toint

class DIGITAL(GPIOPort):

    VALUES = []
    FUNCTIONS = []
    
    def __init__(self, channels=8):
        GPIOPort.__init__(self, toint(channels))
        self.VALUES = [0 for i in range(self.digitalCount())]
        self.FUNCTIONS = [self.IN for i in range(self.digitalCount())]
 
    def __str__(self):
        return "DIGITAL"

    def __getFunction__(self, channel):
        return self.FUNCTIONS[channel]
    
    def __setFunction__(self, channel, func):
        self.FUNCTIONS[channel] = func
    
    def __digitalRead__(self, channel):
        return self.VALUES[channel]
        
    def __portRead__(self):
        val = 0
        for i in range[self.digitalCount()]:
            val |= self.VALUES[i] << i
        return val
    
    def __digitalWrite__(self, channel, value):
        if self.FUNCTIONS[channel] == self.OUT:
            self.VALUES[channel] = value
        
    def __portWrite__(self, value):
        for i in range[self.digitalCount()]:
            val = (value >> i) & 0x1
            self.__digitalWrite__(self, i, val)
      
