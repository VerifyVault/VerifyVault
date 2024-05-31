import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk, messagebox, simpledialog, filedialog
import backend, menu, shutil, qrcode, pyotp, time, os, pyperclip, binascii, json
from labels import LabelsManager
from search import SearchFunctions
from settings_tab import SettingsTab
from add_account_tab import AddAccountTab
from notifications import NotificationManager

class TwoFactorAppGUI:
    def __init__(self, master):
        #Main Menu window Configurations
        self.master = master
        master.title("VerifyVault")
        master.geometry("700x700")
        master.configure(bg="red")
        master.resizable(False, False)

        #Icon
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, "VerifyVault Logo.png")
        img = Image.open(image_path)
        icon = ImageTk.PhotoImage(img)
        master.iconphoto(True, icon)

        #Intializting main text/frames
        self.search_var = tk.StringVar()
        self.title_font = ("Helvetica", 20, "bold")
        self.accounts = backend.load_accounts()

        self.label = tk.Label(master, text="VerifyVault", font=self.title_font, bg="red", fg="white")
        self.label.pack()
        self.add_separator = tk.Frame(master, height=1, bg="black")
        self.add_separator.pack(fill="x", padx=10, pady=0)

        self.top_button_frame = tk.Frame(master, bg="red", bd=1)
        self.top_button_frame.pack(side="top", fill="x", padx=5, pady=5)
        self.button_style = ttk.Style()
        self.button_style.configure('Red.TButton', background='white', padding=5, relief="flat", borderwidth=0, bordercolor="red")

        self.canvas_frame = tk.Frame(master)
        self.canvas_frame.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(self.canvas_frame, bg="white")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.secframe = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.secframe, anchor="nw")
        self.accounts_frame = tk.Frame(self.secframe, pady=10, padx=20, bg="white")
        self.accounts_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        #Intializting constructors from other classes
        self.search_functions = SearchFunctions(master, self.search_var, self.update_labels, self.top_button_frame, self.accounts)
        self.notifications = NotificationManager(master)
        self.add_account_tab = AddAccountTab(master, self.canvas, self.accounts, self.notifications, self.update_labels, self.search_functions)
        self.create_header_label()
        self.labels_manager = LabelsManager(master, self.canvas, self.secframe, self.accounts, self.scrollbar, self.notifications, self.on_mousewheel, self.accounts_frame, self.add_account_tab)
        self.update_labels()
        self.settings_tab = SettingsTab(master, self.accounts, self.notifications, self.update_labels, self.search_functions)
        
        #Intializting buttons
        self.add_button = ttk.Button(self.top_button_frame, text="Add Account", command=self.add_account_tab.add_account, style='Red.TButton')
        self.add_button.pack(side="left", padx=10)
        self.settings_button = ttk.Button(self.top_button_frame, text="Settings", command=self.settings, style='Red.TButton')
        self.settings_button.pack(side="left", padx=10)
        self.exit_button = ttk.Button(self.top_button_frame, text="Exit", command=self.close_window, style='Red.TButton')
        self.exit_button.pack(side="left", padx=10)

        #Setting others windows to closed
        self.name_window_open = False 
        self.settings_window_open = False
        self.export_window_open = False
        self.edit_window_open = False
        self.edit_name_window_open = False
        self.edit_name_window = None

    #Calling functions from settings_tab.py
    def settings(self):
        self.settings_tab.settings()

    def export_and_close(self):
        self.settings_tab.export_and_close()

    def export_json(self):
        self.settings_tab.export_json()

    def import_data(self):
        self.settings_tab.import_data()

    def close_settings_window(self):
        self.settings_tab.close_settings_window() 

    #TOTP copied notification
    def copy_totp(self, event, totp_text):
        pyperclip.copy(totp_text)
        self.notifications.show_notification("TOTP copied to clipboard!")
    
    #Updates accounts on main screen
    def update_labels(self, accounts=None):
        self.labels_manager.update_labels(accounts)

    #Setting scrollbar
    def on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

    #Creates header frame
    def create_header_label(self):
        header_frame = tk.Frame(self.secframe, bg="white")
        header_frame.pack(fill="both", expand=True)

    #Exit Button
    def close_window(self):
        self.master.destroy()

def main():
    root = tk.Tk()
    menu_manager = menu.MenuManager(root)
    TwoFactorAppGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
