
import cv2
import numpy as np

class ImageProcessor:
    def analyze(self, image):
        self.image = image

    def debugShow(self, image):
        cv2.imshow("V", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def victima_o_cartel(self):
        gris = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        ret, thresh=cv2.threshold(gris, 140, 255, cv2.THRESH_BINARY)


        contornos, jerarquia = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contornos) == 0:
            return None
        
        imagen = cv2.drawContours(self.image, contornos, -1, (0, 0, 255), 1)

    
        approx=cv2.minAreaRect(contornos[0])
        angulo=approx[2]

        if len(contornos) == 1 and len(contornos[0]) <= 10 and angulo % 90 == 0:
            x = int(approx[0][0])
            y = int(approx[0][1])
            mitad_ancho = int(approx[1][0] / 2)
            mitad_alto = int(approx[1][1] / 2)

            rect = thresh[y - mitad_alto:y + mitad_alto, x - mitad_ancho:x + mitad_ancho]

            tamanio = rect.shape[0] * rect.shape[1]
            if tamanio == 0: return None
            
            pixeles_negros = np.count_nonzero(rect == 0)
            if pixeles_negros == 0: 
                print("CHAU porque no hay pixeles negros")
                return None
            
            porcentaje_negros = pixeles_negros / tamanio
            print("Porcentaje de negros: ", porcentaje_negros)
            if porcentaje_negros < 0.1:
                print("CHAU porque hay muy pocos negros")
                return None
            
            if abs(rect.shape[0] - rect.shape[1]) > 2:
                print("CHAU porque no es un cuadrado")
                return None
                
            cuadrito_arriba = thresh[y - mitad_alto:y - int(mitad_alto / 3), x - int(mitad_ancho / 3):x + int(mitad_ancho / 3)]
            cuadrito_abajo = thresh[y + int(mitad_alto / 3):y + mitad_alto, x - int(mitad_ancho / 3):x + int(mitad_ancho / 3)]

            if cuadrito_abajo.size == 0: return None
            if cuadrito_arriba.size == 0: return None

            if np.count_nonzero(cuadrito_arriba == 0) / cuadrito_arriba.size < 0.2 and np.count_nonzero(cuadrito_abajo == 0) / cuadrito_abajo.size < 0.2:
                return "H"
            elif np.count_nonzero(cuadrito_arriba == 0) / cuadrito_arriba.size < 0.2 and np.count_nonzero(cuadrito_abajo == 0) / cuadrito_abajo.size >= 0.2:
                return "U"
            elif np.count_nonzero(cuadrito_arriba == 0) / cuadrito_arriba.size >= 0.2 and np.count_nonzero(cuadrito_abajo == 0) / cuadrito_abajo.size >= 0.2:
                return "S"
        elif abs(angulo) == 45 and len(contornos) == 1:
            alto, ancho=thresh.shape[0], thresh.shape[1]
            M=cv2.getRotationMatrix2D((ancho/2,alto/2),angulo,1)
            thresh_rot=cv2.warpAffine(thresh,M,(ancho,alto))
            imagen_rot=cv2.warpAffine(self.image,M,(ancho,alto))
            contornos, jerarquia = cv2.findContours(thresh_rot, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            approx = cv2.minAreaRect(contornos[0])
            x=int(approx[0][0])
            y=int(approx[0][1])
            mitadAncho=int(approx[1][0]/2)
            mitadAlto=int(approx[1][1]/2)
            rect = imagen_rot[y-mitadAlto:y+mitadAlto, x-mitadAncho:x+mitadAncho]

            amarillo=0
            rojo=0
            negro=0
            blanco=0
            for x in range(rect.shape[0]):
                for y in range(rect.shape[1]):
                    b, g, r=rect[x,y]
                    if b>150 and g>150 and r>150:
                        blanco+=1
                    elif b<50 and g<50 and r<50:
                        negro+=1
                    elif b>70 and g<10 and r>180:
                        rojo+=1
                    elif b<10 and g>180 and r>190:
                        amarillo+=1
        
            if  rojo > 1 and (rojo + blanco) > (negro + amarillo) and blanco > rojo and blanco > negro: 
                return "F"
            elif negro > 1 and (blanco + negro) > (amarillo + rojo) and blanco > negro:
                return "P"
            elif negro > 1 and (blanco + negro) > (amarillo + rojo): # b< 120 n <25
                return "C"
            elif amarillo > 1 and (rojo + amarillo) > (negro + blanco):
                return "O"   

