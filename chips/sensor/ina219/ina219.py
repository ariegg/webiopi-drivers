#   Copyright 2017 Andreas Riegg - t-h-i-n-x.net
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
#   1.0    2017/01/03    Initial release
#
#   Config parameters
#
#   - slave         8 bit       Value of the I2C slave address for the chip.
#                               Defaults to 0x40. Possible values are from 0x40 to 0x4F.
#   - shunt         Float       Value of the shunt resistor in Ohms. Default is 0.1.
#   - vrange        Integer     Vrange value of the chip. Valid values are 16 or 32.
#                               Default is 32.
#   - gaindiv       Integer     Gain divider (PGA) value of the chip. Valid values
#                               are from (1, 2, 4 , 8). Default is 8.
#   - mode          Integer     Value of the chip mode. Possible values are from
#                               0x0 to 0x7. Default is 0x7.
#   - badc          Integer     Value of the voltage bus ADC settings. Possible
#                               values are from 0x0 to 0xF. Default is 0x3.
#   - sadc          Integer     Value of the shunt voltage ADC settings. Possible
#                               values are from 0x0 to 0xF. Default is 0x3.
#   - vmax          Float       Value of the desired vmax value for automatic
#                               calibration. Default is None. This parameter will
#                               only be used of imax is also not None.
#   - imax          Float       Value of the desired imax value for automatic
#                               calibration. Default is None. If imax is given,
#                               the values for vrange, gaindiv and currentLSB will be
#                               ignored and calculated instead. If imax is higher than
#                               possible, then the highest possible value will be
#                               used instead and overflow may occur.
#   - currentLSB    Float       Value of the current LSB to use. Default is None.
#                               If you mistrust the automatic calibration you can
#                               set the current LSB manual with this parameter. If
#                               used, make sure to manual set the desired gaindiv also.
#   - bus           String      Name of the I2C bus
#
#   Usage remarks
#
#   - The default values of this driver are valid for a 32 V Bus range, a maximum
#     possible current of 3.2 A and a current resolution of around 98 microAmperes/Bit.
#     If you are fine with this you can just use those defaults.
#   - If you want to have some more configuration while keeping it still simple you
#     can provide parameters for vmax and imax and the driver will do its best to
#     automatically calculate vrange, gaindiv and calibration with a very good resolution.
#   - If you prefer complete manual setup you should set vrange, gaindiv, currentLSB and
#     optional fine-tuned calibration (in this order).
#   - Setting the calibration register via setCalibration() is to be used for the final
#     calibration as explained in the chip spec for the final fine tuning. It must not
#     be used for the currentLSB setting as this is calculated automatically by this
#     driver based on the values of shunt and gaindiv.
#   - This driver implements an automatical calibration feature calibrate(vmax, imax)
#     that can be used during device creation and also at runtime. The value for vmax
#     is used to set vrange within the allowed limits. The value for imax is used to
#     set gaindiv so that the maximal desired current can be measured at the highest
#     possible resolution for current LSB. If the desired imax is higher than the
#     possible imax based on the value of shunt, then the maximum possible imax will
#     be used. You get the choosen values via the response of the calibrate(...) call.
#     In this case, sending a higher current through the shunt will result in overflow
#     which will generate a debugging message (only when reading the bus voltage).
#   - If values for vmax and imax are given at device creation they will override the
#     init values for vrange and gaindiv as those will be ignored then and calculated via
#     the automatic calibration feature instead.
#   - All chip parameters with the exception of shunt can be changed at runtime. If
#     an updated parameter has an influence on the currentLSB and/or calibration value,
#     then this/these will be re-calculated automatically and the calibration register
#     will be set also. If you use setCalibration() for final fine-tuning you have to
#     repeat that step again if automatic calibration has taken place.
#   - Updating of the mode value at runtime allows triggered conversions and power-down
#     of the chip.
#   - If you are unsure about the calculated values set debugging to "True" and look at
#     the debugging messages as they will notify you about all resulting values. Or
#     call getConfiguration() to see all values.
#   - If you encounter overflow (getting the overflow error) try to increase the
#     gaindiv value or reduce the shunt value (please as real hardware change).
#
#   Implementation remarks
#
#   - This driver is implemented based on the specs from Intel.
#   - The default value for the shunt resistor of 0.1 Ohms is appropriate for the
#     breakout board from Adafruit for this chip (Adafruit PRODUCT ID: 904).
#   - The parameter value for shunt can't be changed at runtime after device
#     creation because it is very unlikely to modify the shunt resistor during operation
#     of the chip. Please provide the correct value via the config options or at
#     device creation if the default value does not suit your hardware setup.
#   - This driver uses floating point calculation and takes no care about integer
#     only arithmetics. For that reason, the mathematical lowest possible LSB value is
#     calculated automatically and used for best resolution with the exception when you
#     manual set your own current LSB value.
#   - If you want to override/select the current LSB value manual you can do that
#     via config parameter or at runtime. In this case make sure to use the correct
#     corresponding gaindiv value otherwise the value readings will be wrong.
#   - If for some reason (e.g. an impropriate setting of the currentLSB) the value
#     of the calibration register would be out of its allowed bounds it will be set
#     to zero so that all current and power readings will also be zero to avoid wrong
#     measurements until the calibration register is set again to an allowed range.
#   - This driver does not use the shunt adc register as this value is not needed
#     for operation if the calibration register is used.
#

