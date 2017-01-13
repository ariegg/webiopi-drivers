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
#   Changelog
#
#   1.0    2016-06-03    Initial release.
#   1.1    2016-06-14    Reduced number of basic SPI calls a bit to save time.
#   1.2    2016-07-25    Added support for bus selection.
#   1.3    2016-08-18    Added @api annotations.
#
#
#   Config parameters
#
#   - chip          Integer     Number of the used chip select (CS) pin/port.
#                               Defaults to 0.
#   - mode          Integer     SPI mode, valid values are [0..3], defaults to 1.
#   - speed         Integer     SPI speed frequency in Hz, valid values are 
#                               [1..5000000], defaults to 5000000.
#   - bus           String      Name ot the SPI bus
#
#
#   Usage remarks
#
#   - Reading inputs is implemented via the diagnostic current/ open load feature
#
#   Implementation remarks
#
#   - SPI read protocol of this chip is a bit ...strange..., for this reason,
#     every SPI read command is sent in a modified way via sequential SPI xfer() calls.
#     As the second command is only a dummy the command byte 0xFF is used as this is
#     not a valid command code and will cause no harm.
#   - Returned SPI results are taken from the first (and only) byte of the second
#     SPI xfer() call. See readRegister() for details.
#   - The separate diagnose command is implemented in the same way as this also reads
#     some status from the chip.
#   - SPI write commands work as usual with a single xfer() call.
#

from webiopi.utils.types import toint
from webiopi.devices.spi import SPI
from webiopi.devices.digital import GPIOPort
from webiopi.decorators.rest import request, response, api
from webiopi.utils.logger import debug

class TLE7238SL(GPIOPort, SPI):

#---------- Class initialisation ----------

    COUNT        = 8
    
    ICRBASEADDR  = 0b000 #Input configuration register base address
    DCCRBASEADDR = 0b100 #Diagnostic current register base address
    CMDADDR      = 0b110 #Command register address
    DRBASEADDR   = 0b000 #Diagnostic register base address

    CONTROLBANK  = 0
    DIAGNOSEBANK = 1 

    INXOFF    = 0b00
    INXON     = 0b11
    INXMASK   = 0b11

    DCENOFF   = 0b0
    DCENON    = 0b1
    DCENMASK  = 0b1
    DATAMASK  = 0b00001111

    WRITEFLAG = 0b10000000
    WAKEFLAG  = 0b1000
    SLEEPFLAG = 0b0100

    RD_STD_DIAGNOSE_CMD = 0b00000010
    DUMMY_CMD           = 0xFF

    FUNCTIONS = [GPIOPort.OUT for i in range(COUNT)]

    def __init__(self, chip=0, mode=1, speed=5000000, bus=None):
        speed = toint(speed)
        if speed < 1 or speed > 5000000:
            raise ValueError("%d Hz speed out of range [%d..%d] Hz" % (speed, 0, 5000000))
        SPI.__init__(self, toint(chip), toint(mode), 8, speed, bus)
        GPIOPort.__init__(self, self.COUNT)
        self.wake()

#---------- Abstraction framework contracts ----------

    def __str__(self):
        return "TLE7238SL(chip=%d, mode=%d, dev=%s)" % (self.chip, self.mode, self.device())

#---------- Additional REST mappings to support wakeup, sleep and diagnose ----------

    @api("Device", 3, "feature", "driver")
    @request("POST", "run/wake")
    def wake(self):
        self.writeRegister(self.CMDADDR, self.WAKEFLAG)
        return "Wake sent"

    @api("Device", 3, "feature", "driver")
    @request("POST", "run/sleep")
    def sleep(self):
        self.writeRegister(self.CMDADDR, self.SLEEPFLAG)
        return "Sleep sent"

    @api("Device", 3, "feature", "driver")
    @request("GET", "run/diagnose")
    @response("0x%02X")
    def diagnose(self):
        senddata = [self.RD_STD_DIAGNOSE_CMD]
        debug("%s diagnose command=[0x%02X]" % (self.__str__(), senddata[0]))
        self.xfer(senddata)          # 1st call
        readdata = self.xfer([self.DUMMY_CMD]) # 2nd call
        return readdata[0]
   
