import cv2
from voice_command_module import VoiceCommandModule
from output_module import OutputModule
from camera_module import CameraModule
from facial_recognition_module import FacialRecognitionModule

class LEOSystem:
    def __init__(self):
        self.voice_command = VoiceCommandModule()
        self.output = OutputModule()
        self.face_recognizer = FacialRecognitionModule()
        self.scanning = False

    def run_scan(self):
        self.output.speak("Starting face scan...")
        self.face_recognizer.run()
        self.output.speak("Face scan ended.")

    def run(self):
        self.output.speak("LEO is starting up")
        self.output.speak("LEO is ready")

        while True:
            command = self.voice_command.listen_for_command()
            if command is None:
                continue
            if command == "ERROR":
                self.output.speak("Speech recognition error")
                continue

            print(f"Processing command: {command}")
            if command == "QUIT":
                self.output.speak("Shutting down LEO")
                break
            elif command == "SCAN":
                if not self.scanning:
                    self.scanning = True
                    self.run_scan()
                    self.scanning = False
            else:
                self.output.speak("Unknown command")





























#     def open_camera(self):
#         try:
#             # Use the PiCameraStreamer class to handle the camera
#             self.camera = CameraModule()
#             self.output.speak("Starting camera...")
#             self.camera.start()
            
#             # If we get here, it means the camera opened and is streaming
#             return True
#         except Exception as e:
#             # Handle errors, in case something goes wrong with camera initialization
#             self.output.speak(f"Failed to open camera: {e}")
#             return False

#     def run(self):
#         self.output.speak("LEO ready")
#         while True:
#             command = self.voice_command.listen_for_command()
#             if command is None:
#                 continue
#             if command == "ERROR":
#                 self.output.speak("Speech recognition error")
#                 continue

#             print(f"Processing command: {command}")
#             # if command == "OPEN CAMERA":
#             self.open_camera()
#             if command == "LEO EXIT":
#                 self.output.speak("Shutting down LEO")
#                 break
#             else:
#                 self.output.speak("Unknown command")

if __name__ == "__main__":
    leo = LEOSystem()
    leo.run()