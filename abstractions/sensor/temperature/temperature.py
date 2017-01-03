#   This code has to be added to __init__.py in folder .../devices/sensor

class Temperature():
    def __family__(self):
        return "Temperature"

    def __getKelvin__(self):
        raise NotImplementedError

    def __getCelsius__(self):
        raise NotImplementedError

    def __getFahrenheit__(self):
        raise NotImplementedError

    def Kelvin2Celsius(self, value=None):
        if value == None:
            value = self.getKelvin()
        return value - 273.15

    def Kelvin2Fahrenheit(self, value=None):
        if value == None:
            value = self.getKelvin()
        return value * 1.8 - 459.67

    def Celsius2Kelvin(self, value=None):
        if value == None:
            value = self.getCelsius()
        return value + 273.15

    def Celsius2Fahrenheit(self, value=None):
        if value == None:
            value = self.getCelsius()
        return value * 1.8 + 32

    def Fahrenheit2Kelvin(self, value=None):
        if value == None:
            value = self.getFahrenheit()
        return (value - 459.67) / 1.8

    def Fahrenheit2Celsius(self, value=None):
        if value == None:
            value = self.getFahrenheit()
        return (value - 32) / 1.8

    @api("Temperature", 0)
    @request("GET", "sensor/temperature/*")
    @response(contentType=M_JSON)
    def temperatureWildcard(self):
        values = {}
        temperature = self.__getCelsius__()
        values["c"] = "%.02f" % temperature
        values["k"] = "%.02f" % self.Celsius2Kelvin(temperature)
        values["f"] = "%.02f" % self.Celsius2Fahrenheit(temperature)
        return values

    @api("Temperature")
    @request("GET", "sensor/temperature/k")
    @response("%.02f")
    def getKelvin(self):
        return self.__getKelvin__()

    @api("Temperature")
    @request("GET", "sensor/temperature/c")
    @response("%.02f")
    def getCelsius(self):
        return self.__getCelsius__()

    @api("Temperature")
    @request("GET", "sensor/temperature/f")
    @response("%.02f")
    def getFahrenheit(self):
        return self.__getFahrenheit__()

