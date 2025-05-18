import tkinter as tk
from tkinter import simpledialog, messagebox
import threading
import sqlite3
import os
from image_capture import capture_photos  
from model_training import train_face_recognition_model  

class CriminalInfoForm(tk.Toplevel):
    def __init__(self, master, on_submit_callback):
        super().__init__(master)
        self.title("Enter Criminal Information")
        self.geometry("350x350")
        self.on_submit_callback = on_submit_callback

        # Input fields
        self.entries = {}
        fields = ["Name", "Age", "Description", "Offence", "Status"]
        for field in fields:
            label = tk.Label(self, text=field + ":")
            label.pack()
            entry = tk.Entry(self)
            entry.pack(fill='x', padx=10, pady=5)
            self.entries[field.lower()] = entry

        tk.Button(self, text="Submit", command=self.submit).pack(pady=10)

    def submit(self):
        info = {k: v.get() for k, v in self.entries.items()}
        if not info["name"]:
            messagebox.showerror("Missing Info", "Name is required")
            return
        self.on_submit_callback(info)
        self.destroy()

class DashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LEO Dashboard")
        self.root.geometry("300x200")

        self.name = None
        self.init_db()

        self.capture_button = tk.Button(root, text="Start Capture", command=self.prompt_criminal_info)
        self.capture_button.pack(pady=20)

        self.train_button = tk.Button(root, text="Train Model", command=self.train_model_prompt)
        self.train_button.pack(pady=20)

    def prompt_criminal_info(self):
        def on_form_submit(info):
            self.save_criminal_to_db(info)  # Save to SQLite
            self.name = info["name"]
            threading.Thread(target=self.capture_photos_thread, args=(self.name,), daemon=True).start()

        CriminalInfoForm(self.root, on_form_submit)

    def capture_photos_thread(self, name):
        try:
            capture_photos(name)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to capture photos: {e}")
        else:
            messagebox.showinfo("Done", f"Photos captured for {name}.")

    def train_model_prompt(self):
        confirm = messagebox.askyesno("Train Model", "Train the model now?")
        if confirm:
            threading.Thread(target=self.train_model_thread, daemon=True).start()

    def train_model_thread(self):
        try:
            train_face_recognition_model()
        except Exception as e:
            messagebox.showerror("Error", f"Training failed: {e}")
        else:
            messagebox.showinfo("Done", "Model training completed.")


    def init_db(self):
        if not os.path.exists("criminals.db"):
            conn = sqlite3.connect("criminals.db")
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS criminals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    age TEXT,
                    description TEXT,
                    offence TEXT,
                    status TEXT
                )
            """)
            conn.commit()
            conn.close()

    def save_criminal_to_db(self, info):
        conn = sqlite3.connect("criminals.db")
        c = conn.cursor()
        c.execute("""
            INSERT INTO criminals (name, age, description, offence, status)
            VALUES (?, ?, ?, ?, ?)
        """, (info["name"], info["age"], info["description"], info["offence"], info["status"]))
        conn.commit()
        conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardApp(root)
    root.mainloop()
