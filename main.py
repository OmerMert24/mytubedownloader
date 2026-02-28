import tkinter
import customtkinter
from pytubefix import YouTube
import os, certifi
os.environ["SSL_CERT_FILE"] = certifi.where()
import subprocess

def sanitize_filename(name: str) -> str:
    bad = '<>:"/\\|?*'
    for ch in bad:
        name = name.replace(ch, "")
    return name.strip()[:150]

def get_available_resolutions(ytObject):
    # Get unique resolutions from mp4 video-only streams
    streams = (ytObject.streams
               .filter(only_video=True, mime_type="video/mp4")
               .order_by("resolution")
               .desc())

    resolutions = []
    for s in streams:
        if s.resolution and s.resolution not in resolutions:
            resolutions.append(s.resolution)

    return resolutions

def pick_video_stream(ytObject, resolution: str):
    # Pick the best mp4 video-only stream at the chosen resolution (highest fps)
    return (ytObject.streams
            .filter(only_video=True, mime_type="video/mp4", res=resolution)
            .order_by("fps")
            .desc()
            .first())

def pick_audio_stream(ytObject):
    # Pick best m4a audio-only stream (highest abr)
    return (ytObject.streams
            .filter(only_audio=True, mime_type="audio/mp4")
            .order_by("abr")
            .desc()
            .first())

def download_with_resolution(ytObject, resolution: str):
    video_stream = pick_video_stream(ytObject, resolution)
    audio_stream = pick_audio_stream(ytObject)

    if video_stream is None:
        raise RuntimeError(f"No suitable video stream found for {resolution}.")
    if audio_stream is None:
        raise RuntimeError("No suitable audio stream found.")

    v_path = video_stream.download(filename="__video.mp4")
    a_path = audio_stream.download(filename="__audio.m4a")

    out_name = f"{sanitize_filename(ytObject.title)}_{resolution}.mp4"

    subprocess.run([
        "ffmpeg", "-y",
        "-i", v_path,
        "-i", a_path,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",
        "-c:a", "aac",
        "-b:a", "192k",
        out_name
    ], check=True)

    os.remove(v_path)
    os.remove(a_path)

def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize or 0
    if total_size == 0:
        return

    bytes_downloaded = total_size - bytes_remaining
    percentage = bytes_downloaded / total_size * 100
    per = str(int(percentage))

    progressPercentage.configure(text=per + "%")
    progressPercentage.update()
    progressBar.set(float(percentage) / 100)

def fetch_qualities():
    try:
        ytLink = link.get().strip()
        yt = YouTube(ytLink, on_progress_callback=on_progress)
        app.ytObject = yt  # cache it so we don't re-create it later

        title.configure(text=yt.title, text_color="white")
        finishLabel.configure(text="")

        qualities = get_available_resolutions(yt)
        if not qualities:
            raise RuntimeError("No MP4 video-only streams found for this video.")

        qualityBox.configure(values=qualities)
        qualityBox.set(qualities[0])  # default: highest available
        finishLabel.configure(text="Qualities loaded.", text_color="green")

    except Exception as e:
        finishLabel.configure(text=f"Error: {type(e).__name__}: {e}", text_color="red")

def startDownload():
    try:
        yt = getattr(app, "ytObject", None)
        ytLink = link.get().strip()

        # If user clicks Download without Fetch, create object anyway
        if yt is None:
            yt = YouTube(ytLink, on_progress_callback=on_progress)
            app.ytObject = yt
            title.configure(text=yt.title, text_color="white")

        selected_res = qualityBox.get().strip()
        if not selected_res or "Fetch" in selected_res:
            raise RuntimeError("Please fetch qualities and select one first.")

        finishLabel.configure(text="Downloading...", text_color="white")
        download_with_resolution(yt, selected_res)
        finishLabel.configure(text=f"Downloaded ({selected_res})!", text_color="green")

    except Exception as e:
        finishLabel.configure(text=f"Error: {type(e).__name__}: {e}", text_color="red")

# ---------------- UI ----------------
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

app = customtkinter.CTk()
app.geometry("720x480")
app.title("MyTube Downloader")

title = customtkinter.CTkLabel(app, text="Insert a YouTube link")
title.pack(padx=10, pady=10)

url_var = tkinter.StringVar()
link = customtkinter.CTkEntry(app, width=350, height=40, textvariable=url_var)
link.pack()

fetchBtn = customtkinter.CTkButton(app, text="Get Qualities", command=fetch_qualities)
fetchBtn.pack(padx=10, pady=10)

qualityBox = customtkinter.CTkComboBox(app, values=["(fetch qualities first)"], width=200)
qualityBox.set("(fetch qualities first)")
qualityBox.pack(padx=10, pady=10)

finishLabel = customtkinter.CTkLabel(app, text="")
finishLabel.pack()

progressPercentage = customtkinter.CTkLabel(app, text="%0")
progressPercentage.pack()

progressBar = customtkinter.CTkProgressBar(app, width=400)
progressBar.set(0)
progressBar.pack(padx=10, pady=10)

download = customtkinter.CTkButton(app, text="Download", command=startDownload)
download.pack(padx=10, pady=10)

app.mainloop()