#---------- GPIOPort abstraction related methods ----------

    def __getFunction__(self, channel):
        return self.FUNCTIONS[channel]

    def __setFunction__(self, channel, value):
        if not value in [self.IN, self.OUT]:
            raise ValueError("Requested function not supported")
        # Reset channel to off state and en/disable diagnostic current when changing function
        self.__digitalWrite__(channel, 0)

        if value == self.IN:
            self.__setDiagnosticCurrent__(channel, True)
        else:
            self.__setDiagnosticCurrent__(channel, False)

        self.FUNCTIONS[channel] = value

    def __digitalRead__(self, channel):
        if self.FUNCTIONS[channel] == self.OUT:
            # Read ICRx values for output ports
            addr = self.__getAddress__(self.ICRBASEADDR, channel)
            data = self.readRegister(addr, self.CONTROLBANK)
            shift = self.__shiftForChannel__(channel)
            bits = (data >> shift) & self.INXMASK
            if bits == self.INXOFF:
                return 0
            elif bits == self.INXON:
                return 1
            else:
                raise ValueError("Unsupported values in input control register")
        else:
            # Read DRx values for input ports
            addr = self.__getAddress__(self.DRBASEADDR, channel)
            data = self.readRegister(addr, self.DIAGNOSEBANK)
            shift = self.__shiftForChannel__(channel)
            return (data >> shift + 1) & 0x01

    def __digitalWrite__(self, channel, value):
        # Read full 4 register bits, then set relevant 2 bits and rewrite
        addr = self.__getAddress__(self.ICRBASEADDR, channel)
        shift = self.__shiftForChannel__(channel)
        currentData = self.readRegister(addr, self.CONTROLBANK)
        currentBits = (currentData >> shift) & self.INXMASK
        newBits = self.INXON << shift

        if (value & (currentBits == self.INXON)) | ((not value) & (currentBits == self.INXOFF)):
            return # value is already correct, nothing to do, ommit write command
        elif value:
            newData = currentData + newBits
        else:
            newData = currentData - newBits

        self.writeRegister(addr, newData)

    def __portRead__(self):
        value = 0
        for i in range(self.count):
            value |= self.__digitalRead__(i) << i
        return
    
    def __portWrite__(self, value):
        for i in range(self.count):
            self.__digitalWrite__(i, (value >> i) & 0x01)
        return

#---------- Local helpers ----------

    def __getAddress__(self, register, channel=0):
        return register + int(channel / 2)

    def __shiftForChannel__(self, channel):
        return (channel % 2) * 2
    
    def __getDCCRxAddress__(self, channel=0):
        return self.DCCRBASEADDR + int(channel / 4)

    def __dccrxShiftForChannel__(self, channel):
        return channel % 4

    def __setDiagnosticCurrent__(self, channel, enable=True):
        # Read full 4 register bits, then set relevant bit and rewrite
        addr = self.__getDCCRxAddress__(channel)
        shift = self.__dccrxShiftForChannel__(channel)
        currentData = self.readRegister(addr, self.CONTROLBANK)
        currentBit = (currentData >> shift) & self.DCENMASK
        newBit = self.DCENON << shift

        if (enable & (currentBit == self.DCENON)) | ((not enable) & (currentBit == self.DCENOFF)):
            return # enable is already correct, nothing to do, ommit write command
        elif enable:
            newData = currentData + newBit
        else:
            newData = currentData - newBit

        self.writeRegister(addr, newData)
        
    def readRegister(self, addr, bank):
        # Sending two SPI bytes at once seems not work, cut this into two sequential SPI send calls
        cmd = self.__readRegisterCommand__(addr, bank)
        debug("%s readregister command=[0x%02X]" % (self.__str__(), cmd))
        self.xfer([cmd])             # 1st call to send command byte for read
        readdata = self.xfer([self.DUMMY_CMD]) # 2nd dummy call to push out and receive SPI slave out value
        return readdata[0] & self.DATAMASK

    def __readRegisterCommand__(self, addr, bank):
        return (addr << 4) | (bank & 0x01)

    def writeRegister(self, addr, value):
        cmd = self.__writeRegisterCommand__(addr, value)
        debug("%s writeRegister command=[0x%02X]" % (self.__str__(), cmd))
        self.writeBytes([cmd]) # 1st call

    def __writeRegisterCommand__(self, addr, data):
        return (addr << 4) | (data & self.DATAMASK) | self.WRITEFLAG
        


