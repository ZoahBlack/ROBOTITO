import cv2
import numpy as np

def detectaLetras(imagen):
    imagen = cv2.imread(imagen)
 
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    
    ret, thresh = cv2.threshold(gris, 140, 255, cv2.THRESH_BINARY)

    contornos, jerarquia = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contornos) == 1 and len(contornos[0]) <= 10:

        approx = cv2.minAreaRect(contornos[0])
        angulo = approx[2]
        
        if angulo % 90 == 0:
            x = int(approx[0][0])
            y = int(approx[0][1])
            mitad_ancho = int(approx[1][0] / 2)
            mitad_alto = int(approx[1][1] / 2)

            rect = thresh[y - mitad_alto:y + mitad_alto, x - mitad_ancho:x + mitad_ancho]

            tamanio = rect.shape[0] * rect.shape[1]
            pixeles_negros = np.count_nonzero(rect == 0)
            porcentaje_negros = pixeles_negros / tamanio
            
            cuadrito_arriba = thresh[y - mitad_alto:y - int(mitad_alto / 3), x - int(mitad_ancho / 3):x + int(mitad_ancho / 3)]
            cuadrito_abajo = thresh[y + int(mitad_alto / 3):y + mitad_alto, x - int(mitad_ancho / 3):x + int(mitad_ancho / 3)]

            if np.count_nonzero(cuadrito_arriba == 0) / cuadrito_arriba.size < 0.2 and np.count_nonzero(cuadrito_abajo == 0) / cuadrito_abajo.size < 0.2:
                return "H"
            elif np.count_nonzero(cuadrito_arriba == 0) / cuadrito_arriba.size < 0.2 and np.count_nonzero(cuadrito_abajo == 0) / cuadrito_abajo.size >= 0.2:
                return "U"
            elif np.count_nonzero(cuadrito_arriba == 0) / cuadrito_arriba.size >= 0.2 and np.count_nonzero(cuadrito_abajo == 0) / cuadrito_abajo.size >= 0.2:
                return "S"

    return None

letra = detectaLetras('capturasSinOrdenar/CI0114.png')
if letra:
    print(f"La letra detectada es: {letra}")
else:
    print("No se detectó un cartel.")