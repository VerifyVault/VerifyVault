import tkinter as tk
from tkinter import ttk, filedialog
import configparser

class ManagePreferences:
    def __init__(self, master, backup_folder_path, backup_frequency, backup_file_format):
        # Initial manage_pref configurations
        self.master = master
        self.backup_folder_path = backup_folder_path
        self.backup_frequency = backup_frequency
        self.backup_file_format = backup_file_format
        self.active_window = None
        self.preferences_window = None

    # Method to open the Preferences window
    def open_preferences_window(self):
        if self.preferences_window and tk.Toplevel.winfo_exists(self.preferences_window):
            self.preferences_window.lift()
            return

        self.preferences_window = tk.Toplevel(self.master)
        self.preferences_window.title("Preferences")
        self.preferences_window.geometry("150x100")
        self.preferences_window.resizable(False, False)
        self.preferences_window.configure(bg="white")

        # Automatic Backups button
        automatic_backups_button = ttk.Button(self.preferences_window, text="Automatic Backups", command=self.open_automatic_backups_window, style='Red.TButton')
        automatic_backups_button.pack(pady=10)

        self.active_window = self.preferences_window

    # Automatic Backups window configurations
    def open_automatic_backups_window(self):
        self.close_active_window()
        automatic_backups_window = tk.Toplevel(self.master)
        automatic_backups_window.title("Automatic Backups")
        automatic_backups_window.geometry("300x420")
        automatic_backups_window.resizable(False, False)
        automatic_backups_window.configure(bg="white")
        self.load_preferences()

        # Selects backup folder
        def select_backup_folder():
            folder_path = filedialog.askdirectory()
            if folder_path:
                self.backup_folder_path = folder_path
                self.save_preferences()
                backup_folder_path_label.config(text=folder_path if folder_path else "None")

        # Configures automatic backups window
        folder_frame = tk.Frame(automatic_backups_window, bg="white")
        folder_frame.pack(fill="both", expand=True, padx=10, pady=10)

        backup_folder_label = tk.Label(folder_frame, text="Backup Folder:", bg="white")
        backup_folder_label.pack(pady=(10, 0))
        backup_folder_path_label = tk.Label(folder_frame, text=self.backup_folder_path if self.backup_folder_path else "None", bg="white")
        backup_folder_path_label.pack(pady=(0, 0))
        backup_folder_button = ttk.Button(folder_frame, text="Select Folder", command=select_backup_folder, style='Red.TButton')
        backup_folder_button.pack(pady=(5, 0))

        separator = ttk.Separator(automatic_backups_window, orient='horizontal')
        separator.pack(fill='x', padx=10, pady=20)
        frequency_label = tk.Label(automatic_backups_window, text="Backup Frequency:", bg="white")
        frequency_label.pack(pady=(0, 15))

        # Configures backup frequency dropdown
        backup_frequencies = ["None", "Every Session"]
        self.backup_frequency_var = tk.StringVar(value=self.backup_frequency)
        self.frequency_dropdown = ttk.Combobox(automatic_backups_window, textvariable=self.backup_frequency_var, values=backup_frequencies, state="readonly")
        self.frequency_dropdown.pack(pady=(0, 30))

        if self.backup_frequency in backup_frequencies:
            self.frequency_dropdown.set(self.backup_frequency)
        else:
            self.frequency_dropdown.set("None")

        separator2 = ttk.Separator(automatic_backups_window, orient='horizontal')
        separator2.pack(fill='x', padx=10, pady=20)
        file_format_label = tk.Label(automatic_backups_window, text="Backup File Format:", bg="white")
        file_format_label.pack(pady=(0, 15))

        # Configures file format dropdown
        backup_file_formats = ["Encrypted", "Unencrypted", "TXT"]
        self.backup_file_format_var = tk.StringVar(value=self.backup_file_format)
        self.file_format_dropdown = ttk.Combobox(automatic_backups_window, textvariable=self.backup_file_format_var, values=backup_file_formats, state="readonly")
        self.file_format_dropdown.pack(pady=(0, 10))

        if self.backup_file_format in backup_file_formats:
            self.file_format_dropdown.set(self.backup_file_format)
        else:
            self.file_format_dropdown.set("Encrypted")
        save_button = ttk.Button(automatic_backups_window, text="Save", command=self.save_backup_format, style='Red.TButton')
        save_button.pack(pady=(0, 30))

        self.active_window = automatic_backups_window

    # Saves/Loads automatic backup preferences
    def save_backup_format(self):
        backup_format = self.backup_file_format_var.get() 
        self.backup_file_format = backup_format
        self.backup_frequency = self.backup_frequency_var.get()
        self.save_preferences()
        self.close_active_window()
    def save_preferences(self):
        config = configparser.ConfigParser()
        config['AutomaticBackups'] = {
            'backup_folder_path': self.backup_folder_path if self.backup_folder_path else "",
            'backup_frequency': self.backup_frequency if self.backup_frequency else "None",
            'backup_file_format': self.backup_file_format if self.backup_file_format else "Encrypted"
        }

        with open('preferences.ini', 'w') as configfile:
            config.write(configfile)
    def load_preferences(self):
        config = configparser.ConfigParser()
        config.read('preferences.ini')

        self.backup_folder_path = config.get('AutomaticBackups', 'backup_folder_path', fallback=None)
        self.backup_frequency = config.get('AutomaticBackups', 'backup_frequency', fallback="None")
        self.backup_file_format = config.get('AutomaticBackups', 'backup_file_format', fallback="Encrypted")

    # Closes active window
    def close_active_window(self):
        if self.active_window:
            self.active_window.destroy()
