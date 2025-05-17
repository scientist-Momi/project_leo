from flask import Flask, request, jsonify, Response
import os
from picamera2 import Picamera2
import cv2
import face_recognition
import sqlite3
import pickle
import numpy as np
import time
import io
from PIL import Image

app = Flask(__name__)

# Directory to save captured images
IMAGE_DIR = "captured_images"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# Initialize the database
def init_db():
    conn = sqlite3.connect("criminals.db", timeout=10)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS criminals (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT,
                 age INTEGER,
                 description TEXT,
                 crime TEXT,
                 encodings BLOB
                 )""")
    conn.commit()
    conn.close()

init_db()

# Initialize the camera and face detection state
camera = None
captured_images = []
face_detected = False

def initialize_camera():
    global camera
    try:
        if camera is None:
            print("Initializing camera...")
            camera = Picamera2()
            camera.configure(camera.create_preview_configuration(main={"size": (640, 480)}))
            camera.start()
            time.sleep(2)  # Allow camera to warm up
            print("Camera initialized successfully")
            return True
        else:
            print("Camera already initialized")
            return True
    except Exception as e:
        print(f"Failed to initialize camera: {e}")
        camera = None
        return False

def close_camera():
    global camera
    try:
        if camera is not None:
            print("Closing camera...")
            camera.stop()
            camera = None
            print("Camera closed successfully")
    except Exception as e:
        print(f"Error closing camera: {e}")
        camera = None

def generate_frames():
    global camera, face_detected
    if not initialize_camera():
        print("Camera initialization failed, sending placeholder image")
        placeholder = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(placeholder, "Camera not available", (150, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        _, buffer = cv2.imencode('.jpg', placeholder)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        return

    while True:
        try:
            if camera is None:
                print("Camera became None during streaming, reinitializing...")
                if not initialize_camera():
                    break

            # Capture frame
            frame = camera.capture_array()
            if frame is None:
                print("Captured frame is None, reinitializing camera...")
                close_camera()
                continue

            # Convert to RGB for face detection
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            face_locations = face_recognition.face_locations(frame_rgb)
            face_detected = len(face_locations) > 0

            # Draw bounding boxes around detected faces
            for (top, right, bottom, left) in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            # Convert to JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            # Yield frame in MJPEG format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except Exception as e:
            print(f"Error capturing frame: {e}")
            close_camera()
            break

@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/check_face", methods=["GET"])
def check_face():
    global face_detected
    return jsonify({"face_detected": face_detected})

@app.route("/open_camera", methods=["GET"])
def open_camera():
    global camera
    try:
        if initialize_camera():
            return jsonify({"status": "success", "message": "Camera opened"})
        else:
            return jsonify({"status": "error", "message": "Failed to initialize camera"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/capture_single_image", methods=["GET"])
def capture_single_image():
    global camera, captured_images, face_detected
    if not initialize_camera():
        return jsonify({"status": "error", "message": "Camera not opened"})

    if not face_detected:
        return jsonify({"status": "error", "message": "No face detected"})

    try:
        # Capture a single frame
        image = camera.capture_array()
        image_path = os.path.join(IMAGE_DIR, f"criminal_{int(time.time())}_{len(captured_images)+1}.jpg")
        cv2.imwrite(image_path, image)
        captured_images.append(image_path)
        print(f"{image_path} written!")
        return jsonify({"status": "success", "image_path": image_path, "images_captured": len(captured_images)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/train_and_store", methods=["POST"])
def train_and_store():
    global camera, captured_images
    if not initialize_camera():
        return jsonify({"status": "error", "message": "Camera not opened"})

    try:
        # Get form data
        name = request.form["name"]
        age = int(request.form["age"])
        description = request.form["description"]
        crime = request.form["crime"]
        image_paths = request.form.getlist("image_paths[]")

        # Generate face encodings
        encodings = []
        for image_path in image_paths:
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)
            if face_encodings:
                encodings.append(face_encodings[0])

        if not encodings:
            return jsonify({"status": "error", "message": "No faces detected in the images"})

        # Average the encodings
        encoding = np.mean(encodings, axis=0)
        encoding_blob = pickle.dumps(encoding)

        # Store in database
        conn = sqlite3.connect("criminals.db", timeout=10)
        c = conn.cursor()
        c.execute("INSERT INTO criminals (name, age, description, crime, encodings) VALUES (?, ?, ?, ?, ?)",
                  (name, age, description, crime, encoding_blob))
        conn.commit()
        conn.close()

        # Clean up: close camera and delete images
        close_camera()
        for image_path in image_paths:
            if os.path.exists(image_path):
                os.remove(image_path)
        captured_images = []  # Reset the list

        return jsonify({"status": "success", "message": "Criminal data stored and model trained"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/")
def index():
    return app.send_static_file("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)