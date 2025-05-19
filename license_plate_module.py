import cv2
import numpy as np
import pytesseract
from picamera2 import Picamera2
import time
import sqlite3

class BasicLicensePlateRecognition:
    def __init__(self, piCamera, resolution=(1280, 960), format='RGB888'):
        self.picam2 = piCamera
        # config = self.picam2.create_preview_configuration(main={"format": format, "size": resolution})
        # self.picam2.configure(config)
        self.window_name = "License Plate Recognition"
        self.running = False

    def preprocess_frame(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 50, 150)
        return edges, gray

    def find_plate_candidates(self, edges):
        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        candidates = []
        for contour in contours:
            approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = w / float(h)
                if 2 < aspect_ratio < 6 and w > 60 and h > 20:
                    candidates.append((x, y, w, h))
        return candidates

    def recognize_plate_text(self, frame, candidates):
        for (x, y, w, h) in candidates:
            roi = frame[y:y+h, x:x+w]
            gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray_roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            text = pytesseract.image_to_string(thresh, config='--psm 7')
            plate_number = ''.join(filter(str.isalnum, text)).strip()

            if plate_number:
                print(f"[INFO] Detected Text: {plate_number}")
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
                cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # === Lookup DB ===
                vehicle_info = self.get_vehicle_info(plate_number)
                if vehicle_info:
                    print(f"[MATCHED VEHICLE] {vehicle_info}")
                    # self.running = False
                    # cv2.destroyAllWindows()
                    # self.show_vehicle_info_gui(vehicle_info)
                else:
                    print(f"[INFO] Plate '{plate_number}' not found in database.")



    def start(self):
        self.picam2.start()
        time.sleep(2)
        self.running = True
        print("[INFO] Starting camera feed...")

        while self.running:
            frame = self.picam2.capture_array()
            edges, _ = self.preprocess_frame(frame)
            candidates = self.find_plate_candidates(edges)
            self.recognize_plate_text(frame, candidates)

            cv2.imshow(self.window_name, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.stop()

    def stop(self):
        print("[INFO] Stopping camera feed...")
        self.running = False
        self.picam2.stop()
        cv2.destroyAllWindows()


    def get_vehicle_info(self, plate_number):
        conn = sqlite3.connect("vehicles.db")
        c = conn.cursor()
        c.execute("SELECT * FROM vehicles WHERE plate_number = ?", (plate_number,))
        result = c.fetchone()
        conn.close()
        if result:
            return {
                "id": result[0],
                "plate_number": result[1],
                "owner": result[2],
                "make": result[3],
                "model": result[4],
                "status": result[5]
            }
        return None

if __name__ == "__main__":
    recognizer = BasicLicensePlateRecognition()
    recognizer.start()
