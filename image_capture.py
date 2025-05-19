import cv2
import os
from datetime import datetime
from picamera2 import Picamera2
import time
import random

# Change this to the name of the person you're photographing
PERSON_ID = random.randint(100000, 999999) 

def create_folder(id):
    dataset_folder = "dataset"
    if not os.path.exists(dataset_folder):
        os.makedirs(dataset_folder)
    
    person_folder = os.path.join(dataset_folder, id)
    if not os.path.exists(person_folder):
        os.makedirs(person_folder)
    return person_folder

def capture_photos(id):
    folder = create_folder(id)
    
    # Initialize the camera
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (1280, 960)}))
    picam2.start()

    # Allow camera to warm up
    time.sleep(2)

    photo_count = 0
    
    print(f"Taking photos for {id}. Press SPACE to capture, 'q' to quit.")
    
    while True:
        # Capture frame from Pi Camera
        frame = picam2.capture_array()
        
        # Display the frame
        cv2.imshow('Capture', frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord(' '):  # Space key
            photo_count += 1
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{id}_{timestamp}.jpg"
            filepath = os.path.join(folder, filename)
            cv2.imwrite(filepath, frame)
            print(f"Photo {photo_count} saved: {filepath}")
        
        elif key == ord('q'):  # Q key
            break
    
    # Clean up
    cv2.destroyAllWindows()
    picam2.stop()
    print(f"Photo capture completed. {photo_count} photos saved for {id}.")

if __name__ == "__main__":
    capture_photos(PERSON_ID)