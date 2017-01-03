class Voltage():
    def __family__(self):
        return "Voltage"

    def __getVolt__(self):
        raise NotImplementedError

    @api("Voltage", 0)
    @request("GET", "sensor/voltage/*")
    @response(contentType=M_JSON)
    def voltageWildcard(self):
        values = {}
        voltage = self.__getVolt__()
        values["V"]  = "%.03f" % voltage
        values["mV"] = "%.03f" % (voltage / 1000)
        return values

    @api("Voltage")
    @request("GET", "sensor/voltage/V")
    @response("%.03f")
    def getVolt(self):
        return self.__getVolt__()

    @api("Voltage")
    @request("GET", "sensor/voltage/mV")
    @response("%.03f")
    def getMillivolt(self):
        return self.__getVolt__() / 1000
