
class Tiles:
    def __init__(self, r, g, b):
        self.red = r
        self.green = g
        self.blue = b

    def CommonTile(self):
        return abs(self.red - 249) < 15 \
            and abs(self.green - 249) < 15 \
            and abs(self.blue - 249) < 15

    def Swamp(self):
        return abs(self.red - 195) < 15 \
            and abs(self.green - 161) < 15 \
            and abs(self.blue - 87) < 15
    
    def BlackHole(self):
        return abs(self.red - 54) < 15 \
            and abs(self.green - 54) < 15 \
            and abs(self.blue - 54) < 15
    
    def What_Tile(self):
        avoid = False
        if self.CommonTile():
            return avoid
        elif self.Swamp():
            avoid = True
            return avoid
        elif self.BlackHole():
            avoid = True
            return avoid
        else:
            return avoid
