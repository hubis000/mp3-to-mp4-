import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from moviepy.editor import AudioFileClip, ColorClip


def convert_audio_to_mp4(audio_path: str, output_path: str, resolution=(1280, 720)):
    """
    Převede zvukový soubor (M4A/MP3) na MP4 video s černým pozadím pomocí MoviePy.
    """
    # Načtení zvukové stopy
    audio_clip = AudioFileClip(audio_path)
    
    # Vytvoření černého pozadí o stejné délce, jako má zvuk
    video_clip = ColorClip(size=resolution, color=(0, 0, 0), duration=audio_clip.duration)
    video_clip = video_clip.set_audio(audio_clip)
    
    # Export do MP4 (AAC / H.264)
    video_clip.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        logger=None  # Skryje detailní výstup do konzole
    )
    
    # Uvolnění paměti a zavření souborů
    audio_clip.close()
    video_clip.close()


class MoviePyBatchApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MoviePy Batch Audio to MP4 Converter")
        self.geometry("620x430")
        self.resizable(False, False)

        self.audio_files = []
        self.output_dir_var = tk.StringVar()

        self._build_ui()

    def _build_ui(self):
        pad = {'padx': 10, 'pady': 6}

        # 1. Seznam vybraných souborů
        tk.Label(self, text="Vybrané soubory:").grid(row=0, column=0, sticky="nw", **pad)
        
        frame_list = tk.Frame(self)
        frame_list.grid(row=0, column=1, **pad)
        
        self.file_listbox = tk.Listbox(frame_list, width=45, height=7)
        self.file_listbox.pack(side="left", fill="y")
        
        scrollbar = tk.Scrollbar(frame_list, orient="vertical", command=self.file_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.file_listbox.config(yscrollcommand=scrollbar.set)

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=0, column=2, sticky="n", **pad)
        tk.Button(btn_frame, text="Přidat soubory...", command=self.browse_audio_files, width=14).pack(pady=2)
        tk.Button(btn_frame, text="Vyčistit seznam", command=self.clear_file_list, width=14).pack(pady=2)

        # 2. Volba cílové složky
        tk.Label(self, text="Cílová složka (volitelně):").grid(row=1, column=0, sticky="w", **pad)
        tk.Entry(self, textvariable=self.output_dir_var, width=45).grid(row=1, column=1, **pad)
        tk.Button(self, text="Procházet...", command=self.browse_output_dir, width=14).grid(row=1, column=2, **pad)

        # 3. Ukazatel průběhu (Progressbar)
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=590, mode="determinate")
        self.progress_bar.grid(row=2, column=0, columnspan=3, padx=10, pady=(20, 5))

        # 4. Stavový text
        self.status_label = tk.Label(self, text="Vyberte audio soubory (.m4a / .mp3) k převodu", fg="gray")
        self.status_label.grid(row=3, column=0, columnspan=3, pady=(0, 10))

        # 5. Tlačítko pro spuštění
        self.convert_btn = tk.Button(
            self, text="Spustit hromadný převod", command=self.start_batch_conversion,
            bg="#2196F3", fg="white", font=("Arial", 11, "bold"), height=2
        )
        self.convert_btn.grid(row=4, column=0, columnspan=3, sticky="we", padx=10, pady=5)

    def browse_audio_files(self):
        files = filedialog.askopenfilenames(
            title="Vyberte M4A nebo MP3 soubory",
            filetypes=[("Audio soubory", "*.m4a *.mp3"), ("Všechny soubory", "*.*")]
        )
        if files:
            for f in files:
                if f not in self.audio_files:
                    self.audio_files.append(f)
                    self.file_listbox.insert(tk.END, os.path.basename(f))
            self.status_label.config(text=f"Vybráno {len(self.audio_files)} souborů.", fg="black")

    def clear_file_list(self):
        self.audio_files.clear()
        self.file_listbox.delete(0, tk.END)
        self.status_label.config(text="Vyberte audio soubory (.m4a / .mp3) k převodu", fg="gray")

    def browse_output_dir(self):
        dir_path = filedialog.askdirectory(title="Vyberte složku pro uložení MP4")
        if dir_path:
            self.output_dir_var.set(dir_path)

    def start_batch_conversion(self):
        if not self.audio_files:
            messagebox.showerror("Chyba", "Vyberte prosím alespoň jeden audio soubor.")
            return

        out_dir = self.output_dir_var.get().strip() or None

        self.convert_btn.config(state="disabled")
        self.progress_bar["value"] = 0
        self.progress_bar["maximum"] = len(self.audio_files)

        # Spuštění ve vedlejším vlákně, aby GUI nezamrzlo
        threading.Thread(
            target=self._batch_worker,
            args=(list(self.audio_files), out_dir),
            daemon=True
        ).start()

    def _batch_worker(self, audio_files, out_dir):
        total = len(audio_files)
        errors = []

        for index, audio_path in enumerate(audio_files, start=1):
            filename = os.path.basename(audio_path)
            self.after(0, self._update_status, f"Převádění ({index}/{total}): {filename}")

            if out_dir:
                out_path = os.path.join(out_dir, os.path.splitext(filename)[0] + ".mp4")
            else:
                out_path = os.path.splitext(audio_path)[0] + ".mp4"

            try:
                convert_audio_to_mp4(audio_path, out_path)
            except Exception as e:
                errors.append((filename, str(e)))

            self.after(0, self._update_progress, index)

        self.after(0, self._on_batch_complete, total, errors)

    def _update_status(self, text):
        self.status_label.config(text=text, fg="blue")

    def _update_progress(self, val):
        self.progress_bar["value"] = val

    def _on_batch_complete(self, total, errors):
        self.convert_btn.config(state="normal")
        if not errors:
            self.status_label.config(text=f"Všech {total} souborů bylo úspěšně převedeno!", fg="green")
            messagebox.showinfo("Úspěch", f"Všech {total} souborů bylo převedeno na MP4!")
        else:
            success_count = total - len(errors)
            self.status_label.config(
                text=f"Dokončeno: {success_count}/{total} úspěšně.", fg="orange"
            )
            error_details = "\n".join([f"- {fname}: {msg[:90]}" for fname, msg in errors])
            messagebox.showwarning(
                "Dokončeno s chybami",
                f"Převedeno {success_count} z {total} souborů.\n\nChybové soubory:\n{error_details}"
            )


if __name__ == "__main__":
    app = MoviePyBatchApp()
    app.mainloop()
