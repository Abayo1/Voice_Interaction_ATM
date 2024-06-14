import os
import cv2
import time

class ImageCapture:
    def __init__(self):
        self.camera = cv2.VideoCapture(0)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def capture_image(self):
        image_dir = "static"
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)
        image_path = os.path.join(image_dir, "captured_image.jpg")
        index = 0
        while os.path.exists(image_path):
            index += 1
            image_path = os.path.join(image_dir, f"captured_image_{index}.jpg")

        return_value, image = self.camera.read()
        if return_value:
            cv2.imwrite(image_path, image)
            print("Image captured:", image_path)
            return image_path
        else:
            print("Failed to capture image.")
            return None

    def check_faces(self, image_path):
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        return len(faces) > 0

    def stop_capture(self):
        self.camera.release()

    def __del__(self):
        self.camera.release()

