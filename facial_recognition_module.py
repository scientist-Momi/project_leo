# import face_recognition
# import sqlite3
# import pickle
# import numpy as np

import face_recognition
import cv2
import numpy as np
from picamera2 import Picamera2
import time
import pickle

class FacialRecognitionModule:
    def __init__(self, encodings_path="encodings.pickle", cv_scaler=4):
        self.cv_scaler = cv_scaler
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.frame_count = 0
        self.start_time = time.time()
        self.fps = 0

        print("[INFO] Loading encodings...")
        with open(encodings_path, "rb") as f:
            data = pickle.loads(f.read())
        self.known_face_encodings = data["encodings"]
        self.known_face_names = data["names"]
        print(f"[INFO] Loaded {len(self.known_face_names)} known faces")

        print("[INFO] Starting camera...")
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (1280, 960)}))
        self.picam2.start()

    def _calculate_fps(self):
        self.frame_count += 1
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 1:
            self.fps = self.frame_count / elapsed_time
            self.frame_count = 0
            self.start_time = time.time()
        return self.fps

    def _process_frame(self, frame):
        resized_frame = cv2.resize(frame, (0, 0), fx=(1/self.cv_scaler), fy=(1/self.cv_scaler))
        rgb_resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        self.face_locations = face_recognition.face_locations(rgb_resized_frame)
        self.face_encodings = face_recognition.face_encodings(rgb_resized_frame, self.face_locations, model='large')
        self.face_names = []

        for face_encoding in self.face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = self.known_face_names[best_match_index]
            self.face_names.append(name)
        return frame

    def _draw_results(self, frame):
        for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
            top *= self.cv_scaler
            right *= self.cv_scaler
            bottom *= self.cv_scaler
            left *= self.cv_scaler

            cv2.rectangle(frame, (left, top), (right, bottom), (244, 42, 3), 3)
            cv2.rectangle(frame, (left -3, top - 35), (right+3, top), (244, 42, 3), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, top - 6), font, 1.0, (255, 255, 255), 1)
        return frame

    def run(self):
        while True:
            frame = self.picam2.capture_array()
            processed_frame = self._process_frame(frame)
            display_frame = self._draw_results(processed_frame)
            current_fps = self._calculate_fps()
            cv2.putText(display_frame, f"FPS: {current_fps:.1f}", (display_frame.shape[1] - 150, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow('Video', display_frame)

            if cv2.waitKey(1) == ord("q"):
                break

        cv2.destroyAllWindows()
        self.picam2.stop()














    # def __init__(self, db_path='training/criminals.db'):
    #     self.conn = sqlite3.connect(db_path)
    #     self.cursor = self.conn.cursor()
    #     self.known_face_encodings = []
    #     self.known_face_names = []
    #     self.known_face_records = []
    #     self._load_known_faces()

    # def _load_known_faces(self):
    #     self.cursor.execute('SELECT name, encodings, crime FROM criminals')
    #     for name, encoding_blob, crime in self.cursor.fetchall():
    #         encoding = pickle.loads(encoding_blob)
    #         self.known_face_encodings.append(encoding)
    #         self.known_face_names.append(name)
    #         self.known_face_records.append(crime)

    # def recognize_face(self, frame):
    #     rgb_frame = frame[:, :, ::-1]  # BGR to RGB
    #     print("rgb_frame shape:", rgb_frame.shape, "dtype:", rgb_frame.dtype)

    #     face_locations = face_recognition.face_locations(rgb_frame)
    #     print("face_locations:", face_locations)
    #     print("face_locations type:", type(face_locations))
    #     if len(face_locations) > 0:
    #         print("face_locations[0] type:", type(face_locations[0]))
    #     face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    #     results = []
    #     for face_encoding, location in zip(face_encodings, face_locations):
    #         matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.6)
    #         name = "Unknown"
    #         record = "No record found"
    #         face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
    #         if len(face_distances) > 0:
    #             best_match_index = np.argmin(face_distances)
    #             if matches[best_match_index]:
    #                 name = self.known_face_names[best_match_index]
    #                 record = self.known_face_records[best_match_index]
    #         results.append((name, record, location))
    #     return results


    # def close(self):
    #     self.conn.close()
