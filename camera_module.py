import cv2
import time
import threading
from picamera2 import Picamera2

class CameraModule:
    def __init__(self, face_recognizer=None, output=None, resolution=(320, 240), format='RGB888'):
        self.picam2 = Picamera2()
        self.preview_config = self.picam2.create_preview_configuration(
            main={"format": format, "size": resolution}
        )
        self.picam2.configure(self.preview_config)
        self.window_name = "Pi Camera Feed"
        self.running = False
        self.thread = None
        self.face_recognizer = face_recognizer  
        self.output = output                    
        self.last_detected_name = None

    def start(self):
        if self.running:
            return  # Prevent multiple starts

        print("[INFO] Starting camera stream...")
        self.picam2.start()
        time.sleep(2)
        self.running = True
        self.thread = threading.Thread(target=self._stream)
        self.thread.start()
        print("[INFO] Camera stream started.")

    def _stream(self):
        while self.running:
            frame = self.picam2.capture_array()

            current_recognizer = self.face_recognizer  # get fresh reference
            if current_recognizer:
                results = current_recognizer.recognize_face(frame)
                for name, record, (top, right, bottom, left) in results:
                    # Draw bounding box (green for known, red for unknown)
                    color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                    # Display name above the box
                    cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    # Display record below the box
                    cv2.putText(frame, record, (left, bottom + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                    # Speak only if newly detected
                    if self.output and name != "Unknown" and name != self.last_detected_name:
                        self.output.speak(f"{name} detected. {record}")
                        self.last_detected_name = name
                if not results:
                    self.last_detected_name = None  # Reset if nothing detected

            cv2.imshow(self.window_name, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.stop()

    def stop(self):
        if not self.running:
            return

        print("[INFO] Stopping camera...")
        self.running = False
        self.thread.join()
        self.picam2.stop()
        cv2.destroyAllWindows()
        print("[INFO] Camera stream stopped.")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # def start(self):
    #     print("[INFO] Starting camera stream...")
    #     self.picam2.start()
    #     time.sleep(2)  # Allow camera to warm up
    #     print("[INFO] Camera stream started. Press 'q' to quit.")
    #     self._stream()

    # def _stream(self):
    #     while True:
    #         frame = self.picam2.capture_array()
    #         cv2.imshow(self.window_name, frame)

    #         key = cv2.waitKey(1) & 0xFF
    #         if key == ord('q'):
    #             break

    #     self._cleanup()

    # def _cleanup(self):
    #     print("[INFO] Stopping camera...")
    #     cv2.destroyAllWindows()
    #     self.picam2.stop()
    #     print("[INFO] Camera stream stopped.")