from src.image import ImageProcessor
import cv2

imageProcessor = ImageProcessor()

imageProcessor.analyze(cv2.imread("imgs\\CD0002 (2).png"))

print(imageProcessor.victima_o_cartel())
