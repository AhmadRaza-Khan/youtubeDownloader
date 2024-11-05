import os
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from yt_dlp import YoutubeDL

DOWNLOAD_DIRECTORY = os.path.expanduser("~/Downloads/YoutubeDownloads")

os.makedirs(DOWNLOAD_DIRECTORY, exist_ok=True)

def progress_hook(d):
    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes', 1)
        downloaded_bytes = d.get('downloaded_bytes', 0)

        percent = downloaded_bytes / total_bytes * 100
        progress_bar['value'] = percent

        downloaded_mb = downloaded_bytes / (1024 * 1024)
        speed = d.get('speed', 0) / (1024 * 1024)

        stats_label.config(text=f"Downloaded: {downloaded_mb:.2f} MB | Speed: {speed:.2f} MB/s | {percent:.2f}%")
        app.update_idletasks()

def download_media():
    url = url_entry.get()
    quality = quality_var.get()
    download_type = download_type_var.get()

    if not url:
        messagebox.showerror("Error", "Please enter a YouTube URL")
        return

    ydl_opts_info = {
        'format': 'bestaudio' if download_type == 'Audio' else quality,
        'noplaylist': True,
        'quiet': True,
    }

    try:
        with YoutubeDL(ydl_opts_info) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            title = info_dict.get('title', 'downloaded_file')
            ext = 'mp3' if download_type == 'Audio' else 'mp4'
            output_file = os.path.join(DOWNLOAD_DIRECTORY, f"{title}.{ext}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while extracting video info: {e}")
        return


    ydl_opts = {
        'format': 'bestaudio' if download_type == 'Audio' else quality,
        'outtmpl': output_file,
        'noplaylist': True,
        'progress_hooks': [progress_hook],
        'continuedl': True,
        'retries': 5,
    }


    progress_bar['value'] = 0
    stats_label.config(text=f"Downloading {download_type.lower()}...")
    download_button.config(state=tk.DISABLED)
    url_entry.config(state=tk.DISABLED)
    quality_menu.config(state=tk.DISABLED)
    download_type_menu.config(state=tk.DISABLED)

    threading.Thread(target=perform_download, args=(ydl_opts, url, title, ext, download_type)).start()

def perform_download(ydl_opts, url, title, ext, download_type):
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            messagebox.showinfo("Success", f"Download completed! Saved as {title}.{ext}")
            progress_bar['value'] = 100
            stats_label.config(text="Download completed!") 
    except Exception as e:

        stats_label.config(text="Requested format not found, trying to download best available format...")
        ydl_opts['format'] = 'bestaudio' if download_type == 'Audio' else 'best'
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                messagebox.showinfo("Success", f"Download completed! Saved as {title}.{ext}")
                progress_bar['value'] = 100
                stats_label.config(text="Download completed!") 
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while downloading: {e}")
    finally:
        download_button.config(state=tk.NORMAL)
        url_entry.config(state=tk.NORMAL)
        quality_menu.config(state=tk.NORMAL)
        download_type_menu.config(state=tk.NORMAL)


        url_entry.delete(0, tk.END)
        progress_bar['value'] = 0
        stats_label.config(text="")
        spinner_label.pack_forget()

def show_spinner():
    spinner_label.pack(pady=10)
    app.update_idletasks()

def hide_spinner():
    spinner_label.pack_forget()

app = tk.Tk()
app.title("YouTube Media Downloader")
app.geometry("400x600")
app.configure(bg="#000000")

title_label = tk.Label(app, text="YouTube Media Downloader", font=("Helvetica", 16, "bold"), bg="#000000", fg="#61dafb")
title_label.pack(pady=10)

name_label = tk.Label(app, text="Ahmad Raza Khan", font=("Helvetica", 12), bg="#000000", fg="#ffffff")
name_label.pack(pady=5)

url_label = tk.Label(app, text="YouTube URL:", font=("Helvetica", 12), bg="#000000", fg="#ffffff")
url_label.pack(pady=10)
url_entry = tk.Entry(app, width=50)
url_entry.pack(pady=5)

download_type_label = tk.Label(app, text="Download Type:", font=("Helvetica", 12), bg="#000000", fg="#ffffff")
download_type_label.pack(pady=10)

download_type_var = tk.StringVar(app)
download_type_var.set("Video")

download_type_menu = tk.OptionMenu(app, download_type_var, "Video", "Audio")
download_type_menu.config(bg="#ffffff", fg="#000000")
download_type_menu.pack(pady=5)

quality_label = tk.Label(app, text="Select Video Quality:", font=("Helvetica", 12), bg="#000000", fg="#ffffff")
quality_label.pack(pady=10)

quality_var = tk.StringVar(app)
quality_var.set("bestvideo+bestaudio")

quality_options = [
    "bestvideo+bestaudio",
    "worstvideo+bestaudio",
    "bestvideo[height<=720]+bestaudio",
    "bestvideo[height<=480]+bestaudio",
    "bestvideo[height<=360]+bestaudio",
]

quality_menu = tk.OptionMenu(app, quality_var, *quality_options)
quality_menu.config(bg="#ffffff", fg="#000000")
quality_menu.pack(pady=5)

download_button = tk.Button(app, text="Download", command=lambda: [show_spinner(), download_media()], bg="#61dafb", fg="#282c34", font=("Helvetica", 12))
download_button.pack(pady=20)

progress_bar = ttk.Progressbar(app, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=20)

stats_label = tk.Label(app, text="", font=("Helvetica", 10), bg="#000000", fg="#ffffff")
stats_label.pack(pady=10)

spinner_label = tk.Label(app, text="Downloading... Please wait...", font=("Helvetica", 12), bg="#000000", fg="#ffffff")
spinner_label.pack_forget()

app.mainloop()