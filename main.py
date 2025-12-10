import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from PIL import Image, ImageTk
import cv2
import csv
import json
import warnings
import time

# Suppress warnings for a clean demo
warnings.filterwarnings("ignore")

# ==============================================================================
#  CONFIGURATION
# ==============================================================================
API_KEY = "YOUR_API_KEY"
CSV_FILE = "my_expenses.csv"
# ==============================================================================

import google.generativeai as genai


class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Receipt Scanner & Expense Tracker")
        self.root.geometry("1100x800")
        self.root.configure(bg="#f0f2f5")

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)

        # --- Header ---
        header = tk.Frame(root, bg="white", pady=15, padx=20)
        header.pack(fill="x")
        tk.Label(header, text="🧾 AI Expense Automator", bg="white",
                 font=("Segoe UI", 16, "bold"), fg="#2ecc71").pack(side="left")

        # --- Main Layout ---
        main_frame = tk.Frame(root, bg="#f0f2f5", pady=20, padx=20)
        main_frame.pack(fill="both", expand=True)

        # Left Column: Camera
        self.left_col = tk.Frame(main_frame, bg="white", width=450, relief="flat", padx=10, pady=10)
        self.left_col.pack(side="left", fill="y", padx=(0, 20))
        self.left_col.pack_propagate(False)

        # Buttons
        btn_frame = tk.Frame(self.left_col, bg="white")
        btn_frame.pack(fill="x", pady=(0, 10))

        self.btn_cam = ttk.Button(btn_frame, text="🔴 Start Camera", command=self.toggle_camera)
        self.btn_cam.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.btn_upload = ttk.Button(btn_frame, text="📁 Upload Image", command=self.upload_image)
        self.btn_upload.pack(side="left", expand=True, fill="x", padx=(5, 0))

        self.btn_capture = tk.Button(self.left_col, text="SNAP RECEIPT & SAVE", bg="#2ecc71", fg="white",
                                     font=("Segoe UI", 11, "bold"), command=self.capture_frame, state="disabled")
        self.btn_capture.pack(fill="x", pady=(0, 10))

        self.lbl_image = tk.Label(self.left_col, text="Point Camera at Receipt\n(Or upload JPG/PNG)", bg="#eee",
                                  fg="#888", height=25)
        self.lbl_image.pack(fill="both", expand=True)

        # Right Column: Data Table
        right_col = tk.Frame(main_frame, bg="#f0f2f5")
        right_col.pack(side="left", fill="both", expand=True)

        self.lbl_status = tk.Label(right_col, text="Ready to scan...",
                                   bg="#f0f2f5", font=("Segoe UI", 12, "bold"), fg="#333", anchor="w")
        self.lbl_status.pack(fill="x", pady=(0, 10))

        # Table
        cols = ("Date", "Vendor", "Total", "Category")
        self.tree = ttk.Treeview(right_col, columns=cols, show="headings", height=20)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        self.tree.pack(fill="both", expand=True)

        # Initialize CSV if not exists
        if not os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "Vendor", "Total", "Category"])

        self.load_history()

        self.cap = None
        self.camera_active = False

    def load_history(self):
        # Clear current view
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Load from CSV
        if os.path.exists(CSV_FILE):
            try:
                with open(CSV_FILE, 'r') as f:
                    reader = csv.reader(f)
                    next(reader, None)  # Skip header
                    for row in reader:
                        if row: self.tree.insert("", 0, values=row)  # Insert at top
            except:
                pass

    # --- CAMERA ---
    def toggle_camera(self):
        if self.camera_active:
            self.stop_camera()
        else:
            self.start_camera()

    def start_camera(self):
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened(): raise Exception("No Webcam found")
            self.camera_active = True
            self.btn_cam.config(text="⬛ Stop")
            self.btn_capture.config(state="normal", bg="#2ecc71")
            self.update_video_stream()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def stop_camera(self):
        self.camera_active = False
        if self.cap: self.cap.release()
        self.btn_cam.config(text="🔴 Camera")
        self.btn_capture.config(state="disabled", bg="#cccccc")
        self.lbl_image.config(image='', text="Camera Stopped")

    def update_video_stream(self):
        if self.camera_active and self.cap:
            ret, frame = self.cap.read()
            if ret:
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                img.thumbnail((430, 550))
                imgtk = ImageTk.PhotoImage(image=img)
                self.lbl_image.imgtk = imgtk
                self.lbl_image.config(image=imgtk, text="")
                self.root.after(10, self.update_video_stream)

    def capture_frame(self):
        if self.cap and self.camera_active:
            ret, frame = self.cap.read()
            if ret:
                self.stop_camera()
                temp_path = "receipt_temp.jpg"
                cv2.imwrite(temp_path, frame)

                # Show static
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                img.thumbnail((430, 550))
                imgtk = ImageTk.PhotoImage(image=img)
                self.lbl_image.config(image=imgtk, text="")
                self.lbl_image.image = imgtk

                self.process_receipt(temp_path)

    def upload_image(self):
        # Restrict to Images Only to prevent PDF crash
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg;*.jpeg;*.png;*.webp")])
        if path:
            try:
                # Test opening it
                with Image.open(path) as img:
                    img.thumbnail((430, 550))
                    self.tk_img = ImageTk.PhotoImage(img)
                    self.lbl_image.config(image=self.tk_img, text="")
                self.process_receipt(path)
            except Exception:
                messagebox.showerror("File Error", "Cannot open file. Please upload an Image (JPG/PNG), not a PDF.")

    # --- AI LOGIC (WITH RETRY) ---
    def process_receipt(self, path):
        self.lbl_status.config(text="AI Extracting Data...", fg="orange")
        self.root.update()

        threading.Thread(target=self.ai_extraction, args=(path,), daemon=True).start()

    def ai_extraction(self, path):
        genai.configure(api_key=API_KEY)

        # Priority List: Try newest first, fallback to standard if Quota hit
        models_to_try = [
            'models/gemini-2.5-flash',
            'models/gemini-2.0-flash',
            'models/gemini-2.0-flash-lite',
            'models/gemini-1.5-flash'
        ]

        extracted_data = None
        success_model = ""

        try:
            with Image.open(path) as img:
                prompt = """
                You are a Financial Assistant. Analyze this receipt/bill image.
                Extract these fields strictly:
                1. Date (YYYY-MM-DD format)
                2. Vendor Name (e.g. Starbucks, Amazon, Uber)
                3. Total Amount (Number only, e.g. 150.00)
                4. Category (Food, Travel, Office, Shopping, Bills)

                Return valid JSON:
                { "date": "...", "vendor": "...", "total": "...", "category": "..." }
                """

                # --- RETRY LOOP ---
                for model_name in models_to_try:
                    try:
                        print(f"Attempting with {model_name}...")
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content([prompt, img])

                        # If successful, parse and break loop
                        text = response.text.replace("```json", "").replace("```", "").strip()
                        extracted_data = json.loads(text)
                        success_model = model_name
                        break

                    except Exception as e:
                        print(f"Model {model_name} failed: {e}")
                        # Only continue if it's a Quota/Limit error
                        if "429" in str(e) or "quota" in str(e).lower() or "404" in str(e):
                            continue
                        else:
                            break  # Stop on other errors (like file corrupt)

                if extracted_data:
                    # Save to CSV
                    with open(CSV_FILE, 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            extracted_data.get('date', '-'),
                            extracted_data.get('vendor', 'Unknown'),
                            extracted_data.get('total', '0'),
                            extracted_data.get('category', 'Other')
                        ])

                    self.root.after(0, self.load_history)
                    self.root.after(0, lambda: self.lbl_status.config(text=f"Saved! (via {success_model})", fg="green"))
                else:
                    self.root.after(0,
                                    lambda: self.lbl_status.config(text="Quota limit reached on all models.", fg="red"))

        except Exception as e:
            print(f"Critical Error: {e}")
            self.root.after(0, lambda: self.lbl_status.config(text="Extraction Failed.", fg="red"))


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)

    root.mainloop()
