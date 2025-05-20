import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os, shutil

# === Custom Window Setup ===
# Create main application window with no title bar
app = tk.Tk()
app.overrideredirect(True)  # Disable default title bar
app.update_idletasks()

# Center the window on the screen
w, h = 400, 400
x = (app.winfo_screenwidth() // 2) - (w // 2)
y = (app.winfo_screenheight() // 2) - (h // 2)
app.geometry(f"{w}x{h}+{x}+{y}")
app.resizable(False, False)

# Window drag logic
x_offset = y_offset = 0

def start_move(event):
    global x_offset, y_offset
    x_offset, y_offset = event.x, event.y

def do_move(event):
    app.geometry(f"+{event.x_root - x_offset}+{event.y_root - y_offset}")

def close_window():
    app.destroy()

def minimize_window():
    app.overrideredirect(False)
    app.iconify()

def restore_window(event):
    app.overrideredirect(True)

def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_var.set(folder)

# Reapply custom title bar on restore
app.bind("<Map>", restore_window)

# === Title Bar Configuration ===
TITLE_COLOR = "#007fff"
HOVER_COLOR = "#005bb5"

title_bar = tk.Frame(app, bg=TITLE_COLOR, height=30)
title_bar.pack(fill="x")
title_bar.bind("<ButtonPress-1>", start_move)
title_bar.bind("<B1-Motion>", do_move)

# Application title label
tk.Label(
    title_bar,
    text="File Organizer",
    bg=TITLE_COLOR,
    fg="white",
    font=("Helvetica", 10, "bold")
).pack(side="left", padx=10)

# Hover effect for title bar buttons
def add_hover_effect(widget, normal_bg, hover_bg):
    widget.bind("<Enter>", lambda e: widget.config(bg=hover_bg))
    widget.bind("<Leave>", lambda e: widget.config(bg=normal_bg))

# Close button
close_btn = tk.Button(title_bar, text="✕", command=close_window, bd=0, bg=TITLE_COLOR, fg="white")
close_btn.pack(side="right")
add_hover_effect(close_btn, TITLE_COLOR, "#d32f2f")

# Help button
help_btn = tk.Button(
    title_bar, text="?", bd=0, bg=TITLE_COLOR, fg="white",
    command=lambda: messagebox.showinfo("Help", "1. Select a folder\n2. Choose file types\n3. Click 'Organize Files'")
)
help_btn.pack(side="right")
add_hover_effect(help_btn, TITLE_COLOR, HOVER_COLOR)

# Minimize button
minimize_btn = tk.Button(title_bar, text="━", command=minimize_window, bd=0, bg=TITLE_COLOR, fg="white")
minimize_btn.pack(side="right")
add_hover_effect(minimize_btn, TITLE_COLOR, HOVER_COLOR)

# === Main Application Frame ===
main_container = tk.Frame(app)
main_container.pack(fill="both", expand=True)

# Variables used by the program
folder_var = tk.StringVar()
move_var = tk.IntVar(value=1)
org_mode_var = tk.IntVar(value=1)
subfolders_var = tk.BooleanVar()
status_var = tk.StringVar()

# File categories and extensions
CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"],
    "Videos": [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv"],
    "Audio": [".mp3", ".wav", ".ogg", ".flac"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".xls", ".ppt", ".pptx"],
    "Compressed": [".zip", ".rar", ".7z", ".tar", ".gz"]
}

# Create a BooleanVar for each extension
ext_vars = {ext: tk.BooleanVar() for ext_list in CATEGORIES.values() for ext in ext_list}

# Tabs setup
notebook = ttk.Notebook(main_container)
main_frame = tk.Frame(notebook)
types_frame = tk.Frame(notebook)
notebook.add(main_frame, text="Main")
notebook.add(types_frame, text="File Types")
notebook.pack(expand=True, fill="both")

# === Folder Selection ===
folder_frame = tk.Frame(main_frame)
folder_frame.pack(fill="x", padx=10, pady=(15, 5))
tk.Label(folder_frame, text="Folder:").pack(side="left")
tk.Entry(folder_frame, textvariable=folder_var, width=30).pack(side="left", padx=(5, 0))
tk.Button(folder_frame, text="📁", command=select_folder).pack(side="left", padx=5)

# === Options Section ===
options_frame = tk.LabelFrame(main_frame, text="Options")
options_frame.pack(fill="x", padx=10, pady=5)
tk.Checkbutton(options_frame, text="Include subfolders", variable=subfolders_var).pack(anchor="w", padx=10, pady=2)

org_row = tk.Frame(options_frame)
org_row.pack(anchor="w", padx=10)
tk.Label(org_row, text="Organize by:").pack(side="left")
tk.Radiobutton(org_row, text="Category", variable=org_mode_var, value=1).pack(side="left", padx=5)
tk.Radiobutton(org_row, text="Extension", variable=org_mode_var, value=0).pack(side="left", padx=5)

action_row = tk.Frame(options_frame)
action_row.pack(anchor="w", padx=10)
tk.Label(action_row, text="Action:").pack(side="left")
tk.Radiobutton(action_row, text="Move", variable=move_var, value=1).pack(side="left", padx=5)
tk.Radiobutton(action_row, text="Copy", variable=move_var, value=0).pack(side="left", padx=5)

# Spacer
tk.Frame(main_frame, height=20).pack()

# Organize button
organize_btn = tk.Button(
    main_frame, text="Organize Files", height=2, width=50,
    bg=TITLE_COLOR, fg="white", font=("Helvetica", 10, "bold"),
    activebackground=HOVER_COLOR, activeforeground="white",
    command=lambda: organize_files()
)
organize_btn.pack(padx=10, pady=(5, 10))
add_hover_effect(organize_btn, TITLE_COLOR, HOVER_COLOR)

# Status label
status_label = tk.Label(main_frame, textvariable=status_var, anchor="w")
status_label.pack(anchor="w", padx=10, pady=(0, 10))

# === File Types Tab ===
tk.Label(types_frame, text="Select file types:").pack(anchor="w", padx=10, pady=(10, 0))
scroll_frame = tk.Frame(types_frame)
scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)
canvas = tk.Canvas(scroll_frame)
scrollbar = tk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)
container = tk.Frame(canvas)
canvas.create_window((0, 0), window=container, anchor="nw")
container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

