from customtkinter import *
from tkinter import messagebox
import backend, os, configparser, time, datetime

class PreferencesFunctions:
    def __init__(self, master, accounts, right_frame, update_labels):
        # Initial setup for managing preferences
        self.master = master
        self.accounts = accounts
        self.right_frame = right_frame
        self.update_labels = update_labels

        self.load_preferences() # Load user preferences upon initialization

    # Function to configure preferences frame
    def manage_preferences(self):
        pref_frame = CTkFrame(self.right_frame, width=600, height=700)
        pref_frame.place(relx=0.61, rely=0, anchor="n")

        def close_frame():
            pref_frame.destroy() # Close the preferences frame

        # Button to close the preferences frame
        close_button = CTkButton(pref_frame, command=close_frame, text="❌", fg_color="white", border_color="black", text_color="black", hover_color="red", border_width=2, width=50, height=20, cursor="hand2")
        close_button.place(relx=0.8, rely=0.03, anchor="ne")

        # Title label for the preferences frame
        title_label = CTkLabel(pref_frame, text="Preferences", font=("Helvetica", 30, "bold", "underline"))
        title_label.place(relx=0.2, rely=0.08, anchor="center")

        # Function to configure dark mode toggle
        def color_callback():
            self.dark_mode = color_var.get() # Get the current value of dark mode
            self.save_preferences() # Save the preference
            set_appearance_mode("dark" if self.dark_mode == 'on' else "light") # Set the appearance mode

        color_var = StringVar(value="off") # Default value for dark mode
        color_var.set(value="on" if self.dark_mode == "on" else "off") # Set initial value based on current preference

        # Switch for toggling dark mode
        color_switch = CTkSwitch(pref_frame, text="Dark Mode", command=color_callback, variable=color_var, onvalue="on", offvalue="off", fg_color="red", font=("Helvetica", 26, "bold"))
        color_switch.place(relx=0.05, rely=0.15, anchor="w")

        # Description label for dark mode
        color_desc = CTkLabel(pref_frame, text="Switch to Dark Mode to make the interface easier on your eyes.", font=("Helvetica", 16))
        color_desc.place(relx=0.05, rely=0.2, anchor="w")

        # Function to configure time format toggle
        def time_callback():
            self.time_format = time_var.get() # Get the current value of time format
            self.save_preferences() # Save the preference
            self.update_account_times()  # Update account timestamps with new format

        time_var = StringVar(value="off") # Default value for time format
        time_var.set(value="on" if self.time_format == "on" else "off") # Set initial value based on current preference

        # Switch for toggling military time format
        time_switch = CTkSwitch(pref_frame, text="Military Time", command=time_callback, variable=time_var, onvalue="on", offvalue="off", fg_color="red", font=("Helvetica", 26, "bold"))
        time_switch.place(relx=0.05, rely=0.25, anchor="w")

        # Description label for time format
        time_desc = CTkLabel(pref_frame, text="Switch the time format between Military and Standard Time.", font=("Helvetica", 16))
        time_desc.place(relx=0.05, rely=0.3, anchor="w")

    # Function to update account timestamps with the new time format
    def update_account_times(self):
        backend.unhide_file('preferences.ini')  # Unhide the file before accessing
        key = backend.load_key() # Load the encryption key
        accounts = backend.load_accounts(key) # Load the account data
        
        # Function to format time based on the current time format setting
        def format_datetime(now):
            # Choose format string based on time format preference
            format_str = "%B %d, %Y at %H:%M" if self.time_format == 'on' else "%B %d, %Y at %I:%M%p"
            return now.strftime(format_str)

        # Update account creation times
        for name, info in accounts.items():
            if info['created'].lower() == 'unknown': # Skip unknown creation times
                continue
            try:
                # Parse the existing creation time
                creation_time = datetime.datetime.strptime(info['created'], "%B %d, %Y at %I:%M%p" if 'am' in info['created'] or 'pm' in info['created'] else "%B %d, %Y at %H:%M")
                # Format and update the creation time
                info['created'] = format_datetime(creation_time)
            except ValueError as e:
                messagebox.showerror("Error", f"Error updating account '{name}': {e}") # Log any parsing errors

        # Update account modification times
        for name, info in accounts.items():
            if info['modified'].lower() == 'not modified': # Skip if not modified
                continue
            try:
                # Parse the existing modification time
                modified_time = datetime.datetime.strptime(info['modified'], "%B %d, %Y at %I:%M%p" if 'am' in info['modified'] or 'pm' in info['modified'] else "%B %d, %Y at %H:%M")
                # Format and update the modification time
                info['modified'] = format_datetime(modified_time)
            except ValueError as e:
                messagebox.showerror("Error", f"Error updating account '{name}': {e}") # Log any parsing errors

        # Save updated accounts
        backend.save_accounts(accounts, key) # Save changes to accounts
        backend.mark_file_hidden('preferences.ini')  # Hide the file again after updating
        messagebox.showinfo("Restart", "Time format updated successfully. Restart VerifyVault to reflect the changes")

    # Function to save Preferences section
    def save_preferences(self):
        backend.unhide_file('preferences.ini')  # Unhide the file before saving
        config = configparser.ConfigParser()

        if os.path.exists('preferences.ini'):
            config.read('preferences.ini') # Read existing preferences if file exists
        
        # Ensure the Preferences section exists
        if 'Preferences' not in config:
            config['Preferences'] = {}
         
        # Save current preferences   
        config['Preferences']['dark_mode'] = "on" if self.dark_mode == "on" else "off"
        config['Preferences']['time_format'] = "on" if self.time_format == "on" else "off"
        
        # Write changes to the preferences file
        with open('preferences.ini', 'w') as configfile:
            config.write(configfile)

        backend.mark_file_hidden('preferences.ini')  # Hide the file again after saving

    # Function to load Preferences section 
    def load_preferences(self):
        backend.unhide_file('preferences.ini')  # Unhide the file before loading
        config = configparser.ConfigParser()

        if os.path.exists('preferences.ini'):
            config.read('preferences.ini') # Read preferences from file

        self.dark_mode = config.get('Preferences', 'dark_mode', fallback='off')
        self.time_format = config.get('Preferences', 'time_format', fallback='off')
        
        backend.mark_file_hidden('preferences.ini')  # Hide the file again after loading
