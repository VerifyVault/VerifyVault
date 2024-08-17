from customtkinter import *
from ttkbootstrap.tooltip import ToolTip
from manage_data import ManageData
from manage_pref import ManagePreferences
from manage_security import ManageSecurity
from import_data import ImportDataFunctions
from export_data import ExportDataFunctions

class SettingsTab:
    def __init__(self, master, accounts, right_frame):
        # settings_tab configurations
        self.master = master
        self.accounts = accounts
        self.right_frame = right_frame

        self.import_data = ImportDataFunctions(self.master)
        self.export_data = ExportDataFunctions(self.master, self.accounts)

        self.manage_data = ManageData(master, right_frame, self.accounts)
        self.manage_pref = ManagePreferences(master, right_frame)
        self.manage_security = ManageSecurity(master, right_frame)

    # Function to configure settings frame
    def settings(self):
        settings_frame = CTkFrame(self.right_frame, width=600, height=700)
        settings_frame.place(relx=0.61, rely=0, anchor="n")

        def close_frame():
            settings_frame.destroy()

        x_button = CTkButton(settings_frame, command=close_frame, text="❌", fg_color="white", border_color="black", text_color="black", hover_color="red", border_width=2, width=50, height=20, cursor="hand2")
        x_button.place(relx=0.8, rely= 0.03, anchor="ne")

        title_label = CTkLabel(settings_frame, text="Settings", font=("Helvetica", 30, "bold", "underline"))
        title_label.place(relx=0.42, rely=0.08, anchor="center")

        pref_button = CTkButton(settings_frame, text="✏️Preferences", command=self.manage_pref.preferences, fg_color="white", hover_color="red", text_color="black", cursor="hand2", width=350, height=100, border_width=2, font=("Helvetica", 22, "bold"))
        pref_button.place(relx=0.43, rely=0.25, anchor="center")
        security_button = CTkButton(settings_frame, text="🔒 Security", command=self.manage_security.security, fg_color="white", hover_color="red", text_color="black", cursor="hand2", width=350, height=100, border_width=2, font=("Helvetica", 22, "bold"))
        security_button.place(relx=0.43, rely=0.45, anchor="center")
        data_button = CTkButton(settings_frame, text="📁 Data", command=self.manage_data.data, fg_color="white", hover_color="red", text_color="black", cursor="hand2", width=350, height=100, border_width=2, font=("Helvetica", 22, "bold"))
        data_button.place(relx=0.43, rely=0.65, anchor="center")

        ToolTip(pref_button, text="Customize VerifyVault to your liking")
        ToolTip(security_button, text="Secure your Vault")
        ToolTip(data_button, text="Manage your Data")
