
class Acceleration(LinearAcceleration, AngularAcceleration):
 
    def __family__(self):
        return [LinearAcceleration.__family__(self), AngularAcceleration.__family__(self)]

class AngularAcceleration():
    
    def __family__(self):
        return "AngularAcceleration"

class LinearAcceleration():
    
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

    @request("GET", "sensor/acceleration/x/m_s2")
    @response("%.2f")
    def getMeterPerSquareSecondX(self):
        return self.__getMeterPerSquareSecondX__()

    @request("GET", "sensor/acceleration/y/m_s2")
    @response("%.2f")
    def getMeterPerSquareSecondY(self):
        return self.__getMeterPerSquareSecondY__()

    @request("GET", "sensor/acceleration/z/m_s2")
    @response("%.2f")
    def getMeterPerSquareSecondZ(self):
        return self.__getMeterPerSquareSecondZ__()

    @request("GET", "sensor/acceleration/x/g")
    @response("%.3f")
    def getGravityX(self):
        return self.__getGravityX__()
    
    @request("GET", "sensor/acceleration/y/g")
    @response("%.3f")
    def getGravityY(self):
        return self.__getGravityY__()

    @request("GET", "sensor/acceleration/z/g")
    @response("%.3f")
    def getGravityZ(self):
        return self.__getGravityZ__()

    @request("GET", "sensor/acceleration/x/mg")
    @response("%d")
    def getMilliGravityX(self):
        return float(self.__getGravityX__()) / 1000.0
    
    @request("GET", "sensor/acceleration/y/mg")
    @response("%d")
    def getMilliGravityY(self):
        return float(self.__getGravityY__()) / 1000.0

    @request("GET", "sensor/acceleration/z/mg")
    @response("%d")
    def getMilliGravityZ(self):
        return float(self.__getGravityZ__()) / 1000.0
   