from webiopi.utils.logger import debug
from webiopi.decorators.rest import request, response, api
from webiopi.utils.types import toint, signInteger, M_JSON
from webiopi.devices.i2c import I2C
from webiopi.devices.sensor import Current, Voltage, Power


#---------- Class definition ----------

class INA219(I2C, Current, Voltage, Power):

    CONFIGURATION_ADDRESS = 0x00
   #SHUNTADC_ADDRESS      = 0x01
    BUSADC_ADDRESS        = 0x02
    POWER_ADDRESS         = 0x03
    CURRENT_ADDRESS       = 0x04
    CALIBRATION_ADDRESS   = 0x05

    RESET_FLAG        = 0b1  << 15

    BRNG_16_VALUE     = 0b0  << 13
    BRNG_32_VALUE     = 0b1  << 13
    BRNG_MASK         = 0b0010000000000000

    GAINDIV_1_VALUE   = 0b00 << 11
    GAINDIV_2_VALUE   = 0b01 << 11
    GAINDIV_4_VALUE   = 0b10 << 11
    GAINDIV_8_VALUE   = 0b11 << 11
    GAINDIV_MASK      = 0b0001100000000000

    BADC_MASK         = 0b0000011110000000
    SADC_MASK         = 0b0000000001111000
    MODE_MASK         = 0b0000000000000111

    OVERFLOW_MASK     = 0b0000000000000001
    CALIBRATION_MASK  = 0b1111111111111110

    VSHUNT_FULL_SCALE_BASE_VALUE   = 0.04    # always fixed to 40mV
    CALIBRATION_CONSTANT_VALUE     = 0.04096 # fixed value from data sheet
    BUS_VOLTAGE_LSB_VALUE          = 0.004   # always fixed to 4mV
    CURRENT_LSB_TO_POWER_LSB_VALUE = 20      # always 20 times the currentLSB value

#---------- Class initialisation ----------

    def __init__(self, slave=0x40, shunt=0.1, vrange=32, gaindiv=8, mode=0x7, badc=0x3, sadc=0x3, vmax=None, imax=None, currentLSB=None, bus=None):
        I2C.__init__(self, toint(slave), bus)
        self.__setShunt__(float(shunt))
        self.__reset__()
        if imax != None:
            if vmax == None:
                vmax = toint(vrange)
            else:
                vmax = toint(vmax)
            imax = toint(imax)
            self.__calibrate__(vmax, imax)
        else:
            self.__setVrange__(toint(vrange))
            self.__setGaindiv__(toint(gaindiv))
            if currentLSB != None:
                self.__setCurrentLSB__(float(currentLSB))
        self.__setMode__(toint(mode))
        self.__setBadc__(toint(badc))
        self.__setSadc__(toint(sadc))

#---------- Abstraction framework contracts ----------

    def __str__(self):
        return "INA219(slave=0x%02X, dev=%s, shunt=%f Ohm)" % (self.slave, self.device(), self._shunt)

    def __family__(self):
        return [Current.__family__(self), Voltage.__family__(self), Power.__family__(self)]


#---------- Current abstraction related methods ----------

    def __getMilliampere__(self):
        rawCurrent = self.__read16BitRegister__(self.CURRENT_ADDRESS)
        debug("%s: raw current=%s" % (self.__str__(), bin(rawCurrent)))
        return signInteger(rawCurrent, 15) * self._currentLSB * 1000 # scale from Amperes to milliAmperes

