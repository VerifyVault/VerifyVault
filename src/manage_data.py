import tkinter as tk
from tkinter import ttk
from backend import load_key
from export_data import ExportDataFunctions
from import_data import ImportDataFunctions
from recycle_bin import RecycleBinFunctions

class ManageData:
    def __init__(self, master, accounts, notifications):
        # Initial manage_data configurations
        self.master = master
        self.accounts = accounts
        self.key = load_key()
        self.notifications = notifications
        self.active_window = None
        self.export_data_functions = ExportDataFunctions(self.master, self.accounts, self.notifications)
        self.import_data_functions = ImportDataFunctions(self.master, self.accounts, self.notifications)
        self.recycle_bin_functions = RecycleBinFunctions(self.master, self.accounts, self.notifications)

    # Function to close active window
    def close_active_window(self):
        if self.active_window:
            self.active_window.destroy()

    # Function to open export data window
    def bind_export_data(self):
        self.close_active_window()
        self.export_data_functions.export_and_close()

    # Function to open import data window
    def bind_import_data(self):
        self.close_active_window()
        self.import_data_functions.import_data()

    # Function to open recycle bin window
    def bind_manage_recycle_bin(self):
        self.close_active_window()
        self.recycle_bin_functions.manage_recycle_bin()

    # Manage Data Function
    def manage_data_window(self):
        # Manage Data Window Account window configurations
        self.close_active_window()
        manage_data_window = tk.Toplevel(self.master)
        manage_data_window.title("Manage Data")
        manage_data_window.geometry("200x150")
        manage_data_window.resizable(False, False)
        manage_data_window.configure(bg="white")
        manage_data_window.iconbitmap('VerifyVaultLogo.ico')

        export_button = ttk.Button(manage_data_window, text="Export Data", command=self.bind_export_data, style='Red.TButton')
        export_button.pack(pady=5)

        import_button = ttk.Button(manage_data_window, text="Import Data", command=self.bind_import_data, style='Red.TButton')
        import_button.pack(pady=5)

        recycle_bin_button = ttk.Button(manage_data_window, text="Recycle Bin", command=self.bind_manage_recycle_bin, style='Red.TButton')
        recycle_bin_button.pack(pady=5)

        self.active_window = manage_data_window
