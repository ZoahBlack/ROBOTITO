
import cv2
import numpy as np

class ImageProcessor:
    def analyze(self, image):
        self.image = image

    def victim_or_sign(self):
        grey = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        ret, thresh=cv2.threshold(grey, 140, 255, cv2.THRESH_BINARY)

        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) == 0:
            return None
        
        img = cv2.drawContours(self.image, contours, -1, (0, 0, 255), 1)
        approx=cv2.minAreaRect(contours[0])
        angle=approx[2]

        if len(contours) == 1 and len(contours[0]) <= 10 and angle % 90 == 0:
            x = int(approx[0][0])
            y = int(approx[0][1])
            half_w = int(approx[1][0] / 2)
            half_h = int(approx[1][1] / 2)

            rect = thresh[y - half_h:y + half_h, x - half_w:x + half_h]

            size = rect.shape[0] * rect.shape[1]
            if size == 0: return None
            
            white_px = np.count_nonzero(rect == 255)
            if white_px == 0:
                return None

            black_px = np.count_nonzero(rect == 0)
            if black_px == 0: 
                return None
            
            whitePercentage = white_px / size
            if whitePercentage < 0.6:
                return None

            blackPercentage = black_px / size
            if blackPercentage < 0.1:
                return None
            
            if abs(rect.shape[0] - rect.shape[1]) > 2:
                return None
                
            cuadrito_arriba = thresh[y - half_h:y - int(half_h / 3), x - int(half_w / 3):x + int(half_w / 3)]
            cuadrito_abajo = thresh[y + int(half_h / 3):y + half_h, x - int(half_w / 3):x + int(half_w / 3)]

            if cuadrito_abajo.size == 0: return None
            if cuadrito_arriba.size == 0: return None

            if np.count_nonzero(cuadrito_arriba == 0) / cuadrito_arriba.size < 0.2 and np.count_nonzero(cuadrito_abajo == 0) / cuadrito_abajo.size < 0.2:
                return "H"
            elif np.count_nonzero(cuadrito_arriba == 0) / cuadrito_arriba.size < 0.2 and np.count_nonzero(cuadrito_abajo == 0) / cuadrito_abajo.size >= 0.2:
                return "U"
            elif np.count_nonzero(cuadrito_arriba == 0) / cuadrito_arriba.size >= 0.2 and np.count_nonzero(cuadrito_abajo == 0) / cuadrito_abajo.size >= 0.2:
                return "S"
        
        elif abs(angle) % 45 == 0 and len(contours) >= 1:
            height, width=thresh.shape[0], thresh.shape[1]
            M=cv2.getRotationMatrix2D((width/2,height/2),angle,1)
            thresh_rot=cv2.warpAffine(thresh,M,(width,height))
            image_rot=cv2.warpAffine(self.image,M,(width,height))
            contours, hierarchy = cv2.findContours(thresh_rot, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            approx = cv2.minAreaRect(contours[0])
            x=int(approx[0][0])
            y=int(approx[0][1])
            halfWidth=int(approx[1][0]/2)
            halfHeight=int(approx[1][1]/2)
            rect = image_rot[y-halfHeight:y+halfHeight, x-halfWidth:x+halfWidth]

            size = rect.shape[0] * rect.shape[1]

            black_px = np.count_nonzero(rect == 0)
            white_px = np.count_nonzero(rect == 255)

            if size != 0:
                blackPercentage = black_px / size
                whitePercentage = white_px / size

                if whitePercentage > 0.2:
                    return None
                
            #print(blackPercentage, whitePercentage) # for debugging purposes, remove this line when done

            yellow=0
            red=0
            black=0
            white=0
            for x in range(rect.shape[0]):
                for y in range(rect.shape[1]):
                    b, g, r, _=rect[x,y]
                    if b>150 and g>150 and r>150:
                        white+=1
                    elif b<50 and g<50 and r<50:
                        black+=1
                        if blackPercentage < 0.2 or blackPercentage > 0.3:
                            black-=1
                    elif b>70 and g<10 and r>180:
                        red+=1
                    elif b<10 and g>180 and r>190:
                        yellow+=1

            print(yellow, red, black, white) # for debugging purposes, remove this line when done

            if black == 0 and red == 0 and yellow == 0:
                return None
            elif black > white and red == 0 and yellow == 0:
                return None
            elif  red > 1 and (red + white) > (black + yellow) and white > black: 
                return "F"
            elif black > 1 and (white + black) > (yellow + red) and white < black:
                return "P"
            elif black > 1 and (white + black) > (yellow + red): # b< 120 n <25
                return "C"
            elif yellow > 1 and (red + yellow) > (black + white):
                return "O"
            
    def see_hole(self):
        half = self.image[43:,:]
        size = half.shape[0]*half.shape[1]
        black_px = np.count_nonzero(half < 31)
        blackPercentage = black_px / size

        black_hole = False
        #imagen 64x64
        #inicio agujero justo en la mitad = self.image[44,32]
        if blackPercentage <= 3 and blackPercentage >= 1 or black_px <= 5100 and black_px > 100:
            black_hole = True
        
        return black_hole