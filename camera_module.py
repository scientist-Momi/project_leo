import cv2
import time
from picamera2 import Picamera2

class CameraModule:
    def __init__(self, resolution=(640, 480), format='XRGB8888'):
        self.picam2 = Picamera2()
        self.preview_config = self.picam2.create_preview_configuration(
            main={"format": format, "size": resolution}
        )
        self.picam2.configure(self.preview_config)
        self.window_name = "Pi Camera Feed"

    def start(self):
        print("[INFO] Starting camera stream...")
        self.picam2.start()
        time.sleep(2)  # Allow camera to warm up
        print("[INFO] Camera stream started. Press 'q' to quit.")
        self._stream()

    def _stream(self):
        while True:
            frame = self.picam2.capture_array()
            cv2.imshow(self.window_name, frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

        self._cleanup()

    def _cleanup(self):
        print("[INFO] Stopping camera...")
        cv2.destroyAllWindows()
        self.picam2.stop()
        print("[INFO] Camera stream stopped.")