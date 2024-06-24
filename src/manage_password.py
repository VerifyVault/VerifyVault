import tkinter as tk
from tkinter import ttk, messagebox
from password import PasswordManager
import os

class ManagePassword:
    def __init__(self, master):
        # Initial manage_password configurations
        self.master = master
        self.password_manager = PasswordManager()
        self.password_set = False
        self.confirmation_in_progress = False

    # Manage Password window configurations
    def manage_password(self):
        self.close_active_window()
        password_window = tk.Toplevel(self.master)
        password_window.title("Manage Password")
        password_window.geometry("150x100")
        password_window.resizable(False, False)
        password_window.configure(bg="white")

        password_frame = tk.Frame(password_window, bg="white")
        password_frame.pack(fill="both", expand=True)

        set_password_button = ttk.Button(password_frame, text="Set Password", command=self.set_password, style='Red.TButton')
        set_password_button.pack(pady=5)
        remove_password_button = ttk.Button(password_frame, text="Remove Password", command=self.remove_password, style='Red.TButton')
        remove_password_button.pack(pady=5)

        self.active_window = password_window

    # Set Password window configurations
    def set_password(self):
        self.close_active_window()
        password_window = tk.Toplevel(self.master)
        password_window.title("Set Password")
        password_window.geometry("150x100")
        password_window.resizable(False, False)
        password_window.configure(bg="white")

        password_frame = tk.Frame(password_window, bg="white")
        password_frame.pack(fill="both", expand=True)
        password_label = tk.Label(password_frame, text="Enter Password:", bg="white")
        password_label.pack()

        password_entry = tk.Entry(password_frame, show="*")
        password_entry.pack()
        self.active_window = password_window

        def on_enter(event):
            self.confirm_password(password_entry.get(), password_window)
        password_entry.bind("<Return>", on_enter)
        password_entry.focus_set()

        confirm_button = ttk.Button(password_frame, text="Confirm", command=lambda: self.confirm_password(password_entry.get(), password_window), style='Red.TButton')
        confirm_button.pack(pady=5)
        password_window.protocol("WM_DELETE_WINDOW", lambda: self.close_password_window(password_window))

    # Function that closes the password window
    def close_password_window(self, window):
        window.destroy()

    # Functions that confirm/store/remove the password
    def confirm_password(self, password, window):
        self.close_active_window()
        if password:
            self.password_manager.set_password(password) 
            self.password_set = True
            messagebox.showinfo("Password Set", "Password has been set successfully.")
            window.destroy()
        else:
            messagebox.showwarning("Password Not Set", "You did not enter a password.")
            window.lift()
    def remove_password(self):
        if self.confirmation_in_progress:
            return
        self.close_active_window()
        self.confirmation_in_progress = True

        confirmation = messagebox.askyesno("Confirm", "Are you sure you want to remove the password?")
        self.confirmation_in_progress = False
        if confirmation:
            try:
                os.remove(".secure")
                messagebox.showinfo("Password Removed", "Password has been removed successfully.")
            except FileNotFoundError:
                messagebox.showwarning("No Password Found", "No password has been set.")

    # Function that closes the active window
    def close_active_window(self):
        if hasattr(self, 'active_window') and self.active_window:
            self.active_window.destroy()
