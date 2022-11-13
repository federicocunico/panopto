from __future__ import annotations

import json
import os
import sys
from tkinter import messagebox
from typing import Any, Dict, Optional
from pydantic import BaseModel, ValidationError

from .utils import is_tool

conf_file = "panopto.json"
ffmpeg_default_binaries = "./ffmpeg/ffmpeg.exe"


class Config(BaseModel):
    panopto_base: str
    ASPXAUTH_token: Optional[str]
    default_ffmpeg_location: Optional[str]
    downloads_path: str

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


def attempt_migration() -> None:
    json_data: Dict[str, Any]
    with open(conf_file, "r") as fp:
        json_data = json.load(fp)

    k: str
    converted = {"downloads_path": "downloads"}
    for (k, v) in json_data.items():
        new_k = k.lower()
        if k == "TOKEN":
            new_k = "ASPXAUTH_token"
        converted[new_k] = v

    # validate
    _ = Config(**converted)

    with open(conf_file+".old", "w") as fp:
        json.dump(json_data, fp)
    with open(conf_file, "w") as fp:
        json.dump(converted, fp)

    print("Updated config file")


def config_setup() -> Config:
    if not os.path.isfile(conf_file):
        c = Config(
            panopto_base="https://univr.cloud.panopto.eu",
            downloads_path="downloads"
        )
        c.dump()

    try:
        config = Config.load()
    except ValidationError as e:
        # retrocompatibility, v1 to v2
        attempt_migration()

        config = Config.load()

    return config


def ensure_ffmpeg(config: Optional[Config] = None) -> bool:
    if config is not None and config.default_ffmpeg_location is not None:
        found = os.path.isfile(config.default_ffmpeg_location)
        return found, True

    found = is_tool("ffmpeg")
    local_binaries = False
    if not found and sys.platform == "win32":
        # Hardcoded for Windows
        if config is None:
            binaries_location = ffmpeg_default_binaries
        else:
            if config.default_ffmpeg_location is None:
                binaries_location = ffmpeg_default_binaries
            else:
                binaries_location = config.default_ffmpeg_location
        found = os.path.isfile(binaries_location)
        local_binaries = True

        # updates default ffmpeg location is found and is None
        if found and config.default_ffmpeg_location is None:
            config.default_ffmpeg_location = binaries_location
            config.dump()

    return found, local_binaries


def initialize_app() -> Config:
    # 1. Load Config from file
    config = config_setup()

    # 2. Find FFMPEG on system
    ffmpeg_found, local_binaries = ensure_ffmpeg(config)

    if not ffmpeg_found:
        error = f"FFMPEG not found in system nor in \"{config.default_ffmpeg_location}\". Please install it, or download the binaries and place them in the folder as \"{config.default_ffmpeg_location}\"."
        messagebox.showerror("Error!", error)
        sys.exit(-1)

    if local_binaries:
        config.ydl_opts["ffmpeg_location"] = config.default_ffmpeg_location
        print(f"FFMPEG found locally in {config.default_ffmpeg_location}")
    else:
        print(f"FFMPEG found")

    return config
