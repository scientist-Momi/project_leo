import sqlite3
import face_recognition
import cv2
import numpy as np
from picamera2 import Picamera2
import time
import pickle

class FacialRecognitionModule:
    def __init__(self, piCamera, encodings_path="encodings.pickle", cv_scaler=4):
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
        self.known_face_ids = data["ids"]
        print(f"[INFO] Loaded {len(self.known_face_ids)} known faces")

        print("[INFO] Starting camera...")
        self.picam2 = piCamera

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
        self.face_ids = []

        for face_encoding in self.face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            criminal_id = "Unknown"
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                criminal_id = self.known_face_ids[best_match_index]
            self.face_ids.append(criminal_id)

            if criminal_id != "Unknown":
                person_info = self.get_person_info(criminal_id)
                if person_info:
                    print(f"[MATCH] Found: {person_info}")
                else:
                    print(f"[INFO] ID matched but no record in DB for {criminal_id}")
            else:
                print("[INFO] Unknown face detected")
        return frame

    def _draw_results(self, frame):
        for (top, right, bottom, left), criminal_id in zip(self.face_locations, self.face_ids):
            top *= self.cv_scaler
            right *= self.cv_scaler
            bottom *= self.cv_scaler
            left *= self.cv_scaler

            cv2.rectangle(frame, (left, top), (right, bottom), (244, 42, 3), 3)
            cv2.rectangle(frame, (left -3, top - 35), (right+3, top), (244, 42, 3), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, criminal_id, (left + 6, top - 6), font, 1.0, (255, 255, 255), 1)
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


    def get_person_info(self, criminal_id):
        conn = sqlite3.connect("criminals.db")
        c = conn.cursor()
        c.execute("SELECT * FROM criminals WHERE criminal_id = ?", (criminal_id,))
        result = c.fetchone()
        conn.close()
        if result:
            return {
                "id": result[0],
                "criminal_id": result[1],
                "name": result[2],
                "age": result[3],
                "description": result[4],
                "offence": result[5],
                "status": result[6]
            }
        return None


