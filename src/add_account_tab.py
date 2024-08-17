from customtkinter import *
from ttkbootstrap.tooltip import ToolTip
from tkinter import messagebox
from labels import LabelsManager
from search import SearchFunctions
import backend, pyotp, binascii, time, datetime, configparser

class AddAccountTab:
    def __init__(self, master, right_frame, accounts, update_labels, search_functions, groups):
        # Initial add_accout_tab configurations
        self.master = master
        self.right_frame = right_frame
        self.accounts = accounts
        self.update_labels = update_labels
        self.search_functions = search_functions
        self.groups = ["None"] + [group for group in groups if group not in ["All Accounts", "Add Group"]]
        self.load_preferences()

    # Function to validate TOTP key through backend
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

    # Add Account Function
    def add_account(self):
        # Add Account frame configurations
        name_frame = CTkFrame(self.right_frame, width=600, height=700)
        name_frame.place(relx=0.61, rely=0, anchor="n")

        def close_frame():
            name_frame.destroy()

        x_button = CTkButton(name_frame, command=close_frame, text="❌", fg_color="white", border_color="black", text_color="black", hover_color="red", border_width=2, width=50, height=20, cursor="hand2")
        x_button.place(relx=0.8, rely= 0.03, anchor="ne")

        title_label = CTkLabel(name_frame, text="Add Account", font=("Helvetica", 30, "bold", "underline"))
        title_label.place(relx=0.45, rely=0.15, anchor="center")

        name_label = CTkLabel(name_frame, text="Enter Name:", font=("Helvetica", 20, "bold"))
        name_label.place(relx=0.05, rely=0.21, anchor="nw")
        key_label = CTkLabel(name_frame, text="Enter Key:", font=("Helvetica", 20, "bold"))
        key_label.place(relx=0.05, rely=0.31, anchor="nw")

        # Function to validate account name
        def validate_name(name):
            invalid_chars = "\\/:*?\"<>|"
            for char in invalid_chars:
                if char in name:
                    messagebox.showerror("Invalid Character", f"Name cannot contain '{char}'")
                    return False
            return True

        # Entry configurations
        vcmd = (name_frame.register(validate_name), "%P")
        name_entry = CTkEntry(name_frame, validate="key", validatecommand=vcmd, placeholder_text="Enter Name", width=300, height=40, border_width=2, border_color="red")
        name_entry.place(relx=0.25, rely=0.2, anchor="nw")
        name_entry.focus_set()

        key_entry = CTkEntry(name_frame, placeholder_text="Enter Key", width=300, height=40, border_width=2, border_color="red")
        key_entry.place(relx=0.25, rely=0.3, anchor="nw")

        # Add Group Dropdown
        group_label = CTkLabel(name_frame, text="Select Group:", font=("Helvetica", 20, "bold"))
        group_label.place(relx=0.05, rely=0.4, anchor="nw")
        
        self.group_dropdown = CTkOptionMenu(name_frame, values=self.groups, height=35, font=("Helvetica", 14), fg_color="white", text_color="black", dropdown_font=("Helvetica", 14), dropdown_text_color="black", corner_radius=2, button_color="red", button_hover_color="#EE4B2B", dropdown_fg_color="white", dropdown_hover_color="red", hover=True, anchor="center")
        self.group_dropdown.place(relx=0.3, rely=0.4, anchor="nw")
        self.group_dropdown.set(self.groups[0])

        # Function to verify/create account
        def confirm_account():
            # Function to get date of account ceation 
            def get_ordinal_suffix(day):
                if 10 <= day % 100 <= 20:
                    suffix = 'th'
                else:
                    suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
                return suffix

            # Function to format time
            def format_datetime():
                now = datetime.datetime.now()
                day = now.day
                suffix = get_ordinal_suffix(day)
                if self.time_format == 'on':
                    formatted_date = now.strftime(f"%B {day}{suffix}, %Y at %H:%M")
                else:
                    formatted_date = now.strftime(f"%B {day}{suffix}, %Y at %I:%M%p")
                return formatted_date

            global creation_time
            creation_time = format_datetime()
            print(f"Exact Time of Save: {creation_time}")

            name = name_entry.get().strip()
            key = key_entry.get().strip()
            group = self.group_dropdown.get()

            # Validates the name/key
            if not name:
                messagebox.showerror("Invalid Entry", "Name is required.")
                return
            if not key:
                messagebox.showerror("Invalid Entry", "Key is required.")
                return
            if not self.is_valid_totp_key(key):
                messagebox.showerror("Invalid Entry", "Invalid Key.")
                return

            # Checks if name is alreaduy used
            original_name = name
            count = 1
            while name in self.accounts:
                name = f"{original_name} ({count})"
                count += 1
            group = None if group == "None" else group
            self.accounts[name] = {'key': key, 'secret': pyotp.TOTP(key).secret, 'group': group, 'created': creation_time}

            # Saves/updates accounts
            backend.save_accounts(self.accounts, backend.load_key())
            self.update_labels(self.accounts)
            close_frame()
            messagebox.showinfo("Success", "Account added successfully!")

        # Save button configurations
        save_button = CTkButton(name_frame, text="💾", command=confirm_account, fg_color="white", hover_color="red", text_color="black", width=100, height=40, border_width=2, font=("Helvetica", 20, "bold"), cursor='hand2')
        save_button.place(relx=0.7, rely=0.425, anchor="center")
        ToolTip(save_button, text="Save Account")
        key_entry.bind("<Return>", lambda event: confirm_account())

    # Function to load preferences
    def load_preferences(self):
        config = configparser.ConfigParser()
        config.read('preferences.ini')
        self.time_format = config.get('Preferences', 'time_format', fallback=None)