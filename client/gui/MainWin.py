from tkinter import *
from tkinter.ttk import Notebook
from gui.Frames import LoginFrame, FileTransFrame, ContactsFrame, OfflineTransFrame
import settings.config as c


class MainWindow(Tk):
    def __init__(self):
        super().__init__()
        self.language_dict = c.loadLangDict()

        self.notebook = Notebook(self)
        self.notebook.pack()

        self.login_frame = LoginFrame(self)
        self.login_frame.pack()

        self.file_trans_frame = FileTransFrame(self)
        self.file_trans_frame.pack()

        self.contacts_frame = ContactsFrame(self)
        self.contacts_frame.pack()

        self.offline_trans_frame = OfflineTransFrame(self)
        self.offline_trans_frame.pack()

        self.notebook.add(self.login_frame, text=self.language_dict["Configuration"])
        self.notebook.add(self.contacts_frame, text=self.language_dict["Contact"])
        self.notebook.add(self.file_trans_frame, text=self.language_dict["FileTransfer"])
        self.notebook.add(self.offline_trans_frame, text=self.language_dict["OfflineFileTransRequests"])

        self.isOnline_var = BooleanVar(self, value=False)
        self.isOnline_var.trace("w", self._changeFrameState)
        self.after(500, self._changeFrameState)
        self.mainloop()

    def _changeFrameState(self, *args):
        self._changeFrameWidgetsState(self.contacts_frame)
        self._changeFrameWidgetsState(self.file_trans_frame)
        self._changeFrameWidgetsState(self.offline_trans_frame)
        if self.isOnline_var.get():
            self.contacts_frame.refresh_request_labelframe()
            self.file_trans_frame.refresh_contact_labelframe()

    def _changeFrameWidgetsState(self, frame: Frame):
        new_state = self.isOnline_var.get()
        if new_state:
            state = NORMAL
        else:
            state = DISABLED
        for c in frame.winfo_children():
            ctype = c.winfo_class()
            if ctype not in ("Frame", "Labelframe"):
                c.config(state=state)
            else:
                self._changeFrameWidgetsState(c)
