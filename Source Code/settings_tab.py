import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import backend, json, qrcode, pyotp, os, binascii, sys, subprocess
from labels import LabelsManager
from search import SearchFunctions

class SettingsTab:
    def __init__(self, master, accounts, notifications, update_labels, search_functions):
        ##Configuring settings_tab constructor
        self.master = master
        self.accounts = accounts
        self.notifications = notifications
        self.update_labels = update_labels
        self.search_functions = search_functions

        self.settings_window_open = False
        self.export_window_open = False
        self.settings_window = None
        self.export_window = None

    #Opens, closes, and configures Settings window
    def settings(self):
        if not self.settings_window_open:
            self.settings_window_open = True

            self.settings_window = tk.Toplevel(self.master)
            self.settings_window.title("Settings")
            self.settings_window.geometry("200x100")
            self.settings_window.resizable(False, False)
            self.settings_window.configure(bg="white")

            import_button = ttk.Button(self.settings_window, text="Import Data", command=self.import_data, style='Red.TButton')
            import_button.pack(pady=5)

            export_button = ttk.Button(self.settings_window, text="Export Data", command=self.export_and_close, style='Red.TButton')
            export_button.pack(pady=5)

            def close_settings_window():
                self.settings_window_open = False
                self.settings_window.destroy()

            self.settings_window.protocol("WM_DELETE_WINDOW", close_settings_window)

    #Opens, closes, and configures Export window
    def export_and_close(self):
        if not self.export_window_open:
            if getattr(self, 'settings_window', None):
                self.settings_window.destroy()
                self.settings_window_open = False 
                
            self.export_window_open = True
            self.export_window = tk.Toplevel(self.master)
            self.export_window.title("Export Data")
            self.export_window.geometry("200x150")
            self.export_window.resizable(False, False)
            self.export_window.configure(bg="white")

            json_button = ttk.Button(self.export_window, text="Export JSON", command=self.export_json, style='Red.TButton')
            json_button.pack(pady=5)
            qr_button = ttk.Button(self.export_window, text="Export QR Codes", command=self.export_qr_codes, style='Red.TButton')
            qr_button.pack(pady=5)

            def close_export_window():
                self.export_window_open = False
                self.export_window.destroy()
                self.settings_window_open = False

            self.export_window.protocol("WM_DELETE_WINDOW", close_export_window)

    #Export .json functionality
    def export_json(self):
        self.export_window_open = False
        self.export_window.destroy()
        
        file_path = filedialog.asksaveasfile(defaultextension=".json", filetypes=[("JSON files", "*.json")], mode="w", 
                                            initialfile="exported_data.json")
        if file_path:
            try:
                json.dump(self.accounts, file_path)
                self.notifications.show_notification("Data exported successfully as JSON.")
            except Exception as e:
                self.notifications.show_notification(f"Error exporting JSON: {str(e)}", color="red")
            finally:
                file_path.close()
        else:
            self.notifications.show_notification("Export canceled by user.")
        
        self.close_settings_window()

    #Export QR codes functionality
    def export_qr_codes(self):
        self.export_window_open = False
        self.export_window.destroy()
        dest_folder = filedialog.askdirectory()
        if dest_folder:
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
                    qr_code_file_path = os.path.join(dest_folder, f"{name}_QR_code.png")
                    qr_img = qr.make_image(fill_color="black", back_color="white")
                    qr_img.save(qr_code_file_path)
            self.notifications.show_notification("QR codes exported successfully.")
        self.close_settings_window()

    #Import data functionality
    def import_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                existing_accounts = {}
                if os.path.exists("data.json") and os.path.getsize("data.json") > 0:
                    with open("data.json", "r") as original_file:
                        existing_accounts = json.load(original_file)

                with open(file_path, "r") as imported_file:
                    imported_data = json.load(imported_file)

                duplicate_accounts = set(imported_data.keys()) & set(existing_accounts.keys())
                if duplicate_accounts:
                    override = messagebox.askyesno(
                        "Duplicate Accounts",
                        "At least one of your accounts already exists. Would you like to override them?"
                    )
                    if not override:
                        for name in duplicate_accounts:
                            suffix = 1
                            new_name = f"{name} ({suffix})"
                            while new_name in existing_accounts:
                                suffix += 1
                                new_name = f"{name} ({suffix})"
                            existing_accounts[new_name] = existing_accounts.pop(name)

                existing_accounts.update(imported_data)
                with open("data.json", "w") as updated_file:
                    json.dump(existing_accounts, updated_file)

                self.update_labels(existing_accounts)
                self.search_functions.update_accounts(existing_accounts)

                messagebox.showinfo("Restart", "Data imported successfully!")

                if getattr(self, 'master', None):
                    try:
                        self.master.destroy()
                    except tk.TclError as e:
                        if "application has been destroyed" not in str(e):
                            raise e
                    
                python = sys.executable
                subprocess.call([python, *sys.argv])
                
            except (json.JSONDecodeError, ValueError):
                self.notifications.show_notification("Invalid JSON format")
            except Exception as e:
                self.notifications.show_notification(f"An error occurred: {str(e)}")
        self.close_settings_window()

    #Closes Settings window
    def close_settings_window(self):
        if getattr(self, 'settings_window', None):
            try:
                self.settings_window.destroy()
                self.settings_window_open = False
            except tk.TclError as e:
                if "application has been destroyed" not in str(e):
                    raise e
