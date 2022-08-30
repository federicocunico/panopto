# Panopto Downloader
A tkinter python tool for downloading lessons from panopto.

You will need the ASPXAUTH token. Follow the instructions below

<!-- ## Instructions
1. If the file \"panopto.ini\" does not exists in the location of the executable file, run the executable file: it will create the file with correct headers, then follow step 2.\n\n2a. Insert your token under the TOKEN attribute, after the equal (=) sign. -->

- If you do not know where to find it:
    - (A) open any panopto recorded lesson on a browser.
    - (B) Press F12 to open developer tools.
    - (C) Then go to the \"Network\" tab and refresh (F5).
    - (D) After the web page has loaded, press CTRL+F on the developer tools in the \"Network\" section.
    - (E) Then search for this string \"ASPXAUTH\".
    - (F) You will find several files with \".ASPXAUTH=<blablabla>;\". Select any file with such string in it, and copy the content from the equal sign (=) after \".ASPXAUTH=\" to the first semicolon (;) you find. The resulting string should be only capital letters and numbers. This is your token.
    <!-- - (G) Now update the \"panopto.ini\" then restart." -->

## Requirements
- Python >=3.6
- ffmpeg 
    - Linux: suggested install: `apt-get install ffmpeg`
    - Windows: download the ffmpeg [binaries zip](https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip) or [binaries 7z](https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z) and place it in the same folder of the executable/python file with the following structure: `./ffmpeg/<executables>.exe`
- Python modules:
    - youtube_dl
    - tk
    - requests
    - pydantic

## Windows instructions

Download the ffmpeg binaries.
From powershell: 

```powershell
# Download file
Invoke-WebRequest -OutFile ffmpeg.zip -Uri https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
# Extract archive
Expand-Archive ./ffmpeg.zip -DestinationPath ./ffmpeg_build
# Create new folder
New-Item -ErrorAction Ignore -Path "./" -Name "ffmpeg" -ItemType "directory"
# Copy binaries
Get-ChildItem -Path ./ffmpeg_build -Recurse -File | Move-Item -Destination ./ffmpeg
# Remove old folder
Remove-Item -LiteralPath "./ffmpeg_build" -Force -Recurse
```

Run the main file (`main_tk.py`) file or the executable, after placing the ffmpeg binaries (see requirements) in the same folder as the main file / executable. The structure should be:

```
ROOT
│   main_tk.py / main_tk.exe
├───ffmpeg
│       ffmpeg.exe
│       ffplay.exe
│       ffprobe.exe

```

## Linux Instructions
Install ffmpeg, ensure it is found in the system.
Then distribute or execute the main file (`main_tk.py`).


## Distribution:
You can distribute in two modes: `pyinstaller` and `nuitka`.

### Pyinstaller
First, install `pyinstaller` with 

```bash
pip install pyinstaller
```

Then execute (use `pyinstaller.exe` instead of `pyinstaller` on windows)

```bash
pyinstaller --onefile main_tk.py
```

### Nuitka
`TODO`