#---------- Voltage abstraction related methods ----------

    def __getVolt__(self):
        rawVoltage = self.__read16BitRegister__(self.BUSADC_ADDRESS)
        debug("%s: raw voltage=%s" % (self.__str__(), bin(rawVoltage)))
        overflow = rawVoltage & self.OVERFLOW_MASK
        if overflow:
            debug("%s: overflow condition" % self.__str__())
        return (rawVoltage >> 3) * self.BUS_VOLTAGE_LSB_VALUE

#---------- Power abstraction related methods ----------

    def __getWatt__(self):
        rawWatt = self.__read16BitRegister__(self.POWER_ADDRESS)
        debug("%s: raw watt=%s" % (self.__str__(), bin(rawWatt)))
        return rawWatt * self.CURRENT_LSB_TO_POWER_LSB_VALUE * self._currentLSB

#---------- Device methods that implement features including additional REST mappings ----------

    @api("Device", 3, "feature", "driver")
    @request("POST", "run/calibrate/%(pars)s")
    @response(contentType=M_JSON)
    def calibrate(self, pars):
        (vmax, imax) = pars.split(",")
        vmax = float(vmax)
        if vmax <= 0 or vmax > 32:
            raise ValueError("Calibration parameter error, vmax:%f out of allowed range [0 < vmax <= 32]" % vmax)
        imax = float(imax)
        self.__calibrate__(vmax, imax)
        values = self.getConfiguration()
        values["vmax required"] = "%f" % vmax
        values["imax required"] = "%f" % imax
        return values

    def __calibrate__(self, vmax, imax):
        if vmax > 16:
            self.setVrange(32)
        else:
            self.setVrange(16)
        gaindiv = 1
        shuntdiv = 1 / self._shunt
        while True:
            imaxpossible = self.__calculateImaxpossible__(gaindiv, shuntdiv)
            if gaindiv == 8:
                break
            if imax > imaxpossible:
                gaindiv *= 2
            else:
                break
        self.setGaindiv(gaindiv)
        debug("%s: auto-calibrated, max possible current=%f A" % (self.__str__(), imaxpossible))

    @api("Device", 3, "feature", "driver")
    @request("POST", "run/reset")
    @response("%s")
    def reset(self):
        self.__reset__()
        return "Chip is reset."

    def __reset__(self):
        self.__write16BitRegister__(self.CONFIGURATION_ADDRESS, self.RESET_FLAG)
        debug("%s: chip reset" % self.__str__())

    @api("Device", 3, "feature", "driver")
    @request("POST", "run/recalibrate")
    @response("%d")
    def reCalibrate(self):
        self.__reCalibrate__()
        return self.__getCalibration__()


