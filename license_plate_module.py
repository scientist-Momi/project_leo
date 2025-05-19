import cv2
import numpy as np
import pytesseract
from picamera2 import Picamera2
import time
import sqlite3
from PIL import Image, ImageTk
import tkinter as tk

class BasicLicensePlateRecognition:
    def __init__(self, piCamera):
        self.picam2 = piCamera
        self.window_name = "License Plate Recognition"
        self.running = False
        self.matched_vehicle_info = None
        self.root = None
        self.current_gui = None 
        self.camera_started = False

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
                    self.matched_vehicle_info = vehicle_info
                    self.running = False  
                    cv2.destroyAllWindows() 
                    self.show_vehicle_info_gui(vehicle_info)
                    return True 
        return False 


    def start(self):
        # Initialize Tkinter root if not already done
        if self.root is None:
            self.root = tk.Tk()
            self.root.withdraw()  # Hide the root window

        # Set up the OpenCV window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        win_width = 1280
        win_height = 720
        win_x = (screen_width - win_width) // 2
        win_y = (screen_height - win_height) // 2

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, win_width, win_height)
        cv2.moveWindow(self.window_name, win_x, win_y)

        # Start the camera
        self.running = True
        if not self.camera_started:
            print("[INFO] Starting camera feed...")
            self.picam2.start()
            time.sleep(2)
            self.camera_started = True

        # Main loop for capturing frames
        while self.running:
            frame = self.picam2.capture_array()
            edges, _ = self.preprocess_frame(frame)
            candidates = self.find_plate_candidates(edges)
            match_found = self.recognize_plate_text(frame, candidates)

            if match_found:
                break  # Immediately exit loop

            cv2.imshow(self.window_name, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.stop()
                break

            if self.root:
                self.root.update()

    def stop_camera_and_windows(self):
        print("[INFO] Stopping camera feed...")
        self.running = False
        if self.camera_started:
            self.picam2.stop()
            self.camera_started = False
        cv2.destroyAllWindows()

    def stop(self):
        self.stop_camera_and_windows()
        # Close any open GUI windows and quit Tkinter
        if self.current_gui:
            self.current_gui.destroy()
            self.current_gui = None
        if self.root:
            self.root.destroy()
            self.root = None


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
    
    def show_vehicle_info_gui(self, vehicle_info):
        if self.root is None:
            self.root = tk.Tk()
            self.root.withdraw()

        win = tk.Toplevel(self.root)
        win.title("Vehicle Info Match")
        win.geometry("350x300")

        self.current_gui = win  # So it can be destroyed on stop()

        info = f"""
        Plate Number: {vehicle_info['plate_number']}
        Owner: {vehicle_info['owner']}
        Make: {vehicle_info['make']}
        Model: {vehicle_info['model']}
        Status: {vehicle_info['status']}
        """

        label = tk.Label(win, text=info.strip(), justify='left', font=('Arial', 12))
        label.pack(padx=20, pady=20)

        tk.Button(win, text="Close", command=win.destroy).pack(pady=10)

        # Ensure the GUI becomes visible
        win.update_idletasks()
        win.lift()
        win.focus_force()

if __name__ == "__main__":
    recognizer = BasicLicensePlateRecognition()
    recognizer.start()
