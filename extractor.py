import cv2
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tqdm import tqdm

class VideoExtractorGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Video Extractor")

        self.create_widgets()

    def create_widgets(self):
        self.label_video = ttk.Label(self.master, text="Video:")
        self.label_video.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.entry_video = ttk.Entry(self.master, width=40, state="readonly")
        self.entry_video.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.button_browse_video = ttk.Button(self.master, text="Durchsuchen", command=self.browse_video)
        self.button_browse_video.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.label_output = ttk.Label(self.master, text="Ausgabeordner:")
        self.label_output.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.entry_output = ttk.Entry(self.master, width=40, state="readonly")
        self.entry_output.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.button_browse_output = ttk.Button(self.master, text="Durchsuchen", command=self.browse_output)
        self.button_browse_output.grid(row=1, column=2, padx=5, pady=5, sticky="w")

        self.button_extract = ttk.Button(self.master, text="Extrahieren", command=self.extract_frames)
        self.button_extract.grid(row=2, column=0, columnspan=3, pady=10)

        self.progress_bar = ttk.Progressbar(self.master, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.grid(row=3, column=0, columnspan=3, pady=10)

    def browse_video(self):
        video_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi;*.mkv")])
        if video_path:
            self.entry_video.config(state="normal")
            self.entry_video.delete(0, "end")
            self.entry_video.insert(0, video_path)
            self.entry_video.config(state="readonly")

    def browse_output(self):
        output_folder = filedialog.askdirectory()
        if output_folder:
            self.entry_output.config(state="normal")
            self.entry_output.delete(0, "end")
            self.entry_output.insert(0, output_folder)
            self.entry_output.config(state="readonly")

    def extract_frames(self):
        video_path = self.entry_video.get()
        output_folder = self.entry_output.get()

        if video_path and output_folder:
            self.button_extract.config(state="disabled")

            # Öffne das Video
            cap = cv2.VideoCapture(video_path)

            # Stelle sicher, dass das Video erfolgreich geöffnet wurde
            if not cap.isOpened():
                print("Fehler beim Öffnen des Videos.")
                return

            # Erstelle den Ausgabeordner, wenn er nicht existiert
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            # Zähle die Frames im Video
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            # Extrahiere und speichere jedes Frame
            for frame_number in tqdm(range(total_frames), desc="Fortschritt", unit="Frames"):
                ret, frame = cap.read()

                # Überprüfe, ob das Lesen erfolgreich war
                if not ret:
                    print(f"Fehler beim Lesen von Frame {frame_number}.")
                    break

                # Speichere das Frame als Bild
                frame_path = os.path.join(output_folder, f"frame_{frame_number:04d}.jpg")
                cv2.imwrite(frame_path, frame)

                # Aktualisiere den Fortschrittsbalken
                progress_value = int((frame_number + 1) / total_frames * 100)
                self.progress_bar["value"] = progress_value
                self.master.update_idletasks()

            # Schließe das Video
            cap.release()

            print("Extraktion abgeschlossen.")
            self.button_extract.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoExtractorGUI(root)
    root.mainloop()
