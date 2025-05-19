import os
from imutils import paths
import face_recognition
import pickle
import cv2


def train_face_recognition_model(dataset_path="dataset", output_path="encodings.pickle"):
    print("[INFO] start processing faces...")
    imagePaths = list(paths.list_images(dataset_path))
    knownEncodings = []
    knownIds = []

    for (i, imagePath) in enumerate(imagePaths):
        print(f"[INFO] processing image {i + 1}/{len(imagePaths)}")
        criminal_id = imagePath.split(os.path.sep)[-2]
        
        image = cv2.imread(imagePath)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        boxes = face_recognition.face_locations(rgb, model="hog")
        encodings = face_recognition.face_encodings(rgb, boxes)
        
        for encoding in encodings:
            knownEncodings.append(encoding)
            knownIds.append(criminal_id)

    print("[INFO] serializing encodings...")
    data = {"encodings": knownEncodings, "ids": knownIds}
    with open(output_path, "wb") as f:
        f.write(pickle.dumps(data))

    print(f"[INFO] Training complete. Encodings saved to '{output_path}'")