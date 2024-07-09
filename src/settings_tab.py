import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image
from manage_data import ManageData
from manage_pref import ManagePreferences
from backend import load_key, load_accounts
from notifications import NotificationFrame, NotificationManager
import json, os, shutil, time, schedule, configparser, threading, glob, qrcode, pyotp

class SettingsTab:
    def __init__(self, master, accounts, notifications):
        # settings_tab configurations
        self.master = master
        self.accounts = accounts
        self.load_preferences()
        
        self.backup_folder_path = None
        self.backup_file_format = None
        self.notifications = notifications
        self.key = None
        self.active_window = None

        self.manage_data_handler = ManageData(self.master, self.accounts, self.notifications)
        self.manage_preferences_instance = ManagePreferences(master, self.backup_folder_path, self.backup_file_format)

        self.key = load_key()
        self.setup_backup_schedule_on_startup()
        self.frequency_dropdown = None

    # Function to close the active window
    def close_active_window(self):
        if self.active_window:
            self.active_window.destroy()

    # Settings window configurations
    def settings(self):
        self.close_active_window()
        self.active_window = tk.Toplevel(self.master)
        self.active_window.title("Settings")
        self.active_window.geometry("220x100")
        self.active_window.resizable(False, False)
        self.active_window.configure(bg="white")

        data_button = ttk.Button(self.active_window, text="Manage Data", command=self.manage_data_handler.manage_data_window, style='Red.TButton')
        data_button.pack(pady=5)
        preferences_button = ttk.Button(self.active_window, text="Manage Preferences", command=self.manage_preferences_instance.open_preferences_window, style='Red.TButton')
        preferences_button.pack(pady=5)
        
    # Function to load preferences
    def load_preferences(self):
        config = configparser.ConfigParser()
        config.read('preferences.ini')

        self.backup_folder_path = config.get('AutomaticBackups', 'backup_folder_path', fallback=None)
        self.backup_file_format = config.get('AutomaticBackups', 'backup_file_format', fallback="Encrypted")  # Read backup_file_format

    # Functions to schedule/perform automatic backups
    def setup_backup_schedule_on_startup(self):
        self.load_preferences()
        self.setup_backup_schedule()
    def setup_backup_schedule(self):
        schedule.clear()

        self.perform_automatic_backup()
        threading.Thread(target=self.schedule_runner, daemon=True).start()
    def schedule_runner(self):
        while True:
            schedule.run_pending()
            time.sleep(60)
    def perform_automatic_backup(self):
        import backend
        current_time = time.strftime("%Y-%m-%d_%H%M", time.localtime())
        if self.manage_preferences_instance.automatic_backups_enabled:
            if self.backup_folder_path:
                src_file = "data.vv"
                dest_file_base = f"vv_automatic_export_{self.backup_file_format}_{current_time}"
                dest_file = os.path.join(self.backup_folder_path, dest_file_base)

                if self.backup_file_format == "Encrypted":
                    json_file_path = os.path.join(self.backup_folder_path, f"{dest_file_base}.json")
                    shutil.copy("data.vv", json_file_path)
                    os.chmod(json_file_path, 0o700)

                elif self.backup_file_format == "Unencrypted":
                    json_file_path = os.path.join(self.backup_folder_path, f"{dest_file_base}.json")
                    key = backend.load_key()
                    accounts = backend.load_accounts(key)  

                    try:
                        with open(json_file_path, 'w') as file_path:
                            json.dump(accounts, file_path, indent=4)
                    except Exception as e:
                        messagebox.showerror("Error", f"Error exporting unencrypted JSON: {str(e)}")
                
                elif self.backup_file_format == "TXT Encrypted":
                    txt_file_path = os.path.join(self.backup_folder_path, f"{dest_file_base}.txt")
                    shutil.copy("data.vv", txt_file_path)
                    os.chmod(txt_file_path, 0o700)

                elif self.backup_file_format == "TXT Unencrypted":
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

                elif self.backup_file_format ==  "Secrets":
                    txt_file_path = os.path.join(self.backup_folder_path, f"{dest_file_base}.txt")
                    try:
                        with open(txt_file_path, 'w') as file_path:
                            for name, info in self.accounts.items():
                                file_path.write(f"Name: {name}\n")
                                file_path.write(f"Secret: {info['secret']}\n\n")
                    except Exception as e:
                        print(f"Error exporting secrets as TXT: {str(e)}")

                elif self.backup_file_format == "QR Codes":
                    try:
                        for name, info in self.accounts.items():
                            if 'secret' in info:
                                secret_key = info['secret']
                                provisioning_uri = pyotp.totp.TOTP(secret_key).provisioning_uri(name)
                                qr = qrcode.QRCode(
                                    version=1,
                                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                                    box_size=10,
                                    border=4,
                                )
                                qr.add_data(provisioning_uri)
                                qr.make(fit=True)
                                qr_code_file_path = os.path.join(self.backup_folder_path, f"{name}_QR_code.png")
                                qr_img = qr.make_image(fill_color="black", back_color="white")
                                qr_img.save(qr_code_file_path)
                    except Exception as e:
                        messagebox.showerror("Error", f"Error exporting QR Codes: {str(e)}")

                backup_files = glob.glob(os.path.join(self.backup_folder_path, "*.json"))
                if len(backup_files) > 5:
                    backup_files.sort(key=os.path.getmtime)
                    oldest_backup = backup_files[0]
                    os.remove(oldest_backup)

    # Function that closes the settings window
    def close_settings_window(self):
        if getattr(self, 'active_window', None):
            try:
                self.active_window.destroy()
            except tk.TclError as e:
                if "application has been destroyed" not in str(e):
                    raise e
