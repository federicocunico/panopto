import threading
import tkinter as tk
from tkinter import BOTH, LEFT, RIGHT, Y, messagebox
import tkinter.font as tkFont

from ..models.panopto_model import PanoptoModel
from ..utils import is_token_valid


class MainWindow(tk.Tk):
    def __init__(self, panopto_model: PanoptoModel):
        super().__init__()
        self.panopto_model = panopto_model
        self.root = self

        self.set_window_properties(title="Panopto Downloader")
        self.make_main_label_ui()
        self.make_token_ui()

        self.make_courses_frame_ui()
        self.make_downloading_progress_frame_ui()
        self.make_download_button_ui()

        self.load()

    # UI ELEMENTS

    def set_window_properties(self, title: str):
        # setting title
        self.root.title(title)
        # setting window size
        width = 520
        height = 640  # 480
        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height,
                                    (screenwidth - width) / 2, (screenheight - height) / 2)
        self.root.geometry(alignstr)
        self.root.resizable(width=False, height=False)

    def make_main_label_ui(self):
        title_label = tk.Label(self.root)
        ft = tkFont.Font(family='Times', size=24)
        title_label["font"] = ft
        title_label["fg"] = "#333333"
        title_label["justify"] = "center"
        title_label["text"] = "Panopto Record Downloader"
        title_label.place(x=60, y=30)

    def make_courses_frame_ui(self):
        listbox_width = 450

        # USE FRAME
        courses_frame = tk.Frame(self.root)
        courses_frame.place(x=20, y=170, width=470, height=230)
        self.courses_listbox = tk.Listbox(
            courses_frame, width=listbox_width, height=200)

        # USE ROOT
        # self.courses_listbox = tk.Listbox(root)

        courses_label = tk.Label(courses_frame)
        ft = tkFont.Font(family='Times', size=16)
        courses_label["font"] = ft
        courses_label["fg"] = "#333333"
        courses_label["justify"] = "center"
        courses_label["text"] = "Courses list"
        courses_label.place(x=0, y=0, width=listbox_width, height=40)

        self.courses_listbox["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times', size=12)
        self.courses_listbox["font"] = ft
        self.courses_listbox["fg"] = "#333333"
        self.courses_listbox["justify"] = "left"
        # self.courses_listbox.place(x=20, y=190, width=470, height=200)  # use ROOT
        self.courses_listbox.place(x=0, y=40, width=listbox_width, height=200)
        self.courses_listbox.bind('<<ListboxSelect>>', self.on_course_select)

        # Scrollbar only on frame
        scrollbar = tk.Scrollbar(courses_frame)
        self.courses_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.courses_listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)

    def make_downloading_progress_frame_ui(self):
        listbox_width = 450
        listbox_height = 150

        # USE FRAME
        download_frame = tk.Frame(self.root)
        download_frame.place(x=20, y=470, width=470, height=listbox_height)
        self.download_listbox = tk.Listbox(
            download_frame, width=listbox_width, height=listbox_height)

        # USE ROOT
        # self.courses_listbox = tk.Listbox(root)

        download_progress_label = tk.Label(download_frame)
        ft = tkFont.Font(family='Times', size=16)
        download_progress_label["font"] = ft
        download_progress_label["fg"] = "#333333"
        download_progress_label["justify"] = "center"
        download_progress_label["text"] = "Download in progress"
        download_progress_label.place(x=0, y=0, width=listbox_width, height=40)

        self.download_listbox["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times', size=12)
        self.download_listbox["font"] = ft
        self.download_listbox["fg"] = "#333333"
        self.download_listbox["justify"] = "left"
        self.download_listbox.place(x=0, y=40, width=listbox_width, height=listbox_height)

        # Scrollbar only on frame
        download_scrollbar = tk.Scrollbar(download_frame)
        self.download_listbox.config(yscrollcommand=download_scrollbar.set)
        download_scrollbar.config(command=self.courses_listbox.yview)
        download_scrollbar.pack(side=RIGHT, fill=Y)

    def make_token_ui(self):
        show_token_button = tk.Button(self.root)
        show_token_button["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times', size=12)
        show_token_button["font"] = ft
        show_token_button["fg"] = "#000000"
        show_token_button["justify"] = "center"
        show_token_button["text"] = "Show Token"
        show_token_button.place(x=310, y=130, width=100, height=25)
        show_token_button["command"] = self.show_token

        set_token_button = tk.Button(self.root)
        set_token_button["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times', size=12)
        set_token_button["font"] = ft
        set_token_button["fg"] = "#000000"
        set_token_button["justify"] = "center"
        set_token_button["text"] = "Set Token"
        set_token_button.place(x=420, y=130, width=70, height=25)
        set_token_button["command"] = self.set_token

        self.token_entry = tk.Entry(self.root)
        self.token_entry.config(font=("helvetica", 10))
        self.token_entry.place(x=20, y=130, width=280, height=25)
        self.set_last_token(self.panopto_model.config.ASPXAUTH_token)

    def make_download_button_ui(self):
        download_button = tk.Button(self.root)
        download_button["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times', size=12)
        download_button["font"] = ft
        download_button["fg"] = "#000000"
        download_button["justify"] = "center"
        download_button["text"] = "Download"
        download_button.place(x=220, y=420, width=70, height=25)
        download_button["command"] = self.download_course

    # UI FUNCTIONS

    def reload(self):
        self.panopto_model = self.panopto_model.__class__(
            self.panopto_model.config)
        self.load()

    def load(self):
        courses = self.panopto_model.get_courses()
        for c in courses:
            self.courses_listbox.insert(tk.END, c)

    def set_last_token(self, value: str) -> None:
        self.token_entry.delete(0, tk.END)
        if is_token_valid(value):
            self.token_entry.insert(0, value)
        else:
            self.token_entry.insert(0, "<INSERT TOKEN HERE>")

    def on_course_select(self, event):
        w = event.widget
        if w.curselection():
            index = int(w.curselection()[0])
            value = w.get(index)
            self.panopto_model.selected_course = value

    def download_course(self):
        thread = self.panopto_model.async_start_download(self.download_listbox)

    def show_token(self):
        token = self.panopto_model.config.ASPXAUTH_token
        if not token:
            return
        messagebox.showinfo("Token", f"Your token is:\n\n{token}")

    def set_token(self):
        self.panopto_model.set_token(self.token_entry.get())
        self.reload()


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
