import customtkinter as ctk
import tkinter as tk
import os
import subprocess
import ctypes

# --- Admin check ---
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# --- Command runner ---
def run_command(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        return result.stdout.strip() + result.stderr.strip()
    except Exception as e:
        return str(e)

# --- Service control ---
def stop_and_disable_service(service):
    log_message(f"Stopping service: {service} ...")
    run_command(f"sc stop {service}")
    app.after(3000, lambda: run_command(f"sc config {service} start= disabled"))
    log_message(f"Disabled service: {service}")
    update_status()

def enable_and_start_service(service):
    log_message(f"Enabling service: {service} ...")
    run_command(f"sc config {service} start= auto")
    run_command(f"sc start {service}")
    log_message(f"Started service: {service}")
    update_status()

def check_service_status(service):
    out = run_command(f"sc query {service}")
    starttype = run_command(f"sc qc {service}")

    running = "RUNNING" in out
    disabled = "DISABLED" in starttype
    return running, disabled

# --- Console log ---
def log_message(msg):
    console.configure(state="normal")
    console.insert("end", msg + "\n")
    console.configure(state="disabled")
    console.see("end")

# --- Panic (open chrome + exit) ---
def panic_action():
    log_message("⚠ PANIC BUTTON PRESSED ⚠")
    paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    ]
    for path in paths:
        if os.path.exists(path):
            subprocess.Popen([path])
            app.destroy()
            return
    log_message("Chrome not found at default paths.")

# --- Status update ---
def update_status():
    running, disabled = check_service_status("AristotleK12FilterService")

    if (not running) and disabled:
        status_frame.configure(fg_color="#6ECB63")  # green
        status_label.configure(text="Filter Disabled", text_color="white")
    else:
        status_frame.configure(fg_color="#D9534F")  # red
        status_label.configure(text="Filter Enabled", text_color="white")

# --- UI setup ---
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Simple Tool - Glass Style")
app.geometry("1000x650")

# Background panel
bg_frame = ctk.CTkFrame(app, fg_color="#F5F5F5", corner_radius=0)
bg_frame.pack(fill="both", expand=True)

# --- Admin warning ---
if not is_admin():
    warning_frame = ctk.CTkFrame(bg_frame, fg_color="#E6E6E6", corner_radius=15)
    warning_frame.pack(pady=20, padx=20, fill="x")
    ctk.CTkLabel(
        warning_frame,
        text="⚠ Please Run As Administrator for this Program to Work",
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color="red"
    ).pack(pady=(10,0))
    ctk.CTkLabel(
        warning_frame,
        text="To run as administrator: Right Click the Program and select Run As Administrator.",
        font=ctk.CTkFont(size=14),
        text_color="black"
    ).pack(pady=(0,10))

# --- Buttons frame ---
button_frame = ctk.CTkFrame(bg_frame, fg_color="#E6E6E6", corner_radius=20)
button_frame.pack(pady=20)

# Panic button (big & red)
panic_btn = ctk.CTkButton(
    button_frame, text="🚨 PANIC 🚨", command=panic_action,
    width=250, height=60, corner_radius=15,
    fg_color="#D9534F", hover_color="#C9302C", text_color="white", font=ctk.CTkFont(size=18, weight="bold")
)
panic_btn.pack(pady=12, padx=10)

# Other buttons
buttons = [
    ("Fix 1", lambda: stop_and_disable_service("AristotleK12FilterService")),
    ("Undo Fix 1", lambda: enable_and_start_service("AristotleK12FilterService")),
    ("Fix 2 (IN BETA)", lambda: (log_message("Fix 2 pressed!"), update_status())),
    ("Undo Fix 2 (IN BETA)", lambda: (log_message("Undo Fix 2 pressed!"), update_status())),
    ("Check Status", update_status),
]

for text, cmd in buttons:
    b = ctk.CTkButton(button_frame, text=text, command=cmd, width=200, height=40, corner_radius=12)
    b.pack(pady=6, padx=10)

# --- Status Box ---
status_frame = ctk.CTkFrame(bg_frame, fg_color="#AAAAAA", corner_radius=15)
status_frame.pack(pady=15, padx=20, fill="x")

status_label = ctk.CTkLabel(status_frame, text="Checking...", font=ctk.CTkFont(size=18, weight="bold"))
status_label.pack(pady=20)

ctk.CTkLabel(
    status_frame,
    text="Green = Filter Disabled, Red = Filter Enabled",
    font=ctk.CTkFont(size=14), text_color="white"
).pack(pady=(0,10))

# --- Console Box ---
console_frame = ctk.CTkFrame(bg_frame, fg_color="#E6E6E6", corner_radius=20)
console_frame.pack(pady=15, padx=20, fill="both", expand=True)

ctk.CTkLabel(console_frame, text="Console Log:", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=10, pady=(5,0))

console = ctk.CTkTextbox(console_frame, wrap="word", state="disabled", fg_color="#FFFFFF", corner_radius=10)
console.pack(fill="both", expand=True, padx=10, pady=10)

# --- Initial status check after 2 seconds ---
app.after(2000, update_status)

app.mainloop()
