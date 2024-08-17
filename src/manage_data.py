from customtkinter import *
from import_data import ImportDataFunctions
from export_data import ExportDataFunctions
from backend import load_key, load_accounts
from PIL import Image
from tkinter import messagebox
import backend, json, os, shutil, time, configparser, glob, qrcode, pyotp, zipfile, io

class ManageData:
    def __init__(self, master, right_frame, accounts):
        # Initial manage_data configurations
        self.master = master
        self.right_frame = right_frame
        self.accounts = accounts

        self.autobackups = None
        self.backup_folder_path = None
        self.backup_file_format = None

        self.load_preferences()
        self.perform_automatic_backup()
        self.cleanup_old_backups()

        self.export_data = ExportDataFunctions(master, self.accounts)
        self.import_data = ImportDataFunctions(master)

    # Data Function
    def data(self):
        # Data Settings frame configurations
        data_frame = CTkFrame(self.right_frame, width=600, height=700)
        data_frame.place(relx=0.61, rely=0, anchor="n")

        def close_frame():
            data_frame.destroy()

        x_button = CTkButton(data_frame, command=close_frame, text="❌", fg_color="white", border_color="black", text_color="black", hover_color="red", border_width=2, width=50, height=20, cursor="hand2")
        x_button.place(relx=0.8, rely=0.03, anchor="ne")

        title_label = CTkLabel(data_frame, text="Data", font=("Helvetica", 30, "bold", "underline"))
        title_label.place(relx=0.42, rely=0.08, anchor="center")

        export_selected_option = StringVar(value="Encrypted JSON")
        import_selected_option = StringVar(value="JSON")

        # Function to set export dropdown options
        def export_function(event=None):
            selected_value = export_selected_option.get()
            if selected_value == "Encrypted JSON":
                self.export_data.export_encrypted()
            elif selected_value == "Unencrypted JSON":
                self.export_data.export_unencrypted()
            elif selected_value == "Encrypted TXT":
                self.export_data.export_txt_encrypted()
            elif selected_value == "Unencrypted TXT":
                self.export_data.export_txt()
            elif selected_value == "Secrets":
                self.export_data.export_secrets()
            elif selected_value == "QR Code(s)":
                self.export_data.export_qr_codes()

        # Function to set import dropdown options
        def import_function(event=None):
            selected_value = import_selected_option.get()
            if selected_value == "JSON":
                self.import_data.import_json()
            elif selected_value == "QR Code(s)":
                self.import_data.import_from_qr()
        
        # Function to import/export preferences
        def import_preferences(event=None):
            self.import_data.import_preferences()
        def export_preferences(event=None):
            self.export_data.export_preferences()

        # Creating export dropdown
        export_label = CTkLabel(data_frame, text="Export Data", font=("Helvetica", 18, "bold", "underline"))
        export_label.place(relx=0.16, rely=0.35, anchor="w")
        export_dropdown = CTkOptionMenu(data_frame, values=["Encrypted JSON", "Unencrypted JSON", "Encrypted TXT", "Unencrypted TXT", "Secrets", "QR Code(s)"], variable=export_selected_option, height=35, font=("Helvetica", 14), fg_color="white", text_color="black", dropdown_font=("Helvetica", 14), dropdown_text_color="black", corner_radius=10, button_color="red", button_hover_color="#EE4B2B", dropdown_fg_color="white", dropdown_hover_color="red", hover=True, anchor="center", state="normal")
        export_dropdown.place(relx=0.12, rely=0.4, anchor="w")
        export_button = CTkButton(data_frame, text="Export", command=export_function, fg_color="white", hover_color="red", text_color="black", cursor="hand2", width=100, height=35, border_width=2, font=("Helvetica", 16, "bold"))
        export_button.place(relx=0.23, rely=0.47, anchor="center")

        # Creating import dropdown
        import_label = CTkLabel(data_frame, text="Import Data", font=("Helvetica", 18, "bold", "underline"))
        import_label.place(relx=0.47, rely=0.35, anchor="w")
        import_dropdown = CTkOptionMenu(data_frame, values=["JSON", "QR Code(s)"], variable=import_selected_option, height=35, font=("Helvetica", 14), fg_color="white", text_color="black", dropdown_font=("Helvetica", 14), dropdown_text_color="black", corner_radius=10, button_color="red", button_hover_color="#EE4B2B", dropdown_fg_color="white", dropdown_hover_color="red", hover=True, anchor="center", state="normal")
        import_dropdown.place(relx=0.44, rely=0.4, anchor="w")
        import_button = CTkButton(master=data_frame, text="Import", command=import_function, fg_color="white", hover_color="red", text_color="black", cursor="hand2", width=100, height=35, border_width=2, font=("Helvetica", 16, "bold"))
        import_button.place(relx=0.55, rely=0.47, anchor="center")
        import_dropdown.bind("<<MenuSelected>>", import_function)

        autobackups_label = CTkLabel(data_frame, text=f"Location {self.backup_folder_path if self.backup_folder_path else '- None'}", font=("Helvetica", 14, "bold"))
        autobackups_label.place(relx=0.25, rely=0.25, anchor="center")
        
        # Creating VerifyVault data options
        impref_label = CTkLabel(data_frame, text="Import VerifyVault Data", font=("Helvetica", 18, "bold", "underline"))
        impref_label.place(relx=0.05, rely=0.55, anchor="w")
        impref_button = CTkButton(master=data_frame, text="Import Preferences", command=import_preferences, fg_color="white", hover_color="red", text_color="black", cursor="hand2", width=100, height=35, border_width=2, font=("Helvetica", 16, "bold"))
        impref_button.place(relx=0.05, rely=0.6, anchor="w")

        expref_label = CTkLabel(data_frame, text="Export VerifyVault Data", font=("Helvetica", 18, "bold", "underline"))
        expref_label.place(relx=0.8, rely=0.55, anchor="e")
        expref_button = CTkButton(master=data_frame, text="Export Preferences", command=export_preferences, fg_color="white", hover_color="red", text_color="black", cursor="hand2", width=100, height=35, border_width=2, font=("Helvetica", 16, "bold"))
        expref_button.place(relx=0.73, rely=0.6, anchor="e")

        # Function to display Automatic Backup Folder location
        def select_backup_folder():
            folder_path = filedialog.askdirectory()
            if folder_path:
                self.backup_folder_path = folder_path
                self.save_preferences()
                autobackups_label.configure(text=f"Location {self.backup_folder_path if self.backup_folder_path else '- Exported Data'}")

        # Function to toggle Automatic Backups
        def autobackups_callback():
            self.autobackups = autobackups_var.get()
            self.save_preferences()

        autobackups_var = StringVar(value="off")
        autobackups_var.set(value="on" if self.autobackups == "on" else "off")
        autobackups_switch = CTkSwitch(data_frame, text="Automatic Backups", command=autobackups_callback, variable=autobackups_var, onvalue="on", offvalue="off", fg_color="red", font=("Helvetica", 18, "bold"))
        autobackups_switch.place(relx=0.22, rely=0.15, anchor="w")

        autobackup_location = CTkButton(data_frame, text="Backup Location", command=select_backup_folder, fg_color="white", hover_color="red", text_color="black", cursor="hand2", width=100, height=35, border_width=2, font=("Helvetica", 16, "bold"))
        autobackup_location.place(relx=0.25, rely=0.2, anchor="center")

        # Function to save Automatic Backup file format
        def autobackups_format_callback(*args):
            folder_format = autobackups_formatvar.get()
            self.backup_file_format = folder_format
            self.save_preferences()

        autobackups_formatvar = StringVar(value=self.backup_file_format)
        backup_formats = ["Encrypted JSON", "Unencrypted JSON", "Encrypted TXT", "Unencrypted TXT", "Secrets", "QR Code(s)"]
        autobackups_format = CTkOptionMenu(data_frame, values=backup_formats, command=autobackups_format_callback, variable=autobackups_formatvar, height=35, font=("Helvetica", 14), fg_color="white", text_color="black", dropdown_font=("Helvetica", 14), dropdown_text_color="black", corner_radius=10, button_color="red", button_hover_color="#EE4B2B", dropdown_fg_color="white", dropdown_hover_color="red", hover=True, anchor="center", state="normal")
        autobackups_format.place(relx=0.55, rely=0.2, anchor="center")

    # Function to save preferences
    def save_preferences(self):
        config = configparser.ConfigParser()
        if os.path.exists('preferences.ini'):
            config.read('preferences.ini')

        backups_status = "on" if self.autobackups == "on" else "off"

        config['Automatic Backups'] = {
            'backups': backups_status,
            'folder': self.backup_folder_path if self.backup_folder_path else "",
            'format': self.backup_file_format if self.backup_file_format else "Encrypted JSON",
        }

        with open('preferences.ini', 'w') as configfile:
            config.write(configfile)

    # Function to load preferences
    def load_preferences(self):
        config = configparser.ConfigParser()
        if os.path.exists('preferences.ini'):
            config.read('preferences.ini')

        self.autobackups = config.get('Automatic Backups', 'backups', fallback=None)
        self.backup_folder_path = config.get('Automatic Backups', 'folder', fallback=None)
        self.backup_file_format = config.get('Automatic Backups', 'format', fallback="Encrypted JSON")

    # Function to perform automatic backups
    def perform_automatic_backup(self):
        if self.autobackups == 'on' and self.backup_folder_path:
            current_time = time.strftime("%Y-%m-%d_%H%M", time.localtime())
            src_file = "data.vv"
            dest_file_base = f"vv_automatic_export_{self.backup_file_format}_{current_time}"
            dest_file = os.path.join(self.backup_folder_path, dest_file_base)

            try:
                if "Encrypted JSON" in self.backup_file_format:
                    json_file_path = os.path.join(self.backup_folder_path, f"{dest_file_base}.json")
                    shutil.copy(src_file, json_file_path)
                    os.chmod(json_file_path, 0o700)

                elif "Unencrypted JSON" in self.backup_file_format:
                    json_file_path = os.path.join(self.backup_folder_path, f"{dest_file_base}.json")
                    key = load_key()
                    accounts = load_accounts(key)
                    with open(json_file_path, 'w') as file_path:
                        json.dump(accounts, file_path, indent=4)

                elif "Encrypted TXT" in self.backup_file_format:
                    txt_file_path = os.path.join(self.backup_folder_path, f"{dest_file_base}.txt")
                    shutil.copy(src_file, txt_file_path)
                    os.chmod(txt_file_path, 0o700)

                elif "Unencrypted TXT" in self.backup_file_format:
                    txt_file_path = os.path.join(self.backup_folder_path, f"{dest_file_base}.txt")
                    with open(src_file, 'rb') as src_file_path:
                        encrypted_data = src_file_path.read()
                    key = backend.load_key()
                    decrypted_data = backend.decrypt_message(encrypted_data, key)
                    accounts = json.loads(decrypted_data)
                    with open(txt_file_path, 'w') as file_path:
                        json.dump(accounts, file_path, indent=4)

                elif "Secrets" in self.backup_file_format:
                    txt_file_path = os.path.join(self.backup_folder_path, f"{dest_file_base}.txt")
                    with open(txt_file_path, 'w') as file_path:
                        accounts = load_accounts(load_key())
                        for name, info in accounts.items():
                            file_path.write(f"Name: {name}\n")
                            file_path.write(f"Secret: {info['secret']}\n\n")

                elif "QR Code(s)" in self.backup_file_format:
                    zip_file_path = os.path.join(self.backup_folder_path, f"{dest_file_base}.zip")
                    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
                        accounts = load_accounts(load_key())
                        for name, info in accounts.items():
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
                                qr_code_img = qr.make_image(fill_color="black", back_color="white")
                                
                                qr_code_file_path = f"{name}_QR_code.png"
                                with io.BytesIO() as qr_code_io:
                                    qr_code_img.save(qr_code_io, format='PNG')
                                    zipf.writestr(qr_code_file_path, qr_code_io.getvalue())
            except Exception as e:
                messagebox.showerror("Error", f"Error performing backup: {str(e)}")

    # Function to only save 5 automatic backups
    def cleanup_old_backups(self):
        if self.backup_folder_path:
            backup_files = glob.glob(os.path.join(self.backup_folder_path, "*.json"))
            backup_files += glob.glob(os.path.join(self.backup_folder_path, "*.txt"))
            if len(backup_files) > 5:
                backup_files.sort(key=os.path.getmtime)
                while len(backup_files) > 5:
                    oldest_backup = backup_files.pop(0)
                    os.remove(oldest_backup)