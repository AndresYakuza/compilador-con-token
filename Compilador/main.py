from tkinter import Tk
from view import CodeEditorApp
from logic import CodeEditorLogic

if __name__ == "__main__":
    root = Tk()
    gui = CodeEditorApp(root)
    logic = CodeEditorLogic(gui)
    root.mainloop()