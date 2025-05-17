import subprocess

class OutputModule:
    def speak(self, message):
        subprocess.run(["espeak", message])