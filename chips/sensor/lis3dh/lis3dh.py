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
#   1.0    2017/01/13    Initial release
#
#   Config parameters
#
#   - slave         8 bit       Value of the I2C slave address for the chip.
#                               Defaults to 0x18. Possible values are 0x18 and 0x19.
#   - grange        Integer     G range value of the chip. Valid values are 2, 4, 8
#                               or 16. Default is 2.
#   - odr           Integer     Output data rate (ODR) value of the chip in Hz in
#                               running in normal mode. Valid values are from
#                               (1, 10, 25, 50, 100, 200, 400, 1250). Default is 50.
#   - hr            Boolean     Value of the high resolution bit. Possible values are
#                               "yes" or "no". Default is "yes".
#   - bus           String      Name of the I2C bus
#
#   Usage remarks
#
#   - You can change the G range and ODR parameters of the chip at runtime.
#
#   Implementation remarks
#
#   - This driver is implemented based on the specs from ST Microelectronics.
#   - This driver uses floating point calculation and takes no care about integer
#     only arithmetics. For that reason, the mathematical lowest possible LSB value is
#     calculated automatically and used.
#   - This driver does NOT implement all interrupt and click detection featutres of the
#     chip.
#   - This driver does currently not implement the auxiliary ADC and temperature
#     features of the chip.
#

from webiopi.utils.logger import debug
from webiopi.decorators.rest import request, response, api
from webiopi.utils.types import toint, signInteger, str2bool, M_JSON
from webiopi.devices.i2c import I2C
from webiopi.devices.sensor import LinearAcceleration


#---------- Class definition ----------

class LIS3DH(I2C, LinearAcceleration):

    CTRL_REG1_ADDRESS = 0x20
    CTRL_REG4_ADDRESS = 0x23
   
    OUT_X_L_ADDRESS   = 0x28
   #OUT_X_H_ADDRESS   = 0x29
    OUT_Y_L_ADDRESS   = 0x2A
   #OUT_Y_H_ADDRESS   = 0x2B
    OUT_Z_L_ADDRESS   = 0x2C
   #OUT_Z_H_ADDRESS   = 0x2D

    AUTO_INCREM_FLAG  = 0b1 << 7
    BLOCK_UPDATE_FLAG = 0b1 << 7
    HR_FLAG           = 0b1 << 3
        
    FS_2G_VALUE       = 0b00 << 4
    FS_4G_VALUE       = 0b01 << 4
    FS_8G_VALUE       = 0b10 << 4
    FS_16G_VALUE      = 0b11 << 4
    FS_MASK           = 0b00110000

    ODR_NOPOWER_VALUE = 0b0000 << 4
    ODR_1_HZ_VALUE    = 0b0001 << 4
    ODR_10_HZ_VALUE   = 0b0010 << 4
    ODR_25_HZ_VALUE   = 0b0011 << 4
    ODR_50_HZ_VALUE   = 0b0100 << 4
    ODR_100_HZ_VALUE  = 0b0101 << 4
    ODR_200_HZ_VALUE  = 0b0110 << 4
    ODR_400_HZ_VALUE  = 0b0111 << 4
   #ODR_1600_HZ_VALUE = 0b1000 << 4
    ODR_1250_HZ_VALUE = 0b1001 << 4
    ODR_MASK          = 0b11110000

    ACCEL_FS_2G_LSB_VALUE  =  2.0 / 32767 #      1mg/digit at +/-  2g (@15 bit) full scale
    ACCEL_FS_4G_LSB_VALUE  =  4.0 / 32767 #  2 x 1mg/digit
    ACCEL_FS_8G_LSB_VALUE  =  8.0 / 32767 #  4 x 1mg/digit
    ACCEL_FS_16G_LSB_VALUE = 24.0 / 32767 #  6 x 1mg/digit

#---------- Class initialisation ----------

    def __init__(self, slave=0x18, grange=2, odr=50, hr="yes" , bus=None):
        I2C.__init__(self, toint(slave), bus)
        self._odrBeforeSleep = None
        self._hr = str2bool(hr)
        if self._hr:
            reg4initval = self.BLOCK_UPDATE_FLAG | self.HR_FLAG
        else:
            reg4initval = self.BLOCK_UPDATE_FLAG
        self.writeRegister(self.CTRL_REG4_ADDRESS, reg4initval)
        self.__setGrange__(toint(grange))
        self.__setOdr__(toint(odr))

