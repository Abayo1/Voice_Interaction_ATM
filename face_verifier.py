import cv2
from deepface import DeepFace
import numpy as np

class FaceVerifier:
    
    threshold = 11.55

    def detect_faces(self, image_path):
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        return faces, image

    def extract_face_embeddings(self, image_path):
        result = DeepFace.represent(image_path, model_name="Facenet")
        return np.array(result[0]['embedding'])

    def calculate_euclidean_distance(self, embedding1, embedding2):
        return np.linalg.norm(embedding1 - embedding2)

    def verify_faces(self, image1_path, image2_path):
        faces1, image1 = self.detect_faces(image1_path)
        faces2, image2 = self.detect_faces(image2_path)

        if len(faces1) == 0 and len(faces2) == 0:
            print("No faces detected in both images.")
            return False
        elif len(faces1) == 0:
            print("No faces detected in the first image.")
            return False
        elif len(faces2) == 0:
            print("No faces detected in the second image.")
            return False
        
        embedding1 = self.extract_face_embeddings(image1_path)
        embedding2 = self.extract_face_embeddings(image2_path)

        distance = self.calculate_euclidean_distance(embedding1, embedding2)
        print("Euclidean Distance between embeddings:", distance)

        if distance < self.threshold:
            return True
        else:
            return False

    @classmethod
    def set_threshold(cls, threshold):
        cls.threshold = threshold

    def verify_and_print_result(self, image1_path, image2_path):
        if self.verify_faces(image1_path, image2_path):
            print("Faces are verified as similar.")
        else:
            print("Faces are not verified as similar.")



