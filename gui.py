import customtkinter as ctk
from tkinter import filedialog
from controller import process_files

selected_files = []
output_folder = ""
textbox = None
progress_bar = None


def log(message, tag="info"):
    textbox.insert("end", message + "\n", tag)
    textbox.see("end")
    textbox.update_idletasks()


def browse_files():
    global selected_files
    file_paths = filedialog.askopenfilenames(
        title="Select DMO files",
        filetypes=[("DMO files", "*.dmo"), ("All files", "*.*")]
    )

    textbox.delete("1.0", "end")
    progress_bar.set(0)

    if not file_paths:
        log("⚠️ No files selected.", "warning")
        return

    selected_files = list(file_paths)
    log(f"📂 Selected {len(selected_files)} files:", "success")
    for f in selected_files:
        log(f"   - {f}", "info")


def select_output_folder():
    global output_folder
    folder = filedialog.askdirectory(title="Select output folder")
    if folder:
        output_folder = folder
        log(f"📁 Output folder set to:\n{output_folder}", "success")
    else:
        log("⚠️ Output folder not selected.", "warning")


def start_processing():
    process_files(selected_files, output_folder, log, progress_bar)


def start_gui():
    global textbox, progress_bar

    ctk.set_appearance_mode("dark")

    root = ctk.CTk()
    root.title("DMO Header Editor")
    root.geometry("760x540")

    ctk.CTkLabel(root, text="Select DMO files to process:").pack(pady=5)
    ctk.CTkButton(root, text="📂 Select Files", command=browse_files).pack(pady=5)
    ctk.CTkButton(root, text="📁 Select Output Folder", command=select_output_folder).pack(pady=5)
    ctk.CTkButton(root, text="⚙️ Process Files", command=start_processing).pack(pady=5)
    ctk.CTkButton(root, text="❌ Quit", command=root.destroy).pack(pady=5)

    progress_bar = ctk.CTkProgressBar(root, width=600)
    progress_bar.pack(pady=10)
    progress_bar.set(0)

    textbox = ctk.CTkTextbox(root, width=720, height=300)
    textbox.pack(pady=10)

    textbox.tag_config("info", foreground="lightgray")
    textbox.tag_config("success", foreground="#57ff57")
    textbox.tag_config("warning", foreground="#ffcc00")
    textbox.tag_config("error", foreground="#ff5555")

    root.mainloop()