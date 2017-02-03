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
#   1.0    2016-06-28    Initial release for bus selection.
#   1.1    2017-02-02    Added class SPI_MCP2210_WINDLL. Removed version number
#                        from file names
#
#

DRIVERS = {}
DRIVERS["i2cdev"]       = ["I2C_DEV"]
DRIVERS["i2cmock"]      = ["I2C_MOCK"]
DRIVERS["i2cmcphidraw"] = ["I2C_MCP2221_HIDRAW"]
DRIVERS["i2cmcpwindll"] = ["I2C_MCP2221_WINDLL"]
DRIVERS["spidev"]       = ["SPI_DEV"]
DRIVERS["spimock"]      = ["SPI_MOCK"]
DRIVERS["spimcphidraw"] = ["SPI_MCP2210_HIDRAW"]
DRIVERS["spimcpwindll"] = ["SPI_MCP2210_WINDLL"]
DRIVERS["uartdev"]      = ["UART_DEV"]
DRIVERS["uartmock"]     = ["UART_MOCK"]
DRIVERS["uartpyserial"] = ["UART_PYSERIAL"]
