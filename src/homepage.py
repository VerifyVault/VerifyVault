import tkinter as tk
from customtkinter import *
from groups import GroupsFunctions
from settings import SettingsTab
from display import DisplayFunctions
from add_account import AddAccountFunctions
from recycle_bin import RecycleBinFunctions
from account_info import AccountInfoFunctions
from security_backend import SecurityBackendFunctions
from PIL import Image
from ttkbootstrap.tooltip import ToolTip
import backend, links, os, sys, subprocess, configparser

class HomepageFunctions:
    def __init__(self, master, key):
        # Home window configurations
        self.master = master
        master.title("VerifyVault") # Set window title
        master.geometry("1300x700") # Define window size
        master.resizable(False, False) # Prevent resizing
        master.iconbitmap('images/VerifyVaultLogo.ico') # Set window icon
        master.bind("<Control-w>", self.close_window) # Bind Ctrl+W to close window
        #master.bind("<Return>", self.restart_program) # Bind Enter to restart program
        
        # Check if dark mode is enabled and set appearance
        self.load_preferences() # Load user preferences
        set_appearance_mode("dark" if self.dark_mode == 'on' else "light") # Set appearance mode

        # Initialize home window variables
        self.search_var = tk.StringVar() # Create a StringVar for search functionality
        self.key, self.accounts = backend.load_key(), backend.load_accounts(key) # Load encryption key and accounts

        # Initialize home window frames
        top_frame = CTkFrame(master, border_width=2, corner_radius=2, width=1300, height=70, fg_color="transparent")
        left_frame = CTkFrame(master, corner_radius=2, width=800, height=700)
        right_frame = CTkFrame(master, border_width=0, corner_radius=2, width=500, height=700)
        
        # Pack frames into the main window
        top_frame.pack(expand=True, anchor="n")
        left_frame.pack(side="left")    
        right_frame.pack(side="right")

        """Initialize buttons on the home window."""
        # Help button
        help_button = CTkButton(right_frame, command=self.open_help_window, text="❓", font=("Helvetica", 20, "bold"), fg_color="white", hover_color="red", width=30, height=10, border_width=2, corner_radius=2, text_color="black", cursor='hand2')
        help_button.place(relx=0.9, rely=0.02, anchor="n")

        # Logo
        logo = CTkImage(light_image=Image.open("images/VVLogo.png"), dark_image=Image.open("images/VVDarkLogo.png"), size=(400,400))
        logo_label = CTkLabel(right_frame, text="", image=logo).place(relx=0.5, rely=0.4, anchor="center")

        # Links manager for handling copying links
        links_manager = links.LinksManager(master, right_frame)

        # Follow button
        follow_button = CTkButton(right_frame, command=links_manager.socials, text="Follow", font=("Helvetica", 20, "bold"), fg_color="white", hover_color="red", width=150, height=36, border_width=2, corner_radius=2, text_color="black", cursor='hand2').place(relx=0.35, rely=0.6, anchor="center")
        
        # Donate button
        donate_button = CTkButton(right_frame, text="Donate", command=links_manager.donations, font=("Helvetica", 20, "bold"), fg_color="white", hover_color="red", width=150, height=36, border_width=2, corner_radius=2, text_color="black", cursor='hand2').place(relx=0.68, rely=0.6, anchor="center")

        # Create instances of functional classes
        settings = SettingsTab(master, self.accounts, right_frame, self.update_labels)
        recycle_bin = RecycleBinFunctions(master, self.accounts, right_frame, self.update_labels)

        self.groups_function = GroupsFunctions(master, self.accounts, top_frame, self.update_labels)
        groups = self.groups_function.load_groups()

        add_account = AddAccountFunctions(master, self.accounts, right_frame, self.update_labels, groups)
        self.account_info = AccountInfoFunctions(master, groups, self.accounts, right_frame, self.update_labels)

        self.display = DisplayFunctions(master, groups, self.accounts, top_frame, left_frame, right_frame)
        self.update_labels()

        # Initialize buttons in the top frame
        buttons = [
            {"text": "➕", "command": add_account.add_account, "relx": 0.02, "rely": 0.2, "tooltip": "Add Account", "font": None},
            {"text": "     🗑️", "command": recycle_bin.manage_recycle_bin, "relx": 0.12, "rely": 0.2, "tooltip": "Recycle Bin", "font": ("Helvetica", 16)},
            {"text": "⚙️", "command": settings.settings_options, "relx": 0.88, "rely": 0.2, "tooltip": "Settings", "font": None},
            {"text": "🔄", "command": self.restart_program, "relx": 0.98, "rely": 0.2, "tooltip": "Restart", "font": ("Helvetica", 16)},
        ]

        # Create and place buttons dynamically
        for btn in buttons:
            button = CTkButton(top_frame, text=btn["text"], command=btn["command"], fg_color="white", hover_color="red", text_color="black", width=100, height=40, border_width=2, corner_radius=2, font=btn["font"], cursor="hand2")
            button.place(relx=btn["relx"], rely=btn["rely"], anchor="nw" if btn["text"] != "⚙️" and btn["text"] != "🔄" else "ne")
            ToolTip(button, text=btn["tooltip"])  # Add tooltips for buttons

        # Create a search entry field with specific dimensions and styling
        search_entry = CTkEntry(top_frame, width=550, height=40, corner_radius=2, textvariable=self.search_var, placeholder_text="🔍 Search Accounts", border_color="black")
        search_entry.place(relx=0.43, rely=0.5, anchor="center")
        search_entry.bind("<KeyRelease>", self.search_accounts)

        # Configure password lock functionality
        security_backend = SecurityBackendFunctions(master, self.update_labels)
        master.bind("<Map>", security_backend.on_restore)
        master.bind("<Unmap>", security_backend.on_minimize)

    # Function to update the accounts
    def update_labels(self, accounts=None):
        self.display.update_labels(accounts)

    # Function to get the current search query and the selected group
    def search_accounts(self, event):
        query = self.search_var.get().lower()
        group = self.groups_function.get_group()

        # Filter accounts based on the selected group
        filtered_by_group = self.accounts if group == "All Accounts" else {name: info for name, info in self.accounts.items() if info['group'] == group or info['group'] is None}

        # Further filter accounts based on the search query
        filtered_accounts = {name: info for name, info in filtered_by_group.items() if query in name.lower() and not info.get("deleted")} if query else filtered_by_group

        # Update the displayed accounts with the filtered results
        self.update_labels(filtered_accounts)

    # Function to open the help window
    def open_help_window(self):
        help_window = CTkToplevel(self.master)
        help_window.geometry("600x600")
        help_window.title("VerifyVault Navigation Help")
        help_window.resizable(False, False)
        help_window.after(250, lambda: help_window.iconbitmap('images/VerifyVaultLogo.ico'))
        help_window.grab_set()

        # Help text content
        help_text = (
            "- Add Account: Add new account.\n\n"
            "- Recycle Bin: Manage deleted accounts.\n\n"
            "- Settings: Configure application preferences.\n\n"
            "- Restart: Restart VerifyVault.\n\n"
            "- Follow: View/Follow VerifyVault social media pages.\n\n"
            "- Donate: View/Donate to VerifyVault.\n\n"
            "- To copy a URL/address, left click it.\n\n"
            "- To open a URL, right click it.\n\n"
            "- Delete a Group: Select the group and right click it.\n\n"
            "- Shortcut to restart program: Hit the Enter key on your keyboard"
        )

        # Create labels for the help window
        title_label = CTkLabel(help_window, text="VerifyVault Navigation Help", font=("Helvetica", 30, "bold", "underline")).place(relx=0.5, rely=0.05, anchor="center")
        help_info = CTkLabel(help_window, text=help_text, font=("Helvetica", 20)).place(relx=0.02, rely=0.1, anchor="nw")

    # Function to load preferences
    def load_preferences(self):
        config = configparser.ConfigParser()
        config.read('preferences.ini')
        self.dark_mode = config.get('Preferences', 'dark_mode', fallback=None)

    # Function to restart the program
    def restart_program(self, event=None):
        if getattr(self, 'master', None):
            try:
                self.master.destroy() # Close the current window
            except tk.TclError as e:
                if "application has been destroyed" not in str(e):
                    raise e
        subprocess.call([sys.executable, *sys.argv]) # Restart the program

    # Function to close the program
    def close_window(self, event=None):
        self.master.destroy()

