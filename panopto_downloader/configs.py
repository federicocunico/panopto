import os
import sys
import configparser
from tkinter import messagebox
from typing import Dict, Optional
from pydantic import BaseModel

conf_file = "panopto.ini"

class Config(BaseModel):
    COURSE: Optional[str]
    PANOPTO_BASE: str
    TOKEN: Optional[str]

    # see youtube_dl.YoutubeDL
    ydl_opts: Dict[str, str] = {}

    def dump(self) -> None:
        with open(conf_file, "w") as fp:
            fp.write("[PANOPTO]\n")
            fp.write(f"BASE_URL={self.PANOPTO_BASE}\n")
            fp.write(
                "# Replace <INSERT TOKEN HERE> with your token, for example like this (yours will be longer):\n")
            fp.write(
                "# TOKEN=BBDE70AB7BB5F57576A6FC97E8DC302F2138F53C4993B60B2A0051DBBAEF12D9923F4FF4CA8C8F67FBE0\n")
            fp.write(f"TOKEN={self.TOKEN}\n")

def config_setup() -> Config:
    if not os.path.isfile(conf_file):
        with open(conf_file, "w") as fp:
            fp.write("[PANOPTO]\n")
            fp.write("BASE_URL=https://univr.cloud.panopto.eu\n")
            fp.write(
                "# Replace <INSERT TOKEN HERE> with your token, for example like this (yours will be longer):\n")
            fp.write(
                "# TOKEN=BBDE70AB7BB5F57576A6FC97E8DC302F2138F53C4993B60B2A0051DBBAEF12D9923F4FF4CA8C8F67FBE0\n")
            fp.write("TOKEN=<INSERT TOKEN HERE>\n")

    config = configparser.ConfigParser()
    config.read(conf_file)

    panopto_base = config["PANOPTO"]["BASE_URL"]
    token = config["PANOPTO"]["TOKEN"]

    config = Config(COURSE=None, PANOPTO_BASE=panopto_base, TOKEN=token)

    return config


def init_config() -> Config:
    config = config_setup()

    # Hardcoded for Windows
    if sys.platform == "win32":
        ffmpeg_file = "./ffmpeg/ffmpeg.exe"
        if not os.path.isfile(ffmpeg_file):
            error = f"FFMPEG not found in {ffmpeg_file}. Download the binaries and place them here."
            messagebox.showerror("Error!", error)
            sys.exit(-1)

        config.ydl_opts["ffmpeg_location"] = ffmpeg_file

    return config
