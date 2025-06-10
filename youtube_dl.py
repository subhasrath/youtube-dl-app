import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yt_dlp
import os
from threading import Thread

class YouTubeDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('Header.TLabel', font=('Arial', 16, 'bold'))
        
        # Main container
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(self.header_frame, text="YouTube Video Downloader", style='Header.TLabel').pack()
        ttk.Label(self.header_frame, text="For educational purposes only").pack()
        
        # URL Entry
        self.url_frame = ttk.Frame(self.main_frame)
        self.url_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.url_frame, text="YouTube URL:").pack(side=tk.LEFT)
        self.url_entry = ttk.Entry(self.url_frame, width=50)
        self.url_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Download Options
        self.options_frame = ttk.LabelFrame(self.main_frame, text="Download Options")
        self.options_frame.pack(fill=tk.X, pady=10)
        
        # Format Selection
        ttk.Label(self.options_frame, text="Format:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.format_var = tk.StringVar(value="best")
        self.format_combobox = ttk.Combobox(self.options_frame, textvariable=self.format_var, 
                                          values=["best", "1080p", "720p", "480p", "360p", "audio only"])
        self.format_combobox.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Output Path
        ttk.Label(self.options_frame, text="Save to:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.path_var = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        self.path_entry = ttk.Entry(self.options_frame, textvariable=self.path_var, width=40)
        self.path_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Button(self.options_frame, text="Browse", command=self.browse_directory).grid(row=1, column=2, padx=5)
        
        # Progress Frame
        self.progress_frame = ttk.LabelFrame(self.main_frame, text="Progress")
        self.progress_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.progress_text = tk.Text(self.progress_frame, height=15, wrap=tk.WORD)
        self.progress_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(self.progress_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.progress_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.progress_text.yview)
        
        # Button Frame
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(self.button_frame, text="Get Info", command=self.get_video_info).pack(side=tk.LEFT, padx=5)
        self.download_button = ttk.Button(self.button_frame, text="Download", command=self.start_download)
        self.download_button.pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Clear", command=self.clear_output).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Exit", command=root.quit).pack(side=tk.RIGHT, padx=5)
        
        # Status Bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.pack(fill=tk.X, pady=(5, 0))
        
        # Initialize downloader
        self.ydl_opts = {
            'quiet': False,
            'no_warnings': False,
            'ignoreerrors': True,
            'extract_flat': False,
        }
        
    def browse_directory(self):
        directory = filedialog.askdirectory(initialdir=self.path_var.get())
        if directory:
            self.path_var.set(directory)
    
    def log_message(self, message):
        self.progress_text.insert(tk.END, message + "\n")
        self.progress_text.see(tk.END)
        self.root.update()
    
    def clear_output(self):
        self.progress_text.delete(1.0, tk.END)
        self.status_var.set("Ready")
    
    def get_video_info(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
        
        self.clear_output()
        self.log_message(f"Fetching info for: {url}")
        
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info is None:
                    self.log_message("\nError: Could not retrieve video information.")
                    self.status_var.set("Error retrieving info")
                    return
                self.log_message("\nVideo Information:")
                self.log_message(f"Title: {info.get('title', 'N/A')}")
                self.log_message(f"Duration: {info.get('duration', 'N/A')} seconds")
                self.log_message(f"Views: {info.get('view_count', 'N/A')}")
                self.log_message(f"Uploader: {info.get('uploader', 'N/A')}")
                
                formats = info.get('formats', [])
                if formats:
                    self.log_message("\nAvailable Formats:")
                    for f in formats:
                        if f.get('vcodec') != 'none':
                            self.log_message(
                                f"ID: {f.get('format_id')} | "
                                f"Resolution: {f.get('height', 'N/A')}p | "
                                f"Extension: {f.get('ext', 'N/A')} | "
                                f"Size: {self.format_size(f.get('filesize'))}"
                            )
                self.status_var.set("Info retrieved successfully")
        except Exception as e:
            self.log_message(f"\nError: {str(e)}")
            self.status_var.set("Error retrieving info")
    
    def format_size(self, size_bytes):
        if not size_bytes:
            return "Unknown"
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
        
        download_thread = Thread(target=self.download_video, daemon=True)
        download_thread.start()
    
    def download_video(self):
        url = self.url_entry.get().strip()
        selected_format = self.format_var.get()
        output_path = self.path_var.get()
        
        self.clear_output()
        self.log_message(f"Starting download for: {url}")
        self.status_var.set("Downloading...")
        self.download_button.config(state=tk.DISABLED)
        
        try:
            ydl_opts = {
                **self.ydl_opts,
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
            }
            
            # Set format based on selection
            if selected_format == "audio only":
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            elif selected_format == "best":
                ydl_opts['format'] = 'bestvideo+bestaudio/best'
            else:
                ydl_opts['format'] = f'bestvideo[height<={selected_format[:-1]}]+bestaudio/best'
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            self.log_message("\nDownload complete!")
            self.status_var.set("Download complete")
        except Exception as e:
            self.log_message(f"\nError during download: {str(e)}")
            self.status_var.set("Download failed")
        finally:
            self.download_button.config(state=tk.NORMAL)
    
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', 'N/A')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            message = f"\rDownloading: {percent} at {speed} - ETA: {eta}"
            self.status_var.set(message)
        elif d['status'] == 'finished':
            self.status_var.set("Finalizing download...")

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()