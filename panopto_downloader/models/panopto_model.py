import json
import os
import threading
import time
from tkinter import messagebox
import tkinter
from typing import Dict, List, Optional, Tuple
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

        self.selected_course: Optional[str] = None

        self.courses_in_download: Dict[str, threading.Thread] = {}

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

    def download_now(self) -> Tuple[bool, str]:
        course_name = self.selected_course

        # if course_name in self.courses_in_download:
        #     return False, "Already downloading"

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
            if matches(name, course_name):
                messagebox.showinfo("Starting download", f"Press OK to download the course: \"{course_name}\"")
                self.dl_folder(folder)
                found = True

        if not found:
            return found, "Course not found."

        # if ending_callback is not None:
        #     ending_callback(course_name)

        return found, course_name

    def async_start_download(self, listbox: Optional[tkinter.Listbox]=None):
        course_name = self.selected_course
        if course_name is None:
            messagebox.showwarning("Warning!", f"No course selected")
            return
        
        if course_name in self.courses_in_download:
            messagebox.showwarning("Warning!", f"Already downloading!")
            return

        def download():
            found, reason = self.download_now()
            if not found:
                messagebox.showwarning(
                    "Warning!", f"{reason}")
            else:
                messagebox.showinfo("Success", f"Successfully downloaded {reason}")

        if listbox is not None:
            listbox.insert(tkinter.END, course_name)
        thread = threading.Thread(target=download)
        thread.start()

        self.courses_in_download[course_name] = thread

        ending_thread = threading.Thread(target=self._remove_finished_download, args=(course_name,listbox))
        ending_thread.start()

    def _remove_finished_download(self, course_name, listbox: Optional[tkinter.Listbox] = None):
        assert course_name in self.courses_in_download, "Error stopping thread"

        th = self.courses_in_download[course_name]
        if th.is_alive():
            th.join()  # wait for completition

        del self.courses_in_download[course_name]

        if listbox is not None:
            idx = listbox.get(0, tkinter.END).index(course_name)
            if idx >= 0:
                listbox.delete(idx)
            else:
                print("Error, not found course in listbox, unexpected!")

