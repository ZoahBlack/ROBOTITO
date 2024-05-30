import math
import utils as utils
import struct
import numpy as np
from point import Point
from image import ImageProcessor
from controller import Robot as WebotsRobot

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
        self.imageProcessor.analyze(self.getCamImage(self.camI))
        self.letraIZ = self.imageProcessor.victima_o_cartel()
        self.imageProcessor.analyze(self.getCamImage(self.camD))
        self.letraDR = self.imageProcessor.victima_o_cartel()
        
        if self.letraIZ != None:
            self.enviarMensajeVoC(self.letraIZ)
        elif self.letraDR != None:
            self.enviarMensajeVoC(self.letraDR)

    def enviarMensaje(self, pos1, pos2, letra):
        let=bytes(letra, 'utf-8')
        mensaje=struct.pack("i i c", pos1, pos2, let)
        self.emitter.send(mensaje)

    def parar(self):
        self.wheelL.setVelocity(0)
        self.wheelR.setVelocity(0)

    def enviarMensajeVoC(self, letra):
        self.parar()
        self.delay(1200)
        self.enviarMensaje(int(self.position.x*100), int(self.position.y*100), letra)

    def girar(self, rad):
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

    def avanzar(self, distance):
        initPos = self.position

        while self.step() != -1:
            diff = abs(distance) - initPos.distance_to(self.position)

            vel = min(max(diff/0.01, 0.1), 1)
            if distance < 0: vel *= -1
            
            self.wheelL.setVelocity(vel*MAX_VEL)
            self.wheelR.setVelocity(vel*MAX_VEL)

            if diff < 0.001:
                break
        
        self.wheelL.setVelocity(0)
        self.wheelR.setVelocity(0)

    def hayAlgoIzquierda(self):
        leftDist = self.rangeImage[128]
        return leftDist < 0.08

    def hayAlgoDerecha(self):
        rightDist = self.rangeImage[128*3]
        return rightDist < 0.08

    def hayAlgoAdelante(self):
        frontDist = self.rangeImage[256]
        return frontDist < 0.08

    def girarIzquierda90(self):
        self.girar(math.tau/4)

    def girarDerecha90(self):
        self.girar(-math.tau/4)

    def girarMediaVuelta(self):
        self.girar(math.tau/2)

    def avanzarBaldosa(self):
        self.avanzar(0.12)