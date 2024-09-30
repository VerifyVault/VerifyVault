from customtkinter import *
from tkinter import messagebox
from ttkbootstrap.tooltip import ToolTip
from data import DataFunctions
from security import ManageSecurity
from preferences import PreferencesFunctions

class SettingsTab:
    def __init__(self, master, accounts, right_frame, update_labels):
        # Initialize the SettingsTab with the main application components
        self.master = master
        self.accounts = accounts  # Dictionary containing account information
        self.right_frame = right_frame  # Frame where settings will be displayed
        self.update_labels = update_labels  # Function to update labels in the UI

        # Initialize components for different settings functionalities
        self.data = DataFunctions(master, accounts, right_frame, self.update_labels)
        self.preferences = PreferencesFunctions(master, accounts, right_frame, self.update_labels)
        self.security = ManageSecurity(master, right_frame, self.update_labels)

        self.frame_open = False # Track if the settings frame is currently open

    # Function to open a help window with information about settings
    def open_help_window(self):
        help_window = CTkToplevel(self.master)
        help_window.geometry("400x300")
        help_window.title("Settings Help")
        help_window.resizable(False, False)
        help_window.after(250, lambda: help_window.iconbitmap('images/VerifyVaultLogo.ico'))
        help_window.grab_set()

        # Help text summarizing the settings available
        help_text = (
            "- Preferences: Customize VerifyVault\n\n"
            "- Security: Edit account security preferences\n\n"
            "- Data: Manage your data"
        )

        # Title label for the help window
        title_label = CTkLabel(help_window, text="Settings Help", font=("Helvetica", 30, "bold", "underline"))
        title_label.place(relx=0.5, rely=0.05, anchor="center")

        # Help text label displaying available settings information
        help_label = CTkLabel(help_window, text=help_text, font=("Helvetica", 20))
        help_label.place(relx=0.02, rely=0.15, anchor="nw")

    # Function to configure settings frame
    def settings_options(self):
        # Check if the settings frame is already open
        if self.frame_open:
            messagebox.showerror("Error", "This window is already open. Please close it before opening a new one.")
            return # Exit if the frame is already open
        
        self.frame_open = True # Mark the frame as open

        # Create a new frame for settings within the right frame
        settings_frame = CTkFrame(self.right_frame, width=600, height=700)
        settings_frame.place(relx=0.61, rely=0, anchor="n")

        # Function to close the settings frame
        def close_frame():
            settings_frame.destroy() # Remove the frame from the UI
            self.frame_open = False # Mark the frame as closed

        # Button to close the settings frame
        close_button = CTkButton(settings_frame, command=close_frame, text="❌", fg_color="white", border_color="black", text_color="black", hover_color="red", border_width=2, width=50, height=20, cursor="hand2")
        close_button.place(relx=0.8, rely= 0.03, anchor="ne")
        ToolTip(close_button, text="Close")

        # Button to open the help window
        help_button = CTkButton(settings_frame, text="❓",command=self.open_help_window, font=("Helvetica", 20, "bold"), fg_color="white", hover_color="red", width=30, height=10, border_width=2, corner_radius=2, text_color="black", cursor='hand2')
        help_button.place(relx=0.05, rely=0.03, anchor="n")
        ToolTip(help_button, text="Help")

        # Title label for the settings frame
        title_label = CTkLabel(settings_frame, text="Settings", font=("Helvetica", 30, "bold", "underline"))
        title_label.place(relx=0.42, rely=0.08, anchor="center")

        # Button to manage preferences
        pref_button = CTkButton(settings_frame, text="✏️Preferences", command=self.preferences.manage_preferences, fg_color="white", hover_color="red", text_color="black", cursor="hand2", width=350, height=100, border_width=2, font=("Helvetica", 22, "bold"))
        pref_button.place(relx=0.43, rely=0.25, anchor="center")
        ToolTip(pref_button, text="Customize VerifyVault to your liking")
        
        # Button to manage security settings
        security_button = CTkButton(settings_frame, text="🔒 Security", command=self.security.manage_security, fg_color="white", hover_color="red", text_color="black", cursor="hand2", width=350, height=100, border_width=2, font=("Helvetica", 22, "bold"))
        security_button.place(relx=0.43, rely=0.45, anchor="center")
        ToolTip(security_button, text="Secure your Vault")

        # Button to manage data settings
        data_button = CTkButton(settings_frame, text="📁 Data", command=self.data.manage_data, fg_color="white", hover_color="red", text_color="black", cursor="hand2", width=350, height=100, border_width=2, font=("Helvetica", 22, "bold"))
        data_button.place(relx=0.43, rely=0.65, anchor="center")
        ToolTip(data_button, text="Manage your Data")