#---------- Abstraction framework contracts ----------

    def __str__(self):
        return "LIS3DH(slave=0x%02X, dev=%s)" % (self.slave, self.device())

    def __family__(self):
        return LinearAcceleration.__family__(self)


#---------- LinearAcceleration abstraction related methods ----------

    def __getMeterPerSquareSecondX__(self):
        return self.Gravity2MeterPerSquareSecond(self.__getGravityX__())

    def __getMeterPerSquareSecondY__(self):
        return self.Gravity2MeterPerSquareSecond(self.__getGravityY__())

    def __getMeterPerSquareSecondZ__(self):
        return self.Gravity2MeterPerSquareSecond(self.__getGravityZ__())

    def __getGravityX__(self):
        rawGravityX = self.__read16BitRegister__(self.OUT_X_L_ADDRESS)
        debug("%s: raw gravity x=%s" % (self.__str__(), bin(rawGravityX)))
        return signInteger(rawGravityX, 16) * self._gravityLSB

    def __getGravityY__(self):
        rawGravityY = self.__read16BitRegister__(self.OUT_Y_L_ADDRESS)
        debug("%s: raw gravity y=%s" % (self.__str__(), bin(rawGravityY)))
        return signInteger(rawGravityY, 16) * self._gravityLSB

    def __getGravityZ__(self):
        rawGravityZ = self.__read16BitRegister__(self.OUT_Z_L_ADDRESS)
        debug("%s: raw gravity z=%s" % (self.__str__(), bin(rawGravityZ)))
        return signInteger(rawGravityZ, 16) * self._gravityLSB

#---------- Device methods that implement features including additional REST mappings ----------

    @api("Device", 3, "feature", "driver")
    @request("POST", "run/sleep")
    @response("%s")
    def sleep(self):
        self.__sleep__()
        return "Chip sent to sleep."

    def __sleep__(self):
        if self._odrBeforeSleep == None:
            self._odrBeforeSleep = self._odr
        bitsOdr = self.ODR_NOPOWER_VALUE
        currentValue = self.readRegister(self.CTRL_REG1_ADDRESS)
        newValue = (currentValue & ~self.ODR_MASK) | bitsOdr
        self.writeRegister(self.CTRL_REG1_ADDRESS, newValue)
        self._odr = 0
        debug("%s: chip sent to power down" % self.__str__())

    @api("Device", 3, "feature", "driver")
    @request("POST", "run/wake")
    @response("%s")
    def wake(self):
        self.__wake__()
        return "Chip woken up."

    def __wake__(self):
        if self._odrBeforeSleep != None:
            self.__setOdr__(self._odrBeforeSleep)
            self._odrBeforeSleep = None
        debug("%s: chip woken up" % self.__str__())

