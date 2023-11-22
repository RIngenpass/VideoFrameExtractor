import cv2
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
from tqdm import tqdm

class VideoExtractorGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Video Extractor V2")

        self.video_path = ""
        self.output_folder = ""
        self.video_length = 0

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

        self.label_start_time = ttk.Label(self.master, text="Extrahieren ab (Sekunden):")
        self.label_start_time.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.entry_start_time = ttk.Entry(self.master)
        self.entry_start_time.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        self.label_video_length = ttk.Label(self.master, text="Videolänge (Sekunden):")
        self.label_video_length.grid(row=3, column=0, padx=5, pady=5, sticky="w")

        self.label_video_length_value = ttk.Label(self.master, text="")
        self.label_video_length_value.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        self.button_extract = ttk.Button(self.master, text="Extrahieren", command=self.extract_frames)
        self.button_extract.grid(row=4, column=0, columnspan=3, pady=10)

        self.progress_bar_label = ttk.Label(self.master, text="Fortschritt:")
        self.progress_bar_label.grid(row=5, column=0, padx=5, pady=5, sticky="w")

        self.progress_bar = ttk.Progressbar(self.master, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.grid(row=5, column=1, columnspan=2, padx=5, pady=5, sticky="w")

        self.label_thumbnail = ttk.Label(self.master, text="Thumbnail:")
        self.label_thumbnail.grid(row=6, column=0, padx=5, pady=5, sticky="w")

        self.thumbnail_canvas = tk.Canvas(self.master, width=150, height=100)
        self.thumbnail_canvas.grid(row=7, column=0, columnspan=3, padx=5, pady=5)

    def browse_video(self):
        video_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi;*.mkv")])
        if video_path:
            self.video_path = video_path
            self.entry_video.config(state="normal")
            self.entry_video.delete(0, "end")
            self.entry_video.insert(0, video_path)
            self.entry_video.config(state="readonly")

            # Anzeige des Thumbnails, Ermittlung der Videolänge und Aktualisierung der Anzeige
            thumbnail, self.video_length = self.get_video_thumbnail_and_length(video_path)
            self.update_thumbnail(thumbnail)
            self.update_video_length_label()

    def get_video_thumbnail_and_length(self, video_path):
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        video_length = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
        cap.release()

        if ret:
            # Konvertiere das OpenCV-Frame in ein Pillow-Image und verkleinere es
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img.thumbnail((150, 100))
            thumbnail = ImageTk.PhotoImage(img)

            return thumbnail, video_length
        else:
            return None, 0

    def update_thumbnail(self, thumbnail):
        if thumbnail:
            self.thumbnail_canvas.config(width=thumbnail.width(), height=thumbnail.height())
            self.thumbnail_canvas.create_image(0, 0, anchor="nw", image=thumbnail)
            self.thumbnail_canvas.image = thumbnail
        else:
            self.thumbnail_canvas.config(width=150, height=100)
            self.thumbnail_canvas.create_text(75, 50, text="Kein Thumbnail verfügbar", anchor="center")

    def update_video_length_label(self):
        self.label_video_length_value.config(text=f"{self.video_length:.2f}")

    def browse_output(self):
        output_folder = filedialog.askdirectory()
        if output_folder:
            self.output_folder = output_folder
            self.entry_output.config(state="normal")
            self.entry_output.delete(0, "end")
            self.entry_output.insert(0, output_folder)
            self.entry_output.config(state="readonly")

    def extract_frames(self):
        start_time_str = self.entry_start_time.get()
        try:
            start_time = float(start_time_str)
        except ValueError:
            messagebox.showerror("Fehler", "Ungültige Eingabe für Startzeit. Bitte eine Zahl eingeben.")
            return

        if not (0 <= start_time <= self.video_length):
            messagebox.showerror("Fehler", "Die Startzeit liegt außerhalb des gültigen Bereichs.")
            return

        self.button_extract.config(state="disabled")

        # Öffne das Video
        cap = cv2.VideoCapture(self.video_path)

        # Stelle sicher, dass das Video erfolgreich geöffnet wurde
        if not cap.isOpened():
            print("Fehler beim Öffnen des Videos.")
            return

        # Springe zum ausgewählten Zeitpunkt im Video
        cap.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000.0)

        # Extrahiere und speichere jedes Frame
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        for frame_number in tqdm(range(total_frames), desc="Fortschritt", unit="Frames"):
            ret, frame = cap.read()

            # Überprüfe, ob das Lesen erfolgreich war
            if not ret:
                print(f"Fehler beim Lesen von Frame {frame_number}.")
                break

            # Speichere das Frame als Bild
            frame_path = os.path.join(self.output_folder, f"frame_{frame_number:04d}.jpg")
            cv2.imwrite(frame_path, frame)

            # Aktualisiere den Fortschrittsbalken
            progress_value = int((frame_number + 1) / total_frames * 100)
            self.progress_bar["value"] = progress_value
            self.master.update_idletasks()

        # Schließe das Video
        cap.release()

        print("Extraktion abgeschlossen.")
        self.button_extract.config(state="normal")

    def mainloop(self):
        self.master.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoExtractorGUI(root)
    root.mainloop()
