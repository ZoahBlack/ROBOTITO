
#Realizar una función que dada la captura de un cartel, me devuelva None o la letra F (Flammable), P (Poison), C (Corrosive) o O (Organic Peroxide)

import cv2
import numpy as np

img = cv2.imread("img02.png")

def giro_cartel(imagen):
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    ret, thresh=cv2.threshold(gris, 140, 255, cv2.THRESH_BINARY)
    contornos, jerarquia = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    imagen = cv2.drawContours(imagen, contornos, -1, (0, 0, 255), 1)
    approx=cv2.minAreaRect(contornos[0])
    angulo=approx[2]

    if abs(angulo) == 45 and len(contornos) == 1:
        alto, ancho=thresh.shape[0], thresh.shape[1]
        M=cv2.getRotationMatrix2D((ancho/2,alto/2),angulo,1)
        thresh_rot=cv2.warpAffine(thresh,M,(ancho,alto))
        imagen_rot=cv2.warpAffine(imagen,M,(ancho,alto))
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
                    print("Blanco:", blanco)
                elif b<50 and g<50 and r<50:
                    negro+=1
                    print("Negro", negro)
                elif b>70 and g<10 and r>180:
                    rojo+=1
                    print("Rojo:", rojo)
                elif b<10 and g>180 and r>190:
                    amarillo+=1
                    print("Amarillo:", amarillo)

    if rojo == 0 and (blanco + negro) > (amarillo + rojo) and blanco > negro:
        return "P"   
    elif rojo > 1 and (rojo + blanco) > (negro + amarillo) and blanco > rojo: 
        return "F"
    elif (blanco + negro) > (amarillo + rojo) and negro > blanco: # b< 120 n <25
        return "C"
    elif amarillo > 1 and (rojo + amarillo) > (negro + blanco):
        return "O"
    
cartel = giro_cartel(img)
print(cartel)