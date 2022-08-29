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
- ffmpeg (suggested install: `apt-get install ffmpeg`)
- Python modules:
    - youtube_dl
    - tk
    - requests
    - pydantic
