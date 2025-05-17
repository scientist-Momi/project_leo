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
        self.camera = CameraModule(face_recognizer=self.face_recognizer, output=self.output)
        self.scanning = False

    def toggle_scan(self, enable):
        self.scanning = enable
        self.camera.face_recognizer = self.face_recognizer if enable else None
        if enable:
            self.camera.start()
            status = "Starting face scan..."
        else:
            self.camera.stop()
            status = "Stopping face scan."
        self.output.speak(status)

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
                if self.scanning:
                    self.camera.stop()
                break
            elif command == "SCAN":
                if not self.scanning:
                    self.toggle_scan(True)
            elif command == "STOP SCAN":
                if self.scanning:
                    self.toggle_scan(False)
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