import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import threading
import sqlite3
import random
import os
from image_capture import capture_photos  
from model_training import train_face_recognition_model  

class CriminalInfoForm(tk.Toplevel):
    def __init__(self, master, on_submit_callback):
        super().__init__(master)
        self.title("Enter Criminal Information")
        self.geometry("350x400")
        self.on_submit_callback = on_submit_callback

        self.entries = {}

        fields = [("Name", tk.Entry),
                  ("Age", tk.Entry),
                  ("Description", tk.Entry),
                  ("Offence", tk.Entry)]

        for label_text, widget_class in fields:
            tk.Label(self, text=label_text + ":").pack(anchor='w', padx=10)
            widget = widget_class(self)
            widget.pack(fill='x', padx=10, pady=5)
            self.entries[label_text.lower()] = widget

        # Dropdown for Status
        tk.Label(self, text="Status:").pack(anchor='w', padx=10)
        status_options = ["Arrested", "Wanted", "Released", "Under Investigation"]
        status_dropdown = ttk.Combobox(self, values=status_options, state='readonly')
        status_dropdown.current(0)
        status_dropdown.pack(fill='x', padx=10, pady=5)
        self.entries["status"] = status_dropdown

        tk.Button(self, text="Submit", command=self.submit).pack(pady=15)

    def submit(self):
        info = {k: v.get() for k, v in self.entries.items()}
        if not info["name"]:
            messagebox.showerror("Missing Info", "Name is required")
            return
        self.on_submit_callback(info)
        self.destroy()

class CarRegistrationForm(tk.Toplevel):
    def __init__(self, master, on_submit_callback):
        super().__init__(master)
        self.title("Register Vehicle")
        self.geometry("350x400")
        self.on_submit_callback = on_submit_callback

        self.entries = {}

        fields = [("Plate Number", tk.Entry),
                  ("Owner", tk.Entry),
                  ("Make", tk.Entry),
                  ("Model", tk.Entry)]

        for label_text, widget_class in fields:
            tk.Label(self, text=label_text + ":").pack(anchor='w', padx=10)
            widget = widget_class(self)
            widget.pack(fill='x', padx=10, pady=5)
            self.entries[label_text.lower().replace(" ", "_")] = widget

        # Dropdown for Status
        tk.Label(self, text="Status:").pack(anchor='w', padx=10)
        status_options = ["Verified", "Stolen", "Unregistered", "Under Investigation"]
        status_dropdown = ttk.Combobox(self, values=status_options, state='readonly')
        status_dropdown.current(0)
        status_dropdown.pack(fill='x', padx=10, pady=5)
        self.entries["status"] = status_dropdown

        tk.Button(self, text="Submit", command=self.submit).pack(pady=15)

    def submit(self):
        info = {k: v.get() for k, v in self.entries.items()}
        if not info["plate_number"]:
            messagebox.showerror("Missing Info", "Plate Number is required")
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
        self.init_vehicle_db()

        self.capture_button = tk.Button(root, text="Start Capture", command=self.prompt_criminal_info)
        self.capture_button.pack(pady=20)
        
        self.license_button = tk.Button(root, text="New License Plate", command=self.prompt_license_info)
        self.license_button.pack(pady=20)

        self.train_button = tk.Button(root, text="Train Model", command=self.train_model_prompt)
        self.train_button.pack(pady=20)

    def prompt_criminal_info(self):
        def on_form_submit(info):
            info["criminal_id"] = str(random.randint(100000, 999999))
            self.save_criminal_to_db(info) 
            self.name = info["name"]
            threading.Thread(target=self.capture_photos_thread, args=(info["criminal_id"],), daemon=True).start()

        CriminalInfoForm(self.root, on_form_submit)

    def prompt_license_info(self):
        def on_form_submit(info):
            self.save_vehicle_to_db(info)
            print(f"[INFO] Vehicle registered: {info['plate_number']} ({info['status']})")

        CarRegistrationForm(self.root, on_form_submit)



    def capture_photos_thread(self, criminal_id):
        try:
            capture_photos(criminal_id)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to capture photos: {e}")
        else:
            messagebox.showinfo("Done", f"Photos captured for {criminal_id}.")

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
                    criminal_id TEXT,
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
            INSERT INTO criminals (criminal_id, name, age, description, offence, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (info["criminal_id"], info["name"], info["age"], info["description"], info["offence"], info["status"]))
        conn.commit()
        conn.close()

    def init_vehicle_db(self):
        if not os.path.exists("vehicles.db"):
            conn = sqlite3.connect("vehicles.db")
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS vehicles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plate_number TEXT UNIQUE,
                    owner TEXT,
                    make TEXT,
                    model TEXT,
                    status TEXT
                )
            """)
            conn.commit()
            conn.close()

    def save_vehicle_to_db(self, info):
        conn = sqlite3.connect("vehicles.db")
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO vehicles (plate_number, owner, make, model, status)
            VALUES (?, ?, ?, ?, ?)
        """, (info["plate_number"], info["owner"], info["make"], info["model"], info["status"]))
        conn.commit()
        conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardApp(root)
    root.mainloop()
