import face_recognition
import sqlite3
import pickle
import numpy as np

class FacialRecognitionModule:
    def __init__(self, db_path='training/criminals.db'):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_records = []
        self._load_known_faces()

    def _load_known_faces(self):
        self.cursor.execute('SELECT name, encodings, crime FROM criminals')
        for name, encoding_blob, crime in self.cursor.fetchall():
            encoding = pickle.loads(encoding_blob)
            self.known_face_encodings.append(encoding)
            self.known_face_names.append(name)
            self.known_face_records.append(crime)

    def recognize_face(self, frame):
        rgb_frame = frame[:, :, ::-1]  # BGR to RGB
        print("rgb_frame shape:", rgb_frame.shape, "dtype:", rgb_frame.dtype)

        face_locations = face_recognition.face_locations(rgb_frame)
        print("face_locations:", face_locations)
        print("face_locations type:", type(face_locations))
        if len(face_locations) > 0:
            print("face_locations[0] type:", type(face_locations[0]))
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        results = []
        for face_encoding, location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.6)
            name = "Unknown"
            record = "No record found"
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
                    record = self.known_face_records[best_match_index]
            results.append((name, record, location))
        return results


    def close(self):
        self.conn.close()
