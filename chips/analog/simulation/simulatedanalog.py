#   Copyright 2016-2017 Andreas Riegg - t-h-i-n-x.net
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
#   1.1    2017-01-27    File rename and comments added.
#
#   Config parameters
#
#   - channels       Integer       Number of analog channels. Default is 2.
#   - resolution     Integer       The resulution of the anlaog values.
#   - frequency      Float         Can be specified but has no usage and is ignored.
#
#   Usage remarks
#
#   - You can use these devices just like ordinary devices by e.g. using them in the
#     config file.
#   - As pure artificial devices they have no hardware dependency at all. For that reason
#     no bus parameter is necessary.
#   - You can use these devices to do some testing prior to having the real physical chips
#     available to e.g. create some user interface in advance.
#   - You can use these devices also to check the correctness of some REST API calls
#     that use the analog I/O values.
#
#   Implementation remarks
#
#   - For simplicity, the simulated analog device names are just the upper case version of
#     the underlying analog abstractions.
#   - As DAC is a functional superset of ADC only DAC has been implemented.
#   - As the name PWM is already in use the name "PUUM" has been used.
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


