#   This code has to be added to __init__.py in folder .../devices/sensor

class Current():
    def __family__(self):
        return "Current"

    def __getMilliampere__(self):
        raise NotImplementedError

    @api("Current", 0)
    @request("GET", "sensor/current/*")
    @response(contentType=M_JSON)
    def currentWildcard(self):
        values = {}
        current = self.__getMilliampere__()
        values["mA"] = "%.03f" % current
        values["A"]  = "%.03f" % (current * 1000)
        return values

    @api("Current")
    @request("GET", "sensor/current/mA")
    @response("%.03f")
    def getMilliampere(self):
        return self.__getMilliampere__()

    @api("Current")
    @request("GET", "sensor/current/A")
    @response("%.03f")
    def getAmpere(self):
        return self.__getMilliampere__() * 1000
