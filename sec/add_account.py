import tkinter as tk
from customtkinter import *
from tkinter import messagebox
from ttkbootstrap.tooltip import ToolTip
import backend, pyotp, datetime, configparser

class AddAccountFunctions:
    def __init__(self, master, accounts, right_frame, update_labels, groups):
        # Store references to the master window and other components
        self.master = master
        self.accounts = accounts
        self.right_frame = right_frame
        self.update_labels = update_labels

         # Initialize groups, ensuring "None" is included and specific groups are excluded
        self.groups = ["None"] + [group for group in groups if group not in ["All Accounts", "Add Group"]] # List of groups
        self.truncated_groups = [group if len(group) <= 12 else group[:12] + "..." for group in self.groups]
        self.load_preferences() # Load user preferences

        self.frame_open = False # Track if the frame is currently open

    def open_help_window(self):
        # Create the help window
        help_window = CTkToplevel(self.master)
        help_window.geometry("500x300")
        help_window.title("Add Account Help")
        help_window.resizable(False, False)
        help_window.after(250, lambda: help_window.iconbitmap('images/VerifyVaultLogo.ico'))
        help_window.grab_set() # Ensure the window is focused

        # Define help text content
        help_text = (
            "- Any duplicate name will automatically be renumbered\n\n"
            "- Name cannot contain the following: \\ / : * ? \" < > |\n\n"
            "- Invalid Key: Secret key isn't valid"
        )

        # Create and place labels in the help window
        title_label = CTkLabel(help_window, text="Add Account Help", font=("Helvetica", 30, "bold", "underline")).place(relx=0.5, rely=0.05, anchor="center")
        help_label = CTkLabel(help_window, text=help_text, font=("Helvetica", 20)).place(relx=0.02, rely=0.15, anchor="nw")

    # Add Account Function
    def add_account(self):
        # Checks if frame is already open
        if self.frame_open:
            messagebox.showerror("Error", "This window is already open. Please close it before opening a new one.")
            return
        self.frame_open = True # Mark the frame as open

        # Configure the Add Account frame
        add_frame = CTkFrame(self.right_frame, width=600, height=700)
        add_frame.place(relx=0.61, rely=0, anchor="n")

        # Function to close the frame
        def close_frame():
            add_frame.destroy() # Destroy the frame
            self.frame_open = False # Mark the frame as closed

        # Close button configuration
        close_button = CTkButton(add_frame, command=close_frame, text="❌", fg_color="white", border_color="black", text_color="black", hover_color="red", border_width=2, width=50, height=20, cursor="hand2")
        close_button.place(relx=0.8, rely=0.03, anchor="ne")
        ToolTip(close_button, text="Close") # Tooltip for close button

        # Help button configuration
        help_button = CTkButton(add_frame, text="❓", command=self.open_help_window, font=("Helvetica", 20, "bold"), fg_color="white", hover_color="red", width=30, height=10, border_width=2, corner_radius=2, text_color="black", cursor='hand2')
        help_button.place(relx=0.05, rely=0.03, anchor="n")
        ToolTip(help_button, text="Help") # Tooltip for help button

        # Title and label configurations
        title_label = CTkLabel(add_frame, text="Add Account", font=("Helvetica", 30, "bold", "underline"))
        title_label.place(relx=0.45, rely=0.15, anchor="center")

        name_label = CTkLabel(add_frame, text="Enter Name:", font=("Helvetica", 20, "bold"))
        name_label.place(relx=0.05, rely=0.21, anchor="nw")

        key_label = CTkLabel(add_frame, text="Enter Key:", font=("Helvetica", 20, "bold"))
        key_label.place(relx=0.05, rely=0.31, anchor="nw")

        # Function to validate the name of the account
        def name_checker(*args):
            name = name_entry.get()
            if not backend.validate_name(name):
                messagebox.showerror("Error", "Name contains invalid character.")
                name_entry.delete(0, tk.END) # Clear the entry if invalid

        # Entry configurations for the account name
        name_entry = CTkEntry(add_frame, placeholder_text="Enter Name", width=300, height=40, border_width=2, border_color="red")
        name_entry.place(relx=0.25, rely=0.2, anchor="nw")
        name_entry.focus_set() # Set focus to the name entry field
        name_entry.bind("<KeyRelease>", name_checker) # Bind the validation function to key release events

        # Entry configurations for the secret key
        key_entry = CTkEntry(add_frame, placeholder_text="Enter Key", width=300, height=40, border_width=2, border_color="red")
        key_entry.place(relx=0.25, rely=0.3, anchor="nw")

        # Group Dropdown configurations
        group_label = CTkLabel(add_frame, text="Select Group:", font=("Helvetica", 20, "bold"))
        group_label.place(relx=0.05, rely=0.4, anchor="nw") # Label for the dropdown
        
        group_dropdown = CTkOptionMenu(add_frame, values=self.truncated_groups, height=35, font=("Helvetica", 14), fg_color="white", text_color="black", dropdown_font=("Helvetica", 14), dropdown_text_color="black", corner_radius=2, button_color="red", button_hover_color="#EE4B2B", dropdown_fg_color="white", dropdown_hover_color="red", hover=True, anchor="center")
        group_dropdown.place(relx=0.3, rely=0.4, anchor="nw") # Place the dropdown menu
        group_dropdown.set(self.groups[0]) # Set default selected group

        # Function to verify/create account
        def confirm_account(): # Function to call when the button is clicked
            
            # Function to format the current date and time
            def format_datetime():
                now = datetime.datetime.now()
                # Format the date based on user preference
                if self.time_format == 'on':
                    return now.strftime("%B %d, %Y at %H:%M") # 24-hour format
                else:
                    return now.strftime("%B %d, %Y at %I:%M%p") # 12-hour format

            creation_time = format_datetime() # Get the formatted creation time

            # Retrieve user input
            name = name_entry.get().strip()
            key = key_entry.get().strip()
            group = group_dropdown.get()

            # Validate the name and key
            if not name or not key:
                messagebox.showerror("Error", "All fields are required.")
                return
            if not backend.validate_name(name):
                messagebox.showerror("Error", "Name contains invalid characters.")
                return
            if not backend.is_valid_totp_key(key):
                messagebox.showerror("Error", "Invalid Key.")
                return

            # Automatically renumber name if it's already in use
            original_name = name
            suffix = 1
            while name in self.accounts:
                name = f"{original_name} ({suffix})" # Append suffix
                suffix += 1

            # Save or update the account
            group = None if group == "None" else group # Handle group selection
            self.accounts[name] = {'key': key, 'secret': pyotp.TOTP(key).secret, 'group': group, 'created': creation_time, 'modified': "Not Modified"}
            
            # Save accounts to backend
            backend.save_accounts(self.accounts, backend.load_key())
            self.update_labels(self.accounts) # Update labels with new account data

            close_frame() # Close the frame after successful addition
            messagebox.showinfo("Success", "Account added successfully!") # Inform the user

        # Save button configurations
        save_button = CTkButton(add_frame, text="💾", command=confirm_account, fg_color="white", hover_color="red", text_color="black", width=100, height=40, border_width=2, font=("Helvetica", 20, "bold"), cursor='hand2')
        save_button.place(relx=0.7, rely=0.425, anchor="center") # Position the button
        ToolTip(save_button, text="Save Account") # Tooltip for save button

        # Bind the Enter key to trigger the confirm_account function
        key_entry.bind("<Return>", lambda event: confirm_account())

    # Function to load user preferences from a configuration file
    def load_preferences(self):
        config = configparser.ConfigParser() # Create a ConfigParser object
        config.read('preferences.ini') # Read the configuration file
        self.time_format = config.get('Preferences', 'time_format', fallback=None) # Load time format preference
