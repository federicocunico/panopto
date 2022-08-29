import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkFont

from panopto_downloader.models.panopto_model import PanoptoModel
from panopto_downloader.utils import is_token_valid


class MainWindow(tk.Tk):
    def __init__(self, panopto_model: PanoptoModel):
        super().__init__()
        self.panopto_model = panopto_model
        root = self

        # setting title
        root.title("Panopto Downloader")
        # setting window size
        width = 510
        height = 550
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height,
                                    (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)

        self.courses_listbox = tk.Listbox(root)
        self.courses_listbox["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times', size=10)
        self.courses_listbox["font"] = ft
        self.courses_listbox["fg"] = "#333333"
        self.courses_listbox["justify"] = "left"
        self.courses_listbox.place(x=20, y=190, width=470, height=200)
        self.courses_listbox.bind('<<ListboxSelect>>', self.on_course_select)

        download_button = tk.Button(root)
        download_button["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times', size=10)
        download_button["font"] = ft
        download_button["fg"] = "#000000"
        download_button["justify"] = "center"
        download_button["text"] = "Download"
        download_button.place(x=220, y=410, width=70, height=25)
        download_button["command"] = self.download_course

        title_label = tk.Label(root)
        ft = tkFont.Font(family='Times', size=24)
        title_label["font"] = ft
        title_label["fg"] = "#333333"
        title_label["justify"] = "center"
        title_label["text"] = "Panopto Record Downloader"
        title_label.place(x=60, y=30)

        set_token_button = tk.Button(root)
        set_token_button["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times', size=10)
        set_token_button["font"] = ft
        set_token_button["fg"] = "#000000"
        set_token_button["justify"] = "center"
        set_token_button["text"] = "Set Token"
        set_token_button.place(x=420, y=130, width=70, height=25)
        set_token_button["command"] = self.set_token

        self.token_entry = tk.Entry(root)
        self.token_entry.config(font=("helvetica", 10))
        self.token_entry.place(x=20, y=130, width=350, height=25)
        self.set_last_token(self.panopto_model.config.TOKEN)

        self.load()

    def reload(self):
        self.panopto_model = self.panopto_model.__class__(self.panopto_model.config)
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
            self.panopto_model.config.COURSE = value

    def download_course(self):
        found = self.panopto_model.download_now()
        if not found:
            messagebox.showwarning("Warning!", f"Course not found: {self.panopto_model.config.COURSE}")
        else:
            messagebox.showinfo("Success", "Download successful")

    def set_token(self):
        self.panopto_model.set_token(self.token_entry.get())
        self.reload()


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
