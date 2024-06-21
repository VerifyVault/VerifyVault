import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image
#from pyzbar.pyzbar import decode
import backend, json, pyotp, os, shutil, time, datetime, qrcode, sys, subprocess
from notifications import NotificationManager
from backend import load_accounts, save_accounts, load_key

class ManageData:
    def __init__(self, master, accounts):
        # Initial manage_data configurations
        self.master = master
        self.accounts = accounts
        self.key = load_key()
        self.active_window = None
        self.load_deleted_accounts()
        
    # Closes active window
    def close_active_window(self):
        if self.active_window:
            self.active_window.destroy()

    # Manage Data window configurations
    def manage_data(self):
        self.close_active_window()
        export_window = tk.Toplevel(self.master)
        export_window.title("Manage Data")
        export_window.geometry("150x150")
        export_window.resizable(False, False)
        export_window.configure(bg="white")

        export_button = ttk.Button(export_window, text="Export Data", command=self.export_and_close, style='Red.TButton')
        export_button.pack(pady=5)
        import_button = ttk.Button(export_window, text="Import Data", command=self.import_data, style='Red.TButton')
        import_button.pack(pady=5)
        recycle_bin_button = ttk.Button(export_window, text="Recycle Bin", command=self.manage_recycle_bin, style='Red.TButton')
        recycle_bin_button.pack(pady=5)

        self.active_window = export_window

    # Export Data window configurations
    def export_and_close(self):
        self.close_active_window()
        export_window = tk.Toplevel(self.master)
        export_window.title("Export Data")
        export_window.geometry("200x100")
        export_window.resizable(False, False)
        export_window.configure(bg="white")

        json_button = ttk.Button(export_window, text="Export via File", command=self.export_json, style='Red.TButton')
        json_button.pack(pady=5)
        qr_button = ttk.Button(export_window, text="Export via QR Code(s)", command=self.export_qr_codes, style='Red.TButton')
        qr_button.pack(pady=5)

        self.active_window = export_window

    # Export via .json window configurations
    def export_json(self):
        self.close_active_window()
        export_window = tk.Toplevel(self.master)
        export_window.title("Export Options")
        export_window.geometry("200x150")
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
                    json.dump(self.accounts, file_path, indent=4)  # Export accounts as unencrypted JSON
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

        export_encrypted_button = ttk.Button(export_window, text="Export via JSON Encrypted", command=export_encrypted, style='Red.TButton')
        export_encrypted_button.pack(pady=5)
        export_unencrypted_button = ttk.Button(export_window, text="Export via JSON Unencrypted", command=export_unencrypted, style='Red.TButton')
        export_unencrypted_button.pack(pady=5)
        export_txt_button = ttk.Button(export_window, text="Export via TXT", command=export_txt, style='Red.TButton')
        export_txt_button.pack(pady=5)

    # Export via QR Code configuration
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

    # Import Data window configurations
    def import_data(self):
        from gui import TwoFactorAppGUI
        self.close_active_window()

        # Import via .json configuration
        def import_json():
            key = backend.load_key()
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
                        override = messagebox.askyesno(
                            "Duplicate Account",
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
                    save_accounts(existing_accounts, key)
                    messagebox.showinfo("Success", "Data imported successfully!")

                    self.master.destroy()
                    TwoFactorAppGUI(tk.Tk(), self.key)
                except (json.JSONDecodeError, ValueError):
                    messagebox.showerror("Invalid JSON format")
                except Exception as e:
                    messagebox.showerror(f"An error occurred: {str(e)}")

        # Import via QR Code configuration
        def import_from_qr():
            # Major Bug
            messagebox.showinfo("Maintenance", "Sorry, this service is temporarily unavailable.")

        import_window = tk.Toplevel(self.master)
        import_window.title("Import Data")
        import_window.geometry("200x100")
        import_window.resizable(False, False)
        import_window.configure(bg="white")

        import_json_button = ttk.Button(import_window, text="Import JSON", command=import_json, style='Red.TButton')
        import_json_button.pack(pady=5)
        import_qr_button = ttk.Button(import_window, text="Import QR Code", command=import_from_qr, style='Red.TButton')
        import_qr_button.pack(pady=5)

        self.active_window = import_window

    # Configures account name window for importing accounts via QR Code
    def ask_for_account_name(self):
        dialog_window = tk.Toplevel(self.master)
        dialog_window.title("Enter Account Name")
        dialog_window.geometry("300x150")
        dialog_window.resizable(False, False)
        dialog_window.configure(bg="white")

        label = tk.Label(dialog_window, text="Enter a unique account name:", bg="white")
        label.pack(pady=10)

        account_name_var = tk.StringVar()
        entry = tk.Entry(dialog_window, textvariable=account_name_var)
        entry.pack(pady=10)
        def confirm(event=None):
            account_name = account_name_var.get()
            if account_name:
                dialog_window.destroy()
            else:
                messagebox.showerror("Error", "Account name cannot be empty.")
        dialog_window.bind("<Return>", confirm)
        entry.focus_set()

        confirm_button = ttk.Button(dialog_window, text="Confirm", command=confirm, style='Red.TButton')
        confirm_button.pack(pady=10)
        dialog_window.transient(self.master)
        dialog_window.grab_set()  # Grab focus
        return account_name_var.get()

    #Configures Recycle Bin window
    def manage_recycle_bin(self):
        self.close_active_window()
        recycle_bin_window = tk.Toplevel(self.master)
        recycle_bin_window.title("Recycle Bin")
        recycle_bin_window.geometry("400x300")
        recycle_bin_window.resizable(False, False)
        recycle_bin_window.configure(bg="white")

        self.update_recycle_bin(recycle_bin_window)
        self.active_window = recycle_bin_window

    # Loads/Saves accounts that have been marked deleted
    def load_deleted_accounts(self):
        try:
            with open('deleted.json', 'r') as f:
                self.deleted_accounts = json.load(f)
        except FileNotFoundError:
            self.deleted_accounts = {}
    def save_deleted_accounts(self):
        with open('deleted.json', 'w') as f:
            json.dump(self.deleted_accounts, f, indent=4)

    # Updates recycle bin
    def update_recycle_bin(self, recycle_bin_window):
        for widget in recycle_bin_window.winfo_children():
            widget.destroy()

        recycle_bin_frame = tk.Frame(recycle_bin_window, bg="white")
        recycle_bin_frame.pack(fill="both", expand=True)

        recycle_bin_label = tk.Label(recycle_bin_frame, text="Recycle Bin", font=("Helvetica", 16), bg="white")
        recycle_bin_label.pack(pady=(10, 5))

        self.load_deleted_accounts()

        if not self.deleted_accounts:
            no_accounts_label = tk.Label(recycle_bin_frame, text="No Accounts Found", bg="white")
            no_accounts_label.pack(pady=20)
        else:
            canvas = tk.Canvas(recycle_bin_frame, bg="white")
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            scrollbar = tk.Scrollbar(recycle_bin_frame, orient=tk.VERTICAL, command=canvas.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

            scrollable_frame = tk.Frame(canvas, bg="white")
            canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)

            for account_name in self.deleted_accounts.keys():
                account_frame = tk.Frame(scrollable_frame, relief="ridge", bg="white", highlightbackground="black", highlightthickness=2)
                account_frame.pack(pady=10, padx=10, fill="x")
                account_label = tk.Label(account_frame, text=f"Account: {account_name}", bg="white")
                account_label.pack(side=tk.LEFT, padx=10)

                restore_button = ttk.Button(account_frame, text="Restore", command=lambda name=account_name: self.restore_account(name))
                restore_button.pack(side=tk.LEFT, padx=10)
                permanent_delete_button = ttk.Button(account_frame, text="Permanently Delete", command=lambda name=account_name: self.permanent_delete_account(name))
                permanent_delete_button.pack(side=tk.LEFT, padx=10)

                separator = ttk.Separator(scrollable_frame, orient="horizontal")
                separator.pack(fill="x", pady=5)
            scrollable_frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))

            def on_mouse_wheel(event):
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            
            canvas.bind_all("<MouseWheel>", on_mouse_wheel)
            scrollable_frame.bind("<MouseWheel>", on_mouse_wheel)

        self.save_deleted_accounts()

    # Automatically clears recycle bin every month
    def monthly_cleanup(self):
        today = datetime.today()
        if today.day == 1:
            self.clear_recycle_bin()
    def clear_recycle_bin(self):
        self.deleted_accounts = {}
        self.save_deleted_accounts()
        messagebox.showinfo("Recycle Bin Cleared", "Recycle Bin has been cleared for the new month.")
        self.update_recycle_bin(self.master.winfo_children()[1])

    # Delete/Restore account functionality
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

                messagebox.showinfo("Account Restored", f"Account '{account_name}' restored successfully!")
                self.manage_recycle_bin()
            except Exception as e:
                messagebox.showerror("Error", f"Error restoring account: {str(e)}")
        else:
            messagebox.showinfo("Account Not Found", f"Account '{account_name}' not found in deleted accounts.")

    # Permanently deletes account
    def permanent_delete_account(self, account_name):
        confirmation = messagebox.askyesno("Confirm Permanent Delete", f"Are you sure you want to permanently delete account '{account_name}'?")
        if confirmation:
            del self.deleted_accounts[account_name]
            self.save_deleted_accounts()
            self.update_recycle_bin(self.master.winfo_children()[1])
            messagebox.showinfo("Permanent Delete", f"Account '{account_name}' permanently deleted.")
            self.manage_recycle_bin()