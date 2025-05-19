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
        self.face_recognizer.match_found = False
        self.face_recognizer.run()
        self.output.speak("Face scan ended.")
        self.scanning = False

    def run_license(self):
        self.output.speak("Starting license plate recognition...")
        self.license_reader.start()
        self.output.speak("A vehicle match was found. License plate recognition stopped.")
        self.license = False

    def stop_license(self):
        self.output.speak("Stopping license plate recognition...")
        self.license_reader.stop()
        self.output.speak("License plate recognition stopped.")

    def stop_scan(self):
        self.output.speak("Stopping face scanning...")
        self.face_recognizer.stop()
        self.output.speak("Face scanning stopped.")

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
                    if self.scanning:
                        self.stop_scan()
                    if self.license:
                        self.stop_license()
                    break
                elif command == "SCAN":
                    # if not self.scanning:
                    #     self.scanning = True
                    #     if self.license:
                    #         self.stop_license()
                    #         self.license = False
                    #     self.run_scan()
                    #     self.scanning = False
                    if not self.scanning:
                        if self.license:
                            self.face_recognizer.stop()
                            self.license = False
                        self.scanning = True
                        self.run_scan()
                elif command == "LICENCE":
                    if not self.license:
                        if self.scanning:
                            self.license_reader.stop()
                            self.scanning = False
                        self.license = True
                        self.run_license()
                elif command == "STOP LICENCE":
                    if self.license:
                        self.stop_license()
                        self.license = False
                else:
                    self.output.speak("Unknown command")
        except KeyboardInterrupt:
            self.output.speak("Keyboard interrupt received. Shutting down LEO.")
            if self.scanning:
                self.license_reader.stop()
            if self.license:
                self.face_recognizer.stop()

if __name__ == "__main__":
    leo = LEOSystem()
    leo.run()