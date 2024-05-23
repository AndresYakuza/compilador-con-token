import tkinter as tk
from tkinter import ttk
from logic import CodeEditorLogic

class CodeEditorApp:
    def __init__(self, master):
        self.master = master
        master.title("COPILADOR")
        master.geometry("800x600")
        master.resizable(False, False)
        self.create_styles()
        self.create_widgets()
        self.logic = CodeEditorLogic(self)

    def create_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TButton', font=('Helvetica', 12), padding=10)
        style.configure('TText', font=('Consolas', 11), padding=10)
        style.configure('TFrame', background='#2e2e2e')
        
        style.map('TButton', background=[('active', '#1e1e1e'), ('!active', '#3e3e3e')], 
                            foreground=[('active', 'white'), ('!active', 'white')])

    def create_widgets(self):
        self.frame = ttk.Frame(self.master)
        self.frame.place(relwidth=1, relheight=1)
        
        self.create_code_editor()
        self.create_console()
        self.create_buttons()

    def create_code_editor(self):
        self.code_editor = tk.Text(self.frame, height=20, width=50, bg='#1e1e1e', fg='white', insertbackground='white')
        self.code_editor.place(relx=0.05, rely=0.05, relwidth=0.65, relheight=0.65)

    def create_console(self):
        self.console = tk.Text(self.frame, state="disabled", height=10, width=50, bg='#1e1e1e', fg='white', insertbackground='white')
        self.console.place(relx=0.05, rely=0.75, relwidth=0.65, relheight=0.2)

    def create_buttons(self):
        self.create_button("Limpiar", self.clear_code, 0.75, 0.2, 0.2, 0.1)
        self.create_button("Validar Código", self.validate_code, 0.75, 0.35, 0.2, 0.1)

    def create_button(self, text, command, relx, rely, relwidth, relheight):
        button = ttk.Button(self.frame, text=text, command=command, style='TButton')
        button.place(relx=relx, rely=rely, relwidth=relwidth, relheight=relheight)

    def compile_code(self):
        self.logic.compile_code() 

    def clear_code(self):
        self.code_editor.delete("1.0", "end")
        self.console.config(state="normal")
        self.console.delete("1.0", "end")
        self.console.config(state="disabled")

    def validate_code(self):
        self.logic.validate_code()  

if __name__ == "__main__":
    root = tk.Tk()
    app = CodeEditorApp(root)
    root.mainloop()