#---------- Device methods that implement chip configuration settings including additional REST mappings ----------

    @api("Device", 3, "configuration", "driver")
    @request("GET", "configure/*")
    @response(contentType=M_JSON)
    def getConfiguration(self):
        values = {}
        values["grange"] = "%d" % self._grange
        values["odr"] = "%d" % self._odr
        values["hr"] = "%s" % self._hr
        values["gravity LSB"] = "%f" % self._gravityLSB
        return values

    @api("Device", 3, "configuration", "driver")
    @request("POST", "configure/grange/%(grange)d")
    @response("%d")
    def setGrange(self, grange):
        self.__setGrange__(grange)
        return self.__getGrange__()

    @api("Device", 3, "configuration", "driver")
    @request("GET", "configure/grange")
    @response("%d")
    def getGrange(self):
        return self.__getGrange__()

    def __setGrange__(self, grange):
        if grange not in (2, 4, 8, 16):
            raise ValueError("Parameter grange:%d not one of the allowed values (2, 4, 8, 16)" % grange)
        if grange   == 2:
            bitsGrange = self.FS_2G_VALUE
            self._gravityLSB = self.ACCEL_FS_2G_LSB_VALUE
        elif grange == 4:
            bitsGrange = self.FS_4G_VALUE
            self._gravityLSB = self.ACCEL_FS_4G_LSB_VALUE
        elif grange == 8:
            bitsGrange = self.FS_8G_VALUE
            self._gravityLSB = self.ACCEL_FS_8G_LSB_VALUE
        elif grange == 16:
            bitsGrange = self.FS_16G_VALUE
            self._gravityLSB = self.ACCEL_FS_16G_LSB_VALUE
        currentValue = self.readRegister(self.CTRL_REG4_ADDRESS)
        newValue = (currentValue & ~self.FS_MASK) | bitsGrange
        self.writeRegister(self.CTRL_REG4_ADDRESS, newValue)
        self._grange = grange
        debug("%s: set grange=+/-%d g" % (self.__str__(), grange))

    def __getGrange__(self):
        bitsGrange = (self.readRegister(self.CTRL_REG4_ADDRESS) & self.FS_MASK) >> 4
        if bitsGrange   == self.ODR_10_HZ_VALUE:
            self._grange = 2
        elif bitsGrange == self.FS_4G_VALUE:
            self._grange = 4
        elif bitsGrange == self.FS_8G_VALUE:
            self._grange = 8
        elif bitsGrange == self.FS_16G_VALUE:
            self._grange = 16
        return self._grange

    @api("Device", 3, "configuration", "driver")
    @request("POST", "configure/odr/%(odr)d")
    @response("%d")
    def setOdr(self, odr):
        self.__setOdr__(odr)
        return self.__getOdr__()

    @api("Device", 3, "configuration", "driver")
    @request("GET", "configure/odr")
    @response("%d")
    def getOdr(self):
        return self.__getOdr__()

    def __setOdr__(self, odr):
        if odr not in (1, 10, 25, 50, 100, 200, 400, 1250):
            raise ValueError("Parameter odr:%d not one of the allowed values (1, 10, 25, 50, 100, 200, 400, 1250)" % odr)
        if odr   == 1:
            bitsOdr = self.ODR_1_HZ_VALUE
        elif odr == 10:
            bitsOdr = self.ODR_10_HZ_VALUE
        elif odr == 25:
            bitsOdr = self.ODR_25_HZ_VALUE
        elif odr == 50:
            bitsOdr = self.ODR_50_HZ_VALUE
        elif odr == 100:
            bitsOdr = self.ODR_100_HZ_VALUE
        elif odr == 200:
            bitsOdr = self.ODR_200_HZ_VALUE
        elif odr == 400:
            bitsOdr = self.ODR_400_HZ_VALUE
        elif odr == 1250:
            bitsOdr = self.ODR_1250_HZ_VALUE
        currentValue = self.readRegister(self.CTRL_REG1_ADDRESS)
        newValue = (currentValue & ~self.ODR_MASK) | bitsOdr
        self.writeRegister(self.CTRL_REG1_ADDRESS, newValue)
        self._odr = odr
        debug("%s: set odr=%d Hz" % (self.__str__(), odr))

    def __getOdr__(self):
        bitsOdr = (self.readRegister(self.CTRL_REG1_ADDRESS) & self.ODR_MASK) >> 4
        if bitsOdr   == self.ODR_1_HZ_VALUE:
            self._odr = 1
        elif bitsOdr == self.ODR_10_HZ_VALUE:
            self._odr = 10
        elif bitsOdr == self.ODR_25_HZ_VALUE:
            self._odr = 25
        elif bitsOdr == self.ODR_50_HZ_VALUE:
            self._odr = 50
        elif bitsOdr == self.ODR_100_HZ_VALUE:
            self._odr = 100
        elif bitsOdr == self.ODR_200_HZ_VALUE:
            self._odr = 200
        elif bitsOdr == self.ODR_400_HZ_VALUE:
            self._odr = 400
        elif bitsOdr == self.ODR_1250_HZ_VALUE:
            self._odr = 1250
        return self._odr

#---------- Register helper methods ----------

    def __read16BitRegister__(self, addr):
        addr = addr | self.AUTO_INCREM_FLAG
        regBytes  = self.readRegisters(addr, 2)
        return regBytes[0] | regBytes[1] << 8 

