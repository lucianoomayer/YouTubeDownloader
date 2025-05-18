# YouTube Downloader
This is my first personal project, created to help me practice and improve my Python skills.

## Installation
Before running the program, make sure you have the following installed: 
- [Python](https://www.python.org/)
- [FFmpeg](https://ffmpeg.org/) — used for audio and video conversion

### Installing Tkinter (if necessary):
Tkinter is used as the graphical user interface (GUI) for this project. It usually comes with standard Python installations, but on some Linux systems you may need to install it manually.
```bash
sudo apt install python3-tk
```

## Dependencies
This project uses the following third-party library:
- [yt-dlp](https://github.com/yt-dlp/yt-dlp): Used for downloading videos from YouTube.

You can install it with:
```bash
pip install yt-dlp
``` 

## Features
* **Video and Audio Download**: Download video or audio-only (MP3 format)
* **Quality Selection**: Choose the video resolution or audio bitrate
* **Progress Bar**: Displays a progress bar with download percentage and updates in real-time
* **Selectable Download Directory**: *Choose and save your download folder for future sessions.
* **Copy and Paste Menu**: Right-click on the input fields to easily copy and paste URLs or file paths

_*The setting is stored in a file located in your Documents folder._

## Packaging the Application
Before packaging the script, make sure you have uncommented the following lines in main.py:
```bash
183 #ffmpeg_path = resource_path("ffmpeg/ffmpeg")
```
```bash
206 #'ffmpeg_location': ffmpeg_path
```
Next, create a "ffmpeg" folder in the project directory and place the FFmpeg binary files.

To create an executable from the script using PyInstaller:

1. Install PyInstaller 
```bash
pip install -U pyinstaller
``` 
2. Execute the following command:
```bash
pyinstaller --onefile --add-binary "ffmpeg/ffmpeg:ffmpeg" --add-data "assets/icons:assets/icons" main.py
``` 

After this, the executable will be located in the "dist" folder.

## Screenshot
<p align="center">
  <img src="assets/screenshots/app_screenshot.png" alt="App Screenshot" width="500"/>
</p>

## License
This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.