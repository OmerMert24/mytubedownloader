# mytubedownloader
mytubedownloader is a simple youtube video downloader. It downloads video with 1080p and merges with audio -using FFmpeg- in a mp4 file.

## Features
- Simple GUI
- Progress Percentage + Progress Bar

## Requirements
- python 3
- `tkinter` (usually included with Python on Windows)
- `customtkinter`
- `pytubefix`
- FFmpeg (installed and available in PATH)

## Installation
```bash
pip install pytubefix
pip install customtkinter
```

## FFmpeg check
```bash
ffmpeg -version

## Run
```bash
python main.py
```

## Notes
- Downloads 1080p video (itag 137/399) and audio (itag 140), then merges them into one MP4.
- Temporary files are deleted after merging.
