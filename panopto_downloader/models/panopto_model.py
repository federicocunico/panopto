import json
import os
from tkinter import messagebox
import requests
import youtube_dl
import re

from ..configs import Config


class PanoptoModel():

    def __init__(self, config: Config) -> None:
        self.session = requests.session()
        self.session.cookies = requests.utils.cookiejar_from_dict(
            {".ASPXAUTH": config.TOKEN})
        self.config = config

    def set_token(self, text: str):
        # preprocess token
        token = ""
        for t in text:
            if t.isalnum():
                token += t
        self.config.TOKEN = token
        self.config.dump()

    # WHYYYY does panopto use at least 3 different types of API!?!?!?
    def json_api(self, endpoint, params=dict(), post=False, paramtype="params"):
        if post:
            r = self.session.post(self.config.PANOPTO_BASE +
                                  endpoint, **{paramtype: params})
        else:
            r = self.session.get(self.config.PANOPTO_BASE +
                                 endpoint, **{paramtype: params})
        if not r.ok:
            print(r.text)
        return json.loads(r.text)

    @staticmethod
    def name_normalize(name):
        illegal_chars = {
            "/": "-",
            ":": "",
            ">": "",
            "<": "",
            "\\": "",
            "|": "",
            "?": "",
            "*": ""
        }
        for k,v in illegal_chars.items():
            name = name.replace(k, v)
        return name

    def dl_session(self, session):
        dest_dir = os.path.join(
            "downloads",
            self.name_normalize(session["FolderName"]),
            self.name_normalize(session["SessionName"]),
        )
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        delivery_info = self.json_api(
            "/Panopto/Pages/Viewer/DeliveryInfo.aspx",
            {"deliveryId": session["DeliveryID"], "responseType": "json"},
            True,
            "data",
        )
        streams = delivery_info["Delivery"]["Streams"]
        for i in range(len(streams)):
            filename = "{:02d}_{}.mp4".format(i, streams[i]["Tag"])
            dest_filename = os.path.join(dest_dir, filename)
            txt = "Downloading: " + dest_filename
            print(txt)

            base_ydl_opts = self.config.ydl_opts  # defaults empty {}
            ydl_opts = {"outtmpl": dest_filename, "quiet": True}

            # merge with configs
            for k,v in base_ydl_opts.items():
                ydl_opts[k] = v

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([streams[i]["StreamUrl"]])

    def dl_folder(self, folder):
        sessions = self.json_api(
            "/Panopto/Services/Data.svc/GetSessions",
            {
                "queryParameters": {
                    "folderID": folder["Id"],
                }
            },
            True,
            "json",
        )["d"]["Results"]

        for session in sessions:
            try:
                self.dl_session(session)
            except:
                print(f"Error downloading session + {session}")

    def is_course(self, text: str):
        regexp = re.compile("\([0-9]+\/[0-9]+\)", re.IGNORECASE)
        return regexp.search(text)

    def get_courses(self):

        folders = self.json_api(
            "/Panopto/Api/v1.0-beta/Folders", {
                "parentId": "null", "folderSet": 1}
        )

        courses_names = [f["Name"] for f in folders]
        # courses = [n for n in courses_names if self.is_course(n)]  # rimuove troppo
        courses = courses_names

        print("-"*55)
        print("Corsi disponibili")
        print("-"*55)
        for c in courses:
            print(c)

        print("-"*55)
        print("Corsi esclusi")
        print("-"*55)
        for c in list(set(courses_names) - set(courses)):
            print(c)

        # with open("courses.txt", "w") as fp:
        #     for c in courses:
        #         fp.write(c + "\n")

        return courses

    def download_now(self) -> bool:
        folders = self.json_api(
            "/Panopto/Api/v1.0-beta/Folders", {
                "parentId": "null", "folderSet": 1
            }
        )

        def matches(folder_name, course): return course.lower(
        ) in folder_name.lower()

        found = False
        for folder in folders:
            name = folder["Name"]
            if matches(name, self.config.COURSE):
                messagebox.showinfo("Starting download", f"Press OK to download the course: \"{self.config.COURSE}\"")
                self.dl_folder(folder)
                found = True

        return found
