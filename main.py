import cv2
from voice_command_module import VoiceCommandModule
from output_module import OutputModule
from camera_module import CameraModule

class LEOSystem:
    def __init__(self):
        self.voice_command = VoiceCommandModule()
        self.output = OutputModule()
        self.camera = None

    # def open_camera(self):
    #     # Initialize the camera (0 for default USB webcam or Pi Camera)
    #     self.camera = cv2.VideoCapture(0)
    #     if not self.camera.isOpened():
    #         self.output.speak("Failed to open camera")
    #         return False

    #     self.output.speak("Camera opened")
    #     # Display the camera feed
    #     while True:
    #         ret, frame = self.camera.read()
    #         if not ret:
    #             self.output.speak("Failed to capture video")
    #             break

    #         cv2.imshow("LEO Camera", frame)
    #         # Press 'q' to quit the camera feed
    #         if cv2.waitKey(1) & 0xFF == ord('q'):
    #             break

    #     # Release the camera and close the window
    #     self.camera.release()
    #     cv2.destroyAllWindows()
    #     self.camera = None
    #     self.output.speak("Camera closed")
    #     return True

    def open_camera(self):
        try:
            # Use the PiCameraStreamer class to handle the camera
            self.camera = CameraModule()
            self.output.speak("Starting camera...")
            self.camera.start()
            
            # If we get here, it means the camera opened and is streaming
            return True
        except Exception as e:
            # Handle errors, in case something goes wrong with camera initialization
            self.output.speak(f"Failed to open camera: {e}")
            return False

    def run(self):
        self.output.speak("LEO ready")
        while True:
            command = self.voice_command.listen_for_command()
            if command is None:
                continue
            if command == "ERROR":
                self.output.speak("Speech recognition error")
                continue

            print(f"Processing command: {command}")
            if command == "OPEN CAMERA":
                self.open_camera()
            elif command == "LEO EXIT":
                self.output.speak("Shutting down LEO")
                break
            else:
                self.output.speak("Unknown command")

if __name__ == "__main__":
    leo = LEOSystem()
    leo.run()