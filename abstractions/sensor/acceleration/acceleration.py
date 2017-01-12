
class LinearAcceleration():

    def StandardGravity(self):
        return 9.80665 
    
    def __family__(self):
        return "LinearAcceleration"

    def __getMeterPerSquareSecondX__(self):
        raise NotImplementedError
        
    def __getMeterPerSquareSecondY__(self):
        raise NotImplementedError
        
    def __getMeterPerSquareSecondZ__(self):
        raise NotImplementedError
        
    def __getGravityX__(self):
        raise NotImplementedError
        
    def __getGravityY__(self):
        raise NotImplementedError

    def __getGravityZ__(self):
        raise NotImplementedError

    def MeterPerSquareSecond2Gravity(self, value=0):
        return value / self.StandardGravity() 

    def Gravity2MeterPerSquareSecond(self, value=0):
        return value * self.StandardGravity() 

    @api("LinearAcceleration", 0)
    @request("GET", "sensor/acceleration/linear/*")
    @response(contentType=M_JSON)
    def linearAccelerationWildcard(self):
        values = {}
        x = self.getMeterPerSquareSecondX()
        y = self.getMeterPerSquareSecondY()
        z = self.getMeterPerSquareSecondZ()
        values["x.m/s2"] = "%.3f" % x
        values["y.m/s2"] = "%.3f" % y
        values["z.m/s2"] = "%.3f" % z
        return values

    @api("LinearAcceleration", 0)
    @request("GET", "sensor/acceleration/gravity/*")
    @response(contentType=M_JSON)
    def gravityAccelerationWildcard(self):
        values = {}
        x = self.getGravityX()
        y = self.getGravityY()
        z = self.getGravityZ()
        values["x.g"] = "%.3f" % x
        values["y.g"] = "%.3f" % y
        values["z.g"] = "%.3f" % z
        return values

    @request("GET", "sensor/acceleration/linear/x/m_s2")
    @response("%.3f")
    def getMeterPerSquareSecondX(self):
        return self.__getMeterPerSquareSecondX__()

    @request("GET", "sensor/acceleration/linear/y/m_s2")
    @response("%.3f")
    def getMeterPerSquareSecondY(self):
        return self.__getMeterPerSquareSecondY__()

    @request("GET", "sensor/acceleration/linear/z/m_s2")
    @response("%.3f")
    def getMeterPerSquareSecondZ(self):
        return self.__getMeterPerSquareSecondZ__()

    @request("GET", "sensor/acceleration/gravity/x/g")
    @response("%.3f")
    def getGravityX(self):
        return self.__getGravityX__()
    
    @request("GET", "sensor/acceleration/gravity/y/g")
    @response("%.3f")
    def getGravityY(self):
        return self.__getGravityY__()

    @request("GET", "sensor/acceleration/gravity/z/g")
    @response("%.3f")
    def getGravityZ(self):
        return self.__getGravityZ__()

    @request("GET", "sensor/acceleration/gravity/x/mg")
    @response("%.3f")
    def getMilliGravityX(self):
        return float(self.__getGravityX__()) * 1000.0
    
    @request("GET", "sensor/acceleration/gravity/y/mg")
    @response("%.3f")
    def getMilliGravityY(self):
        return float(self.__getGravityY__()) * 1000.0

    @request("GET", "sensor/acceleration/gravity/z/mg")
    @response("%.3f")
    def getMilliGravityZ(self):
        return float(self.__getGravityZ__()) * 1000.0

class AngularAcceleration():
    
    def __family__(self):
        return "AngularAcceleration"

    def __getRadianPerSquareSecondX__(self):
        raise NotImplementedError

    def __getRadianPerSquareSecondY__(self):
        raise NotImplementedError

    def __getRadianPerSquareSecondZ__(self):
        raise NotImplementedError

    @api("AngularAcceleration", 0)
    @request("GET", "sensor/acceleration/angular/*")
    @response(contentType=M_JSON)
    def angularAccelerationWildcard(self):
        values = {}
        x = self.getRadianPerSquareSecondX()
        y = self.getRadianPerSquareSecondY()
        z = self.getRadianPerSquareSecondZ()
        values["x.rad/s2"] = "%.3f" % x
        values["y.rad/s2"] = "%.3f" % y
        values["z.rad/s2"] = "%.3f" % z
        return values

    @request("GET", "sensor/acceleration/angular/x/rad_s2")
    @response("%.3f")
    def getRadianPerSquareSecondX(self):
        return self.__getRadianPerSquareSecondX__()

    @request("GET", "sensor/acceleration/angular/y/rad_s2")
    @response("%.3f")
    def getRadianPerSquareSecondY(self):
        return self.__getRadianPerSquareSecondY__()
    
    @request("GET", "sensor/acceleration/angular/z/rad_s2")
    @response("%.3f")
    def getRadianPerSquareSecondZ(self):
        return self.__getRadianPerSquareSecondZ__()

class Acceleration(LinearAcceleration, AngularAcceleration):
 
    def __family__(self):
        return [LinearAcceleration.__family__(self), AngularAcceleration.__family__(self)]
