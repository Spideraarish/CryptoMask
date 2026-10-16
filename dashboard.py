import os
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from access_controller import AccessController
from simulators import legitimate_process, ransomware_simulator, create_dummy_files

class DashboardEventHandler(FileSystemEventHandler):
    """Watchdog event handler to monitor raw file system changes."""
    def __init__(self, ui_callback):
        self.ui_callback = ui_callback

    def on_modified(self, event):
        if not event.is_directory:
            filename = os.path.basename(event.src_path)
            self.ui_callback(f"[WATCHDOG] Raw file modification detected on: {filename}", False, "yellow")

class ModernDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Cryptographic Access-Control Framework")
        
        # Make the window dynamic instead of fixed geometry to prevent cutting things off
        self.root.minsize(900, 600)
        self.root.configure(bg="#1E1E1E") # Modern dark background

        # Configure modern ttk styles (fixes macOS invisible button issue)
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TFrame", background="#1E1E1E")
        style.configure("TButton", font=("Helvetica", 12, "bold"), padding=10)
        
        # Dashboard Title
        title_label = tk.Label(
            root, 
            text="CRYPTOGRAPHIC ACCESS-CONTROL DASHBOARD", 
            font=("Helvetica", 20, "bold"), 
            bg="#1E1E1E", 
            fg="#4DA6FF" # Light blue, high visibility
        )
        title_label.pack(pady=20)

        # Main Content Frame
        content_frame = ttk.Frame(root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        # Log Terminal Window
        self.text_area = scrolledtext.ScrolledText(
            content_frame, 
            wrap=tk.WORD, 
            font=("Consolas", 14), 
            bg="#0D0D0D", # Very dark gray for console
            fg="#D4D4D4", # Light gray text
            insertbackground="white",
            height=15
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Configure high-visibility text tags
        self.text_area.tag_config("green", foreground="#00FF00", font=("Consolas", 14, "bold"))  # Legitimate
        self.text_area.tag_config("red", foreground="#FF3333", font=("Consolas", 14, "bold"))    # Ransomware Alert
        self.text_area.tag_config("blue", foreground="#4DA6FF")                                  # System Logs
        self.text_area.tag_config("yellow", foreground="#FFD700")                                # Watchdog events

        # Control Panel Buttons
        control_frame = ttk.Frame(root)
        control_frame.pack(pady=25)

        ttk.Button(control_frame, text="✅ Simulate Legitimate Process", command=self.run_legitimate).grid(row=0, column=0, padx=15)
        ttk.Button(control_frame, text="⚠️ Simulate Ransomware Attack", command=self.run_ransomware).grid(row=0, column=1, padx=15)
        ttk.Button(control_frame, text="📊 Run Entropy Benchmark Tests", command=self.run_entropy_tests).grid(row=0, column=2, padx=15)
        
        # Initialize Core Components
        self.controller = AccessController()
        create_dummy_files(self.controller.watch_dir)
        self.controller.register_callback(self.log_controller_event)
        
        # Initialize Watchdog to monitor the dummy files
        self.observer = Observer()
        event_handler = DashboardEventHandler(self.log_watchdog_event)
        self.observer.schedule(event_handler, path=self.controller.watch_dir, recursive=False)
        self.observer.start()

        self.log_system("=== SYSTEM INITIALIZATION COMPLETE ===")
        self.log_system("Cryptographic Access-Control Active.")
        self.log_system(f"Monitoring Directory: {os.path.abspath(self.controller.watch_dir)}")
        self.log_system("Ready. Please click the buttons below to test the framework.")

    def log_message(self, msg, tag="blue"):
        """Thread-safe logging to the text area."""
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, msg + "\n\n", tag) # Added extra newline for spacing and readability
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)

    def log_system(self, msg):
        self.log_message(msg, "blue")

    def log_watchdog_event(self, msg, is_alert, tag):
        self.root.after(0, self.log_message, msg, tag)

    def log_controller_event(self, msg, is_alert):
        tag = "red" if is_alert else "green"
        self.root.after(0, self.log_message, msg, tag)
        if is_alert:
            self.root.after(0, self.flash_alert)

    def flash_alert(self):
        """Briefly flashes the terminal to draw attention to an attack."""
        def toggle_bg(color, count):
            self.text_area.config(bg=color)
            if count > 0:
                next_color = "#330000" if color == "#0D0D0D" else "#0D0D0D"
                self.root.after(150, toggle_bg, next_color, count - 1)
            else:
                self.text_area.config(bg="#0D0D0D")
        toggle_bg("#330000", 4)

    def run_legitimate(self):
        self.log_system("[SYSTEM] Launching Legitimate Process...")
        threading.Thread(target=legitimate_process, args=(self.controller,)).start()

    def run_ransomware(self):
        self.log_system("[SYSTEM] Launching Ransomware Simulator...")
        threading.Thread(target=ransomware_simulator, args=(self.controller,)).start()

    def run_entropy_tests(self):
        self.log_system("[SYSTEM] Executing Mathematical Entropy Engine Tests (Running in background...)")
        import subprocess
        def run_tests():
            try:
                result = subprocess.run(["python", "entropy_engine.py"], capture_output=True, text=True)
                for line in result.stdout.split("\n"):
                    if line.strip():
                        self.root.after(0, self.log_message, f"  {line}", "blue")
            except Exception as e:
                self.root.after(0, self.log_message, f"[ERROR] {str(e)}", "red")
        threading.Thread(target=run_tests).start()

    def on_closing(self):
        self.observer.stop()
        self.observer.join()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernDashboard(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
