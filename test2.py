#! /usr/bin/python3

from picamera2 import Picamera2
import cv2
import time

# Initialize Picamera2
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()

# Give the camera time to warm up
time.sleep(2)

print("[INFO] Camera stream started. Press 'q' to quit.")

while True:
    # Capture a frame
    frame = picam2.capture_array()

    # Display the frame
    cv2.imshow("Pi Camera Feed", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

# Clean up
cv2.destroyAllWindows()
picam2.stop()
