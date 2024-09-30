from customtkinter import *
from data_backend import DataBackendFunctions
from import_data import ImportDataFunctions
from export_data import ExportDataFunctions
from tkinter import messagebox
import backend, json, os, shutil, time, configparser, glob, qrcode, pyotp, zipfile, io

class DataFunctions:
    def __init__(self, master, accounts, right_frame, update_labels):
        # Initial file configurations
        self.master = master  # Main application window
        self.accounts = accounts  # User accounts data
        self.right_frame = right_frame  # Frame to contain data management elements
        self.update_labels = update_labels  # Function to update UI labels

        self.load_preferences()  # Load user preferences at startup
        self.data_backend = DataBackendFunctions() # Initialize data backend
        self.data_backend.perform_automatic_backup()  # Perform an automatic backup if enabled

        # Initialize data export and import functionalities
        self.export_data = ExportDataFunctions(master, self.accounts)
        self.import_data = ImportDataFunctions(master, self.accounts, update_labels)

    # Function to manage data settings and UI
    def manage_data(self):
        # Create a frame for data management settings
        data_frame = CTkFrame(self.right_frame, width=600, height=700) # Frame dimensions
        data_frame.place(relx=0.61, rely=0, anchor="n") # Position the frame

        def close_frame():
            # Close the data management frame with checks for automatic backups
            if self.autobackups == 'on' and not self.backup_folder_path:
                messagebox.showerror("Error", "Automatic backups are enabled, but no backup folder path is set. Please set the backup folder path before exiting.")
                auto_backup_folder() # Prompt user to set backup folder path
                return # Exit function if conditions are not met     
            data_frame.destroy() # Destroy the data frame

        # Create a close button for the data frame
        close_button = CTkButton(data_frame, command=close_frame, text="❌", fg_color="white", border_color="black", text_color="black", hover_color="red", border_width=2, width=50, height=20, cursor="hand2")
        close_button.place(relx=0.8, rely=0.03, anchor="ne")

        # Title label for the data management fram
        title_label = CTkLabel(data_frame, text="Data", font=("Helvetica", 30, "bold", "underline"))
        title_label.place(relx=0.42, rely=0.08, anchor="center")

        # Default values for export and import options
        export_option = StringVar(value="Encrypted JSON")
        import_option = StringVar(value="JSON")

        # Function to handle export dropdown options
        def export_fun(event=None):
            selected = export_option.get() # Get the selected export option
            export_methods = {
                "Encrypted JSON": self.export_data.export_encrypted,
                "Unencrypted JSON": self.export_data.export_unencrypted,
                "Encrypted TXT": self.export_data.export_txt_encrypted,
                "Unencrypted TXT": self.export_data.export_txt_unencrypted,
                "Secrets": self.export_data.export_secrets,
                "QR Code(s)": self.export_data.export_qr_codes,
            }
            # Call the corresponding export method if a valid option is selected
            if (export_method := export_methods.get(selected)):
                export_method()

        # Function to handle import dropdown options
        def import_fun(event=None):
            selected = import_option.get() # Get the selected import option
            import_methods = {
                "JSON": self.import_data.import_json,
                "QR Code": self.import_data.import_from_qr,
            }
            # Call the corresponding import method if a valid option is selected
            if (import_method := import_methods.get(selected)):
                import_method()
        
        # Function to import preferences
        def import_preferences(event=None):
            self.import_data.import_preferences() # Call the import preferences method

        # Function to export preferences
        def export_preferences(event=None):
            self.export_data.export_preferences() # Call the export preferences method

        # Creating export dropdown
        export_label = CTkLabel(data_frame, text="Export Data", font=("Helvetica", 18, "bold", "underline"))
        export_label.place(relx=0.16, rely=0.35, anchor="w")
        
        export_dropdown = CTkOptionMenu(data_frame, values=["Encrypted JSON", "Unencrypted JSON", "Encrypted TXT", "Unencrypted TXT", "Secrets", "QR Code(s)"], variable=export_option, height=35, font=("Helvetica", 14), fg_color="white", text_color="black", dropdown_font=("Helvetica", 14), dropdown_text_color="black", corner_radius=10, button_color="red", button_hover_color="#EE4B2B", dropdown_fg_color="white", dropdown_hover_color="red", hover=True, anchor="center", state="normal")
        export_dropdown.place(relx=0.12, rely=0.4, anchor="w")
        
        export_button = CTkButton(data_frame, text="Export", command=export_fun, fg_color="white", hover_color="red", text_color="black", cursor="hand2", width=100, height=35, border_width=2, font=("Helvetica", 16, "bold"))
        export_button.place(relx=0.23, rely=0.47, anchor="center")

        # Creating import dropdown
        import_label = CTkLabel(data_frame, text="Import Data", font=("Helvetica", 18, "bold", "underline"))
        import_label.place(relx=0.47, rely=0.35, anchor="w")
        
        import_dropdown = CTkOptionMenu(data_frame, values=["JSON", "QR Code"], variable=import_option, height=35, font=("Helvetica", 14), fg_color="white", text_color="black", dropdown_font=("Helvetica", 14), dropdown_text_color="black", corner_radius=10, button_color="red", button_hover_color="#EE4B2B", dropdown_fg_color="white", dropdown_hover_color="red", hover=True, anchor="center", state="normal")
        import_dropdown.place(relx=0.44, rely=0.4, anchor="w")
        
        import_button = CTkButton(master=data_frame, text="Import", command=import_fun, fg_color="white", hover_color="red", text_color="black", cursor="hand2", width=100, height=35, border_width=2, font=("Helvetica", 16, "bold"))
        import_button.place(relx=0.55, rely=0.47, anchor="center")
        
        import_dropdown.bind("<<MenuSelected>>", import_fun) # Bind the import function to the dropdown

        # Display the current backup folder path
        autobackups_label = CTkLabel(data_frame, text=f"Location {self.backup_folder_path if self.backup_folder_path else '- None'}", font=("Helvetica", 14, "bold"))
        autobackups_label.place(relx=0.25, rely=0.25, anchor="center")
        
        # Creating VerifyVault data options
        impref_label = CTkLabel(data_frame, text="Import VerifyVault Data", font=("Helvetica", 18, "bold", "underline"))
        impref_label.place(relx=0.05, rely=0.55, anchor="w")

        impref_button = CTkButton(master=data_frame, text="Import Preferences", command=import_preferences, fg_color="white", hover_color="red", text_color="black", cursor="hand2", width=100, height=35, border_width=2, font=("Helvetica", 16, "bold"))
        impref_button.place(relx=0.05, rely=0.6, anchor="w")

        expref_label = CTkLabel(data_frame, text="Export VerifyVault Data", font=("Helvetica", 18, "bold", "underline"))
        expref_label.place(relx=0.8, rely=0.55, anchor="e")

        expref_button = CTkButton(master=data_frame, text="Export Preferences", command=export_preferences, fg_color="white", hover_color="red", text_color="black", cursor="hand2", width=100, height=35, border_width=2, font=("Helvetica", 16, "bold"))
        expref_button.place(relx=0.73, rely=0.6, anchor="e")

        # Function to set the automatic backup folder location
        def auto_backup_folder():
            self.backup_folder_path = filedialog.askdirectory() # Prompt user to select directory
            if self.backup_folder_path:
                self.save_preferences() # Save updated preferences
                autobackups_label.configure(text=f"Location {self.backup_folder_path}") # Update label with path

        # Function to toggle Automatic Backups
        def autobackups_callback():
            self.autobackups = autobackups_var.get() # Update the autobackups setting
            self.save_preferences() # Save the updated preferences

        autobackups_var = StringVar(value="off") # Default value for the switch
        autobackups_var.set(value="on" if self.autobackups == "on" else "off") # Set the current state
        
        # Switch for toggling automatic backups
        autobackups_switch = CTkSwitch(data_frame, text="Automatic Backups", command=autobackups_callback, variable=autobackups_var, onvalue="on", offvalue="off", fg_color="red", font=("Helvetica", 18, "bold"))
        autobackups_switch.place(relx=0.22, rely=0.15, anchor="w")

        # Button to set the backup location
        autobackup_location = CTkButton(data_frame, text="Backup Location", command=auto_backup_folder, fg_color="white", hover_color="red", text_color="black", cursor="hand2", width=100, height=35, border_width=2, font=("Helvetica", 16, "bold"))
        autobackup_location.place(relx=0.25, rely=0.2, anchor="center")

        # Function to save Automatic Backup file format
        def autobackups_format_callback(*args):
            self.backup_file_format  = autobackups_formatvar.get() # Update the file format
            self.save_preferences() # Save the updated preferences

        autobackups_formatvar = StringVar(value=self.backup_file_format) # Variable for the backup file format
        backup_formats = ["Encrypted JSON", "Unencrypted JSON", "Encrypted TXT", "Unencrypted TXT", "Secrets", "QR Code(s)"] # Available formats
        
        # Dropdown for selecting backup file format
        autobackups_format = CTkOptionMenu(data_frame, values=backup_formats, command=autobackups_format_callback, variable=autobackups_formatvar, height=35, font=("Helvetica", 14), fg_color="white", text_color="black", dropdown_font=("Helvetica", 14), dropdown_text_color="black", corner_radius=10, button_color="red", button_hover_color="#EE4B2B", dropdown_fg_color="white", dropdown_hover_color="red", hover=True, anchor="center", state="normal")
        autobackups_format.place(relx=0.55, rely=0.2, anchor="center")

    # Function to save preferences
    def save_preferences(self):
        backend.unhide_file('preferences.ini') # Unhide the preferences file for editing
        config = configparser.ConfigParser()

        if os.path.exists('preferences.ini'):
            config.read('preferences.ini') # Read existing preferences

        # Determine the status of automatic backups
        backups_status = "on" if self.autobackups == "on" else "off"

        # Set configuration options
        config['Automatic Backups'] = {
            'backups': backups_status,
            'folder': self.backup_folder_path or "", # Backup folder path
            'format': self.backup_file_format or "Encrypted JSON", # File format
        }

        with open('preferences.ini', 'w') as configfile:
            config.write(configfile) # Write updated preferences to the file
        backend.mark_file_hidden('preferences.ini') # Re-hide the preferences file

    # Function to load preferences
    def load_preferences(self):
        backend.unhide_file('preferences.ini') # Unhide the preferences file for reading
        config = configparser.ConfigParser()
        if os.path.exists('preferences.ini'):
            config.read('preferences.ini') # Read existing preferences

        # Load settings from the config file
        self.autobackups = config.get('Automatic Backups', 'backups', fallback=None)
        self.backup_folder_path = config.get('Automatic Backups', 'folder', fallback=None)
        self.backup_file_format = config.get('Automatic Backups', 'format', fallback="Encrypted JSON")
        
        # Re-hide the preferences file
        backend.mark_file_hidden('preferences.ini')
