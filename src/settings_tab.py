import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image
#from pyzbar.pyzbar import decode
from labels import LabelsManager
from search import SearchFunctions
from manage_data import ManageData
from password import PasswordManager
from manage_pref import ManagePreferences
from manage_password import ManagePassword
from backend import load_key, load_accounts
import json, os, shutil, time, schedule, configparser, threading, glob

class SettingsTab:
    def __init__(self, master, accounts, notifications, update_labels, search_functions):
        # Initial settings_tab configurations
        self.master = master
        self.accounts = accounts
        self.notifications = notifications
        self.update_labels = update_labels
        self.search_functions = search_functions
        self.password_manager = PasswordManager()
        self.load_preferences()

        self.backup_folder_path = None
        self.backup_frequency = None
        self.backup_file_format = None
        self.last_backup_time = None
        self.active_window = None
        self.password_set = False
        self.passowrd = None
        self.key = None

        self.manage_password_instance = ManagePassword(master)
        self.manage_data_handler = ManageData(self.master, self.accounts)
        self.manage_preferences_instance = ManagePreferences(master, self.backup_folder_path, self.backup_frequency, self.backup_file_format)

        self.key = load_key()
        self.setup_backup_schedule_on_startup()

        self.backup_frequency_var = tk.StringVar()
        self.frequency_dropdown = None 

    # Closes active window
    def close_active_window(self):
        if self.active_window:
            self.active_window.destroy()

    # Settings window configurations
    def settings(self):
        self.close_active_window()
        self.active_window = tk.Toplevel(self.master)
        self.active_window.title("Settings")
        self.active_window.geometry("200x150")
        self.active_window.resizable(False, False)
        self.active_window.configure(bg="white")

        password_button = ttk.Button(self.active_window, text="Manage Password", command=self.manage_password_instance.manage_password, style='Red.TButton')
        password_button.pack(pady=5)
        data_button = ttk.Button(self.active_window, text="Manage Data", command=self.manage_data_handler.manage_data, style='Red.TButton')
        data_button.pack(pady=5)
        preferences_button = ttk.Button(self.active_window, text="Manage Preferences", command=self.manage_preferences_instance.open_preferences_window, style='Red.TButton')
        preferences_button.pack(pady=5)
        
    # Loads preferences
    def load_preferences(self):
        config = configparser.ConfigParser()
        config.read('preferences.ini')

        self.backup_folder_path = config.get('AutomaticBackups', 'backup_folder_path', fallback=None)
        self.backup_frequency = config.get('AutomaticBackups', 'backup_frequency', fallback="None")
        self.backup_file_format = config.get('AutomaticBackups', 'backup_file_format', fallback="Encrypted")  # Read backup_file_format

    # Schedules/performs automatic backups
    def setup_backup_schedule_on_startup(self):
        self.load_preferences()
        self.backup_frequency_var = tk.StringVar(value=self.backup_frequency)

        if self.backup_frequency and self.backup_frequency != "None":
            self.setup_backup_schedule()
    def setup_backup_schedule(self):
        schedule.clear()

        if self.backup_frequency == "Every Session":
            self.perform_automatic_backup()

        threading.Thread(target=self.schedule_runner, daemon=True).start()
    def schedule_runner(self):
        while True:
            schedule.run_pending()
            time.sleep(60)
    def perform_automatic_backup(self):
        import backend
        current_time = time.strftime("%Y-%m-%d_%H%M", time.localtime())
        if self.backup_folder_path:
            src_file = "data.vv"
            dest_file_base = f"vv_automatic_export_{current_time}"
            dest_file = os.path.join(self.backup_folder_path, dest_file_base)

            if self.backup_file_format == "Encrypted":
                    shutil.copy("data.vv", dest_file)
                    os.chmod(dest_file, 0o700)

            elif self.backup_file_format == "Unencrypted":
                key = backend.load_key()
                accounts = backend.load_accounts(key)  

                try:
                    with open(dest_file, 'w') as file_path:
                        json.dump(accounts, file_path, indent=4)
                except Exception as e:
                    messagebox.showerror("Error", f"Error exporting unencrypted JSON: {str(e)}")
            
            elif self.backup_file_format == "TXT":
                txt_file_path = os.path.join(self.backup_folder_path, f"{dest_file_base}.txt")
                try:
                    with open(src_file, 'rb') as src_file_path:
                        encrypted_data = src_file_path.read()
                        key = backend.load_key()
                        decrypted_data = backend.decrypt_message(encrypted_data, key)
                    
                    with open(txt_file_path, 'w') as file_path:
                        file_path.write(decrypted_data)
                except Exception as e:
                    print(f"Error exporting TXT: {str(e)}")
                    messagebox.showerror("Error exporting TXT", str(e))

            backup_files = glob.glob(os.path.join(self.backup_folder_path, "*.json"))
            if len(backup_files) > 5:
                backup_files.sort(key=os.path.getmtime)
                oldest_backup = backup_files[0]
                os.remove(oldest_backup)

    # Closes settings window
    def close_settings_window(self):
        if getattr(self, 'active_window', None):
            try:
                self.active_window.destroy()
            except tk.TclError as e:
                if "application has been destroyed" not in str(e):
                    raise e
