from tkinter import (PhotoImage,ttk,filedialog, messagebox)
from tkinter import *
import yt_dlp
from re import match,sub
import os
import json
import sys

# This class helps manage progress bar updates during download
class ProgressBar(ttk.Progressbar):
    def __init__(self, master, **kwargs):
        kwargs.setdefault("maximum", 100)
        value = kwargs.pop("value", 0)
        super().__init__(master=master, **kwargs)
        self["value"] = value

        self._percent_label = ttk.Label(master, text="0%", font=("Arial", 10))
    
    def show(self, relx, rely, anchor):
        """Displays the progress bar and percentage label 
           at the specified relx and rely positions."""
        self.place(relx=relx, rely=rely, anchor=anchor, ) 
        self._percent_label.place(relx=relx+0.20, rely=rely, anchor="center")   

    def update_value(self, percent):
        """Updates the progress bar based on a value received from a hook function."""
        if percent >= 100:
            self["value"] = 100
            self._percent_label.config(text="100")
            self.after(2000, self.place_forget)
            self._percent_label.after(2000, self._percent_label.place_forget)
        else:
            self["value"] = percent
            self._percent_label.config(text=f"{percent:.1f}%")
            self.update_idletasks()
        
    def progress_hook(self):
        """Returns a hook function that track download progress."""
        def hook(d):
            if d['status'] == "downloading":
                total = d.get('total_bytes_estimate') or d.get('total_bytes')
                downloaded = d.get("downloaded_bytes", 0)
                if total:
                    percent = (downloaded / total) * 100
                    self.update_value(percent)
            elif d["status"] == "finished":
                self.update_value(100)                
        return hook 

def toggle_other_combobox(option, target_combobox, event=None):
    """Disable the target combobox if the selected value 
       of the other combobox is different from "Select"."""
    option = str(option.get())     
    state = "disabled" if option != "Select" else "readonly"
    target_combobox.config(state=state)
    return 

def display_button(root, event, entry):
    """Create a copy and paste menu that appears when a 
       right-click mouse is detected on any of the entries."""
    context_menu = Menu(root, tearoff=0)
      
    def copy():
        """Copy text from link and download directory input fields."""
        text = entry.get()
        root.clipboard_clear()
        root.clipboard_append(text)
           
    def paste():
        """Pastes previously copied text into the appropriate input field."""       
        text = root.clipboard_get()  
        entry.delete(0, "end")
        entry.insert(0, text)
  
    context_menu.add_command(label="Copy", command=copy)
    context_menu.add_command(label="Paste", command=paste)
    context_menu.tk_popup(event.x_root, event.y_root)
    context_menu.grab_release()
    context_menu.after(2000, context_menu.destroy)
    return                   
                              
def show_status(label, message, root):
    """Change warning texts that are shown for users"""
    label.config(text=message)
    root.update()
    return 

def get_config_path():
    """Set config file path to user documents folder"""
    config_dir = os.path.join(os.path.expanduser("~"), "Documents")
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, ".config.json") 

def load_default_directory():
    """Load a saved download directory in the config file."""
    config_path = get_config_path()   
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            configs = json.load(f)
            return configs.get("default_directory")
    else:
        return os.path.join(os.path.expanduser("~"), "Downloads")
      
def update_default_directory(download_path):
    """Update the default directory in the config file 
       when a change is made to the download path StringVar"""
    dl_path = str(download_path.get())
    config_path = get_config_path()

    if os.path.exists(dl_path):
        with open(config_path, 'w') as f:
            json.dump({"default_directory": dl_path}, f)
    return     

def ask_download_directory(download_path):
    """Open a download directory select window."""
    dirname = filedialog.askdirectory()
    if dirname:
        download_path.set(dirname)
    return 
   
def is_valid_url(url):
    """Validate the youtube link"""
    youtube_regex = r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]{11}$'
    return match(youtube_regex, url) is not None

def file_name(download_path,url, ext):
    """Build the file name and verify if it already 
       exist, if so, add a number to the file name"""
    with yt_dlp.YoutubeDL() as yt:
        info = yt.extract_info(url, download=False)
        title = sub(r'[\\/*?:"<>|]', "", info["title"])
        title = sub(r'_+', "_", title)
        
    default_name = f"{title}.{ext}"  
    full_path = os.path.normpath(os.path.join(download_path, default_name))
    if not os.path.exists(full_path):
        return title   
    i = 1  
    while True:
        alt_name = f"{title}.({i}).{ext}"
        full_path = os.path.normpath(os.path.join(download_path, alt_name))
        if not os.path.exists(full_path):
            return f"{title}.({i})"
        i+=1    

def download_format(video_opt, audio_opt):
    """Change download format based on audio/video menu selection"""
    if video_opt != "Select":
        return f'bestvideo[ext=mp4][height<={video_opt}]+bestaudio', False
    elif audio_opt != "Select": 
        return f'bestaudio[ext=m4a][abr<={audio_opt}]', True
    else:
        return None, None
   
