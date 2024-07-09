import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from labels import LabelsManager
from manage_data import ManageData
from search import SearchFunctions
from settings_tab import SettingsTab
from edit_account_tab import EditAccount
from add_account_tab import AddAccountTab
from manage_password import ManagePassword
from import_data import ImportDataFunctions
from notifications import NotificationManager
from backend import key
import backend, menu, os, sys, subprocess, configparser

class TwoFactorAppGUI:
    def __init__(self, master, key):
        # Main window configurations
        self.master = master
        master.title("VerifyVault")
        master.geometry("550x700")
        master.configure(bg="red")
        master.resizable(False, False)
        master.bind("<Control-w>", self.close_window)
        master.bind("<Control-r>", self.restart_program)
        master.bind('<Return>', self.restart_program)
        
        self.check_create_export_folders()
        self.key = backend.load_key()

        # Intializes constructors from other classes
        menu_manager = menu.MenuManager(master)
        self.accounts = backend.load_accounts(key)
        self.notifications = NotificationManager(master)
        self.manage_data = ManageData(master, self.accounts, self.notifications)
        self.import_data = ImportDataFunctions(master, self.accounts, self.notifications)

        # Icon
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, "VerifyVault Logo.png")
        img = Image.open(image_path)
        icon = ImageTk.PhotoImage(img)
        master.iconphoto(True, icon)
        
        self.password_manager = ManagePassword(master)

        # Intializes main window text/frames
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
        self.labels_manager = LabelsManager(master, self.canvas, self.secframe, self.accounts, self.scrollbar, self.import_data, self.on_mousewheel, self.accounts_frame, self.add_account_tab, self.edit_account_tab)
        self.update_labels()
        self.settings_tab = SettingsTab(master, self.accounts, self.notifications)

        # Intializtes buttons
        self.add_button = ttk.Button(self.top_button_frame, text="Add Account", command=self.add_account_tab.add_account, style='Red.TButton')
        self.add_button.pack(side="left", padx=3)
        self.settings_button = ttk.Button(self.top_button_frame, text="Settings", command=self.settings, style='Red.TButton')
        self.settings_button.pack(side="left", padx=3)
        self.restart_button = ttk.Button(self.top_button_frame, text="Restart", command=self.restart_program, style='Red.TButton')
        self.restart_button.pack(side="left", padx=3)

        # Applies Preferences
        self.load_preferences()
        self.apply_preferences()

    # Functions to impelement functionality for the main window
    def settings(self):
        self.settings_tab.settings()
    def import_data(self):
        self.import_data.import_data()
    def close_settings_window(self):
        self.settings_tab.close_settings_window()
    
    # Function to update the accounts on main window
    def update_labels(self, accounts=None):
        self.labels_manager.update_labels(accounts)

    # Function to set the scrollbar
    def on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

    # Function to create the header frame
    def create_header_label(self):
        header_frame = tk.Frame(self.secframe, bg="white")
        header_frame.pack(fill="both", expand=True)

    # Function to create automatic export folders
    def check_create_export_folders(self):
        exported_data_folder = "Exported Data"
        if not os.path.exists(exported_data_folder):
            os.makedirs(exported_data_folder)
        exported_qr_folder = "Exported QR Codes"
        if not os.path.exists(exported_qr_folder):
            os.makedirs(exported_qr_folder)

    # Function to start password reminders on startup (If enabled)
    def start_password_reminders(self):
        self.password_manager.start_password_reminders()

    # Function to load preferences
    def load_preferences(self):
        config = configparser.ConfigParser()
        config.read('preferences.ini')
        self.text_color = config.get('TextColor', 'text_color', fallback='Black')

    # Function to apply preferences
    def apply_preferences(self):
        style = ttk.Style()
        if self.text_color == 'Black':
            style.configure('Red.TButton', foreground='black')
        else:
            style.configure('Red.TButton', foreground='red')
        self.add_button.configure(style='Red.TButton')
        self.settings_button.configure(style='Red.TButton')
        self.restart_button.configure(style='Red.TButton')

    # Function to restart the program
    def restart_program(self, event=None):
        """Restart the current program."""
        if getattr(self, 'master', None):
            try:
                self.master.destroy()
            except tk.TclError as e:
                if "application has been destroyed" not in str(e):
                    raise e
        python = sys.executable
        subprocess.call([python, *sys.argv])

    # Function to close the program
    def close_window(self, event=None):
        self.master.destroy()

