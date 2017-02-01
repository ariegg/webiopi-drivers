#   Copyright 2017 Andreas Riegg - t-h-i-n-x.net
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
#   1.0    2017-01-24    Initial release.
#   1.1    2017-02-01    Added quantities.
#
#
#   Examples
#
#       from quantities import *
#
#       t = Qtemperature(10.8)
#       print("%s" % t)
#
#       p = Qpressure(1000)
#       d = Qdistance(30)
#       h = Qhumidity(0.5)
#       l = Qluminosity(200)
#       i = Qcurrent(2)
#       u = Qvoltage(5)
#       p = Qpower(20)
#       x = Qposition(1)
#       v = Qlinearvelocity(2.6)
#       s = Qspeed(4)
#       v = Qangularvelocity(50)
#       f = Qfrequency(50)
#       a = Qlinearacceleration(2)
#       g = Qgravity(1)
#       a = Qangularacceleration(3)
#       m = Qmass(1)
#       t = Qtime(1)
#       m = Qmolarity(10)
#       i = QluminousIntensity(100)

from vector import QuantityVector


#---------- Predefined quantities according to sensor abstractions ----------
        
def Qtemperature(measurand=0):
        return QuantityVector(measurand, kelvin=1)

def Qpressure(measurand=0):
        return QuantityVector(measurand, meter=-1, kilogram=1, second=-2)

def Qdistance(measurand=0):
        return QuantityVector(measurand, meter=1)

def Qhumidity(measurand=0):
        return QuantityVector(measurand)

def Qluminosity(measurand=0):
        return QuantityVector(measurand, meter=-2, candela=1)

def Qcurrent(measurand=0):
        return QuantityVector(measurand, ampere=1)

def Qvoltage(measurand=0):
        return QuantityVector(measurand, meter=2, kilogram=1, second=-3, ampere=-1)

def Qpower(measurand=0):
        return QuantityVector(measurand, meter=2, kilogram=1, second=-3)

def Qposition(measurand=0):
        return QuantityVector(measurand, meter=1)

def Qlinearvelocity(measurand=0):
        return QuantityVector(measurand, meter=1, second=-1)

def Qspeed(measurand=0):
        return QuantityVector(measurand, meter=1, second=-1)

def Qangularvelocity(measurand=0):
        return QuantityVector(measurand, second=-1)

def Qfrequency(measurand=0):
        return QuantityVector(measurand, second=-1)

def Qlinearacceleration(measurand=0):
        return QuantityVector(measurand, meter=1, second=-2)

def Qgravity(measurand=0):
        return QuantityVector(measurand, meter=1, second=-2)

def Qangularacceleration(measurand=0):
        return QuantityVector(measurand, second=-2)

def Qmass(measurand=0):
        return QuantityVector(measurand, kilogram=1)

def Qtime(measurand=0):
        return QuantityVector(measurand, second=1)

def Qmolarity(measurand=0):
        return QuantityVector(measurand, mol=1)

def QluminousIntensity(measurand=0):
        return QuantityVector(measurand, candela=1)