#---------- Device methods that implement chip configuration settings including additional REST mappings ----------

    @api("Device", 3, "configuration", "driver")
    @request("GET", "configure/*")
    @response(contentType=M_JSON)
    def getConfiguration(self):
        values = {}
        values["vmax possible"] = "%d" % self._vrange
        values["imax possible"] = "%f" % self.__calculateImaxpossible__(self._gaindiv, 1 / self._shunt)
        values["current LSB"] = "%f" % self._currentLSB
        values["calibration"] = "%d" % self._cal
        values["gaindiv"] = "%d" % self._gaindiv
        values["shunt"] = "%f" % self._shunt
        return values


    @api("Device", 3, "configuration", "driver")
    @request("GET", "configure/calibration")
    @response("%d")
    def getCalibration(self):
        return self.__getCalibration__()

    def __getCalibration__(self):
        return self.__read16BitRegister__(self.CALIBRATION_ADDRESS)

    @api("Device", 3, "configuration", "driver")
    @request("POST", "configure/calibration/%(calibration)d")
    @response("%d")
    def setCalibration(self, calibration):
        self.__setCalibration__(calibration)
        return self.__getCalibration__()

    def __setCalibration__(self, calibration):
        if calibration not in range(0, 65535):
            self.__write16BitRegister__(self.CALIBRATION_ADDRESS, 0) # zero out calibration register to avoid wrong measurements
            self._cal = 0
            debug("%s: set calibration=0" % self.__str__())
            raise ValueError("Parameter calibration:%d not in the allowed range [0 .. 65534]" % calibration)
        calibration = calibration & self.CALIBRATION_MASK
        self.__write16BitRegister__(self.CALIBRATION_ADDRESS, calibration)
        self._cal = calibration
        debug("%s: set calibration=%d" % (self.__str__(), self._cal))

    @api("Device", 3, "configuration", "driver")
    @request("POST", "configure/vrange/%(vrange)d")
    @response("%d")
    def setVrange(self, vrange):
        self.__setVrange__(vrange)
        return self.__getVrange__()

    @api("Device", 3, "configuration", "driver")
    @request("GET", "configure/vrange")
    @response("%d")
    def getVrange(self):
        return self.__getVrange__()

    def __setVrange__(self, vrange):
        if vrange not in (16, 32):
            raise ValueError("Parameter vrange:%d not one of the allowed values (16, 32)" % vrange)
        if vrange   == 16:
            bitsVrange = self.BRNG_16_VALUE
        elif vrange == 32:
            bitsVrange = self.BRNG_32_VALUE
        currentValue = self.__read16BitRegister__(self.CONFIGURATION_ADDRESS)
        newValue = (currentValue & ~self.BRNG_MASK) | bitsVrange
        self.__write16BitRegister__(self.CONFIGURATION_ADDRESS, newValue)
        self._vrange = vrange
        debug("%s: set vrange=%d V" % (self.__str__(), vrange))

    def __getVrange__(self):
        bitsVrange = (self.__read16BitRegister__(self.CONFIGURATION_ADDRESS) & self.BRNG_MASK) >> 13
        if bitsVrange   == self.BRNG_16_VALUE:
            self._vrange = 16
        elif bitsVrange == self.BRNG_32_VALUE:
            self._vrange = 32
        return self._vrange

    @api("Device", 3, "configuration", "driver")
    @request("POST", "configure/gaindiv/%(gaindiv)d")
    @response("%d")
    def setGaindiv(self, gaindiv):
        self.__setGaindiv__(gaindiv)
        return self.__getGaindiv__()

    @api("Device", 3, "configuration", "driver")
    @request("GET", "configure/gaindiv")
    @response("%d")
    def getGaindiv(self):
        return self.__getGaindiv__()

    def __setGaindiv__(self, gaindiv):
        if gaindiv not in (1, 2, 4, 8):
            raise ValueError("Parameter gaindiv:%d not one of the allowed values (1, 2, 4, 8)" % gaindiv)
        if gaindiv   == 1:
            bitsGaindiv = self.GAINDIV_1_VALUE
        elif gaindiv == 2:
            bitsGaindiv = self.GAINDIV_2_VALUE
        elif gaindiv == 4:
            bitsGaindiv = self.GAINDIV_4_VALUE
        elif gaindiv == 8:
            bitsGaindiv = self.GAINDIV_8_VALUE
        currentValue = self.__read16BitRegister__(self.CONFIGURATION_ADDRESS)
        newValue = (currentValue & ~self.GAINDIV_MASK) | bitsGaindiv
        self.__write16BitRegister__(self.CONFIGURATION_ADDRESS, newValue)
        self._gaindiv = gaindiv
        debug("%s: set gaindiv=%d" % (self.__str__(), gaindiv))
        self.__reCalculate__()

    def __getGaindiv__(self):
        bitsGaindiv = (self.__read16BitRegister__(self.CONFIGURATION_ADDRESS) & self.GAINDIV_MASK) >> 11
        if bitsGaindiv   == self.GAINDIV_1_VALUE:
            self._gaindiv = 1
        elif bitsGaindiv == self.GAINDIV_2_VALUE:
            self._gaindiv = 2
        elif bitsGaindiv == self.GAINDIV_4_VALUE:
            self._gaindiv = 4
        elif bitsGaindiv == self.GAINDIV_8_VALUE:
            self._gaindiv = 8
        return self._gaindiv

    @api("Device", 3, "configuration", "driver")
    @request("POST", "configure/mode/%(mode)d")
    @response("%d")
    def setMode(self, mode):
        self.__setMode__(mode)
        return self.__getMode__()

    @api("Device", 3, "configuration", "driver")
    @request("GET", "configure/mode")
    @response("%d")
    def getMode(self):
        return self.__getMode__()

    def __setMode__(self, mode):
        if mode not in range(0, 0x8):
            raise ValueError("Parameter mode:0x%1X not in the allowed range [0x0 .. 0x7]" % mode)
        currentValue = self.__read16BitRegister__(self.CONFIGURATION_ADDRESS)
        newValue = (currentValue & ~self.MODE_MASK) | mode
        self.__write16BitRegister__(self.CONFIGURATION_ADDRESS, newValue)
        debug("%s: set mode=0x%1X" % (self.__str__(), mode))

    def __getMode__(self):
        bitsMode = (self.__read16BitRegister__(self.CONFIGURATION_ADDRESS) & self.MODE_MASK)
        return bitsMode

    @api("Device", 3, "configuration", "driver")
    @request("POST", "configure/badc/%(badc)d")
    @response("%d")
    def setBadc(self, badc):
        self.__setBadc__(badc)
        return self.__getBadc__()

    @api("Device", 3, "configuration", "driver")
    @request("GET", "configure/badc")
    @response("%d")
    def getBadc(self):
        return self.__getBadc__()

    def __setBadc__(self, badc):
        if badc not in range(0, 0x10):
            raise ValueError("Parameter badc:0x%1X not in the allowed range [0x0 .. 0xF]" % badc)
        currentValue = self.__read16BitRegister__(self.CONFIGURATION_ADDRESS)
        newValue = (currentValue & ~self.BADC_MASK) | badc << 7
        self.__write16BitRegister__(self.CONFIGURATION_ADDRESS, newValue)
        debug("%s: set badc=0x%1X" % (self.__str__(), badc))

    def __getBadc__(self):
        bitsBadc = (self.__read16BitRegister__(self.CONFIGURATION_ADDRESS) & self.BADC_MASK) >> 7
        return bitsBadc

    @api("Device", 3, "configuration", "driver")
    @request("POST", "configure/sadc/%(sadc)d")
    @response("%d")
    def setSadc(self, sadc):
        self.__setSadc__(sadc)
        return self.__getSadc__()

    @api("Device", 3, "configuration", "driver")
    @request("GET", "configure/sadc")
    @response("%d")
    def getSadc(self):
        return self.__getSadc__()

    def __setSadc__(self, sadc):
        if sadc not in range(0, 0x10):
            raise ValueError("Parameter sadc:0x%1X not in the allowed range [0x0 .. 0xF]" % sadc)
        currentValue = self.__read16BitRegister__(self.CONFIGURATION_ADDRESS)
        newValue = (currentValue & ~self.SADC_MASK) | sadc << 3
        self.__write16BitRegister__(self.CONFIGURATION_ADDRESS, newValue)
        debug("%s: set sadc=0x%1X" % (self.__str__(), sadc))

    def __getSadc__(self):
        bitsSadc = (self.__read16BitRegister__(self.CONFIGURATION_ADDRESS) & self.SADC_MASK) >> 3
        return bitsSadc

    @api("Device", 3, "configuration", "driver")
    @request("POST", "configure/currentlsb/%(currentLSB)f")
    @response("%f")
    def setCurrentLSB(self, currentLSB):
        self.__setCurrentLSB__(currentLSB)
        return self._currentLSB


