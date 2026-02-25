import tkinter
import customtkinter
from pytubefix import YouTube
import os
import subprocess

def download_best_1080p(ytObject):
    video_stream = ytObject.streams.get_by_itag(137) or ytObject.streams.get_by_itag(399)
    audio_stream = ytObject.streams.get_by_itag(140)

    if video_stream is None or audio_stream is None:
        raise RuntimeError("No video or audio stream found.")

    v_path = video_stream.download(filename="__video.mp4")
    a_path = audio_stream.download(filename="__audio.m4a")

    out_name = f"{sanitize_filename(ytObject.title)}.mp4"

    subprocess.run(["ffmpeg", "-y", "-i", v_path, "-i", a_path, "-c", "copy", out_name],check=True)

    os.remove(v_path)
    os.remove(a_path)

def sanitize_filename(name: str) -> str:
    bad = '<>:"/\\|?*'
    for ch in bad:
        name = name.replace(ch, "")
    return name.strip()[:150]


def startDownload():
    try:
        ytLink = link.get().strip()
        ytObject = YouTube(ytLink, on_progress_callback=on_progress)

        title.configure(text=ytObject.title, text_color="white")
        finishLabel.configure(text="")

        # OLD: video = ytObject.streams.get_highest_resolution()
        # OLD: video.download()

        # NEW: download the best 1080p video with audio
        download_best_1080p(ytObject)

        finishLabel.configure(text="Downloaded (1080p)!", text_color="green")

    except Exception as e:
        finishLabel.configure(text=f"Hata: {type(e).__name__}", text_color="red")



    except:
        finishLabel.configure(text="Link is invalid.", text_color="red")


def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_compeletion = bytes_downloaded / total_size * 100
    per = str(int(percentage_of_compeletion))

    progressPercentage.configure(text=per + "%")
    progressPercentage.update()

    # update progress bar
    progressBar.set(float(percentage_of_compeletion) / 100)


# system settings
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

# our app frame
app = customtkinter.CTk()
app.geometry("720x480")
app.title("YouTube Downloader")

# adding ui elements
title = customtkinter.CTkLabel(app, text="Insert a YouTube link")
title.pack(padx=10, pady=10)

# link input
url_var = tkinter.StringVar()
link = customtkinter.CTkEntry(app, width=350, height=40, textvariable=url_var)
link.pack()

# finished downloading
finishLabel = customtkinter.CTkLabel(app, text="")
finishLabel.pack()

# progress percentage
progressPercentage = customtkinter.CTkLabel(app, text="%0")
progressPercentage.pack()

# progress bar
progressBar = customtkinter.CTkProgressBar(app, width=400)
progressBar.set(0)
progressBar.pack(padx=10, pady=10)

# download button
download = customtkinter.CTkButton(app, text="Download", command=startDownload)
download.pack(padx=10, pady=10)

# run app
app.mainloop()

