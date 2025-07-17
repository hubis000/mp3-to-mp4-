import os
import tkinter as tk
from tkinter import filedialog, messagebox
from moviepy.editor import AudioFileClip, ColorClip

def convert_mp3_to_mp4(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    for filename in os.listdir(input_folder):
        if filename.endswith(".mp3"):
            mp3_path = os.path.join(input_folder, filename)
            video_name = os.path.splitext(filename)[0] + ".mp4"
            output_path = os.path.join(output_folder, video_name)

            audio_clip = AudioFileClip(mp3_path)
            video_clip = ColorClip(size=(540, 360), color=(0, 0, 0), duration=audio_clip.duration)
            video_clip = video_clip.set_audio(audio_clip)

            video_clip.write_videofile(output_path, fps=24)

    messagebox.showinfo("Done", "All MP3 files have been converted to MP4 videos!")

def select_folders():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    input_folder = filedialog.askdirectory(title="Select Folder with MP3 Files")
    if not input_folder:
        return

    output_folder = filedialog.askdirectory(title="Select Output Folder for MP4 Videos")
    if not output_folder:
        return

    convert_mp3_to_mp4(input_folder, output_folder)

if __name__ == "__main__":
    select_folders()
