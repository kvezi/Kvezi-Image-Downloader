import platform
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import requests
from bs4 import BeautifulSoup
import os
import threading
import re
from urllib.parse import urlparse

class ImageDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kvezi Image Downloader")
        self.root.geometry("600x800")
        self.root.configure(bg='#000000')
        
        # Add the macOS specific code here
        if platform.system() == 'Darwin':  # macOS
            from tkinter import _tkinter
            try:
                root.createcommand('tk::mac::ReopenApplication', root.lift)
            except:
                pass

        # Configure style
        self.style = ttk.Style()
        self.create_custom_style()
        
        # Main container
        self.main_container = ttk.Frame(root, padding="20", style='Main.TFrame')
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            self.main_container, 
            text="Kvezi Image Downloader",
            style='Title.TLabel'
        )
        title_label.pack(pady=(0, 30))

        # URL Frame
        url_frame = ttk.Frame(self.main_container, style='Main.TFrame')
        url_frame.pack(fill=tk.X, pady=(0, 20))
        
        url_label = ttk.Label(url_frame, text="URL:", style='Header.TLabel')
        url_label.pack(anchor='w')
        
        self.url_entry = ttk.Entry(url_frame, style='Custom.TEntry')
        self.url_entry.pack(fill=tk.X, pady=(5, 0))

        # Save Path Frame
        path_frame = ttk.Frame(self.main_container, style='Main.TFrame')
        path_frame.pack(fill=tk.X, pady=(0, 20))
        
        path_label = ttk.Label(path_frame, text="Save to:", style='Header.TLabel')
        path_label.pack(anchor='w')
        
        self.path_entry = ttk.Entry(path_frame, style='Custom.TEntry')
        self.path_entry.pack(fill=tk.X, pady=(5, 0))
        self.path_entry.insert(0, os.path.expanduser("~/Downloads"))

        # Folder Name Frame
        folder_frame = ttk.Frame(self.main_container, style='Main.TFrame')
        folder_frame.pack(fill=tk.X, pady=(0, 30))
        
        folder_label = ttk.Label(folder_frame, text="Folder Name:", style='Header.TLabel')
        folder_label.pack(anchor='w')
        
        self.folder_entry = ttk.Entry(folder_frame, style='Custom.TEntry')
        self.folder_entry.pack(fill=tk.X, pady=(5, 0))
        self.folder_entry.insert(0, "downloaded_images")

        # Download Button
        self.download_btn = ttk.Button(
            self.main_container,
            text="Start",
            command=self.start_download,
            style='Download.TButton'
        )
        self.download_btn.pack(pady=(0, 30))

        # Progress Log Frame
        log_frame = ttk.LabelFrame(self.main_container, text="Progress logs:", padding="10", style='Log.TLabelframe')
        log_frame.pack(fill=tk.BOTH, expand=True)

        # Status Text Area
        self.status_area = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            font=('Helvetica', 10),
            wrap=tk.WORD,
            bg='#1c1c1e',
            fg='#ffffff'
        )
        self.status_area.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Progress Bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            log_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate',
            style='Custom.Horizontal.TProgressbar'
        )
        self.progress_bar.pack(fill=tk.X)

    def create_custom_style(self):
        """Create custom styles for widgets"""
        # Configure frame style
        self.style.configure('Main.TFrame', background='#000000')
        
        # Configure label styles
        self.style.configure(
            'Title.TLabel',
            font=('Helvetica', 24, 'bold'),
            padding=10,
            background='#000000',
            foreground='#ffffff'
        )
        self.style.configure(
            'Header.TLabel',
            font=('Helvetica', 12),
            background='#000000',
            foreground='#ffffff'
        )
        
        # Configure button style
        self.style.configure(
            'Download.TButton',
            font=('Helvetica', 14),
            padding=10,
            background='#ff3b30',
            foreground='#ffffff'
        )
        
        # Configure entry style
        self.style.configure(
            'Custom.TEntry',
            padding=10,
            fieldbackground='#1c1c1e',
            foreground='#ffffff'
        )
        
        # Configure progress bar
        self.style.configure(
            'Custom.Horizontal.TProgressbar',
            background='#32d74b',
            troughcolor='#1c1c1e'
        )
        
        # Configure log frame
        self.style.configure(
            'Log.TLabelframe',
            background='#000000',
            foreground='#ffffff'
        )
        self.style.configure(
            'Log.TLabelframe.Label',
            background='#000000',
            foreground='#ffffff'
        )

    def validate_url(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    def validate_inputs(self):
        valid = True
        
        # Validate URL
        if not self.validate_url(self.url_entry.get()):
            messagebox.showerror("Error", "Invalid URL format")
            valid = False
            
        # Validate path
        if not os.path.exists(os.path.dirname(self.path_entry.get())):
            messagebox.showerror("Error", "Invalid download path")
            valid = False
            
        # Validate folder name
        if not re.match("^[A-Za-z0-9_-]*$", self.folder_entry.get()):
            messagebox.showerror("Error", "Invalid folder name. Use only letters, numbers, underscore and hyphen")
            valid = False
            
        return valid

    def browse_path(self):
        directory = filedialog.askdirectory(initialdir=self.path_entry.get())
        if directory:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, directory)

    def log_message(self, message, level="info"):
        self.status_area.config(state=tk.NORMAL)
        tag = level.lower()
        if not tag in self.status_area.tag_names():
            if tag == "error":
                self.status_area.tag_configure(tag, foreground="red")
            elif tag == "success":
                self.status_area.tag_configure(tag, foreground="green")
            elif tag == "warning":
                self.status_area.tag_configure(tag, foreground="orange")
        
        self.status_area.insert(tk.END, f"{message}\n", (tag,))
        self.status_area.see(tk.END)
        self.status_area.config(state=tk.DISABLED)

    def download_images(self):
        if not self.validate_inputs():
            self.download_btn.config(state='normal')
            return
            
        url = self.url_entry.get()
        base_path = self.path_entry.get()
        folder_name = self.folder_entry.get()
        download_path = os.path.join(base_path, folder_name)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        }
        
        try:
            self.log_message("Starting download...", "info")
            self.log_message(f"Download path: {download_path}", "info")
            
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            img_tags = soup.find_all('img')
            total_images = len(img_tags)
            
            if total_images == 0:
                self.log_message("No images found!", "warning")
                return
                
            os.makedirs(download_path, exist_ok=True)
            
            for index, img in enumerate(img_tags, 1):
                try:
                    img_url = img['src']
                    if not img_url.startswith('http'):
                        img_url = url + img_url
                    
                    self.log_message(f"Downloading image {index}/{total_images}: {img_url}", "info")
                    img_data = requests.get(img_url, headers=headers).content
                    
                    filename = f"{download_path}/{img_url.split('/')[-1]}"
                    with open(filename, 'wb') as f:
                        f.write(img_data)
                    
                    progress = (index / total_images) * 100
                    self.progress_var.set(progress)
                    
                except Exception as e:
                    self.log_message(f"Failed to download: {str(e)}", "error")
                
            self.log_message("Download completed!", "success")
            messagebox.showinfo("Success", f"All images downloaded successfully!\nSaved to: {download_path}")
            
        except Exception as e:
            self.log_message(f"Error occurred: {str(e)}", "error")
            messagebox.showerror("Error", f"An error occurred during download: {str(e)}")
        
        finally:
            self.download_btn.config(state='normal')

    def start_download(self):
        self.download_btn.config(state='disabled')
        self.progress_var.set(0)
        self.status_area.config(state=tk.NORMAL)
        self.status_area.delete(1.0, tk.END)
        self.status_area.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.download_images)
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageDownloaderApp(root)
    root.mainloop()