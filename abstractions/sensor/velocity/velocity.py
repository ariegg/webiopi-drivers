
class LinearVelocity():
    
    def __family__(self):
        return "LinearVelocity"

    def __getMeterPerSecondX__(self):
        raise NotImplementedError
        
    def __getMeterPerSecondY__(self):
        raise NotImplementedError
        
    def __getMeterPerSecondZ__(self):
        raise NotImplementedError
        
    def MeterPerSecond2KmPerHour(self, value=0):
        return value * 3.6

    def KmPerHour2MeterPerSecond(self, value=0):
        return value / 3.6

    @api("LinearVelocity", 0)
    @request("GET", "sensor/velocity/linear/*")
    @response(contentType=M_JSON)
    def linearVelocityWildcard(self):
        values = {}
        x = self.getMeterPerSecondX()
        y = self.getMeterPerSecondY()
        z = self.getMeterPerSecondZ()
        values["x.m/s"] = "%.3f" % x
        values["y.m/s"] = "%.3f" % y
        values["z.m/s"] = "%.3f" % z
        return values

    @api("LinearVelocity", 0)
    @request("GET", "sensor/velocity/speed/*")
    @response(contentType=M_JSON)
    def speedWildcard(self):
        values = {}
        x = self.MeterPerSecond2KmPerHour(self.getMeterPerSecondX())
        y = self.MeterPerSecond2KmPerHour(self.getMeterPerSecondY())
        z = self.MeterPerSecond2KmPerHour(self.getMeterPerSecondZ())
        values["x.km/h"] = "%.3f" % x
        values["y.km/h"] = "%.3f" % y
        values["z.km/h"] = "%.3f" % z
        return values

    @request("GET", "sensor/velocity/linear/x/m_s")
    @response("%.3f")
    def getMeterPerSecondX(self):
        return self.__getMeterPerSecondX__()

    @request("GET", "sensor/velocity/linear/y/m_s")
    @response("%.3f")
    def getMeterPerSecondY(self):
        return self.__getMeterPerSecondY__()

    @request("GET", "sensor/velocity/linear/z/m_s")
    @response("%.3f")
    def getMeterPerSecondZ(self):
        return self.__getMeterPerSecondZ__()

class AngularVelocity():

    def PI(self):
        return 3.141592653589793
    
    def __family__(self):
        return "AngularVelocity"

    def __getRadianPerSecondX__(self):
        raise NotImplementedError

    def __getRadianPerSecondY__(self):
        raise NotImplementedError

    def __getRadianPerSecondZ__(self):
        raise NotImplementedError

    def RadianPerSecond2DegreePerSecond(self, value=0):
        return value / self.PI() * 180 

    def DegreePerSecond2RadianPerSecond(self, value=0):
        return value * self.PI() / 180

    def RadianPerSecond2Hertz(self, value=0):
        return value / self.PI() / 2

    def Hertz2RadianPerSecond(self, value=0):
        return value * self.PI() * 2


    @api("AngularVelocity", 0)
    @request("GET", "sensor/velocity/angular/*")
    @response(contentType=M_JSON)
    def angularVelocityWildcard(self):
        values = {}
        x = self.getRadianPerSecondX()
        y = self.getRadianPerSecondY()
        z = self.getRadianPerSecondZ()
        values["x.rad/s"] = "%.3f" % x
        values["y.rad/s"] = "%.3f" % y
        values["z.rad/s"] = "%.3f" % z
        return values

    @api("AngularVelocity", 0)
    @request("GET", "sensor/velocity/rotation/*")
    @response(contentType=M_JSON)
    def rotationWildcard(self):
        values = {}
        x = self.RadianPerSecond2Hertz(self.getRadianPerSecondX())
        y = self.RadianPerSecond2Hertz(self.getRadianPerSecondY())
        z = self.RadianPerSecond2Hertz(self.getRadianPerSecondZ())
        values["x.Hz"] = "%.3f" % x
        values["y.Hz"] = "%.3f" % y
        values["z.Hz"] = "%.3f" % z
        return values


    @request("GET", "sensor/velocity/angular/x/rad_s")
    @response("%.3f")
    def getRadianPerSecondX(self):
        return self.__getRadianPerSecondX__()

    @request("GET", "sensor/velocity/angular/y/rad_s")
    @response("%.3f")
    def getRadianPerSecondY(self):
        return self.__getRadianPerSecondY__()
    
    @request("GET", "sensor/velocity/angular/z/rad_s")
    @response("%.3f")
    def getRadianPerSecondZ(self):
        return self.__getRadianPerSecondZ__()

class Velocity(LinearVelocity, AngularVelocity):
 
    def __family__(self):
        return [LinearVelocity.__family__(self), AngularVelocity.__family__(self)]