def download(link, download_path, quality_video, quality_audio, warning_label, root):
    """Function to download the video or audio file"""
    url = str(link.get())

    if not url or not is_valid_url(url): # Verify if the url is valid
        messagebox.showerror("Error", "Inform a valid link!")
        return
    
    dl_path = str(download_path.get())
    if not dl_path or not os.path.isdir(dl_path): # Verify if the download path exist
        messagebox.showerror("Error", "Invalid download directory!")
        return
    
    video_opt = str(quality_video.get()).strip('p')
    audio_opt = str(quality_audio.get()).strip('kbps')

    format, only_audio = download_format(video_opt, audio_opt) # Receive download format and if its only audio
   
    if not format:
        messagebox.showerror("Error", "Select a video or audio option!")
        return
    
    try:
        show_status(warning_label,"Starting download...", root)
        download_bar = ProgressBar(root, orient="horizontal", length=200, mode="determinate")
        download_bar.show(relx=0.28, rely=0.80, anchor="center")
                      
        #ffmpeg_path = resource_path("ffmpeg/ffmpeg")
        # The line above take the path of ffmpeg binary located in "ffmpeg/ffmpeg" folder
        
        # If "only_audio" is True, "ext" var receive "mp3", if not, "mp4"
        # I'm using this to verify later if the file name that will be downloaded already exists
        if only_audio:
            ext = "mp3"
        else:
            ext = "mp4"

        title = file_name(dl_path, url, ext)   

        ydl_options = {
            "format": format,
            "outtmpl": os.path.join(dl_path, f"{title}.%(ext)s"), 
            "merge_output_format": "mp4",
            "restrictfilenames": True,
            "progress_hooks": [download_bar.progress_hook()],           
            "postprocessors":[{
                "key":"FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]if only_audio else [], # If the download is audio only, convert the file to MP3.
            #'ffmpeg_location': ffmpeg_path
            # The above line is for specifying which FFmpeg will be used.
        }
        with yt_dlp.YoutubeDL(ydl_options) as ydl:
            show_status(warning_label, f"Wait\nDownloading file...", root)           
            ydl.download([url])
            show_status(warning_label, "", root)
            messagebox.showinfo("Youtube Downloader", "Download completed")
        link.set('')
    except yt_dlp.DownloadError as err:
        messagebox.showerror("Error", f"Error when downloading the file: {err}")  
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")

def resource_path(relative_path):
    """This function returns the correct path of files (such as images, icons, 
       system path) during development and after the script has been packaged."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        return os.path.join(os.path.abspath("."), relative_path)
       
def main():
    root = Tk(className= " Youtube Downloader")
    root.geometry('600x600')
    root.resizable(False, False)

    upper_frame = ttk.Frame(root,  width=550,  height=300, borderwidth=3, relief="sunken")
    upper_frame.place(rely=0.3, relx=0.5,anchor="center")
    lower_frame = ttk.Frame(root, width= 230, height= 220, borderwidth= 3, relief="sunken")
    lower_frame.place(rely=0.8, relx=0.575, anchor='w')

    link = StringVar()
    download_path = StringVar(value= load_default_directory())
    quality_video = StringVar(value= "Select")
    quality_audio = StringVar(value= "Select")

    insert_link_label = ttk.Label(upper_frame, text="Paste the video link in the field below.", font="Arial 12")
    insert_link_label.place(relx=0.5, rely=0.59, anchor='center')

    link_entry = ttk.Entry(upper_frame, width=40, textvariable=link)
    link_entry.place(relx=0.5, rely=0.72, anchor="center")

    download_path_label = ttk.Label(upper_frame, text="Download Directory", font="Arial 12")
    download_path_label.place(relx=0.5, rely=0.17, anchor="center")

    download_path_entry = ttk.Entry(upper_frame, width=32, textvariable=download_path)
    download_path_entry.place(in_=upper_frame,relx=0.5, rely=0.3, anchor="center")

    directory_button_image_path = resource_path("assets/icons/folder.png")
    directory_button_image = PhotoImage(file=directory_button_image_path, height=18, width=20)
    directory_button = Button(command=lambda: ask_download_directory(download_path),image=directory_button_image)
    directory_button.place(in_=upper_frame, relx=0.78, rely=0.3, anchor="center")

    menu_video_label = ttk.Label(lower_frame, text="Vídeo/Audio", font="Arial 12")
    menu_video_label.place(relx=0.24, rely=0.20, anchor="center")
    menu_video_opts = ['Select','1080p', '720p', '360p', '144p']
    menu_video = ttk.Combobox(lower_frame,textvariable=quality_video, width=10, values=menu_video_opts, state="readonly")   
    menu_video.place(in_=lower_frame, relx=0.25, rely=0.35, anchor="center")
    
    menu_audio_label = ttk.Label(lower_frame, text="Audio(MP3)", font="Arial 12")
    menu_audio_label.place(relx=0.75, rely=0.20, anchor="center")
    menu_audio_opts = ['Select', '320kbps', '256kbps', '128kbps']
    menu_audio = ttk.Combobox(lower_frame,textvariable=quality_audio, width=10, values=menu_audio_opts, state="readonly")
    menu_audio.place(in_=lower_frame, relx=0.75, rely=0.35, anchor="center")

    # Track changes to the download_path StringVar and update the default directory in the "config.json" accordingly
    download_path.trace_add("write", lambda *args: update_default_directory(download_path))
    # Handle combobox state based on the selected option
    menu_video.bind("<<ComboboxSelected>>", lambda event: toggle_other_combobox(quality_video, menu_audio, event))
    menu_audio.bind("<<ComboboxSelected>>", lambda event: toggle_other_combobox(quality_audio, menu_video, event))
    # Monitor Button-3 event to display copy and paste context menu   
    root.bind_class("TEntry", "<Button-3>", lambda event: display_button(root, event, event.widget))

    warning_label = Label(root, text="", font="arial 16")
    warning_label.place(relx=0.28, rely=0.73, anchor="center")
    warning_label.config(wraplength=400)

    download_button = Button(command=lambda: download(link, download_path, quality_video, quality_audio, warning_label, root), text="DOWNLOAD")
    download_button.place(in_=upper_frame, relx=0.5, rely=0.87, anchor="center")

    root.mainloop() 

if __name__ == '__main__':
    main()       
                   