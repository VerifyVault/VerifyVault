import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from password import PasswordManager
from cryptography.fernet import Fernet
import os, configparser, time, datetime, subprocess

# Function to generate/load encryption key
def load_or_generate_key():
    keyfile = '.hint_key'
    if os.path.exists(keyfile):
        with open(keyfile, 'rb') as f:
            hint_key = f.read()
    else:
        hint_key = Fernet.generate_key()
        with open(keyfile, 'wb') as f:
            f.write(hint_key)
    return hint_key

class ManagePassword:
    def __init__(self, master):
        # Initial manage_password configurations
        self.master = master
        self.password_manager = PasswordManager()
        self.password_set = False
        self.confirmation_in_progress = False
        self.password_lock_status = "Off"
        self.password_reminders_status = "Off"
        self.password_hint_status = "Off"

        self.load_preferences()
        self.start_password_reminders()

        self.master.bind("<Map>", self.on_restore)
        self.master.bind("<Unmap>", self.on_minimize)

        self.minimize_time = None
        self.minimize_timer = None
        
    # Manage Password window configurations
    def manage_password(self):
        self.close_active_window()
        password_window = tk.Toplevel(self.master)
        password_window.title("Manage Password")
        password_window.geometry("200x250")
        password_window.resizable(False, False)
        password_window.configure(bg="white")

        password_frame = tk.Frame(password_window, bg="white")
        password_frame.pack(fill="both", expand=True)

        set_password_button = ttk.Button(password_frame, text="Set Password", command=self.set_password, style='Red.TButton')
        set_password_button.pack(pady=5)
        remove_password_button = ttk.Button(password_frame, text="Remove Password", command=self.remove_password, style='Red.TButton')
        remove_password_button.pack(pady=5)
        self.password_lock_button = ttk.Button(password_frame, text=f"Password Lock - {self.password_lock_status}", command=self.toggle_password_lock, style='Red.TButton')
        self.password_lock_button.pack(pady=5)
        self.password_reminders_button = ttk.Button(password_frame, text=f"Password Reminders - {self.password_reminders_status}",
                                                    command=self.toggle_password_reminders, style='Red.TButton')
        self.password_reminders_button.pack(pady=5)
        self.password_hint_button = ttk.Button(password_frame, text=f"Password Hint - {self.password_hint_status}",
                                               command=self.toggle_password_hint, style='Red.TButton')
        self.password_hint_button.pack(pady=5)      

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

        # Toggle to show/hide password
        show_password_var = tk.BooleanVar()
        show_password_var.set(False)

        def toggle_password_visibility():
            if show_password_var.get():
                password_entry.config(show="")
            else:
                password_entry.config(show="*")

        show_password_button = ttk.Checkbutton(password_frame, text="Show Password", var=show_password_var, command=toggle_password_visibility,
                                            style="White.TCheckbutton")
        show_password_button.pack()

        def on_enter(event):
            self.confirm_password(password_entry.get(), password_window)

        password_entry.bind("<Return>", on_enter)
        password_entry.focus_set()

        confirm_button = ttk.Button(password_frame, text="Confirm", command=lambda: self.confirm_password(password_entry.get(), password_window), style='Custom.TButton')
        confirm_button.pack(pady=5)

        password_window.protocol("WM_DELETE_WINDOW", lambda: self.close_password_window(password_window))
        self.active_window = password_window

    # Function to close the password window
    def close_password_window(self, window):
        window.destroy()

    # Functions to confirm/store/remove the password
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

        confirmation = messagebox.askyesnocancel("Confirm", "Are you sure you want to remove the password?")
        self.confirmation_in_progress = False
        if confirmation is True:
            try:
                os.remove(".secure")
                messagebox.showinfo("Password Removed", "Password has been removed successfully.")
            except FileNotFoundError:
                messagebox.showerror("No Password Found", "No password has been set.")

    # Function to toggle password lock
    def toggle_password_lock(self):
        if self.password_lock_status == "Off":
            if not self.is_password_set():
                messagebox.showerror("Password Not Set", "You must set a password before enabling this feature.")
                self.manage_password()
                return
            self.password_lock_status = "On"
        else:
            self.password_lock_status = "Off"
        self.password_lock_button.config(text=f"Password Lock - {self.password_lock_status}")
        self.save_preferences()

    # Function to toggle password reminders
    def toggle_password_reminders(self):
        if self.password_reminders_status == "Off":
            if self.password_lock_status == "Off":
                if not self.is_password_set():
                    messagebox.showerror("Password Not Set", "You must set a password before enabling this feature.")
                    self.manage_password()
                    return
            self.password_reminders_status = "On"
        else:
            self.password_reminders_status = "Off"
        self.password_reminders_button.config(text=f"Password Reminders - {self.password_reminders_status}")
        self.save_preferences() 

    # Function to verify if password is set
    def is_password_set(self):
        return os.path.exists(".secure")

    # Function to start lock timer
    def on_restore(self, event):
        if self.minimize_timer is not None:
            self.master.after_cancel(self.minimize_timer)
        self.minimize_time = None
        if hasattr(self, 'lock_warning'):
            self.lock_warning.destroy()

    # Function to start password lock timer after minimization
    def on_minimize(self, event):
        if self.minimize_timer is None:
            self.minimize_time = time.time()
            self.check_minimize_time()

    # Function to 
    def check_minimize_time(self):
        from main import main
        if self.password_reminders_status == "On":
            if self.master.wm_state() == 'iconic':
                if time.time() - self.minimize_time >= 600:
                    messagebox.showwarning("Inactive", "Program will be closed due to inactivity.")
                    self.master.destroy()
                    subprocess.call(['python', 'main.py'])
            else:
                self.minimize_timer = self.master.after(1000, self.check_minimize_time)

    # Function to toggle password hint
    def toggle_password_hint(self):
        if self.password_hint_status == "Off":
            if self.password_lock_status == "Off":
                if not self.is_password_set():
                    messagebox.showerror("Password Not Set", "You must set a password before enabling this feature.")
                    self.manage_password()
                    return
            self.ask_and_save_hint()
        else:
            confirmation = messagebox.askyesno("Delete Password Hint", "Are you sure you want to delete the password hint?")
            if confirmation:
                self.delete_password_hint()
            else:
                self.password_hint_status = "On"
                self.password_hint_button.config(text=f"Password Hint - {self.password_hint_status}")
        self.save_preferences()

    # Hint window configurations
    def ask_and_save_hint(self):
        hint_window = tk.Toplevel(self.master)
        hint_window.title("Password Hint")
        hint_window.geometry("200x100")
        hint_window.resizable(False, False)
        hint_window.configure(bg="white")

        hint_frame = tk.Frame(hint_window, bg="white")
        hint_frame.pack(fill="both", expand=True)
        hint_label = tk.Label(hint_frame, text="Enter your password hint:", bg="white")
        hint_label.pack()

        hint_entry = tk.Entry(hint_frame)
        hint_entry.pack()
        hint_entry.focus_set()

        # FUnction to save password hint
        def save_hint(event=None):
            hint = hint_entry.get()
            if hint:
                self.set_hint(hint)
                self.password_hint_status = "On"
                self.password_hint_button.config(text=f"Password Hint - {self.password_hint_status}")
                messagebox.showinfo("Password Hint Set", "Password hint set.")
                hint_window.destroy()
            else:
                messagebox.showwarning("No Hint Entered", "Password hint was not set.")

        save_button = ttk.Button(hint_frame, text="Save Hint", command=save_hint, style='Red.TButton')
        save_button.pack(pady=5)
        hint_entry.bind("<Return>", save_hint)

        hint_window.transient(self.master)
        hint_window.grab_set()
        self.master.wait_window(hint_window)

    # Function to save & encrypt hint
    def set_hint(self, hint):
        try:
            key = load_or_generate_key()
            fernet = Fernet(key)
            encrypted_hint = fernet.encrypt(hint.encode())
            with open('.hint', 'wb') as hint_file:
                hint_file.write(encrypted_hint)
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save hint: {str(e)}")

    # Function to toggle password hint
    def save_encrypted_hint(self, encrypted_hint):
        try:
            hint = self.ask_for_hint()
            if hint:
                with open('.hint', 'w') as hint_file:
                    hint_file.write(hint)
                self.password_hint_status = "On"
                self.password_hint_button.config(text=f"Password Hint - {self.password_hint_status}")
            else:
                messagebox.showwarning("No Hint Entered", "Password hint was not set.")
                self.password_hint_status = "Off"
                self.password_hint_button.config(text=f"Password Hint - {self.password_hint_status}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save hint: {str(e)}")

    # Function to decrypt hint
    def decrypt_hint(self):
        try:
            key = load_or_generate_key()
            fernet = Fernet(key)
            if os.path.exists('.hint'):
                with open('.hint', 'rb') as hint_file:
                    encrypted_hint = hint_file.read()
                    decrypted_hint = fernet.decrypt(encrypted_hint).decode()
                    messagebox.showinfo("Password Hint", f"Your password hint is:\n{decrypted_hint}")
            else:
                messagebox.showerror("No Password Hint Found", "No password hint file found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read hint: {str(e)}")

    # Function to delete password hint
    def delete_password_hint(self):
        try:
            os.remove('.hint')
            os.remove('.hint_key')
            messagebox.showinfo("Password Hint Deleted", "Password hint has been deleted successfully.")
            self.password_hint_status = "Off"
            self.password_hint_button.config(text=f"Password Hint - {self.password_hint_status}")
        except FileNotFoundError:
            messagebox.showerror("No Password Hint Found", "No password hint file found.")

    # Save preferences function
    def save_preferences(self):
        config = configparser.ConfigParser()

        if os.path.exists('preferences.ini'):
            config.read('preferences.ini')

        config['PasswordLock'] = {
            'password_lock': self.password_lock_status
        }
        config['PasswordReminders'] = {
            'password_reminders': self.password_reminders_status
        }
        config['PasswordHint'] = { 
            'password_hint': self.password_hint_status
        }

        with open('preferences.ini', 'w') as configfile:
            config.write(configfile)
    def load_preferences(self):
        config = configparser.ConfigParser()
        config.read('preferences.ini')

        if 'PasswordLock' in config:
            self.password_lock_status = config.get('PasswordLock', 'password_lock', fallback="Off")
        else:
            self.password_lock_status = "Off"

        if 'PasswordReminders' in config:
            self.password_reminders_status = config.get('PasswordReminders', 'password_reminders', fallback="Off")
        else:
            self.password_reminders_status = "Off"

        if 'PasswordHint' in config:
            self.password_hint_status = config.get('PasswordHint', 'password_hint', fallback="Off")
        else:
            self.password_hint_status = "Off"

    # Function to schedule password checks
    def schedule_weekly_password_check(self):
        now = datetime.datetime.now()
        one_week = datetime.timedelta(weeks=1)
        next_check = now + one_week

        def weekly_check():
            if self.is_password_set():
                password = self.ask_for_password()
                if password:
                    if self.password_manager.check_password(password):
                        self.master.after(0, weekly_check)
                    else:
                        self.prompt_password_change()
                else:
                    self.master.after(0, weekly_check)
            else:
                self.master.after(0, weekly_check)

        def run_after_week():
            self.master.after(int((next_check - datetime.datetime.now()).total_seconds() * 1000), weekly_check)
        run_after_week()

    # Ask password window
    def ask_for_password(self):
        password_window = tk.Toplevel(self.master)
        password_window.title("Enter Password")
        password_window.geometry("200x100")
        password_window.resizable(False, False)
        password_window.configure(bg="white")

        password_frame = tk.Frame(password_window, bg="white")
        password_frame.pack(fill="both", expand=True)

        password_label = tk.Label(password_frame, text="Enter your password:", bg="white")
        password_label.pack()

        password_entry = tk.Entry(password_frame, show="*")
        password_entry.pack()
        password_entry.focus_set()

        def on_enter(event):
            self.check_password(password_entry.get(), password_window)

        password_entry.bind("<Return>", on_enter)

        confirm_button = ttk.Button(password_frame, text="Confirm", command=lambda: self.check_password(password_entry.get(), password_window), style='Red.TButton')
        confirm_button.pack(pady=5)

        password_window.transient(self.master)
        password_window.grab_set()
        self.master.wait_window(password_window)

        return password_entry.get()

    # Function to check password
    def check_password(self, password, window):
        if self.password_manager.verify_password(password):
            messagebox.showinfo("Password Correct", "Password verification successful.")
            window.destroy()
        else:
            messagebox.showinfo("Password Incorrect", "Password verification unsuccessful. Please consider changing your password.")
            window.destroy()

    # Function to start password reminders
    def start_password_reminders(self):
        if self.password_reminders_status == "On":
            self.schedule_weekly_password_check()

    # Function to close active window
    def close_active_window(self):
        if hasattr(self, 'active_window') and self.active_window:
            self.active_window.destroy()
