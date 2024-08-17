import tkinter as tk
from customtkinter import *
from backend import key
from labels import LabelsManager
from search import SearchFunctions
from settings_tab import SettingsTab
from add_account_tab import AddAccountTab
from manage_security import ManageSecurity
from recycle_bin import RecycleBinFunctions
from PIL import Image
from ttkbootstrap.tooltip import ToolTip
import backend, menu, os, sys, subprocess, configparser

class TwoFactorAppGUI:
    def __init__(self, master, key):
        # Main window configurations
        self.master = master
        master.title("VerifyVault")
        master.geometry("1300x700")
        master.resizable(False, False)
        master.iconbitmap('images/VerifyVaultLogo.ico')
        master.bind("<Control-w>", self.close_window)
        
        self.load_preferences()
        self.check_create_export_folders()
        self.key = backend.load_key()

        if self.dark_mode == 'on':
            set_appearance_mode("dark")
        else:
            set_appearance_mode("light")

        # Intializes main window variables
        self.search_var = tk.StringVar()
        self.accounts = backend.load_accounts(key)

        self.top_button_frame = CTkFrame(master, border_width=2, corner_radius=2, width=1300, height=70, fg_color="transparent")
        self.top_button_frame.pack(expand=True, anchor="n")

        middle_frame = CTkFrame(master, corner_radius=2, width=800, height=700)
        middle_frame.pack(side="left")
        right_frame = CTkFrame(master, border_width=0, corner_radius=2, width=500, height=700)
        right_frame.pack(side="right")

        logo = CTkImage(light_image=Image.open("images/VVLogo.png"), dark_image=Image.open("images/VVDarkLogo.png"), size=(400,400))
        logo_label = CTkLabel(right_frame, text="", image=logo)
        logo_label.place(relx=0.5, rely=0.4, anchor="center")

        menu_manager = menu.MenuManager(master, right_frame)
        follow_button = CTkButton(right_frame, command=menu_manager.socials, text="Follow", font=("Helvetica", 20, "bold"), fg_color="white", hover_color="red", width=150, height=36, border_width=2, corner_radius=2, text_color="black", cursor='hand2')
        follow_button.place(relx=0.35, rely=0.6, anchor="center")
        donate_button = CTkButton(right_frame, text="Donate", command=menu_manager.donations, font=("Helvetica", 20, "bold"), fg_color="white", hover_color="red", width=150, height=36, border_width=2, corner_radius=2, text_color="black", cursor='hand2')
        donate_button.place(relx=0.68, rely=0.6, anchor="center")

        # Intializes constructors from other classes
        self.search_functions = SearchFunctions(master, self.search_var, self.update_labels, self.top_button_frame, key)
        self.labels_manager = LabelsManager(master, self.accounts, middle_frame, right_frame, self.top_button_frame)
        self.settings_tab = SettingsTab(master, self.accounts, right_frame)
        self.recycle_bin = RecycleBinFunctions(master, self.accounts, self.update_labels, right_frame)
        self.update_labels()

        self.groups = self.labels_manager.load_groups()
        self.add_account_tab = AddAccountTab(master, right_frame, self.accounts, self.update_labels, self.search_functions, self.groups)

        # Intializtes buttons
        self.add_button = CTkButton(self.top_button_frame, text="➕", command=self.add_account_tab.add_account, fg_color="white", hover_color="red", text_color="black", width=100, height=40, border_width=2, corner_radius=2, cursor="hand2")
        self.add_button.place(relx=0.02, rely=0.2, anchor="nw")
        self.recycle_button = CTkButton(self.top_button_frame, text="     🗑️", command=self.recycle_bin.manage_recycle_bin, fg_color="white", hover_color="red", text_color="black", width=100, height=40, border_width=2, corner_radius=2, font=("Helvetica", 16), cursor="hand2")
        self.recycle_button.place(relx=0.12, rely=0.2, anchor="nw")
        self.settings_button = CTkButton(self.top_button_frame, text="⚙️", command=self.settings_tab.settings, fg_color="white", hover_color="red", text_color="black", width=100, height=40, border_width=2, corner_radius=2, cursor="hand2")
        self.settings_button.place(relx=0.88, rely=0.2, anchor="ne")
        self.restart_button = CTkButton(self.top_button_frame, text="🔄", command=self.restart_program, fg_color="white", hover_color="red", text_color="black", width=100, height=40, border_width=2, corner_radius=2, font=("Helvetica", 16), cursor="hand2")
        self.restart_button.place(relx=0.98, rely=0.2, anchor="ne")

        ToolTip(self.add_button, text="Add Account")
        ToolTip(self.recycle_button, text="Recycle Bin")
        ToolTip(self.settings_button, text="Settings")
        ToolTip(self.restart_button, text="Restart")

        self.manage_security = ManageSecurity(master, right_frame)
        self.master.bind("<Map>", self.manage_security.on_restore)
        self.master.bind("<Unmap>", self.manage_security.on_minimize)

    # Function to update the accounts on main window
    def update_labels(self, accounts=None):
        self.labels_manager.update_labels(accounts)

    # Function to create export folders
    def check_create_export_folders(self):
        exported_data_folder = "Exported Data"
        if not os.path.exists(exported_data_folder):
            os.makedirs(exported_data_folder)

    # Function to load preferences
    def load_preferences(self):
        config = configparser.ConfigParser()
        config.read('preferences.ini')
        self.dark_mode = config.get('Preferences', 'dark_mode', fallback=None)

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
        import main
        self.master.destroy()
        main.main()

