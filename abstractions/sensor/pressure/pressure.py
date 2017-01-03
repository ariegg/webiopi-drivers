#   This code has to be added to __init__.py in folder .../devices/sensor

class Pressure():
    def __init__(self, altitude=0, external=None):
        self.altitude = toint(altitude)
        if isinstance(external, str):
            self.external = deviceInstance(external)
        else:
            self.external = external

        if self.external != None and not isinstance(self.external, Temperature):
            raise Exception("external must be a Temperature sensor")

    def __family__(self):
        return "Pressure"

    def __getPascal__(self):
        raise NotImplementedError

    def __getPascalAtSea__(self):
        raise NotImplementedError

    @api("Pressure", 0)
    @request("GET", "sensor/pressure/*")
    @response(contentType=M_JSON)
    def pressureWildcard(self):
        values = {}
        pressure = self.__getPascal__()
        values["pa"] = pressure
        values["hpa"] = "%.02f" % (pressure / 100.0)
        return values

    @api("Pressure", 0)
    @request("GET", "sensor/pressure/sea/*")
    @response(contentType=M_JSON)
    def pressureWildcardSea(self):
        values = {}
        pressureAtSea = self.getPascalAtSea()
        values["pa"] = pressureAtSea
        values["hpa"] = "%.02f" % (pressureAtSea / 100.0)
        return values

    @api("Pressure")
    @request("GET", "sensor/pressure/pa")
    @response("%d")
    def getPascal(self):
        return self.__getPascal__()

    @api("Pressure")
    @request("GET", "sensor/pressure/hpa")
    @response("%.2f")
    def getHectoPascal(self):
        return float(self.__getPascal__()) / 100.0

    @api("Pressure")
    @request("GET", "sensor/pressure/sea/pa")
    @response("%d")
    def getPascalAtSea(self):
        pressure = self.__getPascal__()
        if self.external != None:
            k = self.external.getKelvin()
            if k != 0:
                return float(pressure) / (1.0 / (1.0 + 0.0065 / k * self.altitude)**5.255)
        return float(pressure) / (1.0 - self.altitude / 44330.0)**5.255

    @api("Pressure")
    @request("GET", "sensor/pressure/sea/hpa")
    @response("%.2f")
    def getHectoPascalAtSea(self):
        return self.getPascalAtSea() / 100.0

