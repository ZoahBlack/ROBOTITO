from src.image import ImageProcessor
import cv2

imageProcessor = ImageProcessor()

imageProcessor.analyze(cv2.imread("src\\CD0003.png"))

print(imageProcessor.see_hole())
