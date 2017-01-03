#   This code has to be added to __init__.py in folder .../devices/sensor

class Distance():
    def __family__(self):
        return "Distance"

    def __getMillimeter__(self):
        raise NotImplementedError

    @api("Distance", 0)
    @request("GET", "sensor/distance/*")
    @response(contentType=M_JSON)
    def distanceWildcard(self):
        values = {}
        distance = self.__getMillimeter__()
        values["mm"] = "%.02f" % distance
        values["cm"] = "%.02f" % (distance / 10)
        values["m"]  = "%.02f" % (distance / 1000)
        values["in"] = "%.02f" % (distance / 25.4)
        values["ft"] = "%.02f" % (distance / 25.4 / 12)
        values["yd"] = "%.02f" % (distance / 25.4 / 36)
        return values

    @api("Distance")
    @request("GET", "sensor/distance/mm")
    @response("%.02f")
    def getMillimeter(self):
        return self.__getMillimeter__()

    @api("Distance")
    @request("GET", "sensor/distance/cm")
    @response("%.02f")
    def getCentimeter(self):
        return self.getMillimeter() / 10

    @api("Distance")
    @request("GET", "sensor/distance/m")
    @response("%.02f")
    def getMeter(self):
        return self.getMillimeter() / 1000

    @api("Distance")
    @request("GET", "sensor/distance/in")
    @response("%.02f")
    def getInch(self):
        return self.getMillimeter() / 25.4

    @api("Distance")
    @request("GET", "sensor/distance/ft")
    @response("%.02f")
    def getFoot(self):
        return self.getInch() / 12

    @api("Distance")
    @request("GET", "sensor/distance/yd")
    @response("%.02f")
    def getYard(self):
        return self.getInch() / 36

