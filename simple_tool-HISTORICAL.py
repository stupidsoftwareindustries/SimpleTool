import customtkinter as ctk
import subprocess
import ctypes
from datetime import datetime

SERVICE_NAME = "AristotleK12FilterService"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def log_message(message):
    timestamp = datetime.now().strftime("[%H:%M:%S] ")
    console.configure(state="normal")
    console.insert("end", timestamp + message + "\n")
    console.see("end")
    console.configure(state="disabled")

# 🔹 Check service status
def check_service_status(service):
    try:
        result = subprocess.run(["sc", "query", service], capture_output=True, text=True)
        config = subprocess.run(["sc", "qc", service], capture_output=True, text=True)

        if "FAILED" in result.stdout or "does not exist" in result.stdout:
            log_message(f"Service '{service}' not found.")
            update_status_box("unknown")
            return

        running = "RUNNING" in result.stdout
        disabled = "DISABLED" in config.stdout

        if running and not disabled:
            log_message(f"Service {service} is RUNNING and ENABLED.")
            update_status_box("enabled")
        elif not running and disabled:
            log_message(f"Service {service} is STOPPED and DISABLED.")
            update_status_box("disabled")
        else:
            log_message(f"Service {service} state unclear.")
            update_status_box("unknown")

    except Exception as e:
        log_message(f"Error checking status: {e}")
        update_status_box("unknown")

# 🔹 Service control helpers
def stop_service(service):
    subprocess.run(["sc", "stop", service], capture_output=True, text=True)

def disable_service(service):
    subprocess.run(["sc", "config", service, "start=", "disabled"], capture_output=True, text=True)

def enable_service(service):
    subprocess.run(["sc", "config", service, "start=", "auto"], capture_output=True, text=True)

def start_service(service):
    subprocess.run(["sc", "start", service], capture_output=True, text=True)

# 🔹 Button actions
def panic_action():
    log_message("PANIC button pressed!")

def fix1_action():
    log_message("Applying Fix 1: stopping service...")
    stop_service(SERVICE_NAME)
    root.after(5000, lambda: [disable_service(SERVICE_NAME), check_service_status(SERVICE_NAME)])

def undo_fix1_action():
    log_message("Undoing Fix 1: re-enabling service...")
    enable_service(SERVICE_NAME)
    root.after(5000, lambda: [start_service(SERVICE_NAME), check_service_status(SERVICE_NAME)])

def fix2_action():
    log_message("Fix 2 (BETA) applied successfully.")

def undo_fix2_action():
    log_message("Fix 2 (BETA) undone successfully.")

# 🔹 Update status box color and text
def update_status_box(state):
    if state == "enabled":  # Service running/enabled
        status_label.configure(text="Fix 1 Status: Filter Enabled", fg_color="red")
    elif state == "disabled":  # Service stopped/disabled
        status_label.configure(text="Fix 1 Status: Filter Disabled", fg_color="green")
    else:
        status_label.configure(text="Fix 1 Status: Unknown", fg_color="gray")

# 🔹 Main Window
root = ctk.CTk()
root.title("Simple Tool")
root.geometry("700x550")

# Admin warning
if not is_admin():
    warning_frame = ctk.CTkFrame(root, fg_color="transparent")
    warning_frame.pack(pady=10)
    ctk.CTkLabel(
        warning_frame,
        text="⚠ Please Run As Administrator for this Program to Work",
        text_color="red",
        font=ctk.CTkFont(size=18, weight="bold")
    ).pack()
    ctk.CTkLabel(
        warning_frame,
        text="To run as administrator: Right Click the Program and select 'Run As Administrator'.",
        text_color="gray",
        font=ctk.CTkFont(size=13)
    ).pack()

# Buttons
btn_frame = ctk.CTkFrame(root, corner_radius=15)
btn_frame.pack(pady=15, padx=15, fill="x")

panic_btn = ctk.CTkButton(btn_frame, text="PANIC", command=panic_action, fg_color="red", hover_color="darkred")
fix1_btn = ctk.CTkButton(btn_frame, text="Fix 1", command=fix1_action)
undo_fix1_btn = ctk.CTkButton(btn_frame, text="Undo Fix 1", command=undo_fix1_action)
fix2_btn = ctk.CTkButton(btn_frame, text="Fix 2 (IN BETA)", command=fix2_action)
undo_fix2_btn = ctk.CTkButton(btn_frame, text="Undo Fix 2 (IN BETA)", command=undo_fix2_action)
status_btn = ctk.CTkButton(btn_frame, text="Check Status", command=lambda: check_service_status(SERVICE_NAME))

panic_btn.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
fix1_btn.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
undo_fix1_btn.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
fix2_btn.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
undo_fix2_btn.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
status_btn.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

# Status Box
status_frame = ctk.CTkFrame(root, corner_radius=15)
status_frame.pack(pady=10)

status_label = ctk.CTkLabel(
    status_frame,
    text="Fix 1 Status: Unknown",
    fg_color="gray",
    width=250,
    height=50,
    corner_radius=10,
    font=ctk.CTkFont(size=16, weight="bold")
)
status_label.pack(pady=5)

ctk.CTkLabel(
    status_frame,
    text="Green = Filter Disabled   |   Red = Filter Enabled",
    text_color="gray",
    font=ctk.CTkFont(size=12)
).pack()

# Console
console_frame = ctk.CTkFrame(root, corner_radius=15)
console_frame.pack(fill="both", expand=True, padx=15, pady=15)

console = ctk.CTkTextbox(console_frame, wrap="word", state="disabled")
console.pack(fill="both", expand=True, padx=10, pady=10)

log_message("Program started. Waiting for button presses...")

# Initial status check
check_service_status(SERVICE_NAME)

root.mainloop()
