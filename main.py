import cv2
from voice_command_module import VoiceCommandModule
from output_module import OutputModule
from camera_module import CameraModule
from facial_recognition_module import FacialRecognitionModule
from license_plate_module import BasicLicensePlateRecognition
from picamera2 import Picamera2

class LEOSystem:
    def __init__(self):
        self.piCamera = Picamera2()
        config = self.piCamera.create_preview_configuration(
            main={"format": 'XRGB8888', "size": (1280, 720)}
        )
        self.piCamera.configure(config)
        self.piCamera.start()
        self.voice_command = VoiceCommandModule()
        self.output = OutputModule()
        self.face_recognizer = FacialRecognitionModule(self.piCamera)
        self.license_reader = BasicLicensePlateRecognition(self.piCamera)
        self.scanning = False
        self.license = False

    def run_scan(self):
        self.output.speak("Starting face scan...")
        self.face_recognizer.run()
        self.output.speak("Face scan ended.")

    def run_license(self):
        self.output.speak("Starting license plate recognition...")
        self.license_reader.start()
        self.output.speak("License plate recognition ended")


    def run(self):
        self.output.speak("LEO is starting up")
        self.output.speak("LEO is ready")

        try:

            while True:
                command = self.voice_command.listen_for_command()
                if command is None:
                    continue
                if command == "ERROR":
                    self.output.speak("Speech recognition error")
                    continue

                print(f"Processing command: {command}")
                if command == "STOP":
                    self.output.speak("Shutting down LEO")
                    break
                elif command == "SCAN":
                    if not self.scanning:
                        self.scanning = True
                        self.run_scan()
                        self.scanning = False
                elif command == "LICENCE":
                    if not self.license:
                        self.license = True
                        self.run_license()
                        self.license = False
                else:
                    self.output.speak("Unknown command")
        except KeyboardInterrupt:
            self.output.speak("Keyboard interrupt received. Shutting down LEO.")
            if self.license:
                self.license_reader.stop()




























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