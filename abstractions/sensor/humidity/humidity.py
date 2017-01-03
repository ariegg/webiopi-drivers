#   This code has to be added to __init__.py in folder .../devices/sensor

class Humidity():
    def __family__(self):
        return "Humidity"

    def __getHumidity__(self):
        raise NotImplementedError

    @api("Humidity", 0)
    @request("GET", "sensor/humidity/*")
    @response(contentType=M_JSON)
    def humidityWildcard(self):
        values = {}
        humidity = self.__getHumidity__()
        values["float"]   = "%f" % humidity
        values["percent"] = "%d" % (humidity * 100)
        return values

    @api("Humidity")
    @request("GET", "sensor/humidity/float")
    @response("%f")
    def getHumidity(self):
        return self.__getHumidity__()

    @api("Humidity")
    @request("GET", "sensor/humidity/percent")
    @response("%d")
    def getHumidityPercent(self):
        return self.__getHumidity__() * 100