group_check_vars = {}

def toggle_group(group):
    # Toggle all extensions in a group when the group is clicked
    value = group_check_vars[group].get()
    for ext in CATEGORIES[group]:
        ext_vars[ext].set(value)

# Generate group checkboxes and individual extension checkboxes
for group, exts in CATEGORIES.items():
    group_check_vars[group] = tk.BooleanVar()
    tk.Checkbutton(
        container, text=group, variable=group_check_vars[group],
        font=("Arial", 10, "bold"), command=lambda g=group: toggle_group(g)
    ).pack(anchor="w", pady=(10, 0), padx=5)
    for ext in sorted(exts):
        def update_group_state(e=ext, g=group):
            all_selected = all(ext_vars[x].get() for x in CATEGORIES[g])
            group_check_vars[g].set(all_selected)
        cb = tk.Checkbutton(container, text=ext, variable=ext_vars[ext], command=update_group_state)
        cb.pack(anchor="w", padx=25)

# === File Organization Logic ===
def organize_files():
    folder = folder_var.get()
    if not folder:
        status_var.set("Error: Please select a folder.")
        status_label.config(fg="red")
        return

    status_var.set("Processing...")
    status_label.config(fg="black")
    app.update_idletasks()

    try:
        count = 0
        exts_selected = [ext for ext, var in ext_vars.items() if var.get()]
        if not exts_selected:
            raise Exception("No file types selected.")

        walk = os.walk(folder) if subfolders_var.get() else [(folder, [], os.listdir(folder))]
        for dirpath, _, files in walk:
            for file in files:
                filepath = os.path.join(dirpath, file)
                if os.path.isfile(filepath):
                    ext = os.path.splitext(file)[1].lower()
                    if ext in exts_selected:
                        if org_mode_var.get() == 1:
                            for group, group_exts in CATEGORIES.items():
                                if ext in group_exts:
                                    target = os.path.join(folder, group)
                                    break
                            else:
                                target = os.path.join(folder, ext[1:])
                        else:
                            target = os.path.join(folder, ext[1:])

                        os.makedirs(target, exist_ok=True)
                        dest = os.path.join(target, file)
                        if move_var.get() == 1:
                            shutil.move(filepath, dest)
                        else:
                            shutil.copy2(filepath, dest)
                        count += 1

        status_var.set(f"Done. {count} files organized.")
        status_label.config(fg="green")

    except Exception as e:
        status_var.set(f"Error: {str(e)}")
        status_label.config(fg="red")

# Start the main loop
app.mainloop()