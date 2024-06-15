
import cv2

class Tiles:
    def analyze(self, r, g, b):
        self.red = r
        self.green = g
        self.blue = b

    def CommonTile(self):
        return abs(self.red - 249) < 15 \
            and abs(self.green) < 15 \
            and abs(self.blue) < 15

    def Swamp(self):
        return abs(self.red - 152) < 15 \
            and abs(self.green - 119) < 15 \
            and abs(self.blue - 60) < 15
    
    def BlackHole(self):
        return abs(self.red) < 15 \
            and abs(self.green) < 15 \
            and abs(self.blue) < 15

    def What_Tile(self):
        avoid = False
        if self.BlackHole():
            avoid = True
            
        return avoid