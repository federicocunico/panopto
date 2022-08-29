import tkinter as tk
from tkinter import *
import requests
import json
import os
import youtube_dl
import configparser


"""
Place the value of your .ASPXAUTH token in the config file.
"""

class ScrollableListbox(tk.Listbox):
    def __init__(self, master, *arg, **key):
        self.frame = tk.Frame(master)
        self.yscroll = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        tk.Listbox.__init__(self, self.frame, yscrollcommand=self.yscroll.set, *arg, **key)
        self.yscroll['command'] = self.yview

    def grid(self, *arg, **key):
        self.frame.grid(*arg, **key)
        tk.Listbox.grid(self, row=0, column=0, sticky='nswe')
        self.yscroll.grid(row=0, column=1, sticky='ns')

s: requests.Session = None

conf_file = "panopto.ini"
if not os.path.isfile(conf_file):
    with open(conf_file, "w") as fp:
        fp.write("[PANOPTO]\n")
        fp.write("BASE_URL=https://univr.cloud.panopto.eu\n")
        fp.write("# Replace <INSERT TOKEN HERE> with your token, for example like this (yours will be longer):\n")
        fp.write("# TOKEN=BBDE70AB7BB5F57576A6FC97E8DC302F2138F53C4993B60B2A0051DBBAEF12D9923F4FF4CA8C8F67FBE0\n")
        fp.write("TOKEN=<INSERT TOKEN HERE>\n")

config = configparser.ConfigParser()
config.read(conf_file)
PANOPTO_BASE = config["PANOPTO"]["BASE_URL"]
TOKEN = config["PANOPTO"]["TOKEN"]

COURSE = ""

def is_token_valid(token: str):
    if not token:
        return False
    valid = True
    for v in token:
        if not (v.isalpha() or v.isdigit()):
            valid = False
            break
    return valid

# WHYYYY does panopto use at least 3 different types of API!?!?!?
def json_api(endpoint, params=dict(), post=False, paramtype="params"):
    if post:
        r = s.post(PANOPTO_BASE + endpoint, **{paramtype: params})
    else:
        r = s.get(PANOPTO_BASE + endpoint, **{paramtype: params})
    if not r.ok:
        print(r.text)
    return json.loads(r.text)


def name_normalize(name):
    return name.replace("/", "-")


