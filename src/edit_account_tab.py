import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox, filedialog
from notifications import NotificationManager
from backend import load_key, encrypt_message, decrypt_message
import pyotp, qrcode, os, time, pyperclip, json, qrcode

class EditAccount:
    def __init__(self, master, key, accounts, notifications):
        # Initial add_accout_tab configurations
        self.master = master
        self.key = load_key()
        self.accounts = accounts
        self.notifications = notifications
        self.edit_window_open = False
        self.edit_name_window_open = False
    # Retrieves accounts
    def get_accounts(self):
        return self.accounts

    # Displays TOTP Copied notification
    def copy_totp(self, event, totp_text):
        pyperclip.copy(totp_text)
        self.notifications.show_notification("TOTP code copied to clipboard!")

    # Function to handle editing an account
    def edit_account(self, name):
        # Closes the edit window
        def close_edit_window():
            self.edit_window_open = False
            edit_window.destroy()

        # Opens and configures the edit window
        if not self.edit_window_open:
            self.edit_window_open = True
            edit_window = tk.Toplevel(self.master)
            edit_window.title("Edit Account")
            edit_window.geometry("150x150")
            edit_window.resizable(False, False)
            edit_window.configure(bg="white")

            edit_frame = tk.Frame(edit_window, bg="white")
            edit_frame.pack(fill="both", expand=True)

            # Exports via QR code
            def export_qr_code():
                if edit_window:
                    edit_window.destroy()
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
                close_edit_window()
            
            # Function to edit the account name
            def edit_name():
                # Closes the edit name window
                def close_edit_name_window():
                    self.edit_name_window_open = False
                    edit_name_window.destroy()

                # Sets/configures edit account name window
                if not self.edit_name_window_open:
                    self.edit_name_window_open = True
                    close_edit_window()

                    edit_name_window = tk.Toplevel(self.master)
                    edit_name_window.title(f"Edit {name}")
                    edit_name_window.geometry("150x150")
                    edit_name_window.resizable(False, False)
                    edit_name_window.configure(bg="white")

                    edit_name_frame = tk.Frame(edit_name_window, bg="white")
                    edit_name_frame.pack(fill="both", expand=True)
                    name_label = tk.Label(edit_name_frame, text="Enter New Name:", bg="white")
                    name_label.pack()
                    initial_character_count = len(name)

                    # Validates that the account name is <30 characters and has no invalid chars
                    def validate_name_len(name):
                        if len(name) > 30:
                            messagebox.showinfo("Character Limit", "Character Limit is 30")
                            name_window.lift()
                            return False
                        return True
                    def validate_name_chars(name):
                        invalid_chars = "\\/:*?\"<>|"
                        for char in invalid_chars:
                            if char in name:
                                messagebox.showinfo("Invalid Character", f"Name cannot contain '{char}'")
                                name_window.lift()
                                return False
                        return True
                    name_entry = tk.Entry(edit_name_frame, validate="key", validatecommand=vcmd_chars)
                    name_entry.pack()
                    name_entry.insert(0, name)
                    name_entry.focus_set()
                    
                    # Updates character count label
                    def update_char_count(event):
                        char_count_label.config(text=f"Characters: {len(name_entry.get())}")
                    name_entry.bind("<KeyRelease>", update_char_count)
                    char_count_label = tk.Label(edit_name_frame, text=f"Characters: {initial_character_count}", bg="white")
                    char_count_label.pack()

                    def remove_focus(event):
                        name_entry.focus_set()
                        edit_name_frame.focus_set()
                    edit_name_frame.bind("<Button-1>", remove_focus)

                    # Saves the new account name
                    def save_name():
                        from gui import TwoFactorAppGUI
                        new_name = name_entry.get().strip()
                        if validate_name(new_name) and new_name != name:
                            if new_name in self.accounts:
                                error_label = tk.Label(edit_name_frame, text="Invalid Name", fg="red", bg="white")
                                error_label.pack()
                            else:
                                self.accounts[new_name] = self.accounts.pop(name)
                                key = backend.load_key()
                                backend.save_accounts(self.accounts, key)
                                messagebox.showinfo("Success", "Account Name edited successfully!")
                                self.master.destroy()
                                TwoFactorAppGUI(tk.Tk(), self.key)
                        else:
                            error_label = tk.Label(edit_name_frame, text="Invalid Name", fg="red", bg="white")
                            error_label.pack()
                            self.master.after(3000, lambda: error_label.pack_forget())
                    name_entry.bind("<Return>", lambda event: save_name())

                    continue_button = ttk.Button(edit_name_frame, text="Save", command=save_name, style='Red.TButton')
                    continue_button.pack(pady=5)
                    edit_name_window.transient(self.master)
                    edit_name_window.grab_set()
                    edit_name_window.protocol("WM_DELETE_WINDOW", close_edit_name_window)

            # Moves deleted account to the Recycle Bin
            def delete_account():
                from gui import TwoFactorAppGUI
                try:
                    with open('data.vv', 'rb') as file:
                        encrypted_data = file.read()
                        decrypted_data = decrypt_message(encrypted_data, self.key)
                        accounts_data = json.loads(decrypted_data)
                except FileNotFoundError:
                    accounts_data = {}

                if name in accounts_data:
                    confirmed = messagebox.askyesno("Delete Account", "Are you sure you want to delete this account?")
                    if confirmed:
                        accounts_data[name]['deleted'] = True
                        accounts_data[name]['delete_timestamp'] = int(time.time())  # Record deletion time
                        
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
                        messagebox.showinfo("Success", "Account moved to deleted.json.")
                        self.master.destroy()
                else:
                    messagebox.showerror("Error", "Account not found in data.")
                TwoFactorAppGUI(tk.Tk(), self.key)

            # Configures edit window 
            edit_name_button = ttk.Button(edit_frame, text="Edit Name", command=edit_name, style='Red.TButton')
            edit_name_button.pack(pady=5, padx=10)
            export_qr_button = ttk.Button(edit_frame, text="Export QR Code", command=export_qr_code, style='Red.TButton')
            export_qr_button.pack(pady=5, padx=10)
            delete_account_button = ttk.Button(edit_frame, text="Delete Account", command=delete_account, style='Red.TButton')
            delete_account_button.pack(pady=5, padx=10)

            edit_window.protocol("WM_DELETE_WINDOW", close_edit_window)
