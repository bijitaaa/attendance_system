import dlib
import cv2
import numpy as np
from django.conf import settings
detector = dlib.get_frontal_face_detector()
shape_predictor_path = settings.SHAPE_PREDICTOR_PATH
predictor = dlib.shape_predictor(shape_predictor_path)
face_rec_model = dlib.face_recognition_model_v1(settings.FACE_REC_MODEL_PATH)
def get_face_encoding_from_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    
    if len(faces) == 0:
        return None
    
    # Assume we take the first face detected
    face = faces[0]
    landmarks = predictor(gray, face)
    encoding = np.array(face_rec_model.compute_face_descriptor(frame, landmarks))
    return encoding
def match_face(encoding, database_encodings, threshold=0.6):
    best_match = None
    min_distance = float("inf")
    
    for db_encoding in database_encodings:
        distance = np.linalg.norm(encoding - np.frombuffer(db_encoding))
        print(f"comparing encodings: Distance = {distance}, Threshold = {threshold}")
        
        if distance < threshold and distance < min_distance:
            min_distance = distance
            best_match = db_encoding
            
    return best_match is not None