def dl_session(session):
    dest_dir = os.path.join(
        "downloads",
        name_normalize(session["FolderName"]),
        name_normalize(session["SessionName"]),
    )
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    delivery_info = json_api(
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
        update_gui(txt)
        ydl_opts = {"outtmpl": dest_filename, "quiet": True}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([streams[i]["StreamUrl"]])


def dl_folder(folder):
    sessions = json_api(
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
        dl_session(session)

def get_courses():
    global s

    s = requests.session()  # cheeky global variable
    s.cookies = requests.utils.cookiejar_from_dict({".ASPXAUTH": TOKEN})

    folders = json_api(
        "/Panopto/Api/v1.0-beta/Folders", {"parentId": "null", "folderSet": 1}
    )
    import re
    regexp = re.compile("\([0-9]+\/[0-9]+\)", re.IGNORECASE)
    is_course = lambda x: regexp.search(x)

    courses = [f["Name"] for f in folders if is_course(f["Name"])]

    print("-"*55)
    print("Corsi disponibili")
    print("-"*55)
    for c in courses:
        print(c)

    with open("courses.txt", "w") as fp:
        for c in courses:
            fp.write(c + "\n")
    
    return courses



def download_now():
    global s

    s = requests.session()  # cheeky global variable
    s.cookies = requests.utils.cookiejar_from_dict({".ASPXAUTH": TOKEN})

    folders = json_api(
        "/Panopto/Api/v1.0-beta/Folders", {"parentId": "null", "folderSet": 1}
    )

    # print([f["Name"] for f in folders])
    matches = lambda folder_name,course: course.lower() in folder_name.lower()
    found = False
    for folder in folders:
        """
        Put an if statement here based on folder["Name"] if you just want a certain
        module or year etc.
        e.g.:
        """
        name = folder["Name"]
        # if name.startswith(COURSE):
        if matches(name, COURSE):
            dl_folder(folder)
            found = True
    return found


def start_download() -> bool:
    global COURSE
    COURSE = entry1.get()
    if COURSE == "":
        update_gui(f"Please, enter a valid course")
        return    
    update_gui(f"Starting download course {COURSE}...")
    found = download_now()
    if found:
        update_gui("Download done.")
    else:
        update_gui("Course not found!!")


root = tk.Tk()

WIDTH = 800
HEIGHT = 650
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, relief="raised")

label1 = tk.Label(root, text="Download courses from Panopto")
label1.config(font=("helvetica", 22))
canvas.create_window(WIDTH//2, 25, window=label1)


instructions = "Instructions:\n\n1. If the file \"panopto.ini\" does not exists in the location of the executable file, run the executable file: it will create the file with correct headers, then follow step 2.\n\n2a. Insert your token under the TOKEN attribute, after the equal (=) sign.\n2b. If you do not know where to find it:\n\t(A) open any panopto recorded lesson on a browser.\n\t(B) Press F12 to open developer tools.\n\t(C) Then go to the \"Network\" tab and refresh (F5).\n\t(D) After the web page has loaded, press CTRL+F on the developer tools in the \"Network\" section.\n\t(E) Then search for this string \"ASPXAUTH\".\n\t(F) You will find several files with \".ASPXAUTH=<blablabla>;\". Select any file with such string in it, and copy the content from the equal sign (=) after \".ASPXAUTH=\" to the first semicolon (;) you find. The resulting string should be only capital letters and numbers. This is your token.\n\t(G) Now update the \"panopto.ini\" then restart and follow step 2a."

instructions_label = tk.Label(root, text=instructions, wraplength=800, justify="left")
instructions_label.config(font=("helvetica", 16))
# canvas.create_window(WIDTH//2, 280, window=instructions_label)

label2 = tk.Label(root, text="Enter the course name:")
label2.config(font=("helvetica", 16))
canvas.create_window(WIDTH//2, 520, window=label2)

entry1 = tk.Entry(root)
entry1.config(font=("helvetica", 16))
canvas.create_window(WIDTH//2, 550, window=entry1)


def update_gui(text, x=None, y=None):
    if x is None:
        x = WIDTH//2
    if y is None:
        y = 630

    label3 = tk.Label(root, text=text, font=("helvetica", 16))
    canvas.create_window(x, y, window=label3)


button1 = tk.Button(
    text="Start",
    command=start_download,
    bg="brown",
    fg="white",
    font=("helvetica", 14, "bold"),
)
canvas.create_window(WIDTH//2, 600, window=button1)

if not is_token_valid(TOKEN):
    canvas.delete("all")

    canvas.create_window(WIDTH//2, 280, window=instructions_label)  
    update_gui("INVALID TOKEN SET.\n PLEASE, SET THE \"panopto.ini\" FILE AND RESTART THE PROGRAM", WIDTH//2, 520)
else:
    courses = get_courses()
    
    ## MANUAL
    # listbox = tk.Listbox(canvas)
    # scrollbar = tk.Scrollbar(canvas)

    # # Insert elements into the listbox
    # for c in courses:
    #     listbox.insert(END, c)
        
    # # Since we need to have a vertical 
    # # scroll we use yscrollcommand
    # listbox.config(yscrollcommand = scrollbar.set)    
    # # setting scrollbar command parameter 
    # # to listbox.yview method its yview because
    # # we need to have a vertical view
    # scrollbar.config(command = listbox.yview)

    # # listbox.pack()
    # # scrollbar.pack()
    
    # FRAME
    listbox = ScrollableListbox(root)
    for c in courses:
        listbox.insert(END, c)
    listbox.pack()

    # canvas.create_window(WIDTH//2, 280, window=listbox)


canvas.pack()
root.mainloop()
