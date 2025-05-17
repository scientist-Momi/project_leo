import cv2
import time

def test_camera_with_gstreamer():
    print("Testing camera with GStreamer pipeline...")
    # GStreamer pipeline for libcamera
    pipeline = (
        "libcamerasrc ! "
        "video/x-raw, width=640, height=480, framerate=30/1 ! "
        "videoconvert ! "
        "appsink"
    )
    try:
        cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
        if not cap.isOpened():
            print("Failed to open camera with GStreamer: Could not initialize pipeline")
            return False

        print("Camera opened successfully with GStreamer")
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame with GStreamer")
                break

            cv2.imshow("Test Camera (GStreamer)", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        return True
    except Exception as e:
        print(f"GStreamer error: {e}")
        return False

def test_camera_with_v4l2():
    print("Testing camera with V4L2 (legacy stack)...")
    # Use V4L2 for legacy camera stack
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Failed to open camera with V4L2")
        return False

    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    # Allow camera to initialize
    time.sleep(2)

    print("Camera opened successfully with V4L2")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame with V4L2")
            break

        cv2.imshow("Test Camera (V4L2)", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return True

if __name__ == "__main__":
    # Try GStreamer first (libcamera stack)
    if not test_camera_with_gstreamer():
        print("GStreamer approach failed. Trying V4L2 (legacy stack)...")
        # Fallback to V4L2 if GStreamer fails
        test_camera_with_v4l2()