import math
import utils as utils
import struct
import numpy as np
from point import Point
from image import ImageProcessor
from floor import Tile
from controller import Robot as WebotsRobot

import cv2


TIME_STEP = 16
MAX_VEL = 3.14 # Reduzco la velocidad para minimizar desvío

class Robot:
    def __init__(self):
        self.robot = WebotsRobot()

        self.emitter=self.robot.getDevice("emitter")
        
        self.wheelL = self.robot.getDevice("wheel1 motor") 
        self.wheelL.setPosition(float("inf"))

        self.wheelR = self.robot.getDevice("wheel2 motor") 
        self.wheelR.setPosition(float("inf"))

        self.lidar = self.robot.getDevice("lidar")
        self.lidar.enable(TIME_STEP)

        self.inertialUnit = self.robot.getDevice("inertial_unit")
        self.inertialUnit.enable(TIME_STEP)

        self.gps = self.robot.getDevice("gps")
        self.gps.enable(TIME_STEP)

        self.colorSensor = self.robot.getDevice("colour_sensor")
        self.colorSensor.enable(TIME_STEP)

        self.camI = self.robot.getDevice("camaraIzquierda")
        self.camI.enable(TIME_STEP)

        self.camD = self.robot.getDevice("camaraDerecha")
        self.camD.enable(TIME_STEP)

        self.imageProcessor = ImageProcessor()

        self.position = None
        self.rotation = 0
        self.rangeImage = None


        self.nroImagen = 0

        self.wheelL.setVelocity(0)
        self.wheelR.setVelocity(0)
        self.step()

    def step(self):
        result = self.robot.step(TIME_STEP)
        self.updateVars()
        return result
    
    def delay(self, ms):
        initTime = self.robot.getTime()
        while self.robot.step(TIME_STEP) != -1:
            if (self.robot.getTime() - initTime) * 1000.0 >= ms:
                break

    def updateVars(self):
        self.updatePosition()
        self.updateRotation()
        self.updateRangeImage()
        self.updateCapturarImage()
        print(f"Position: {self.position}, Rotation: {self.rotation:.3f} rad ({self.rotation*180/math.pi:.3f} deg)")
    
    def updatePosition(self):
        x, _, y = self.gps.getValues()
        self.position = Point(x, y)
        
    def updateRotation(self):
        _, _, yaw = self.inertialUnit.getRollPitchYaw()
        self.rotation = yaw % math.tau # Normalizamos el valor del ángulo (0 a 2*PI)

    def updateRangeImage(self):
        self.rangeImage = self.lidar.getRangeImage()[1024:1536]

    def convertirCamara(self, imagen, alto, ancho): #Convierte la imagen de la camara a una imagen de opencv
        return np.array(np.frombuffer(imagen, np.uint8).reshape((alto,ancho, 4)))

    def getCamImage(self, camera):
        img = camera.getImage()
        w = camera.getWidth()
        h = camera.getHeight()
        return self.convertirCamara(img, h, w)
    
    def updateCapturarImage(self):

        rightDist = self.rangeImage[128*3]
        if rightDist < 0.08:
            self.imageProcessor.analyze(self.getCamImage(self.camD))
            self.letterR = self.imageProcessor.victim_or_sign()
            if self.letterR != None:
                self.enviarMensajeVoC(self.letterR)
        else:
            return None

        leftDist = self.rangeImage[128]
        if leftDist < 0.08:
            self.imageProcessor.analyze(self.getCamImage(self.camI))
            self.letterL = self.imageProcessor.victim_or_sign()
            if self.letterL != None:
                self.enviarMensajeVoC(self.letterL)
        else:
            return None

    def updateCamImgBH_R(self):
        self.imageProcessor.analyze(self.getCamImage(self.camD))
        self.holeDR = self.imageProcessor.see_hole()

        if self.holeDR != None:
            return self.holeDR
    
    def updateCamImgBH_L(self):
        self.imageProcessor.analyze(self.getCamImage(self.camI))
        self.holeIZ = self.imageProcessor.see_hole()
        if self.holeIZ != None:
            return self.holeIZ

    def enviarMensaje(self, pos1, pos2, letra):
        let=bytes(letra, 'utf-8')
        mensaje=struct.pack("i i c", pos1, pos2, let)
        self.emitter.send(mensaje)

    def stop(self):
        self.wheelL.setVelocity(0)
        self.wheelR.setVelocity(0)

    def enviarMensajeVoC(self, letra):
        self.stop()
        self.delay(1500)
        self.enviarMensaje(int(self.position.x*100), int(self.position.y*100), letra)
        self.delay(100)

        self.record()
        
    def record(self):
        self.nroImagen+=1
        cv2.imwrite(f"CI{str(self.nroImagen).rjust(4,'0')}.png",self.convertirCamara(self.camI.getImage(), 64, 64))
        cv2.imwrite(f"CD{str(self.nroImagen).rjust(4,'0')}.png",self.convertirCamara(self.camD.getImage(), 64, 64))

    def bh_ahead(self):
        b, g, r, _ = self.colorSensor.getImage()
        tile = Tile(r, g, b)
        return tile.is_BH()

    def turn(self, rad):
        lastRot = self.rotation
        deltaRot = 0

        while self.step() != -1:
            deltaRot += utils.angle_diff(self.rotation, lastRot)
            lastRot = self.rotation

            diff = utils.angle_diff(deltaRot, abs(rad))

            mul = (5/math.pi) * diff
            mul = min(max(mul, 0.05), 1)

            if rad > 0:
                self.wheelL.setVelocity(mul*MAX_VEL)
                self.wheelR.setVelocity(-mul*MAX_VEL)
            else:
                self.wheelL.setVelocity(-mul*MAX_VEL)
                self.wheelR.setVelocity(mul*MAX_VEL)

            if diff <= 0.005:
                break

        self.wheelL.setVelocity(0)
        self.wheelR.setVelocity(0)

    def moveAhead(self, distance):
        initPos = self.position

        while self.step() != -1:
            diff = abs(distance) - initPos.distance_to(self.position)

            vel = min(max(diff/0.01, 0.1), 1)
            if distance < 0: vel *= -1
            
            self.wheelL.setVelocity(vel*MAX_VEL)
            self.wheelR.setVelocity(vel*MAX_VEL)

            if diff < 0.001:
                break
        
        self.stop()

    def smh_Left(self):
        leftDist = self.rangeImage[128]
        if leftDist < 0.08:
            return True
        else:
            return self.updateCamImgBH_L

    def smh_Right(self):
        rightDist = self.rangeImage[128*3]
        if rightDist < 0.08:
            return True
        else:
            return self.updateCamImgBH_R()

    def smh_Ahead(self):
        frontDist = self.rangeImage[256]
        if frontDist < 0.08:
            return True
        else:
            return self.bh_ahead()

    def rotateLeft90(self):
        self.turn(math.tau/4)

    def rotateRight90(self):
        self.turn(-math.tau/4)

    def turnAround(self):
        self.delay(500)
        self.rotateLeft90()
        self.stop()
        self.delay(500)
        self.rotateLeft90()
        self.stop()
        self.delay(500)

    def moveForwardTile(self):
        self.moveAhead(0.12)