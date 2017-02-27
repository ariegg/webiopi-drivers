#   Copyright 2016-2017 Andreas Riegg - t-h-i-n-x.net
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable la(w or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#   ----------------------------------------------------------------------------
#
#   Changelog
#
#   1.0    2017-02-26    Initial release.
#

from webiopi.utils.logger import debug
from webiopi.devices.bustemplate import busTemplate

class AuxiliaryBus():

    def openAuxiliaryBus(self, busName=None):
        debug("Opening auxiliary bus - %s"  % busName)
        busClass, kwargs = self.__getAuxiliaryBusPattern__(busName)
        return busClass(**kwargs)

    def __getAuxiliaryBusPattern__(self, busName):
        bustemplate = self.__getAuxiliaryBusTemplate__(busName)
        if bustemplate is None:
            raise Exception("Bus creation: Undefined or missing auxiliary bus, template for bus named \'%s\' not found." % busName)
        busClass = bustemplate["class"]
        kwargs = bustemplate["kwargs"]
        return busClass, kwargs

    def __getAuxiliaryBusTemplate__(self, busName):
        if busName is None:
            return None
        return busTemplate(busName)

