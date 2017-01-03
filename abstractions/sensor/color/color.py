class Color():
    def __family__(self):
        return "Color"

    def __getRGB__(self):
        # Expected result: tuple r,g,b all values integer between 0 and 255
        raise NotImplementedError

    def __getRGB16bpp__(self):
        # Expected result: tuple r,g,b all values integer between 0 and 65535
        raise NotImplementedError

    def RGB16bpp2Kelvin(self, rgb16bpp_values=None):
        # This calculation is based on the tech note from ams (formerly TAOS)
        # Maybe this code should go to the TAOS drivers
        # Keep in mind: This conversion makes only sense to colors near to white!

        if rgb16bpp_values == None:
            r, g, b = self.__getRGB16bpp__()
        else:
            r, g, b = rgb16bpp_values

        # X = (-0.14282 * r) + (1.54924 * g) + (-0.95641 * b)
        # Y = (-0.32466 * r) + (1.57837 * g) + (-0.73191 * b)
        # Z = (-0.68202 * r) + (0.77073 * g) + ( 0.56332 * b)
        # x = X /(X+Y+Z)
        # y = Y /(X+Y+Z)
        # n = (x - 0.3320) / (0.1858 - y)

        n = ((0.23881 * r) + (0.25499 * g) + (-0.58291 * b)) / ((0.11109 * r) + (-0.85406 * g) +(0.52289 * b))
        cct = 449 * n**3 + 3525 * n**2 + 6823.3 * n + 5520.33

        return int(round(cct))


    @api("Color", 0)
    @request("GET", "sensor/color/*")
    @response(contentType=M_JSON)
    def colorWildcard(self):
        values = {}
        rgb16bpp_values = self.__getRGB16bpp__()
        r16, g16, b16 = rgb16bpp_values
        r = int(round(r16 / 256))
        g = int(round(g16 / 256))
        b = int(round(b16 / 256))
        values["hex"]   = "#%02X%02X%02X" % (r, g, b)
        values["red"]   = "%d" % r
        values["green"] = "%d" % g
        values["blue"]  = "%d" % b
        values["k"]     = "%d"    % self.RGB16bpp2Kelvin(rgb16bpp_values)
        return values

    @api("Color", 1)
    @request("GET", "sensor/color/16bpp/*")
    @response(contentType=M_JSON)
    def colorWildcard16bpp(self):
        values = {}
        rgb16bpp_values = self.__getRGB16bpp__()
        r16, g16, b16 = rgb16bpp_values
        values["red"]   = "%d" % r16
        values["green"] = "%d" % g16
        values["blue"]  = "%d" % b16
        values["k"]     = "%d"    % self.RGB16bpp2Kelvin(rgb16bpp_values)
        return values

    @api("Color")
    @request("GET", "sensor/color/rgb")
    @response("%s")
    def getRGB(self):
        r, g, b = self.__getRGB__()
        return "%s,%s,%s" % (r, g, b)

    @api("Color")
    @request("GET", "sensor/color/rgb/hex")
    @response("%s")
    def getRGBHex(self):
        r, g, b = self.__getRGB__()
        return "#%02X%02X%02X" % (r, g, b)

    @api("Color")
    @request("GET", "sensor/color/red")
    @response("%d")
    def getRed(self):
        r, g, b = self.__getRGB__()
        return r

    @api("Color")
    @request("GET", "sensor/color/green")
    @response("%d")
    def getGreen(self):
        r, g, b = self.__getRGB__()
        return g

    @api("Color")
    @request("GET", "sensor/color/blue")
    @response("%d")
    def getBlue(self):
        r, g, b = self.__getRGB__()
        return b

    @api("Color", 3)
    @request("GET", "sensor/color/rgb/16bpp")
    @response("%s")
    def getRGB16bpp(self):
        r, g, b = self.__getRGB16bpp__()
        return "%s,%s,%s" % (r, g, b)

    @api("Color")
    @request("GET", "sensor/color/k")
    @response("%d")
    def getKelvin(self):
        return self.RGB16bpp2Kelvin()

