from customtkinter import *
from security_backend import SecurityBackendFunctions
from tkinter import messagebox
from cryptography.fernet import Fernet
from ttkbootstrap.tooltip import ToolTip
import backend, keys, os, configparser

class ManageSecurity:
    def __init__(self, master, right_frame, update_labels):
        # Initialize ManageSecurity with main window and UI elements
        # Initial manage_security configurations
        self.master = master
        self.right_frame = right_frame
        self.update_labels = update_labels
        self.load_preferences() # Load user preferences for security settings
        self.security_backend = SecurityBackendFunctions(master, self.update_labels)# Initialize backend functions for security

    # Configure the Security Settings frame
    def manage_security(self):
        # Create a frame for security settings within the right frame
        security_frame = CTkFrame(self.right_frame, width=600, height=700)
        security_frame.place(relx=0.61, rely=0, anchor="n")

        def close_frame():
            # Function to close the security settings frame
            security_frame.destroy()

        # Button to close the security frame
        close_button = CTkButton(security_frame, command=close_frame, text="❌", fg_color="white", border_color="black", text_color="black", hover_color="red", border_width=2, width=50, height=20, cursor="hand2")
        close_button.place(relx=0.8, rely=0.03, anchor="ne")
        ToolTip(close_button, text="Close")

        # Title label for the security settings frame
        title_label = CTkLabel(security_frame, text="Security", font=("Helvetica", 30, "bold", "underline"))
        title_label.place(relx=0.15, rely=0.08, anchor="center")

        # Function to handle password enable/disable actions
        def password_callback():
            self.password = password_var.get()  # Get the current password state
            self.save_preferences()  # Save updated preferences

            # If the password is toggled on
            if self.password == 'on':
                password_var.set('off')
                self.password = 'off'

                if keys.retrieve_key('pw_hash'): # Check if password is already enabled
                    messagebox.showerror("Error", "Password has already been enabled")
                    self.password = 'on'
                    password_var.set('on') # Keep the toggle in the 'on' state
                else:
                    # Proceed to set a new password
                    self.security_backend.set_password()  # Set the password in the backend

                self.save_preferences()
                
            # If password is toggled off
            elif self.password == 'off':
                # Confirm with the user before removing the password
                if messagebox.askyesno("Remove Password", "Are you sure you want to remove your password?"):
                    self.password = 'off' # Update internal state
                    password_var.set('off') # Update toggle state

                    # Disable related security features
                    self.hint, self.lock, self.twofa, self.reminder = 'off', 'off', 'off', 'off'
                    hint_var.set('off')
                    lock_var.set('off')
                    twofa_var.set('off')
                    reminder_var.set('off')

                    keys.delete_key('pw_hash') # Remove password hash from storage

                    # Clean up additional keys if they exist
                    if keys.retrieve_key('hint_key'):
                        keys.delete_key('hint_key')
                    if keys.retrieve_key('secret_key'):
                        keys.delete_key('secret_key')

                    messagebox.showinfo("Success", "The Password has been deleted successfully.")
                    self.save_preferences()

                else:
                    # User canceled the removal, set toggle back to 'on'
                    self.password = 'on'
                    password_var.set('on')
                    self.save_preferences()

            self.save_preferences() # Save preferences after any changes
        
        # Password toggle configurations
        password_var = StringVar(value="off" if self.password == "off" else "on")
        password_switch = CTkSwitch(security_frame, text="Password", command=password_callback, variable=password_var, onvalue="on", offvalue="off", fg_color="red", font=("Helvetica", 26, "bold"))
        password_switch.place(relx=0.05, rely=0.15, anchor="w")
        password_desc = CTkLabel(security_frame, text="Set a password to secure your vault.", font=("Helvetica", 16)).place(relx=0.05, rely=0.2, anchor="w")

        # Function to handle enabling and managing the password hint
        def hint_callback():
            hint_var.set('off')
            messagebox.showerror("Disabled", "Password Hints are temporarily disabled. Sorry.")

            """self.hint = hint_var.get() # Get the current state of the hint toggle

            # If the password is disabled, prevent enabling the hint
            if not keys.retrieve_key('pw_hash'):
                messagebox.showerror("Error", "You must have a password in order to enable this feature.")
                self.hint = 'off'  # Reset hint state
                hint_var.set('off')  # Update toggle
                self.save_preferences()  # Save changes
                return

            # If the hint is being toggled on
            if self.hint == 'on':
                # Check if a hint is already set
                if keys.retrieve_key('hint_key') and keys.retrieve_key('hint'):
                    messagebox.showerror("Error", "Password Hint has already been enabled")
                    hint_var.set('on')  # Keep toggle in the 'on' state
                    self.save_preferences()  # Save preferences
                elif keys.retrieve_key('pw_hash'):
                    # Prompt user to set a new password hint
                    hint_entry = CTkInputDialog(text="Set Password Hint", font=("Helvetica", 16, "bold"), title="Set Password Hint", button_fg_color="white", button_hover_color="red", button_text_color="black", entry_border_color="black")
                    hint_entry.after(250, lambda: hint_entry.iconbitmap('images/VerifyVaultLogo.ico'))
                    hint_entry.grab_set() # Focus on the input dialog
                    hint_entry.focus_set()

                    hint = hint_entry.get_input() # Get user input for hint
                    if not hint:
                        self.hint = 'off'  # Reset if no hint provided
                        hint_var.set('off')  # Update toggle state
                        hint_entry.destroy()  # Close dialog
                        return

                    # Encrypt and save the hint
                    try:
                        key = backend.load_hint_key()  # Load encryption key
                        fernet = Fernet(key)  # Create Fernet instance for encryption
                        encrypted_hint = fernet.encrypt(hint.encode())  # Encrypt the hint

                        keys.insert_key('hint', encrypted_hint) # Store encrypted hint
                        keys.insert_key('hint_key', key.decode()) # Store key
                        messagebox.showinfo("Success", "Password hint has been successfully set.")
                        
                    except Exception as e:
                        # Handle errors during saving
                        messagebox.showerror("Error", f"Failed to save hint: {str(e)}")
                        self.hint = 'off'  # Reset hint state
                        hint_var.set('off')  # Update toggle
                        
                    hint_entry.destroy()  # Close the input dialog
                    self.save_preferences()  # Save changes

            # If the password is toggled off
            else:
                delete_hint = messagebox.askyesno("Remove Password Hint", "Are you sure you want to remove your password hint?")
                if delete_hint:
                    self.hint = 'off'  # Reset internal state
                    hint_var.set('off')  # Update toggle
                    self.save_preferences()  # Save changes

                    # Attempt to delete stored hint
                    try:
                        keys.delete_key('hint')  # Remove hint from storage
                        keys.delete_key('hint_key')  # Remove associated key
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to delete hint: {str(e)}")

                    messagebox.showinfo("Success", "Password Hint has been deleted successfully.")
                else:
                    # If user cancels deletion, reset hint state to 'on'
                    self.hint = 'on'
                    hint_var.set('on')
                    self.save_preferences() # Save changes"""

        # Configure the password hint toggle switch in the UI
        hint_var = StringVar(value="off" if self.hint == "off" else "on")
        hint_switch = CTkSwitch(security_frame, text="Password Hint", command=hint_callback, variable=hint_var, onvalue="on", offvalue="off", fg_color="red", font=("Helvetica", 26, "bold"))
        hint_switch.place(relx=0.05, rely=0.25, anchor="w")

        # Description label for the password hint feature
        hint_desc = CTkLabel(security_frame, text="Set a password hint to help you remember your password.", font=("Helvetica", 16))
        hint_desc.place(relx=0.05, rely=0.3, anchor="w")

        # Function to handle enabling and managing the password lock
        def lock_callback():
            self.lock = lock_var.get()  # Get the current state of the lock toggle
            self.save_preferences()  # Save updated preferences

            # If the password is disabled, prevent enabling the lock feature
            if not keys.retrieve_key('pw_hash'):
                messagebox.showerror("Error", "You must have a password in order to enable this feature.")
                self.lock = 'off'  # Reset lock state
                lock_var.set('off')  # Update toggle state
                self.save_preferences() # Save updated preferences

        # Configure the password lock toggle in the UI
        lock_var = StringVar(value="off" if self.lock == "off" else "on")
        lock_switch = CTkSwitch(security_frame, text="Password Lock", command=lock_callback, variable=lock_var, onvalue="on", offvalue="off", fg_color="red", font=("Helvetica", 26, "bold"))
        lock_switch.place(relx=0.05, rely=0.35, anchor="w")

        # Description for the password lock feature
        lock_desc = CTkLabel(security_frame, text="Enable this feature to automatically lock VerifyVault after 10 minutes.", font=("Helvetica", 16))
        lock_desc.place(relx=0.05, rely=0.4, anchor="w")

        # Function to handle enabling and managing password reminders
        def reminder_callback():
            self.reminder = reminder_var.get()  # Get the current state of the reminder toggle
            self.save_preferences()  # Save updated preferences

            # If the password is disabled, prevent enabling reminders
            if not keys.retrieve_key('pw_hash'):
                messagebox.showerror("Error", "You must have a password in order to enable this feature.")
                self.reminder = 'off'  # Reset reminder state
                reminder_var.set('off')  # Update toggle state
                self.save_preferences() # Save updated preferences

        # Configure the password reminders toggle in the UI
        reminder_var = StringVar(value="off" if self.reminder == "off" else "on")
        reminder_switch = CTkSwitch(security_frame, text="Password Reminders", command=reminder_callback, variable=reminder_var, onvalue="on", offvalue="off", fg_color="red", font=("Helvetica", 26, "bold"))
        reminder_switch.place(relx=0.05, rely=0.45, anchor="w")

        # Description for the password reminders feature
        reminder_desc = CTkLabel(security_frame, text="Enable this feature to help you memorize your password.", font=("Helvetica", 16))
        reminder_desc.place(relx=0.05, rely=0.5, anchor="w")

        # Function to handle enabling and managing two-factor authentication (2FA)
        def twofa_callback():
            self.twofa = twofa_var.get()  # Get the current state of the 2FA toggle
            self.save_preferences()  # Save updated preferences

            # If the password is disabled, prevent enabling 2FA
            if not keys.retrieve_key('pw_hash'):
                messagebox.showerror("Error", "You must have a password in order to enable this feature.")
                self.twofa = 'off'  # Reset 2FA state
                twofa_var.set('off')  # Update toggle state
                self.save_preferences() # Save updated preferences
                return

            # If 2FA is being toggled on
            if self.twofa == 'on':
                if keys.retrieve_key('secret_key'):
                    messagebox.showerror("Error", "2FA has already been enabled")
                    twofa_var.set('on')  # Keep toggle in the 'on' state
                    self.save_preferences()  # Save preferences
                else:
                    twofa_var.set('off')  # Reset toggle for user input
                    self.security_backend.set_2fa()  # Set up 2FA

                    if keys.retrieve_key('secret_key'):
                        twofa_var.set('on')  # Update toggle if successful

            # If 2FA is being toggled off
            elif self.twofa == 'off':
                if messagebox.askyesno("Remove 2FA", "Are you sure you want to remove 2FA?"):
                    self.twofa = 'off'  # Reset internal state
                    twofa_var.set('off')  # Update toggle
                    keys.delete_key('secret_key')  # Remove secret key
                    messagebox.showinfo("Success", "2FA has been disabled successfully.")
                else:
                    self.twofa = 'on' # Reset toggle if user cancels
                    twofa_var.set('on')

            self.save_preferences() # Save preferences after any changes

        # Configure the 2FA toggle in the UI
        twofa_var = StringVar(value="off" if self.twofa == "off" else "on")
        twofa_switch = CTkSwitch(security_frame, text="2 Factor Authentication", command=twofa_callback, variable=twofa_var, onvalue="on", offvalue="off", fg_color="red", font=("Helvetica", 26, "bold"))
        twofa_switch.place(relx=0.05, rely=0.55, anchor="w")

        # Description for the 2FA feature
        twofa_desc = CTkLabel(security_frame, text="Enable 2FA to add an extra layer of security to your vault.", font=("Helvetica", 16))
        twofa_desc.place(relx=0.05, rely=0.6, anchor="w")

        # Danger Zone section header
        danger_label = CTkLabel(security_frame, text="Danger Zone", font=("Helvetica", 30, "bold", "underline"), text_color="red")
        danger_label.place(relx=0.05, rely=0.7, anchor="w")

        # Button to reset user preferences
        reset_pref = CTkButton(security_frame, text="Reset Preferences", command=self.security_backend.reset_preferences, fg_color="red", hover_color="white", text_color="black", width=150, height=40, border_width=2, font=("Helvetica", 16, "bold"), cursor="hand2")
        reset_pref.place(relx=0.18, rely=0.77, anchor="center")

        # Button to purge accounts
        purge_acc = CTkButton(security_frame, text="Purge Accounts", command=self.security_backend.purge_accounts, fg_color="red", hover_color="white", text_color="black", width=150, height=40, border_width=2, font=("Helvetica", 16, "bold"), cursor="hand2")
        purge_acc.place(relx=0.48, rely=0.77, anchor="center")

    # Function to save user preferences to a configuration file
    def save_preferences(self):
        backend.unhide_file('preferences.ini')  # Make the preferences file visible
        config = configparser.ConfigParser()  # Create a new config parser

        # Check if the preferences file exists
        if os.path.exists('preferences.ini'):
            config.read('preferences.ini') # Read existing preferences
    
        # Ensure the 'Security' section exists in the config
        if 'Security' not in config:
            config['Security'] = {}

        # Set security preferences based on current states
        config['Security'] = {
            'password': "on" if self.password == "on" else "off",
            'hint': "on" if self.hint == "on" else "off",
            'lock': "on" if self.lock == "on" else "off",
            'reminder': "on" if self.reminder == "on" else "off",
            'twofactor': "on" if self.twofa == "on" else "off",
        }
        
        # Write updated preferences back to the file
        with open('preferences.ini', 'w') as configfile:
            config.write(configfile)

        backend.mark_file_hidden('preferences.ini') # Hide the preferences file again

    # Function to load user preferences from the configuration file
    def load_preferences(self):
        backend.unhide_file('preferences.ini')  # Make the preferences file visible
        config = configparser.ConfigParser()  # Create a new config parser

        # Check if the preferences file exists
        if os.path.exists('preferences.ini'):
            config.read('preferences.ini') # Read preferences
            
            # Load each preference with a fallback value of 'off'
            self.password = config.get('Security', 'password', fallback='off')
            self.hint = config.get('Security', 'hint', fallback='off')
            self.lock = config.get('Security', 'lock', fallback='off')
            self.twofa = config.get('Security', 'twofactor', fallback='off')
            self.reminder = config.get('Security', 'reminder', fallback='off')

        backend.mark_file_hidden('preferences.ini') # Hide the preferences file again
