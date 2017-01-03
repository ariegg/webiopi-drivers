#   This code has to be added to __init__.py in folder .../devices/sensor

class Luminosity():
    def __family__(self):
        return "Luminosity"

    def __getLux__(self):
        raise NotImplementedError

    @api("Luminosity", 0)
    @request("GET", "sensor/luminosity/*")
    @response(contentType=M_JSON)
    def luminosityWildcard(self):
        values = {}
        luminosity = self.__getLux__()
        values["lux"] = "%.02f" % luminosity
        return values

    @api("Luminosity")
    @request("GET", "sensor/luminosity/lux")
    @response("%.02f")
    def getLux(self):
        return self.__getLux__()

