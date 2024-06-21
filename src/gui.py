import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from labels import LabelsManager
from manage_data import ManageData
from search import SearchFunctions
from settings_tab import SettingsTab
from add_account_tab import AddAccountTab
from edit_account_tab import EditAccount
from notifications import NotificationManager
import backend, menu, os, pyperclip, json, sys, subprocess

class TwoFactorAppGUI:
    def __init__(self, master, key):
        # Main menu window Configurations
        self.master = master
        master.title("VerifyVault")
        master.geometry("550x700")
        master.configure(bg="red")
        master.resizable(False, False)
        master.bind("<Control-w>", self.close_window)
        menu_manager = menu.MenuManager(master)
        self.accounts = backend.load_accounts(key)
        self.notifications = NotificationManager(master)
        self.manage_data = ManageData(master, self.accounts)

        # Icon
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, "VerifyVault Logo.png")
        img = Image.open(image_path)
        icon = ImageTk.PhotoImage(img)
        master.iconphoto(True, icon)

        # Intializes main text/frames
        self.search_var = tk.StringVar()
        self.title_font = ("Helvetica", 20, "bold")
        self.accounts = backend.load_accounts(key)
        self.edit_account_tab = EditAccount(master, key, self.accounts, self.notifications)

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
        self.secframe.pack(fill="both", expand=True)
        self.canvas.create_window((0, 0), window=self.secframe, anchor="nw")
        self.accounts_frame = tk.Frame(self.secframe, pady=10, padx=20, bg="white")
        self.accounts_frame.pack(fill="both", expand=True, padx=55, pady=(0, 10))

        # Intializes constructors from other classes
        self.search_functions = SearchFunctions(master, self.search_var, self.update_labels, self.top_button_frame, key)
        self.notifications = NotificationManager(master)
        self.add_account_tab = AddAccountTab(master, self.canvas, self.accounts, self.notifications, self.update_labels, self.search_functions)
        self.create_header_label()
        self.labels_manager = LabelsManager(master, self.canvas, self.secframe, self.accounts, self.scrollbar, self.import_data, self.notifications, self.on_mousewheel, self.accounts_frame, self.add_account_tab, self.edit_account_tab)
        self.update_labels()
        self.settings_tab = SettingsTab(master, self.accounts, self.notifications, self.update_labels, self.search_functions)

        # Intializtes buttons
        self.add_button = ttk.Button(self.top_button_frame, text="Add Account", command=self.add_account_tab.add_account, style='Red.TButton')
        self.add_button.pack(side="left", padx=3)
        self.settings_button = ttk.Button(self.top_button_frame, text="Settings", command=self.settings, style='Red.TButton')
        self.settings_button.pack(side="left", padx=3)
        self.restart_button = ttk.Button(self.top_button_frame, text="Restart", command=self.restart_program, style='Red.TButton')
        self.restart_button.pack(side="left", padx=3)

        # Sets other windows to closed
        self.name_window_open = False 
        self.settings_window_open = False
        self.export_window_open = False
        self.edit_window_open = False
        self.edit_name_window_open = False
        self.edit_name_window = None

    # Calis functions from the settings tab
    def settings(self):
        self.settings_tab.settings()
    def export_and_close(self):
        self.settings_tab.export_and_close()
    def export_json(self):
        self.settings_tab.export_json()
    def import_data(self):
        self.manage_data.import_data()
    def close_settings_window(self):
        self.settings_tab.close_settings_window()
    
    # Updates accounts on main screen
    def update_labels(self, accounts=None):
        self.labels_manager.update_labels(accounts)

    # Sets scrollbar
    def on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

    # Creates header frame
    def create_header_label(self):
        header_frame = tk.Frame(self.secframe, bg="white")
        header_frame.pack(fill="both", expand=True)

    # Restarts program
    def restart_program(self):
        """Restart the current program."""
        if getattr(self, 'master', None):
            try:
                self.master.destroy()
            except tk.TclError as e:
                if "application has been destroyed" not in str(e):
                    raise e
        python = sys.executable
        subprocess.call([python, *sys.argv])

    # Exit Program
    def close_window(self, event=None):
        self.master.destroy()
        