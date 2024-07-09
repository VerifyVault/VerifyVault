import tkinter as tk
from tkinter import ttk, filedialog
from manage_password import ManagePassword
import configparser

class ManagePreferences:
    def __init__(self, master, backup_folder_path, backup_file_format):
        # Initial manage_pref configurations
        self.master = master
        self.backup_folder_path = backup_folder_path
        self.backup_file_format = backup_file_format
        self.text_color = "Black"
        self.active_window = None
        self.preferences_window = None

        self.load_preferences()

    # Preferences window configurations
    def open_preferences_window(self):
        self.close_active_window()
        if self.preferences_window and tk.Toplevel.winfo_exists(self.preferences_window):
            self.preferences_window.lift()
            return
        self.preferences_window = tk.Toplevel(self.master)
        self.preferences_window.title("Preferences")
        self.preferences_window.geometry("200x150")
        self.preferences_window.resizable(False, False)
        self.preferences_window.configure(bg="white")

        customize_button = ttk.Button(self.preferences_window, text="Customize", command=self.open_customize_window, style='Red.TButton')
        customize_button.pack(pady=5)
        automatic_backups_button = ttk.Button(self.preferences_window, text="Automatic Backups", command=self.open_automatic_backups_window, style='Red.TButton')
        automatic_backups_button.pack(pady=5)
        password_management_button = ttk.Button(self.preferences_window, text="Password Management", command=self.open_password_management_window, style='Red.TButton')
        password_management_button.pack(pady=5)
        self.active_window = self.preferences_window

    # Function to open Password Management window
    def open_password_management_window(self):
        self.close_active_window()
        password_manager = ManagePassword(self.master)
        password_manager.manage_password()
        self.active_window = password_manager.active_window

    # Automatic Backups window configurations
    def open_automatic_backups_window(self):
        self.close_active_window()
        automatic_backups_window = tk.Toplevel(self.master)
        automatic_backups_window.title("Automatic Backups")
        automatic_backups_window.geometry("300x300")
        automatic_backups_window.resizable(False, False)
        automatic_backups_window.configure(bg="white")

        self.load_preferences()
        self.active_window = automatic_backups_window

        # Function to prompt the user to select a backup folder
        def select_backup_folder():
            folder_path = filedialog.askdirectory()
            if folder_path:
                self.backup_folder_path = folder_path
                self.save_preferences()
                backup_folder_path_label.config(text=folder_path if folder_path else "None")

        # Configures backup folder frame 
        folder_frame = tk.Frame(automatic_backups_window, bg="white")
        folder_frame.pack(fill="both", expand=True, padx=10, pady=10)

        backup_folder_label = tk.Label(folder_frame, text="Backup Folder:", bg="white", font=("Helvetica", 12, "bold"))
        backup_folder_label.pack(pady=(0, 10))

        backup_folder_path_label = tk.Label(folder_frame, text=self.backup_folder_path if self.backup_folder_path else "None", bg="white")
        backup_folder_path_label.pack(pady=(0, 0))

        backup_folder_button = ttk.Button(folder_frame, text="Select Folder", command=select_backup_folder, style='Red.TButton')
        backup_folder_button.pack(pady=(5, 0))

        file_format_label = tk.Label(folder_frame, text="Backup File Type:", bg="white", font=("Helvetica", 12, "bold"))
        file_format_label.pack(pady=(10, 0))

        # Create a frame to hold the dropdown and save button
        format_frame = tk.Frame(folder_frame, bg="white")
        format_frame.pack(pady=(0, 10))

        # Configures file format dropdown
        backup_file_formats = ["Encrypted", "Unencrypted", "TXT Encrypted", "TXT Unencrypted", "Secrets", "QR Codes"]
        self.backup_file_format_var = tk.StringVar(value=self.backup_file_format)
        self.file_format_dropdown = ttk.Combobox(format_frame, textvariable=self.backup_file_format_var, values=backup_file_formats, state="readonly")
        self.file_format_dropdown.pack(side=tk.LEFT, padx=10)

        if self.backup_file_format in backup_file_formats:
            self.file_format_dropdown.set(self.backup_file_format)
        else:
            self.file_format_dropdown.set("Encrypted")

        save_button = ttk.Button(format_frame, text="Save", command=self.save_backup_format, style='Red.TButton')
        save_button.pack(padx=10)

        # Toggle button for enabling/disabling automatic backups
        self.toggle_button_text = tk.StringVar()
        self.toggle_button_text.set("Automatic Backups are ENABLED" if self.automatic_backups_enabled else "Automatic Backups are DISABLED")
        toggle_button = ttk.Button(folder_frame, textvariable=self.toggle_button_text, command=self.toggle_automatic_backups, style='Red.TButton')
        toggle_button.pack(pady=(10, 0))
        self.active_window = automatic_backups_window

    # Function to toggle automatic backups
    def toggle_automatic_backups(self):
        self.automatic_backups_enabled = not self.automatic_backups_enabled
        self.toggle_button_text.set("Automatic Backups are ENABLED" if self.automatic_backups_enabled else "Automatic Backups are DISABLED")
        self.save_preferences()

    # Function to open customize window
    def open_customize_window(self):
        self.close_active_window()
        self.customize_window = tk.Toplevel(self.master)
        self.customize_window.title("Customize VerifyVault")
        self.customize_window.geometry("250x100")
        self.customize_window.resizable(False, False)
        self.customize_window.configure(bg="white")

        customize_frame = tk.Frame(self.customize_window, bg="white")
        customize_frame.pack(fill="both", expand=True)

        self.load_preferences()

        style = ttk.Style()
        if self.text_color == "Black":
            style.configure('Red.TButton', foreground='black')
        else:
            style.configure('Red.TButton', foreground='red')

        # Button for toggling text color
        self.text_color_var = tk.StringVar(value=self.text_color)
        self.toggle_button = ttk.Button(customize_frame, text=f"Customize Text Color - {self.text_color}", command=self.toggle_text_color, style='Red.TButton')
        self.toggle_button.pack(pady=10)

        self.active_window = self.customize_window

    # Function to toggle text color
    def toggle_text_color(self):
        if self.text_color == "Black":
            self.text_color = "Red"
        else:
            self.text_color = "Black"

        # Changes text color
        style = ttk.Style()
        if self.text_color == "Black":
            style.configure('Red.TButton', foreground='black')
        else:
            style.configure('Red.TButton', foreground='red')

        self.toggle_button.config(text=f"Customize Text Color - {self.text_color}")
        self.save_text_color()

    # Function to save text color preference
    def save_text_color(self):
        config = configparser.ConfigParser()
        config.read('preferences.ini')

        # Update only the text_color section
        config.set('TextColor', 'text_color', self.text_color)

        # Write the entire configuration back to preferences.ini
        with open('preferences.ini', 'w') as configfile:
            config.write(configfile)

    # Functions to save/load automatic backup preferences
    def save_backup_format(self):
        backup_format = self.backup_file_format_var.get() 
        self.backup_file_format = backup_format
        
        if self.backup_file_format in ["Encrypted", "Unencrypted", "TXT Encrypted", "TXT Unencrypted", "Secrets"] and (self.backup_folder_path == "None" or self.backup_folder_path == "Exported QR Codes"):
            self.backup_folder_path = "Exported Data"
        elif self.backup_file_format == "QR Codes" and (self.backup_folder_path == "None" or self.backup_folder_path == "Exported Data"):
            self.backup_folder_path = "Exported QR Codes"
        
        self.save_preferences()
        self.close_active_window()

    # Function to save preferences
    def save_preferences(self):
        config = configparser.ConfigParser()
        config['AutomaticBackups'] = {
            'backup_folder_path': self.backup_folder_path if self.backup_folder_path else "",
            'backup_file_format': self.backup_file_format if self.backup_file_format else "Encrypted",
            'automatic_backups_enabled': str(self.automatic_backups_enabled)
        }
        config['TextColor'] = {
            'text_color': self.text_color
        }

        with open('preferences.ini', 'w') as configfile:
            config.write(configfile)

    # Function to load preferences
    def load_preferences(self):
        config = configparser.ConfigParser()
        config.read('preferences.ini')

        self.backup_folder_path = config.get('AutomaticBackups', 'backup_folder_path', fallback=None)
        self.backup_file_format = config.get('AutomaticBackups', 'backup_file_format', fallback="Encrypted")
        self.text_color = config.get('TextColor', 'text_color', fallback="Black")
        self.automatic_backups_enabled = config.getboolean('AutomaticBackups', 'automatic_backups_enabled', fallback=False)

    # Function to close the active window
    def close_active_window(self):
        if self.active_window:
            self.active_window.destroy()
