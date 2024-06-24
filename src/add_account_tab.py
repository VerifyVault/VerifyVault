import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from labels import LabelsManager
from search import SearchFunctions
from notifications import NotificationManager
import backend, pyotp, binascii

class AddAccountTab:
    def __init__(self, master, canvas, accounts, notifications, update_labels, search_functions):
        # Initial edit_accout_tab configurations
        self.canvas = canvas
        self.master = master
        self.accounts = accounts
        self.notifications = notifications
        self.update_labels = update_labels
        self.search_functions = search_functions
        self.active_window = None

    # Funtion that closes the active window
    def close_active_window(self):
        if self.active_window:
            self.active_window.destroy()
            self.active_window = None

    # Function that validates the TOTP key through the backend
    def is_valid_totp_key(self, key):
        try:
            totp = pyotp.TOTP(key)
            if totp.verify(totp.now()):
                return True
            else:
                print("Invalid TOTP code.")
                return Falseadd
        except (ValueError, binascii.Error) as e:
            if "Non-base32 digit found" in str(e):
                print("Invalid TOTP Key Format.")
            else:
                print(f"Error generating TOTP: {e}")
            return False

    # Add Account function
    def add_account(self):
        # Opens and configures Add Account window
        self.close_active_window()
        name_window = tk.Toplevel(self.master)
        name_window.title("Add Account")
        name_window.geometry("150x120")
        name_window.resizable(False, False)
        name_window.configure(bg="white")

        name_frame = tk.Frame(name_window, bg="white")
        name_frame.pack(fill="both", expand=True)
        name_label = tk.Label(name_frame, text="Enter Name:", bg="white")
        name_label.pack()
        self.active_window = name_window

        # Funtion that validates the account name
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
        vcmd = (name_frame.register(validate_name), "%P")
        name_entry = tk.Entry(name_frame, validate="key", validatecommand=vcmd)
        name_entry.pack()
        name_entry.focus_set()

        # Function that counts the number of characters in the account name 
        def update_char_count(event):
            char_count_label.config(text=f"Characters: {len(name_entry.get())}")
        name_entry.bind("<KeyRelease>", update_char_count)
        char_count_label = tk.Label(name_frame, text="Characters: 0", bg="white")
        char_count_label.pack()

        # Funtion that checks if the account name already exists
        def add_account_callback():
            name = name_entry.get().strip()
            if name:
                if name in self.accounts:
                    override = messagebox.askyesno("Override Account", f"An account with the name '{name}' already exists. Do you want to override it?")
                    if override:
                        del self.accounts[name]
                    else:
                        count = 1
                        while f"{name} ({count})" in self.accounts:
                            count += 1
                        name = f"{name} ({count})"
                # Key window Configurations
                self.close_active_window()
                key_window = tk.Toplevel(self.master)
                key_window.title("Add Key")
                key_window.geometry("150x120")
                key_window.resizable(False, False)
                key_window.configure(bg="white")

                key_frame = tk.Frame(key_window, bg="white")
                key_frame.pack(fill="both", expand=True)
                key_label = tk.Label(key_frame, text="Enter Key:", bg="white")
                key_label.pack()

                key_entry = tk.Entry(key_frame)
                key_entry.pack()
                key_entry.focus_set()

                self.error_label = tk.Label(key_frame, text="", fg="red", bg="white")
                self.error_label.pack()
                self.active_window = key_window

                # Function that validates the key and adds the account
                def confirm_account():
                    key = key_entry.get().strip()
                    if key:
                        if self.is_valid_totp_key(key):
                            self.accounts[name] = {'key': key, 'secret': pyotp.TOTP(key).secret}
                            
                            key = backend.load_key()
                            backend.save_accounts(self.accounts, key)
                            
                            self.update_labels(self.accounts)
                            self.notifications.show_notification("Account added successfully!")
                            self.close_active_window()
                        else:
                            self.error_label.config(text="Invalid Key")
                            self.master.after(3000, lambda: self.error_label.config(text=""))

                # Sets canvas/buttons for key window
                self.canvas.update_idletasks()
                self.canvas.config(scrollregion=self.canvas.bbox("all"))

                confirm_button = ttk.Button(key_frame, text="Confirm", command=confirm_account, style='Red.TButton')
                confirm_button.pack(pady=5)

                key_entry.bind("<Return>", lambda event: confirm_account())
                key_window.transient(self.master)
                key_window.grab_set()
            else:
                # Error message if no name was inputted
                error_label = tk.Label(name_frame, text="Name Required", fg="red", bg="white")
                error_label.pack()
                self.master.after(3000, lambda: error_label.pack_forget())

        # Sets buttons for Name window        
        name_entry.bind("<Return>", lambda event: add_account_callback())
        continue_button = ttk.Button(name_frame, text="Continue", command=add_account_callback)
        continue_button.pack(pady=5)

        name_window.transient(self.master)
        name_window.grab_set()
        
        # Updates accounts
        key = backend.load_key()
        backend.save_accounts(self.accounts, key)
        self.update_labels(self.accounts)
        self.search_functions.update_accounts(self.accounts)