#---------- Device methods that implement chip configuration settings ----------

    def __setShunt__(self, shunt):
        self._shunt = shunt

    def __setCurrentLSB__(self, currentLSB):
        self._currentLSB = currentLSB
        debug("%s: set current LSB=%f mA" % (self.__str__(), self._currentLSB * 1000))
        self.__setCalibration__(self.__calculateCalibration__())


#---------- Calibration helper methods ----------

    def __reCalculate__(self):
        self.__setCurrentLSB__(self.__calculateCurrentLSB__())

    def __reCalibrate__(self):
        self.__setCalibration__(self._cal)

    def __calculateCurrentLSB__(self):
        calCurrentLSB = self.VSHUNT_FULL_SCALE_BASE_VALUE * self._gaindiv / self._shunt / 2**15 # in Amperes
        debug("%s: calculated current LSB=%f mA" % (self.__str__(), calCurrentLSB * 1000))
        return calCurrentLSB

    def __calculateCalibration__(self):
        calCal = int(self.CALIBRATION_CONSTANT_VALUE / self._currentLSB / self._shunt) # this does trunc
        debug("%s: calculated calibration=%d" % (self.__str__(), calCal))
        return calCal

    def __calculateImaxpossible__(self, gaindiv, shuntdiv):
        return self.VSHUNT_FULL_SCALE_BASE_VALUE * gaindiv * shuntdiv


#---------- Register helper methods ----------

    def __read16BitRegister__(self, addr):
        regBytes  = self.readRegisters(addr, 2)
        return regBytes[0] << 8 | regBytes[1]

    def __write16BitRegister__(self, addr, word):
        data = bytearray(2)
        data[0] = (word >> 8) & 0xFF
        data[1] = word & 0xFF
        self.writeRegisters(addr , data)

