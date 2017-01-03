#   Copyright 2014-2016 Andreas Riegg - t-h-i-n-x.net
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
#   1.0    2014-08-25    Initial release.
#   1.1    2014-09-04    Improved file open/close handling.
#                        Reimplemented writeMemoryBytes().
#   1.2    2014-11-13    Updated to match v1.3 of __init__.py
#                        plus some optimizations
#   1.3    2014-12-08    Updated to match v1.4 of Memory implementation
#   1.4    2015-09-08    Bugfix on file writing for writeWord and writelong.
#   1.5    2015-09-09    Added JSON file and refactoring to support this.
#   1.6    2016-08-26    Replaced very big range() check by simple > < testing.
#
#   Config parameters
#
#   - slots         integer       Number of memory bytes
#   - filename      string        Name/path of memory file
#
#   Usage remarks
#
#   - This class is mainly targeted to store some 100's of bytes on the
#     server disk.
#     It is abolutely NOT suited to save 10's of kilobytes or even more.
#     Values are kept in server RAM, so reading is very fast but allocates
#     server RAM memory, so be sparse on slot sizes. Every update
#     is written immediately to disk, so writing is slower and initiates
#     server disk activity for every write.
#   - Multiple device instances are possible within one server. Make sure
#     to have different filenames/pathes for each device instance via the
#     filename parameter
#   - Slot sizes can be changed at every instance creation time. If old size
#     was smaller, the slots will be filled from the first slot until done.
#     Remaining slots will be initialized with 0x00. If old size was bigger,
#     the slots will be filled to the last available slot and the remainder
#     of the old slot bytes will be discarded.
#

import os
import pickle
import json
from webiopi.utils.types import toint
from webiopi.devices.memory import Memory

class ABSTRACTFILE(Memory):
#   This class provides all generic code to store the bytes.

#---------- Constants and definitions ----------

    BYTES = []
    MAXSLOT_VALUE    = 2**16

    FILENAME_DEFAULT = "unknown" # Local memory default name

#---------- Class initialisation ----------

    def __init__(self, slots=256, filename=None):
        slots = toint(slots)
        if slots < 1 or slots > self.MAXSLOT_VALUE:
            raise ValueError("slots value [%d] out of range [%d..%d]" % (slots, 1, self.MAXSLOT_VALUE))

        if filename != None:
            self.filename = filename
        else:
            self.filename = self.FILENAME_DEFAULT

        Memory.__init__(self, slots)
        self.BYTES = [0 for i in range(slots)]

        if os.path.exists(self.filename):
            self.__readFile__()


#---------- Abstraction framework contracts ----------

    def __str__(self):
        return "ABSTRACTFILE (%s)" % self.filename

    def close(self):
        self.__writeFile__()

#---------- Memory abstraction related methods ----------

    def __readMemoryByte__(self, address):
        return self.BYTES[address]

    def __writeMemoryByte__(self, address, value):
        self.BYTES[address] = value
        self.__writeFile__()
        return self.__readMemoryByte__(address)

    def __writeMemoryWord__(self, address, value):
        byte0 = (value >>  8) & 0xFF
        byte1 = value & 0xFF
        self.writeMemoryBytes(address * 2, [byte0, byte1])

    def __writeMemoryLong__(self, address, value):
        byte0 = (value >> 24) & 0xFF
        byte1 = (value >> 16) & 0xFF
        byte2 = (value >>  8) & 0xFF
        byte3 = value & 0xFF
        self.writeMemoryBytes(address * 4, [byte0, byte1, byte2, byte3])


#---------- Memory abstraction NON-REST re-implementation ----------
# Avoid file writing for every byte, do this for all bytes at the end

    def writeMemoryBytes(self, start=0, byteValues=[]):
        self.checkByteAddress(start)
        stop = start + len(byteValues)
        self.checkStopByteAddress(stop)
        i = 0
        for byte in byteValues: # do nothing if list is empty
            position = i + start
            self.BYTES[position] = byte
            i += 1
        self.__writeFile__()


#---------- Local helpers ----------
        
    def __populateFromFilebytes__(self, filebytes):
        byteCountFile = len(filebytes)
        if (byteCountFile > self.byteCount()):
            slots = self.byteCount()
        else:
            slots = byteCountFile
        for i in range(slots):
            self.BYTES[i] = filebytes[i]

#---------- Local helper contracts ----------

    def __readFile__(self):
        raise NotImplementedError

    def __writeFile__(self):
        raise NotImplementedError


class PICKLEFILE(ABSTRACTFILE):
#   This class uses the standard Pickle utility of Python to store the
#   bytes.

#---------- Constants and definitions ----------

    FILENAME_DEFAULT = "webiopimem.pkl" # Local Pickle memory file default name

#---------- Class initialisation ----------

    def __init__(self, slots=256, filename=None):
        ABSTRACTFILE.__init__(self, slots, filename)
        

#---------- Abstraction framework contracts ----------

    def __str__(self):
        return "PICKLEFILE (%s)" % self.filename


#---------- Local helpers ----------

    def __readFile__(self):
        with open(self.filename, "rb") as f:
            filebytes = pickle.load(f)
        self.__populateFromFilebytes__(filebytes)

    def __writeFile__(self):
        with open(self.filename, "wb") as f:
            pickle.dump(self.BYTES, f)

class JSONFILE(ABSTRACTFILE):
#   This class uses the standard JSON utility of Python to store the
#   bytes in JSON format.

#---------- Constants and definitions ----------

    FILENAME_DEFAULT = "webiopimem.json" # Local JSON memory file default name

#---------- Class initialisation ----------

    def __init__(self, slots=256, filename=None):
        ABSTRACTFILE.__init__(self, slots, filename)

#---------- Abstraction framework contracts ----------

    def __str__(self):
        return "JSONFILE (%s)" % self.filename

#---------- Local helpers ----------

    def __readFile__(self):
        with open(self.filename, "rb") as f:
            filebytes = json.load(f)            
        self.__populateFromFilebytes__(filebytes)

    def __writeFile__(self):
        with open(self.filename, "wb") as f:
            json.dump(self.BYTES, f, indent=0)

