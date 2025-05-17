import speech_recognition as sr
import threading
import queue

class VoiceCommandModule:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone(sample_rate=16000)  # Matches earpiece's sample rate
        self.stop_event = threading.Event()
        self.command_queue = queue.Queue()

    def listen_for_command(self):
        self.stop_event.clear()
        thread = threading.Thread(target=self._listen_thread)
        thread.start()
        try:
            command = self.command_queue.get(timeout=10)
            return command
        except queue.Empty:
            return None

    def _listen_thread(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            print("Listening for command...")
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)
                if self.stop_event.is_set():
                    self.command_queue.put(None)
                    return
                command = self.recognizer.recognize_google(audio).upper()
                print(f"Heard: {command}")
                self.command_queue.put(command)
            except sr.UnknownValueError:
                self.command_queue.put(None)
            except sr.RequestError:
                print("Speech recognition service unavailable")
                self.command_queue.put("ERROR")

    def stop_listening(self):
        self.stop_event.set()