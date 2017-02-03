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
#   1.0    2016-08-30    Initial release.
#
#   Implementation and usage remarks
#
#   Version for UART implementation via pySerial. This device driver does only
#   work if the PySerial package (http://pythonhosted.org/pyserial/) has been
#   installed before. PySerial is supporting many platforms that Python runs on
#   and is compatible with Python 2 and Python 3.
#
#   PySerial is the tool of choice if the intended platform does not provide
#   Linux-like standard serial devices via /dev/tty...... but it can be used
#   also for those serial interfaces as well. Just set the dev: parameter to
#   the correct path including the prefix /dev/....
#


from webiopi.devices.bus import Bus, UART_Bus
from webiopi.utils.types import toint, str2bool
from serial import Serial
from webiopi.utils.logger import debug

class UART_PYSERIAL(UART_Bus):
    def __init__(self, dev="", baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=0, xonxoff=False, rtscts=False, dsrdtr=False):
        self.port = dev
        self.baudrate = toint(baudrate)
        self.bytesize = toint(bytesize)
        self.parity = parity
        self.stopbits = toint(stopbits)
        self.timeout = toint(timeout)
        self.xonxoff = str2bool(xonxoff)
        self.rtscts = str2bool(rtscts)
        self.dsrdtr = str2bool(dsrdtr)
        Bus.__init__(self, "UART", "pyserial:%s" % dev, None)


    def __str__(self):
        return "UART_PYSERIAL(%s %dbps)" % (self.dev, self.baudrate)

#---------- Bus abstraction methods reimplementation ----------

    def open(self):
        debug("UART_PYSERIAL: Opening serial interface %s (baud=%d,bytesize=%d,parity=%s,stopbits=%d,timeout=%d,xonxoff=%s,rtscts=%s,dsrdtr=%s)" %
              (self.port, self.baudrate, self.bytesize, self.parity, self.stopbits, self.timeout, self.xonxoff, self.rtscts, self.dsrdtr))
        ser = Serial(port=self.port,
                     baudrate=self.baudrate,
                     bytesize=self.bytesize,
                     parity=self.parity,
                     stopbits=self.stopbits,
                     timeout=self.timeout,
                     xonxoff=self.xonxoff,
                     rtscts=self.rtscts,
                     dsrdtr=self.dsrdtr
                     )
        self.ser = ser

    def close(self):
        debug("UART_PYSERIAL: Closing serial interface %s" % self.ser.port)
        self.ser.close()

#---------- UART abstraction communication methods redirected to reading/writing using pySerial ----------

    def read(self, size=1):
        return self.ser.read(size)

    def write(self, data):
        self.ser.write(data)

    def available(self):
        return self.ser.in_waiting






