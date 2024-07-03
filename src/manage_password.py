import tkinter as tk
from tkinter import ttk, messagebox
from password import PasswordManager
import os, configparser, time, datetime, subprocess

class ManagePassword:
    def __init__(self, master):
        # Initial manage_password configurations
        self.master = master
        self.password_manager = PasswordManager()
        self.password_set = False
        self.confirmation_in_progress = False
        self.password_lock_status = "Off"
        self.password_reminders_status = "Off"

        self.load_preferences()
        self.start_password_reminders()

        # Track the state of the main window
        self.master.bind("<Map>", self.on_restore)
        self.master.bind("<Unmap>", self.on_minimize)

        # Initialize timer variables
        self.minimize_time = None
        self.minimize_timer = None
        
    # Manage Password window configurations
    def manage_password(self):
        self.close_active_window()
        password_window = tk.Toplevel(self.master)
        password_window.title("Manage Password")
        password_window.geometry("200x200")
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

        confirmation = messagebox.askyesnocancel("Confirm", "Are you sure you want to remove the password?")
        self.confirmation_in_progress = False
        if confirmation is True:
            try:
                os.remove(".secure")
                messagebox.showinfo("Password Removed", "Password has been removed successfully.")
            except FileNotFoundError:
                messagebox.showerror("No Password Found", "No password has been set.")

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

    def show_inactive_warning(self):
        import main
        messagebox.showwarning("Inactive", "Program will be closed due to inactivity.")
        self.master.destroy()

    def toggle_password_reminders(self):
        if self.password_reminders_status == "Off":
            self.password_reminders_status = "On"
        else:
            self.password_reminders_status = "Off"
        self.password_reminders_button.config(text=f"Password Reminders - {self.password_reminders_status}")
        self.save_preferences() 

    def is_password_set(self):
        # Check if the password is set by looking for the .secure file
        return os.path.exists(".secure")

    def on_restore(self, event):
        # Reset the timer and close any lock warning
        if self.minimize_timer is not None:
            self.master.after_cancel(self.minimize_timer)
        self.minimize_time = None
        if hasattr(self, 'lock_warning'):
            self.lock_warning.destroy()

    def on_minimize(self, event):
        # Start timer when window is minimized
        if self.minimize_timer is None:
            self.minimize_time = time.time()
            self.check_minimize_time()

    def check_minimize_time(self):
        from main import main
        if self.master.wm_state() == 'iconic':
            if time.time() - self.minimize_time >= 600:
                messagebox.showwarning("Inactive.")
                self.master.destroy()
                subprocess.call(['python', 'main.py'])
            else:
                self.minimize_timer = self.master.after(1000, self.check_minimize_time)

    def save_preferences(self):
        config = configparser.ConfigParser()

        # Read existing preferences if preferences.ini exists
        if os.path.exists('preferences.ini'):
            config.read('preferences.ini')

        # Update existing or create new sections with current preferences
        config['PasswordLock'] = {
            'password_lock': self.password_lock_status
        }
        config['PasswordReminders'] = {
            'password_reminders': self.password_reminders_status
        }

        # Write the updated preferences to preferences.ini
        with open('preferences.ini', 'w') as configfile:
            config.write(configfile)
    def load_preferences(self):
        config = configparser.ConfigParser()
        config.read('preferences.ini')

        # Ensure to check if 'PasswordLock' section exists in the config
        if 'PasswordLock' in config:
            self.password_lock_status = config.get('PasswordLock', 'password_lock', fallback="Off")
        else:
            # If section or key not found, default to 'Off'
            self.password_lock_status = "Off"

        if 'PasswordReminders' in config:
            self.password_reminders_status = config.get('PasswordReminders', 'password_reminders', fallback="Off")
        else:
            self.password_reminders_status = "Off"

    def schedule_weekly_password_check(self):
        # Check every week
        now = datetime.datetime.now()
        one_week = datetime.timedelta(weeks=1)
        next_check = now + one_week

        def weekly_check():
            if self.is_password_set():
                password = self.ask_for_password()
                if password:
                    if self.password_manager.check_password(password):
                        # Password correct, continue
                        self.master.after(0, weekly_check)
                    else:
                        # Password incorrect, prompt to change password
                        self.prompt_password_change()
                else:
                    # User canceled entering password
                    self.master.after(0, weekly_check)
            else:
                # No password set, continue
                self.master.after(0, weekly_check)

        def run_after_week():
            # Schedule the next check after one week
            self.master.after(int((next_check - datetime.datetime.now()).total_seconds() * 1000), weekly_check)

        # Start the first check
        run_after_week()

    def ask_for_password(self):
        # Prompt user for password
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

        # Center password_window on the master window
        password_window.transient(self.master)
        password_window.grab_set()
        self.master.wait_window(password_window)

        return password_entry.get()

    def check_password(self, password, window):
        if self.password_manager.verify_password(password):
            messagebox.showinfo("Password Correct", "Password verification successful.")
            window.destroy()
        else:
            messagebox.showinfo("Password Incorrect", "Password verification unsuccessful. Please consider changing your password.")
            window.destroy()

    def start_password_reminders(self):
        # Ensure password reminders are on
        if self.password_reminders_status == "On":
            # Schedule weekly password check
            self.schedule_weekly_password_check()

    # Function that closes the active window
    def close_active_window(self):
        if hasattr(self, 'active_window') and self.active_window:
            self.active_window.destroy()
