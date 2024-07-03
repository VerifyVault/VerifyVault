import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image
from pyzbar.pyzbar import decode
from labels import LabelsManager
from search import SearchFunctions
from notifications import NotificationManager
from backend import load_accounts, save_accounts, load_key
import backend, json, pyotp, os, shutil, time, datetime, qrcode

class ManageData:
    def __init__(self, master, accounts, notifications):
        # Initial manage_data configurations
        self.master = master
        self.accounts = accounts
        self.key = load_key()
        self.load_deleted_accounts()
        self.active_window = None
        self.notifications = notifications

        #self.search_var = tk.StringVar()
        #self.search_var.set("Search...")

    # Function that closes active window
    def close_active_window(self):
        if self.active_window:
            self.active_window.destroy()

    # Function to lift the Settings tab
    def lift_settings_tab(self):
        settings_tab = self.master.winfo_children()[0]
        settings_tab.lift()

    # Manage Data Function
    def manage_data(self):
        # Manage Data window configurations
        self.close_active_window()
        export_window = tk.Toplevel(self.master)
        export_window.title("Manage Data")
        export_window.geometry("200x150")
        export_window.resizable(False, False)
        export_window.configure(bg="white")

        export_button = ttk.Button(export_window, text="Export Data", command=self.export_and_close, style='Red.TButton')
        export_button.pack(pady=5)
        import_button = ttk.Button(export_window, text="Import Data", command=self.import_data, style='Red.TButton')
        import_button.pack(pady=5)
        recycle_bin_button = ttk.Button(export_window, text="Recycle Bin", command=self.manage_recycle_bin, style='Red.TButton')
        recycle_bin_button.pack(pady=5)

        self.active_window = export_window

    # Function that configures Export Data window configurations
    def export_and_close(self):
        self.close_active_window()
        export_window = tk.Toplevel(self.master)
        export_window.title("Export Data")
        export_window.geometry("200x100")
        export_window.resizable(False, False)
        export_window.configure(bg="white")

        json_button = ttk.Button(export_window, text="Export via File", command=self.export_file, style='Red.TButton')
        json_button.pack(pady=5)
        qr_button = ttk.Button(export_window, text="Export via QR Code(s)", command=self.export_qr_codes, style='Red.TButton')
        qr_button.pack(pady=5)

        self.active_window = export_window

    # Function that exports accounts via .json window
    def export_file(self):
        self.close_active_window()
        export_window = tk.Toplevel(self.master)
        export_window.title("Export via File Options")
        export_window.geometry("250x250")
        export_window.resizable(False, False)
        export_window.configure(bg="white")
        self.active_window = export_window

        def export_encrypted():
            self.close_active_window()
            dest_dir = filedialog.askdirectory()
            if dest_dir:
                dest_file = os.path.join(dest_dir, "exported_data_encrypted.json")
                shutil.copy("data.vv", dest_file)
                os.chmod(dest_file, 0o700)
                messagebox.showinfo("Exported", f"Encrypted JSON file exported to {dest_file}")

        def export_unencrypted():
            self.close_active_window()
            file_path = filedialog.asksaveasfile(defaultextension=".json", filetypes=[("JSON files", "*.json")],
                                                mode="w", initialfile="exported_data_unencrypted.json")
            if file_path:
                try:
                    json.dump(self.accounts, file_path, indent=4)
                    messagebox.showinfo("Exported", "Data exported successfully as unencrypted JSON.")
                except Exception as e:
                    messagebox.showerror("Error", f"Error exporting unencrypted JSON: {str(e)}")
                finally:
                    file_path.close()

        def export_txt():
            self.close_active_window()
            file_path = filedialog.asksaveasfile(defaultextension=".txt", filetypes=[("Text files", "*.txt")],
                                                mode="w", initialfile="exported_data.txt")
            if file_path:
                try:
                    for name, info in self.accounts.items():
                        file_path.write(f"Name: {name}\n")
                        file_path.write(f"Key: {info['key']}\n")
                        file_path.write(f"Secret: {info['secret']}\n\n")
                    messagebox.showinfo("Exported", "Data exported successfully as TXT.")
                except Exception as e:
                    messagebox.showerror("Error", f"Error exporting TXT: {str(e)}")
                finally:
                    file_path.close()

        def export_txt_encrypted():
            self.close_active_window()
            dest_dir = filedialog.askdirectory()
            if dest_dir:
                dest_file = os.path.join(dest_dir, "data.txt")
                shutil.copy("data.vv", dest_file)
                os.chmod(dest_file, 0o700)
                messagebox.showinfo("Exported", f"Encrypted TXT file exported to {dest_file}")

        def export_secrets():
            self.close_active_window()
            file_path = filedialog.asksaveasfile(defaultextension=".txt", filetypes=[("Text files", "*.txt")],
                                                mode="w", initialfile="exported_secrets.txt")
            if file_path:
                try:
                    for name, info in self.accounts.items():
                        file_path.write(f"Name: {name}\n")
                        file_path.write(f"Secret: {info['secret']}\n\n")
                    messagebox.showinfo("Exported", "Secrets exported successfully as TXT.")
                except Exception as e:
                    messagebox.showerror("Error", f"Error exporting secrets as TXT: {str(e)}")
                finally:
                    file_path.close()

        export_encrypted_button = ttk.Button(export_window, text="Export via JSON Encrypted", command=export_encrypted, style='Red.TButton')
        export_encrypted_button.pack(pady=5)
        export_unencrypted_button = ttk.Button(export_window, text="Export via JSON Unencrypted", command=export_unencrypted, style='Red.TButton')
        export_unencrypted_button.pack(pady=5)
        export_txt_button = ttk.Button(export_window, text="Export via TXT", command=export_txt, style='Red.TButton')
        export_txt_button.pack(pady=5)
        export_txt_encrypted_button = ttk.Button(export_window, text="Export via TXT Encrypted", command=export_txt_encrypted, style='Red.TButton')
        export_txt_encrypted_button.pack(pady=5)
        export_secrets_button = ttk.Button(export_window, text="Export Secrets via TXT", command=export_secrets, style='Red.TButton')
        export_secrets_button.pack(pady=5)

    # Function that exports accounts via QR Code configuration
    def export_qr_codes(self):
        self.close_active_window()

        def export_from_qr():
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
                messagebox.showinfo("Exported", "QR codes exported successfully.")
        export_from_qr()

    # Function that configures Import Data window configurations
    def import_data(self):
        from gui import TwoFactorAppGUI
        self.close_active_window()

        # Function that imports accounts via .json
        def import_json():
            key = backend.load_key()
            self.close_active_window()
            file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
            if file_path:
                try:
                    existing_accounts = {}
                    if os.path.exists("data.vv"):
                        key = load_key()
                        existing_accounts = load_accounts(key)

                    with open(file_path, "r") as imported_file:
                        imported_data = json.load(imported_file)

                    duplicate_accounts = set(imported_data.keys()) & set(existing_accounts.keys())
                    if duplicate_accounts:
                        override = messagebox.askyesnocancel(
                            "Duplicate Account",
                            "At least one of your accounts already exists. Would you like to override them?"
                        )
                        if override is None:
                            return
                        if override is False:
                            for name in duplicate_accounts:
                                suffix = 1
                                new_name = f"{name} ({suffix})"
                                while new_name in existing_accounts:
                                    suffix += 1
                                    new_name = f"{name} ({suffix})"
                                existing_accounts[new_name] = existing_accounts.pop(name)
                        else:
                            pass

                    existing_accounts.update(imported_data)
                    save_accounts(existing_accounts, key)
                    messagebox.showinfo("Success", "Data imported successfully!")

                    self.master.destroy()
                    TwoFactorAppGUI(tk.Tk(), self.key)
                except (json.JSONDecodeError, ValueError):
                    messagebox.showerror("Invalid JSON format")
                except Exception as e:
                    messagebox.showerror(f"An error occurred: {str(e)}")

        # Function that imports accounts via QR Code
        def import_from_qr():
            from gui import TwoFactorAppGUI
            self.close_active_window()
            try:
                # Loads existing accounts if they exist
                existing_accounts = {}
                if os.path.exists("data.vv"):
                    key = backend.load_key()
                    existing_accounts = backend.load_accounts(key)

                # Asks the user to select QR code image file, then decodes it
                file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg;*.jpeg")])
                if file_path:
                    with open(file_path, 'rb') as img_file:
                        img = Image.open(img_file)
                        result = decode(img)
                        
                        if result:
                            for data in result:
                                qr_data = data.data.decode('utf-8')
                                parts = qr_data.split('secret=')
                                account_name = parts[0].split('/')[-1].rstrip('?').replace('%20', ' ')
                                secret_key = parts[1] if len(parts) > 1 else ''

                                while account_name in existing_accounts:
                                    messagebox.showerror("Duplicate Account", f"Account '{account_name}' already exists.")
                                    new_name = self.ask_for_account_name()
                                    account_name = new_name

                                if account_name:
                                    existing_accounts[account_name] = {'key': secret_key, 'secret': secret_key}
                                    messagebox.showinfo("Imported", f"Account '{account_name}' imported successfully!")
                                    backend.save_accounts(existing_accounts, self.key)
                                    self.master.destroy()
                                    TwoFactorAppGUI(tk.Tk(), self.key)
                        else:
                            messagebox.showerror("Error", "No QR code found in the image.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")

        import_window = tk.Toplevel(self.master)
        import_window.title("Import Data")
        import_window.geometry("200x100")
        import_window.resizable(False, False)
        import_window.configure(bg="white")

        import_json_button = ttk.Button(import_window, text="Import via JSON", command=import_json, style='Red.TButton')
        import_json_button.pack(pady=5)
        import_qr_button = ttk.Button(import_window, text="Import via QR Code", command=import_from_qr, style='Red.TButton')
        import_qr_button.pack(pady=5)

        self.active_window = import_window

    # Ask for Account Name Function
    def ask_for_account_name(self):
        dialog_window = tk.Toplevel(self.master)
        dialog_window.title("Enter Account Name")
        dialog_window.geometry("300x150")
        dialog_window.resizable(False, False)
        dialog_window.configure(bg="white")

    #Functions that validate and process the account name inputted
        def validate_name(name):
            if len(name) > 30:
                messagebox.showerror("Character Limit", "Character Limit is 30")
                return False
            invalid_chars = "\\/:*?\"<>|"
            for char in invalid_chars:
                if char in name:
                    messagebox.showerror("Invalid Character", f"Name cannot contain '{char}'")
                    return False
            return True
        def confirm(event=None):
            account_name = account_name_var.get()
            if account_name:
                if validate_name(account_name):
                    dialog_window.destroy()
                else:
                    account_name_var.set("")
            else:
                messagebox.showerror("Error", "Account name cannot be empty.")
        
        label = tk.Label(dialog_window, text="Enter a unique account name:", bg="white")
        label.pack(pady=10)

        account_name_var = tk.StringVar()
        entry = tk.Entry(dialog_window, textvariable=account_name_var)
        entry.pack(pady=10)

        vcmd = (dialog_window.register(validate_name), "%P")
        entry.config(validate="key", validatecommand=vcmd)
        dialog_window.bind("<Return>", confirm)
        entry.focus_set()

        confirm_button = ttk.Button(dialog_window, text="Confirm", command=confirm, style='Red.TButton')
        confirm_button.pack(pady=10)
        char_count_label = tk.Label(dialog_window, text="Characters: 0", bg="white")
        char_count_label.pack()

        #Function that counts the character length of the name
        def update_char_count(event):
            char_count_label.config(text=f"Characters: {len(account_name_var.get())}")

        entry.bind("<KeyRelease>", update_char_count)
        dialog_window.transient(self.master)
        dialog_window.grab_set()
        return account_name_var.get()

    # Manage Recycle Bin Function
    def manage_recycle_bin(self):
        self.close_active_window()
        recycle_bin_window = tk.Toplevel(self.master)
        recycle_bin_window.title("Recycle Bin")
        recycle_bin_window.geometry("500x300")
        recycle_bin_window.resizable(False, False)
        recycle_bin_window.configure(bg="white")

        self.update_recycle_bin(recycle_bin_window)
        self.active_window = recycle_bin_window

    # Functions that load/save the accounts that have been marked deleted
    def load_deleted_accounts(self):
        try:
            with open('deleted.json', 'r') as f:
                self.deleted_accounts = json.load(f)
        except FileNotFoundError:
            self.deleted_accounts = {}
    def save_deleted_accounts(self):
        with open('deleted.json', 'w') as f:
            json.dump(self.deleted_accounts, f, indent=4)

    # Function that sets/updates the recycle bin window
    def update_recycle_bin(self, recycle_bin_window):
        if isinstance(recycle_bin_window, (tk.Toplevel, tk.Frame)):
            for widget in recycle_bin_window.winfo_children():
                widget.destroy()

            recycle_bin_frame = tk.Frame(recycle_bin_window, bg="white")
            recycle_bin_frame.pack(fill="both", expand=True)

            recycle_bin_label = tk.Label(recycle_bin_frame, text="Recycle Bin", font=("Helvetica", 16), bg="white")
            recycle_bin_label.pack(pady=(10, 5))

            button_frame = tk.Frame(recycle_bin_frame, bg="white")
            button_frame.pack(pady=5)

            clear_all_button = ttk.Button(button_frame, text="Clear All", command=self.clear_all_accounts)
            clear_all_button.pack(side=tk.LEFT, padx=5)

            restore_all_button = ttk.Button(button_frame, text="Restore All", command=self.restore_all_accounts)
            restore_all_button.pack(side=tk.LEFT, padx=5)

            self.load_deleted_accounts()

            if not self.deleted_accounts:
                no_accounts_label = tk.Label(recycle_bin_frame, text="No Accounts Found", bg="white")
                no_accounts_label.pack(pady=20)
            else:
                if len(self.deleted_accounts) >= 4:
                    recycle_bin_canvas = tk.Canvas(recycle_bin_window, bg="white")
                    recycle_bin_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                    recycle_bin_scrollbar = tk.Scrollbar(recycle_bin_window, orient=tk.VERTICAL, command=recycle_bin_canvas.yview)
                    recycle_bin_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

                    recycle_bin_canvas.configure(yscrollcommand=recycle_bin_scrollbar.set)
                    recycle_bin_canvas.bind("<Configure>", lambda e: recycle_bin_canvas.configure(scrollregion=recycle_bin_canvas.bbox("all")))

                    recycle_bin_scrollable_frame = tk.Frame(recycle_bin_canvas, bg="white")
                    recycle_bin_canvas.create_window((0, 0), window=recycle_bin_scrollable_frame, anchor=tk.NW)

                    for account_name in self.deleted_accounts.keys():
                        account_frame = tk.Frame(recycle_bin_scrollable_frame, relief="ridge", bg="white", highlightbackground="black", highlightthickness=2)
                        account_frame.pack(fill="x", padx=50, pady=5)
                        account_label = tk.Label(account_frame, text=f"Account: {account_name}", bg="white")
                        account_label.pack(side=tk.LEFT, padx=10)

                        restore_button = ttk.Button(account_frame, text="Restore", command=lambda name=account_name: self.restore_account(name))
                        restore_button.pack(side=tk.RIGHT, padx=10)
                        permanent_delete_button = ttk.Button(account_frame, text="Permanently Delete", command=lambda name=account_name: self.permanent_delete_account(name))
                        permanent_delete_button.pack(side=tk.RIGHT, padx=10)

                        separator = ttk.Separator(recycle_bin_scrollable_frame, orient="horizontal")
                        separator.pack(fill="x", pady=5)

                    recycle_bin_canvas.bind_all("<MouseWheel>", lambda event: recycle_bin_canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
                else:
                    for account_name in self.deleted_accounts.keys():
                        account_frame = tk.Frame(recycle_bin_frame, relief="ridge", bg="white", highlightbackground="black", highlightthickness=2)
                        account_frame.pack(fill="x", padx=50, pady=5)
                        account_label = tk.Label(account_frame, text=f"Account: {account_name}", bg="white")
                        account_label.pack(side=tk.LEFT, padx=10)

                        restore_button = ttk.Button(account_frame, text="Restore", command=lambda name=account_name: self.restore_account(name))
                        restore_button.pack(side=tk.RIGHT, padx=10)
                        permanent_delete_button = ttk.Button(account_frame, text="Permanently Delete", command=lambda name=account_name: self.permanent_delete_account(name))
                        permanent_delete_button.pack(side=tk.RIGHT, padx=10)

                        separator = ttk.Separator(recycle_bin_frame, orient="horizontal")
                        separator.pack(fill="x", pady=5)

            def on_recycle_bin_close():
                from gui import TwoFactorAppGUI
                recycle_bin_window.destroy()
                self.master.destroy()
                TwoFactorAppGUI(tk.Tk(), self.key)

            recycle_bin_window.protocol("WM_DELETE_WINDOW", on_recycle_bin_close)
        else:
            messagebox.showerror("Window Type Error", "Unexpected window type encountered.")
        self.save_deleted_accounts()

    def restore_all_accounts(self):
        from gui import TwoFactorAppGUI
        if self.deleted_accounts:
            restored_accounts = []
            for account_name in list(self.deleted_accounts.keys()):
                self.restore_account(account_name)
                restored_accounts.append(account_name)

            # Prepare the notification message
            if restored_accounts:
                restored_accounts_message = f"All accounts ({', '.join(restored_accounts)}) have been restored."
                messagebox.showinfo("All Accounts Restored", restored_accounts_message)
                self.update_recycle_bin(self.master.winfo_children()[1])
                self.master.destroy()
                TwoFactorAppGUI(tk.Tk(), self.key)
        else:
            messagebox.showinfo("No Accounts to Restore", "There are no accounts to restore.")

    def clear_all_accounts(self):
        confirmation = messagebox.askyesnocancel("Confirm Clear All", "Are you sure you want to permanently delete all accounts?")
        if confirmation is True:
            if not self.deleted_accounts:
                messagebox.showinfo("No Accounts to Delete", "There are no accounts to delete.")
            else:
                self.deleted_accounts = {}
                self.save_deleted_accounts()
                messagebox.showinfo("All Accounts Cleared", "All accounts have been permanently deleted.")
                self.update_recycle_bin(self.master.winfo_children()[1])
                self.master.destroy()
                TwoFactorAppGUI(tk.Tk(), self.key)

    # Function that automatically clears the recycle bin every month
    def monthly_cleanup(self):
        today = datetime.today()
        if today.day == 1:
            self.clear_recycle_bin()
    def clear_recycle_bin(self):
        self.deleted_accounts = {}
        self.save_deleted_accounts()
        messagebox.showinfo("Recycle Bin Cleared", "Recycle Bin has been cleared for the new month.")
        self.update_recycle_bin(self.master.winfo_children()[1])

    # Functions that delete/restore the account
    def mark_for_deletion(self, account_name):
        current_time = time.time()
        self.deleted_accounts[account_name] = current_time
    def restore_account(self, account_name):
        if account_name in self.deleted_accounts:
            try:
                existing_accounts = load_accounts(self.key)
                account_info = self.deleted_accounts[account_name]

                existing_accounts[account_name] = {
                    'secret': account_info['secret'],
                    'key': account_info['key'],
                    'deleted': False
                }
                save_accounts(existing_accounts, self.key)

                del self.deleted_accounts[account_name]
                self.save_deleted_accounts()
                self.update_recycle_bin(self.master.winfo_children()[1])

                self.notifications.show_notification("Account(s) restored successfully!")
                self.manage_recycle_bin()
            except Exception as e:
                messagebox.showerror("Error", f"Error restoring account: {str(e)}")
        else:
            messagebox.showerror("Account Not Found", f"Account '{account_name}' not found in deleted accounts.")

    # Function that permanently deletes the account
    def permanent_delete_account(self, account_name):
        confirmation = messagebox.askyesnocancel("Confirm Permanent Delete", f"Are you sure you want to permanently delete account '{account_name}'?")
        if confirmation is True:
            del self.deleted_accounts[account_name]
            self.save_deleted_accounts()
            self.update_recycle_bin(self.master.winfo_children()[1])
            messagebox.showinfo("Permanent Delete", f"Account '{account_name}' permanently deleted.")
            self.manage_recycle_bin()