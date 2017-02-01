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
#   1.1    2017-02-01    Bugfix unitShort. Refactoriung of method unit.
#                        Added quantityString.
#
#
#   Examples
#
#       from vector import *
#
#       qv = QuantityVector(9.9)
#       qv = QuantityVector(5, meter=1, second=-1)
#       qv = QuantityVector(-5.89, meter=1, second=-1, mol=3, kelvin=-4)
#
#       q = {'kelvin': -1, 'mol': 2, 'meter': 3}
#       qv = QuantityVector(9.9, **q)
#
#       print("%s" % qv)
#       print("%s" % qv.vectorString())
#       print("%s" % qv.unit())
#       print("%s" % qv.unitShort())
#
#       v = qv.vector()
#
#       import json
#       q = qv.quantities()
#       print(json.dumps(q, sort_keys=True, indent=4))
#


#---------- Class definition ----------

class QuantityVector():
    def __init__(self, measurand=0, meter=0, kilogram=0, second=0, ampere=0, kelvin=0, mol=0, candela=0, **kwargs):
        self._vector = [None, None, None, None, None, None, None, None]
        self.setMeasurand(measurand)
        self.setMeter(meter)
        self.setKilogram(kilogram)
        self.setSecond(second)
        self.setAmpere(ampere)
        self.setKelvin(kelvin)
        self.setMol(mol)
        self.setCandela(candela)
        self._units = ["", "m", "kg", "s", "A", "K", "mol", "cd"]

    def __getitem__(self, index):
        return self._vector[index]

    def __str__(self):
        return self.quantityString()

    def quantityString(self, compact=False):
        return "%g %s" % (self.measurand(), self.unit(compact))

    def vectorString(self):
        return "QuantityVector %s" % self._vector.__str__()

    def vector(self):
        return [self.measurand(), self.meter(), self.kilogram(), self.second(), self.ampere(), self.kelvin(), self.mol(), self.candela()]

    def quantities(self):
        q = {}
        q["q0"] = self.measurand()
        q["q1"] = self.meter()
        q["q2"] = self.kilogram()
        q["q3"] = self.second()
        q["q4"] = self.ampere()
        q["q5"] = self.kelvin()
        q["q6"] = self.mol()
        q["q7"] = self.candela()
        return q

    def unit(self, compact=False):
        if compact:
            return self.unitShort()
        else:
            return self.unitLong()

    def unitLong(self):
        unit = ''
        separator = ''
        for i in range(1,8):
            qi = self._vector[i]
            if qi != 0:
                if qi == 1:
                    unit +=  separator + self._units[i]
                else:
                    unit +=  separator + self._units[i] + '^' + ("%d" % qi)
                separator = '*'
        return unit
    
    def unitShort(self):
        unit = ''
        first = True
        for i in range(1,8):
            qi = self._vector[i]
            if qi != 0:
                if first:
                    if qi < 0:
                        separator = '1/'
                    else:
                        separator = ''
                    first = False
                else:
                    if qi > 0:
                        separator = '*'
                    else:
                        separator = '/'
                if abs(qi) == 1:
                    unit +=  separator + self._units[i]
                else:
                    unit +=  separator + self._units[i] + '^' + ("%d" % abs(qi))
        return unit
    
    def measurand(self):
        return self._vector[0]

    def setMeasurand(self, qmeasurand):
        self._vector[0] = float(qmeasurand)

    def meter(self):
        return self._vector[1]

    def setMeter(self, qmeter):
        self._vector[1] = int(qmeter)

    def kilogram(self):
        return self._vector[2]

    def setKilogram(self, qkilogram):
        self._vector[2] = int(qkilogram)

    def second(self):
        return self._vector[3]

    def setSecond(self, qsecond):
        self._vector[3] = int(qsecond)

    def ampere(self):
        return self._vector[4]

    def setAmpere(self, qampere):
        self._vector[4] = int(qampere)

    def kelvin(self):
        return self._vector[5]

    def setKelvin(self, qkelvin):
        self._vector[5] = int(qkelvin)

    def mol(self):
        return self._vector[6]

    def setMol(self, qmol):
        self._vector[6] = int(qmol)

    def candela(self):
        return self._vector[7]

    def setCandela(self, qcandela):
        self._vector[7] = int(qcandela)

