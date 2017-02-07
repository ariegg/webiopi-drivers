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
#   1.0    2017-02-06    Initial release.
#
#   This utility looks for all driver lookup files named "some.drivers" in the
#   context(source folder) of any Python source file "inifile" (which is typically
#   but not mandatory some __init__.py of the device abstraction folders).
#   
#   The format of the drivers file is:
#   - It is a text file
#   - Comment lines start with "#" and will be ignored
#   - Empty lines are allowed and will be also ignored
#   - Each line consists of exactly one chip class name
#   - White space before and after the chip class names will be deleted
#
#   All found chip class names are added as array of strings to the
#   provided "drivers" dictionary at the key "some". This allows to add new
#   chip driver classes without the need to edit "DRIVERS" at the end of 
#   __init__.py each time a new driver source file gets added.
#
#   The file names "some.py" (for the driver) and "some.drivers" (for the
#   driver class names lookup file) must match exactly. Just copy them to
#   the correct source folder to make them active.
#

import os

def driverDetector(pyFileName, drivers):
    path = os.path.abspath(pyFileName)
    dname = os.path.dirname(path)
    for fname in os.listdir(dname):
        if fname.endswith(".drivers"):
            key = (fname.split(".")[0])
            classNames = []
            with open(os.path.join(dname, fname)) as file:
                lines = file.readlines()
                lines = [line.strip() for line in lines]
                for line in lines:
                    if not (line.startswith('#') or len(line) == 0):
                        classNames.append(line)
            if len(classNames) > 0:
                drivers[key] = classNames
