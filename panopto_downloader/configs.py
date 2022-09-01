from __future__ import annotations

import json
import os
import sys
from tkinter import messagebox
from typing import Dict, Optional
from pydantic import BaseModel

from .utils import is_tool

conf_file = "panopto.json"
ffmpeg_default_binaries = "./ffmpeg/ffmpeg.exe"


class Config(BaseModel):
    COURSE: Optional[str]
    PANOPTO_BASE: str
    TOKEN: Optional[str]
    DEFAULT_FFMPEG_LOCATION: Optional[str]

    # see youtube_dl.YoutubeDL
    ydl_opts: Dict[str, str] = {}

    def dump(self) -> None:
        d = self.dict()

        with open(conf_file, "w") as fp:
            json.dump(d, fp, indent=4, sort_keys=True)

    @staticmethod
    def load() -> Config:
        with open(conf_file, "r") as fp:
            data = json.load(fp)
        return Config(**data)


def config_setup() -> Config:
    if not os.path.isfile(conf_file):
        c = Config(
            COURSE=None,
            PANOPTO_BASE="https://univr.cloud.panopto.eu"
        )
        c.dump()

    config = Config.load()

    return config


def ensure_ffmpeg(config: Optional[Config] = None) -> bool:
    if config is not None and config.DEFAULT_FFMPEG_LOCATION is not None:
        found = os.path.isfile(config.DEFAULT_FFMPEG_LOCATION)
        return found, True

    found = is_tool("ffmpeg")
    local_binaries = False
    if not found and sys.platform == "win32":
        # Hardcoded for Windows
        if config is None:
            binaries_location = ffmpeg_default_binaries
        else:
            if config.DEFAULT_FFMPEG_LOCATION is None:
                binaries_location = ffmpeg_default_binaries
            else:
                binaries_location = config.DEFAULT_FFMPEG_LOCATION
        found = os.path.isfile(binaries_location)
        local_binaries = True

        # updates default ffmpeg location is found and is None
        if found and config.DEFAULT_FFMPEG_LOCATION is None:
            config.DEFAULT_FFMPEG_LOCATION = binaries_location
            config.dump()

    return found, local_binaries


def initialize_app() -> Config:
    config = config_setup()

    ffmpeg_found, local_binaries = ensure_ffmpeg(config)

    if not ffmpeg_found:
        error = f"FFMPEG not found in system nor in \"{config.DEFAULT_FFMPEG_LOCATION}\". Please install it, or download the binaries and place them in the folder as \"{config.DEFAULT_FFMPEG_LOCATION}\"."
        messagebox.showerror("Error!", error)
        sys.exit(-1)

    if local_binaries:
        config.ydl_opts["ffmpeg_location"] = config.DEFAULT_FFMPEG_LOCATION

        print(f"FFMPEG found locally in {config.DEFAULT_FFMPEG_LOCATION}")

    return config
