import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox, filedialog, Toplevel
from notifications import NotificationManager
from backend import load_key, encrypt_message, decrypt_message
import backend, pyotp, qrcode, os, time, json

class EditAccount:
    def __init__(self, master, key, accounts, notifications):
        # Initial add_accout_tab configurations
        self.master = master
        self.key = load_key()
        self.accounts = accounts
        self.notifications = notifications
        self.active_window = None

    # Function that retrieves the accounts
    def get_accounts(self):
        return self.accounts

    # Function that Closes active window
    def close_active_window(self):
        if self.active_window:
            self.active_window.destroy()
            self.active_window = None

    # Edit Account Function
    def edit_account(self, name):
        # Checks if another edit window is open
        if self.active_window:
            messagebox.showinfo("Already Opened", "Another edit window is already open.")
            return
        # Opens and configures the edit window
        edit_window = tk.Toplevel(self.master)
        edit_window.title(f"Edit Account - {name}")
        edit_window.geometry("150x150")
        edit_window.resizable(False, False)
        edit_window.configure(bg="white")

        edit_frame = tk.Frame(edit_window, bg="white")
        edit_frame.pack(fill="both", expand=True)
        self.active_window = edit_window

        # Function that closes active window
        def on_close():
            edit_window.destroy()
            self.active_window = None
        edit_window.protocol("WM_DELETE_WINDOW", on_close)

        # Function that exports the account via QR code
        def export_qr_code():
            self.close_active_window()
            account_info = self.accounts[name]
            secret_key = account_info['secret']
            provisioning_uri = pyotp.totp.TOTP(secret_key).provisioning_uri(name)

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(provisioning_uri)
            qr.make(fit=True)

            dest_folder = filedialog.askdirectory()

            if dest_folder:
                qr_code_file_path = os.path.join(dest_folder, f"{name}_QR_code.png")
                qr_img = qr.make_image(fill_color="black", back_color="white")
                qr_img.save(qr_code_file_path)
                self.notifications.show_notification(f"QR code exported successfully to {qr_code_file_path}")
            else:
                self.notifications.show_notification("QR code export cancelled.")
        
        # Edit Name Function
        def edit_name():
        # Sets/configures edit account name window
            edit_name_window = tk.Toplevel(self.master)
            edit_name_window.title(f"Edit {name}")
            edit_name_window.geometry("150x150")
            edit_name_window.resizable(False, False)
            edit_name_window.configure(bg="white")
            self.active_window = edit_name_window

            edit_name_frame = tk.Frame(edit_name_window, bg="white")
            edit_name_frame.pack(fill="both", expand=True)
            name_label = tk.Label(edit_name_frame, text="Enter New Name:", bg="white")
            name_label.pack()
            initial_character_count = len(name)

            # Function that validates that the account name
            def validate_name(name):
                if len(name) > 30:
                    messagebox.showinfo("Character Limit", "Character Limit is 30")
                    return False
                invalid_chars = "\\/:*?\"<>|"
                for char in invalid_chars:
                    if char in name:
                        messagebox.showinfo("Invalid Character", f"Name cannot contain '{char}'")
                        return False
                return True
            vcmd = (edit_name_frame.register(validate_name), "%P")
            name_entry = tk.Entry(edit_name_frame, validate="key", validatecommand=vcmd)
            name_entry.pack()
            name_entry.insert(0, name)
            name_entry.focus_set()
            
            # Function that updates the character count label
            def update_char_count(event):
                char_count_label.config(text=f"Characters: {len(name_entry.get())}")
            name_entry.bind("<KeyRelease>", update_char_count)
            char_count_label = tk.Label(edit_name_frame, text=f"Characters: {initial_character_count}", bg="white")
            char_count_label.pack()

            error_label = tk.Label(edit_name_frame, text="", fg="red", bg="white")
            error_label.pack()

            # Function that saves the new account name
            def save_name():
                from gui import TwoFactorAppGUI
                new_name = name_entry.get().strip()

                if len(new_name) == 0:
                    error_label.config(text="Name Required")
                    return

                if validate_name(new_name) and new_name != name:
                    if new_name in self.accounts:
                        error_label.config(text="Name already exists")
                    else:
                        self.accounts[new_name] = self.accounts.pop(name)
                        key = backend.load_key()
                        backend.save_accounts(self.accounts, key)
                        messagebox.showinfo("Success", "Account Name edited successfully!")

                        self.master.destroy()
                        TwoFactorAppGUI(tk.Tk(), self.key)
                else:
                    error_label.config(text="Invalid Name")
                error_label.pack()
                self.master.after(3000, lambda: error_label.config(text=""))
            name_entry.bind("<Return>", lambda event: save_name())

            # Edit Account Name configurations
            continue_button = ttk.Button(edit_name_frame, text="Save", command=save_name, style='Red.TButton')
            continue_button.pack(pady=5)
            edit_name_window.transient(self.master)
            edit_name_window.grab_set()

        # Delete Account Function
        def delete_account():
            from gui import TwoFactorAppGUI

            # Function that adds the account to the recycle bin
            def confirm_deletion():
                try:
                    with open('data.vv', 'rb') as file:
                        encrypted_data = file.read()
                        decrypted_data = decrypt_message(encrypted_data, self.key)
                        accounts_data = json.loads(decrypted_data)
                except FileNotFoundError:
                    accounts_data = {}

                if name in accounts_data:
                    accounts_data[name]['deleted'] = True
                    accounts_data[name]['delete_timestamp'] = int(time.time())

                    deleted_data = {}
                    if os.path.exists('deleted.json') and os.path.getsize('deleted.json') > 0:
                        try:
                            with open('deleted.json', 'r') as deleted_file:
                                deleted_data = json.load(deleted_file)
                        except json.JSONDecodeError:
                            messagebox.showerror("Error", "Error loading deleted.json: Invalid JSON format.")
                            return

                    deleted_data[name] = accounts_data[name]

                    with open('deleted.json', 'w') as deleted_file:
                        json.dump(deleted_data, deleted_file, indent=4)
                    del accounts_data[name]
                    with open('data.vv', 'wb') as file:
                        encrypted_data = encrypt_message(json.dumps(accounts_data), self.key)
                        file.write(encrypted_data)

                    messagebox.showinfo("Success", "Account moved to recycle bin.")
                    self.master.destroy()
                    TwoFactorAppGUI(tk.Tk(), self.key)
                else:
                    messagebox.showerror("Error", "Account not found in data.")
                    confirm_window.destroy()

            # Account Deletion Confirmation window configurations
            confirm_window = Toplevel(self.master)
            confirm_window.title("Confirm Delete")
            confirm_window.geometry("300x100")
            confirm_window.resizable(False, False)
            confirm_window.configure(bg="white")
            confirm_window.grab_set()

            confirm_label = tk.Label(confirm_window, text="Are you sure you want to delete this account?", bg="white")
            confirm_label.pack(pady=10)
            button_frame = tk.Frame(confirm_window, bg="white")
            button_frame.pack()

            confirm_button = ttk.Button(button_frame, text="Yes", command=confirm_deletion, style='Red.TButton')
            confirm_button.pack(side="left", padx=10)
            cancel_button = ttk.Button(button_frame, text="No", command=confirm_window.destroy, style='Red.TButton')
            cancel_button.pack(side="left", padx=10)

            confirm_window.transient(self.master)
            confirm_window.wait_window(confirm_window)

        # Configures edit window 
        edit_name_button = ttk.Button(edit_frame, text="Edit Name", command=edit_name, style='Red.TButton')
        edit_name_button.pack(pady=5, padx=10)
        export_qr_button = ttk.Button(edit_frame, text="Export QR Code", command=export_qr_code, style='Red.TButton')
        export_qr_button.pack(pady=5, padx=10)
        delete_account_button = ttk.Button(edit_frame, text="Delete Account", command=delete_account, style='Red.TButton')
        delete_account_button.pack(pady=5, padx=10)
