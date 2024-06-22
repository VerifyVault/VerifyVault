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
        self.name_window_open = False

    # Validates the TOTP key
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

    # Function to handle adding an account
    def add_account(self):
        if not self.name_window_open:
            # Opens and configures Add Account window
            self.name_window_open = True
            name_window = tk.Toplevel(self.master)
            name_window.title("Add Account")
            name_window.geometry("150x120")
            name_window.resizable(False, False)
            name_window.configure(bg="white")

            name_frame = tk.Frame(name_window, bg="white")
            name_frame.pack(fill="both", expand=True)
            name_label = tk.Label(name_frame, text="Enter Name:", bg="white")
            name_label.pack()

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
            vcmd_len = (name_frame.register(validate_name_len), "%P")
            vcmd_chars = (name_frame.register(validate_name_chars), "%P")
            name_entry = tk.Entry(name_frame, validate="key", validatecommand=vcmd_chars)
            name_entry.pack()
            name_entry.focus_set()

            # Counts account name characters
            def update_char_count(event):
                char_count_label.config(text=f"Characters: {len(name_entry.get())}")
            name_entry.bind("<KeyRelease>", update_char_count)
            char_count_label = tk.Label(name_frame, text="Characters: 0", bg="white")
            char_count_label.pack()

            # Voides text bar selection after clicking away from it
            def remove_focus(event):
                name_entry.focus_set()
                name_frame.focus_set()
            name_frame.bind("<Button-1>", remove_focus)

            # Checks if the account name already exists
            def add_account_callback():
                nonlocal name_window
                name = name_entry.get().strip()
                if name:
                    name_window.destroy()
                    self.name_window_open = False

                    if name in self.accounts:
                        override = messagebox.askyesno("Override Account", f"An account with the name '{name}' already exists. Do you want to override it?")
                        if override:
                            del self.accounts[name]
                        else:
                            count = 1
                            while f"{name} ({count})" in self.accounts:
                                count += 1
                            name = f"{name} ({count})"

                    # Configures Key window
                    key_window = tk.Toplevel(self.master)
                    key_window.title("Add Account - Key")
                    key_window.geometry("250x200")
                    key_window.resizable(False, False)
                    key_window.configure(bg="white")

                    key_frame = tk.Frame(key_window, bg="white")
                    key_frame.pack(fill="both", expand=True)
                    key_label = tk.Label(key_frame, text="Enter Key:", bg="white")
                    key_label.pack()

                    key_entry = tk.Entry(key_frame)
                    key_entry.pack()
                    key_entry.focus_set()
                    self.error_label = tk.Label(key_frame, text="", bg="white")
                    self.error_label.pack()

                    def remove_focus(event):
                        key_entry.focus_set()
                        key_frame.focus_set()
                    key_frame.bind("<Button-1>", remove_focus)

                    # Validates key and adds account
                    def confirm_account():
                        nonlocal name_window
                        key = key_entry.get().strip()
                        if key:
                            if self.is_valid_totp_key(key):
                                self.accounts[name] = {'key': key, 'secret': pyotp.TOTP(key).secret}
                                key = backend.load_key()
                                backend.save_accounts(self.accounts, key)
                                self.update_labels(self.accounts)
                                key_window.destroy()
                                name_window.destroy()
                                self.name_window_open = False
                                self.notifications.show_notification("Account added successfully!")
                            else:
                                self.error_label.config(text="Invalid TOTP Key. Please enter a valid key.", fg="red")
                        else:
                            error_label = tk.Label(key_frame, text="Please input a valid key", fg="red", bg="white")
                            error_label.pack()
                            self.master.after(3000, lambda: error_label.pack_forget())

                    # Sets canvas/buttons for key window
                    self.canvas.update_idletasks()
                    self.canvas.config(scrollregion=self.canvas.bbox("all"))

                    confirm_button = ttk.Button(key_frame, text="Confirm", command=confirm_account, style='Red.TButton')
                    confirm_button.pack(pady=5)
                    key_entry.bind("<Return>", lambda event: confirm_account())
                    key_window.transient(self.master)
                    key_window.grab_set()

                else:
                    # Error message if no name was set
                    error_label = tk.Label(name_frame, text="Name Required", fg="red", bg="white")
                    error_label.pack()
                    self.master.after(3000, lambda: error_label.pack_forget())

            # Sets buttons for Name window        
            name_entry.bind("<Return>", lambda event: add_account_callback())
            continue_button = ttk.Button(name_frame, text="Continue", command=add_account_callback)
            continue_button.pack(pady=5)
            name_window.transient(self.master)
            name_window.grab_set()

            # Closes name window
            def close_name_window():
                name_window.destroy()
                self.name_window_open = False
            name_window.protocol("WM_DELETE_WINDOW", close_name_window)
            
            # Updates accounts
            key = backend.load_key()
            backend.save_accounts(self.accounts, key)
            self.update_labels(self.accounts)
            self.search_functions.update_accounts(self.accounts)