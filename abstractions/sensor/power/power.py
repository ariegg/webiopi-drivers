#   This code has to be added to __init__.py in folder .../devices/sensor

class Power():
    def __family__(self):
        return "Power"

    def __getWatt__(self):
        raise NotImplementedError

    @api("Power", 0)
    @request("GET", "sensor/power/*")
    @response(contentType=M_JSON)
    def powerWildcard(self):
        values = {}
        power = self.__getWatt__()
        values["kW"] = "%.03f" % (power * 1000)
        values["W"]  = "%.03f" % power
        values["mW"] = "%.03f" % (power / 1000)
        return values

    @api("Power")
    @request("GET", "sensor/power/kW")
    @response("%.03f")
    def getKilowatt(self):
        return self.__getWatt__() / 1000

    @api("Power")
    @request("GET", "sensor/power/W")
    @response("%.03f")
    def getWatt(self):
        return self.__getWatt__()

    @api("Power")
    @request("GET", "sensor/power/mW")
    @response("%.03f")
    def getMilliwatt(self):
        return self.__getWatt__() * 1000
    
