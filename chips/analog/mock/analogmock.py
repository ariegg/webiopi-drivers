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
#   1.0    2016-08-02    Initial release.
#

from webiopi.devices.analog import DAC
from webiopi.devices.analog import PWM
from webiopi.utils.types import toint

class ANALOG(DAC):

    VALUES = []
    
    def __init__(self, channels=2, resolution=8, vref=5.0):
        DAC.__init__(self, toint(channels), toint(resolution), float(vref))
        self.VALUES = [0 for i in range(self.analogCount())]
 
    def __str__(self):
        return "ANALOG"

    def __analogRead__(self, channel, diff):
        return self.VALUES[channel]

    def __analogWrite__(self, channel, value):
        self.VALUES[channel] = value

class PUUM(PWM):

    VALUES = []
    
    def __init__(self, channels=2, resolution=16, frequency=50):
        PWM.__init__(self, toint(channels), toint(resolution), float(frequency))
        self.VALUES = [0 for i in range(self.pwmCount())]
 
    def __str__(self):
        return "PUUM"

    def __pwmRead__(self, channel):
        return self.VALUES[channel]

    def __pwmWrite__(self, channel, value):
        self.VALUES[channel] = value
    

