import tkinter as tk
from customtkinter import *
from password import PasswordManager
from keys import insert_key, retrieve_key, delete_key
from tkinter import messagebox
from PIL import Image, ImageTk
from cryptography.fernet import Fernet
import keys, os, time, schedule, configparser, qrcode, pyotp, pyperclip, datetime, random

# Function to generate/load the hint key
def load_or_generate_key():
    hint_key = Fernet.generate_key()
    if not retrieve_key('hint_key'):
        insert_key('hint_key', hint_key.decode())
    return hint_key

class ManageSecurity:
    def __init__(self, master, right_frame):
        # Initial manage_security configurations
        self.master = master
        self.right_frame = right_frame

        self.password = None
        self.hint = None
        self.lock = None
        self.twofa = None
        self.reminder = None

        self.password_manager = PasswordManager()
        self.load_preferences()

        self.minimize_time = None
        self.minimize_timer = None

        self.master.bind("<Unmap>", self.on_minimize)
        self.master.bind("<Map>", self.on_restore)
        self.start_password_reminders()

    # Function to generate the secret key for 2FA
    def generate_secret_key(self):
        return pyotp.random_base32()

    # Function to generate the QR code for 2FA
    def generate_qr_code(self, secret_key):
        qr_data = pyotp.totp.TOTP(secret_key).provisioning_uri()
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=7,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        return ImageTk.PhotoImage(qr_img)

    # Security Function
    def security(self):
        # Security Settings frame configurations
        security_frame = CTkFrame(self.right_frame, width=600, height=700)
        security_frame.place(relx=0.61, rely=0, anchor="n")

        def close_frame():
            security_frame.destroy()

        x_button = CTkButton(security_frame, command=close_frame, text="❌", fg_color="white", border_color="black", text_color="black", hover_color="red", border_width=2, width=50, height=20, cursor="hand2")
        x_button.place(relx=0.8, rely=0.03, anchor="ne")

        title_label = CTkLabel(security_frame, text="Security", font=("Helvetica", 30, "bold", "underline"))
        title_label.place(relx=0.15, rely=0.08, anchor="center")

        # Function to enable password
        def password_callback():
            self.password = password_var.get()
            config = configparser.ConfigParser()

            if os.path.exists('preferences.ini'):
                config.read('preferences.ini')
            else:
                self.save_preferences() 

            if 'Security' not in config:
                config['Security'] = {}

            # If the password is toggled on
            if self.password == 'on':
                password_var.set('off')

                password_window = CTkToplevel(self.master)
                password_window.geometry("500x300")
                password_window.title("Set Password")
                password_window.resizable(False, False)
                password_window.iconbitmap('images/VerifyVaultLogo.ico')

                title_label = CTkLabel(password_window, text="Set Password", font=("Helvetica", 30, "bold", "underline"))
                title_label.place(relx=0.5, rely=0.15, anchor="center")

                enter_label = CTkLabel(password_window, text="Enter Password:", font=("Helvetica", 18, "bold"))
                enter_label.place(relx=0.04, rely=0.31, anchor="nw")
                reenter_label = CTkLabel(password_window, text="Re-Enter:", font=("Helvetica", 18, "bold"))
                reenter_label.place(relx=0.16, rely=0.46, anchor="nw")

                password_entry = CTkEntry(password_window, show="*", width=275, height=40, border_width=2, border_color="black")
                password_entry.place(relx=0.35, rely=0.3, anchor="nw")
                reenter_entry = CTkEntry(password_window, show="*", width=275, height=40, border_width=2, border_color="black")
                reenter_entry.place(relx=0.35, rely=0.45, anchor="nw")

                def set_focus():
                    password_entry.focus_set()
                password_window.after(1000, set_focus)

                # Function to verify the password
                def on_set_password(event=None):
                    password = password_entry.get()
                    reentered_password = reenter_entry.get()

                    if not password or not reentered_password:
                        messagebox.showerror("Field(s) Required", "Both password fields must be filled in.")
                        return
                    elif password != reentered_password:
                        messagebox.showerror("Password Mismatch", "Passwords do not match. Please try again.")
                        return
                    else:
                        try:
                            self.password_manager.set_password(password)
                            messagebox.showinfo("Success", "Password has been successfully set.")
                            
                            self.password = 'on'
                            password_var.set('on')
                            
                            config.set('Security', 'password', self.password)
                            with open('preferences.ini', 'w') as configfile:
                                config.write(configfile)
                            password_window.destroy()
                        
                        except Exception as e:
                            messagebox.showerror("Error", f"Failed to set password: {str(e)}")
                reenter_entry.bind("<Return>", on_set_password)

                # Function to toggle password visibility
                def toggle_password_visibility():
                    if show_password_var.get():
                        password_entry.configure(show="")
                        reenter_entry.configure(show="")
                    else:
                        password_entry.configure(show="*")
                        reenter_entry.configure(show="*")
                show_password_var = tk.BooleanVar()
                show_password_var.set(False)

                # Show/Set password configurations
                show_toggle = CTkSwitch(password_window, text="Show Password", variable=show_password_var, command=toggle_password_visibility, cursor="hand2", onvalue="on", offvalue="off", fg_color="red")
                show_toggle.place(relx=0.48, rely=0.65, anchor="center")
                set_button = CTkButton(password_window, text="Set Password", command=on_set_password, fg_color="white", hover_color="red", text_color="black", width=100, height=40, border_width=2, font=("Helvetica", 20, "bold"), cursor='hand2')
                set_button.place(relx=0.48, rely=0.77, anchor="center")

                # Function to set password as off if window is closed
                def on_close():
                    self.password = 'off'
                    password_var.set('off')
                    password_window.destroy()
                password_window.protocol("WM_DELETE_WINDOW", on_close)

            # If password is toggled off
            elif self.password == 'off':
                delete_pass = messagebox.askyesno("Remove Password", "Are you sure you want to remove your password?")
                if delete_pass:
                    self.password = 'off'
                    password_var.set('off')

                    self.hint = 'off'
                    hint_var.set('off')

                    self.lock = 'off'
                    lock_var.set('off')

                    self.twofa = 'off'
                    twofa_var.set('off')

                    self.reminder = 'off'
                    reminder_var.set('off')

                    config.set('Security', 'password', self.password)
                    config.set('Security', 'hint', self.hint)
                    config.set('Security', 'lock', self.lock)
                    config.set('Security', 'twofactor', self.twofa)
                    config.set('Security', 'reminder', self.reminder)
                    delete_key('pw_hash')

                    if retrieve_key('hint_key'):
                        delete_key('hint_key')
                        os.remove('.hint')
                    if retrieve_key('secret_key'):
                        delete_key('secret_key')
                    messagebox.showinfo("Success", "The Password has been deleted successfully.")

                else:
                    self.password = 'on'
                    password_var.set('on')
            with open('preferences.ini', 'w') as configfile:
                config.write(configfile)
        
        # Password toggle configurations
        password_var = StringVar(value="off")
        password_var.set(value="on" if self.password == "on" else "off")
        password_switch = CTkSwitch(security_frame, text="Password", command=password_callback, variable=password_var, onvalue="on", offvalue="off", fg_color="red", font=("Helvetica", 26, "bold"))
        password_switch.place(relx=0.05, rely=0.15, anchor="w")

        password_desc = CTkLabel(security_frame, text="Set a password to secure your vault.", font=("Helvetica", 16))
        password_desc.place(relx=0.05, rely=0.2, anchor="w")

        # Function to enable password hint
        def hint_callback():
            self.hint = hint_var.get()

            # If the password is toggled off
            if self.password == 'off':
                messagebox.showerror("Password Required", "You must have a password in order to enable this feature.")
                self.hint = 'off'
                hint_var.set('off')
                update_preferences()

            # If the password is toggled on
            elif self.hint == 'on':
                config = configparser.ConfigParser()

                hint_entry = CTkInputDialog(text="Set Password Hint", font=("Helvetica", 16, "bold"), title="Set Password Hint", button_fg_color="white", button_hover_color="red", button_text_color="black", entry_border_color="black")
                hint = hint_entry.get_input()

                if hint is None:
                    messagebox.showwarning("Hint Required", "No hint was provided. Please try again.")
                    hint_var.set('off')
                    self.hint = 'off'
                    hint_entry.destroy()
                    return

                try:
                    key = load_or_generate_key()
                    fernet = Fernet(key)
                    encrypted_hint = fernet.encrypt(hint.encode())

                    insert_key('hint', encrypted_hint)
                    insert_key('hint_key', key.decode())
                    
                except Exception as e:
                    messagebox.showerror("Save Error", f"Failed to save hint: {str(e)}")

                    hint_var.set('off')
                    self.hint = 'off'

                    hint_entry.destroy()
                    return

                messagebox.showinfo("Success", "Password hint has been successfully set.")
                hint_entry.destroy()
                update_preferences()

            # If the password is toggled off
            else:
                delete_hint = messagebox.askyesno("Remove Password Hint", "Are you sure you want to remove your password hint?")
                if delete_hint:
                    self.hint = 'off'
                    hint_var.set('off')
                    update_preferences()

                    try:
                        delete_key('hint')
                        delete_key('hint_key')
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to delete hint: {str(e)}")

                    messagebox.showinfo("Success", "Password Hint has been deleted successfully.")
                else:
                    self.hint = 'on'
                    hint_var.set('on')

        # Function to update hint preference
        def update_preferences():
            config = configparser.ConfigParser()

            if os.path.exists('preferences.ini'):
                config.read('preferences.ini')
            else:
                self.save_preferences()

            if 'Security' not in config:
                config['Security'] = {}

            config.set('Security', 'hint', self.hint)
            with open('preferences.ini', 'w') as configfile:
                config.write(configfile)

        # Function to set password hint
        def initialize_hint():
            config = configparser.ConfigParser()
            if os.path.exists('preferences.ini'):
                config.read('preferences.ini')
                self.hint = config.get('Security', 'hint', fallback='off')
            else:
                self.hint = 'off'
            hint_var.set(self.hint)
        hint_var = StringVar(value="off")
        initialize_hint()

        # Configures password hint toggle
        hint_switch = CTkSwitch(security_frame, text="Password Hint", command=hint_callback, variable=hint_var, onvalue="on", offvalue="off", fg_color="red", font=("Helvetica", 26, "bold"))
        hint_switch.place(relx=0.05, rely=0.25, anchor="w")
        hint_desc = CTkLabel(security_frame, text="Set a password hint to help you remember your password.", font=("Helvetica", 16))
        hint_desc.place(relx=0.05, rely=0.3, anchor="w")

        # Function to enable password lock
        def lock_callback():
            self.lock = lock_var.get()

            # If the password is toggled off
            if self.password == 'off':
                messagebox.showerror("Password Required", "You must have a password in order to enable this feature.")
                self.lock = 'off'
                lock_var.set('off')

            # Enables password lock
            else:
                config = configparser.ConfigParser()

                if os.path.exists('preferences.ini'):
                    config.read('preferences.ini')
                else:
                    self.save_preferences()

                if 'Security' not in config:
                    config['Security'] = {}

                config.set('Security', 'lock', self.lock)
                with open('preferences.ini', 'w') as configfile:
                    config.write(configfile)

        # Configures password lock toggle
        lock_var = StringVar(value="off")
        lock_var.set(value="on" if self.lock == "on" else "off")
        lock_switch = CTkSwitch(security_frame, text="Password Lock", command=lock_callback, variable=lock_var, onvalue="on", offvalue="off", fg_color="red", font=("Helvetica", 26, "bold"))
        lock_switch.place(relx=0.05, rely=0.35, anchor="w")

        lock_desc = CTkLabel(security_frame, text="Enable this feature to automatically lock VerifyVault after 10 minutes.", font=("Helvetica", 16))
        lock_desc.place(relx=0.05, rely=0.4, anchor="w")

        # Function to enable password reminders
        def reminder_callback():
            self.reminder = reminder_var.get()

            # If the password is toggled off
            if self.password == 'off':
                messagebox.showerror("Password Required", "You must have a password in order to enable this feature.")
                self.reminder = 'off'
                reminder_var.set('off')

            # Enables password reminders
            else:
                config = configparser.ConfigParser()

                if os.path.exists('preferences.ini'):
                    config.read('preferences.ini')
                else:
                    self.save_preferences()

                if 'Security' not in config:
                    config['Security'] = {}

                config.set('Security', 'reminder', self.reminder)
                with open('preferences.ini', 'w') as configfile:
                    config.write(configfile)

        # COnfigures password reminders toggle
        reminder_var = StringVar(value="off")
        reminder_var.set(value="on" if self.reminder == "on" else "off")
        reminder_switch = CTkSwitch(security_frame, text="Password Reminders", command=reminder_callback, variable=reminder_var, onvalue="on", offvalue="off", fg_color="red", font=("Helvetica", 26, "bold"))
        reminder_switch.place(relx=0.05, rely=0.45, anchor="w")

        reminder_desc = CTkLabel(security_frame, text="Enable this feature to help you memorize your password.", font=("Helvetica", 16))
        reminder_desc.place(relx=0.05, rely=0.5, anchor="w")

        # Function to enable 2FA
        def twofa_callback():
            self.twofa = twofa_var.get()

            # If the password is toggled off
            if self.password == 'off':
                messagebox.showerror("Password Required", "You must have a password in order to enable this feature.")
                self.twofa = 'off'
                twofa_var.set('off')
                return

            config = configparser.ConfigParser()

            if os.path.exists('preferences.ini'):
                config.read('preferences.ini')
            else:
                self.save_preferences() 

            if 'Security' not in config:
                config['Security'] = {}

            # If the 2FA is toggled on
            if self.twofa == 'on':
                # 2FA Window Configurations
                twofa_var.set('off')

                twofa_window = CTkToplevel(self.master)
                twofa_window.geometry("500x700")
                twofa_window.title("2 Factor Authentication")
                twofa_window.resizable(False, False)
                twofa_window.iconbitmap('images/VerifyVaultLogo.ico')

                title_label = CTkLabel(twofa_window, text="Enable 2 Factor Authentication", font=("Helvetica", 30, "bold", "underline"))
                title_label.place(relx=0.5, rely=0.1, anchor="center")

                secret_key = self.generate_secret_key()
                qr_code = self.generate_qr_code(secret_key)
                key_label = CTkLabel(twofa_window, text=f"Secret Key: {secret_key}", font=("Helvetica", 14))
                key_label.place(relx=0.5, rely=0.15, anchor="center")

                def copy_secret_key():
                    pyperclip.copy(secret_key)
                    messagebox.showinfo("Copied", "Secret key copied to clipboard.")
                
                copy_key = CTkButton(twofa_window, text="Copy Secret Key", command=copy_secret_key, fg_color="white", hover_color="red", text_color="black", width=80, height=30, border_width=2, font=("Helvetica", 16, "bold"), cursor='hand2')
                copy_key.place(relx=0.5, rely=0.2, anchor="center")
                qr_label = CTkLabel(twofa_window, text="", image=qr_code)
                qr_label.place(relx=0.5, rely=0.45, anchor="center")

                twofa_entry = CTkEntry(twofa_window, placeholder_text="Verify Code", width=200, height=30, border_width=2, border_color="black")
                twofa_entry.place(relx=0.5, rely=0.7, anchor="center")

                def set_focus():
                    twofa_entry.focus_set()
                twofa_entry.after(1000, set_focus)

                # Function to verify 2FA Code
                def verify_2fa():
                    code = twofa_entry.get().strip()
                    totp = pyotp.TOTP(secret_key)
                    
                    # If the 2FA Code is valid
                    if code and totp.verify(code):
                        keys.insert_key('secret_key', secret_key)
                        messagebox.showinfo("2FA Enabled", "Two-Factor Authentication has been enabled successfully.")
                        
                        twofa_var.set('on')
                        self.twofa = 'on'
                        
                        config.set('Security', 'twofactor', self.twofa)
                        with open('preferences.ini', 'w') as configfile:
                            config.write(configfile)
                        twofa_window.destroy()
                    else:
                        messagebox.showerror("Invalid Code", "Invalid 2FA code. Please try again.")
                verify_2fa_button = CTkButton(twofa_window, text="Verify Code", command=verify_2fa, fg_color="white", hover_color="red", text_color="black", width=100, height=40, border_width=2, font=("Helvetica", 16, "bold"), cursor='hand2')
                verify_2fa_button.place(relx=0.5, rely=0.77, anchor="center")

                def on_close():
                    self.twofa = 'off'
                    twofa_var.set('off')
                    twofa_window.destroy()
                
                twofa_window.protocol("WM_DELETE_WINDOW", on_close)

            # If 2FA is toggled off
            elif self.twofa == 'off':
                delete_2fa = messagebox.askyesno("Remove 2FA", "Are you sure you want to remove 2FA?")
                if delete_2fa:
                    self.twofa = 'off'
                    twofa_var.set('off')
                    config.set('Security', 'twofactor', self.twofa)
                    delete_key('secret_key')
                    messagebox.showinfo("Success", "2FA has been disabled successfully.")
                else:
                    self.twofa = 'on'
                    twofa_var.set('on')

            with open('preferences.ini', 'w') as configfile:
                config.write(configfile)

        # Configures 2FA toggle
        twofa_var = StringVar(value="off")
        twofa_var.set(value="on" if self.twofa == "on" else "off")
        twofa_switch = CTkSwitch(security_frame, text="2 Factor Authentication", command=twofa_callback, variable=twofa_var, onvalue="on", offvalue="off", fg_color="red", font=("Helvetica", 26, "bold"))
        twofa_switch.place(relx=0.05, rely=0.55, anchor="w")

        twofa_desc = CTkLabel(security_frame, text="Enable 2FA to add an extra layer of security to your vault.", font=("Helvetica", 16))
        twofa_desc.place(relx=0.05, rely=0.6, anchor="w")

        danger_label = CTkLabel(security_frame, text="Danger Zone", font=("Helvetica", 30, "bold", "underline"), text_color="red")
        danger_label.place(relx=0.05, rely=0.7, anchor="w")

        def reset_preferences():
            confirm = messagebox.askyesno("WARNING", "This action is irreversible. Are you sure you want to proceed?")
            if confirm:
                os.remove('preferences.ini')
                messagebox.showinfo("Success", "Preferences reset, please restart.")

        def purge_accounts():
            confirm = messagebox.askyesno("WARNING", "This action is irreversible. Are you sure you want to proceed?")
            if confirm:
                os.remove('data.vv')
                os.remove('deleted.json')
                messagebox.showinfo("Success", "Accounts purged, please restart.")

        reset_pref = CTkButton(security_frame, text="Reset Preferences", command=reset_preferences, fg_color="red", hover_color="white", text_color="black", width=150, height=40, border_width=2, font=("Helvetica", 16, "bold"), cursor="hand2")
        reset_pref.place(relx=0.18, rely=0.77, anchor="center")
        purge_acc = CTkButton(security_frame, text="Purge Accounts", command=purge_accounts, fg_color="red", hover_color="white", text_color="black", width=150, height=40, border_width=2, font=("Helvetica", 16, "bold"), cursor="hand2")
        purge_acc.place(relx=0.48, rely=0.77, anchor="center")

    # Function to verify if the password is set
    def is_password_set(self):
        stored_hash = keys.retrieve_key('pw_hash')
        return stored_hash

    # Function to cancel inactive timer
    def on_restore(self, event):
        if self.minimize_timer is not None:
            self.master.after_cancel(self.minimize_timer)
            self.minimize_timer = None
        self.minimize_time = None
        if hasattr(self, 'lock_warning'):
            self.lock_warning.destroy()

    # Function to enable the inactive timer
    def on_minimize(self, event):
        if self.lock == 'on':
            if self.minimize_timer is None:
                self.minimize_time = time.time()
                self.check_minimize_time()

    # Function to check the amount of time the program has been minimized
    def check_minimize_time(self):
        import main

        if self.lock == 'on':
            if self.master.wm_state() in ('iconic', 'withdrawn'):
                if time.time() - self.minimize_time >= 600:
                    messagebox.showwarning("Inactive", "Program will be closed due to inactivity.")
                    self.master.destroy()
                    main.main()
                else:
                    self.minimize_timer = self.master.after(1000, self.check_minimize_time)
            else:
                self.minimize_timer = self.master.after(1000, self.check_minimize_time)

    # Function to start password reminders
    def start_password_reminders(self):
        if self.reminder == 'on':
            self.schedule_random_password_check()

    # Function to ask for password reminder
    def ask_for_password():
        # Password reminder window configurations
        reminder_window = CTkToplevel(self.master)
        reminder_window.geometry("500x300")
        reminder_window.title("Password Reminder")
        reminder_window.resizable(False, False)
        reminder_window.iconbitmap('images/VerifyVaultLogo.ico')

        title_label = CTkLabel(reminder_window, text="Password Reminder", font=("Helvetica", 30, "bold", "underline"))
        title_label.place(relx=0.5, rely=0.15, anchor="center")

        enter_label = CTkLabel(reminder_window, text="Enter Password:", font=("Helvetica", 18, "bold"))
        enter_label.place(relx=0.04, rely=0.31, anchor="nw")
        reminder_entry = CTkEntry(reminder_window, show="*", width=275, height=40, border_width=2, border_color="black")
        reminder_entry.place(relx=0.35, rely=0.3, anchor="nw")

        def set_focus():
            reminder_entry.focus_set()
        reminder_window.after(1000, set_focus)

        # Function to verify the password
        def on_set_password(event=None):
            password = reminder_entry.get()
            try:
                self.password_manager.set_password(password)
                messagebox.showinfo("Success", "Password has been verified successfully.")
                reminder_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", "Failed to verify password. Please consider changing your password.")
                reminder_window.destroy()
        reminder_entry.bind("<Return>", on_set_password)

        # Function to toggle password visibility
        def toggle_password_visibility():
            if show_password_var.get():
                password_entry.configure(show="")
                reminder_entry.configure(show="")
            else:
                password_entry.configure(show="*")
                reminder_entry.configure(show="*")
        show_password_var = tk.BooleanVar()
        show_password_var.set(False)

        # Show/Set password configurations
        show_toggle = CTkSwitch(reminder_window, text="Show Password", variable=show_password_var, command=toggle_password_visibility, cursor="hand2", onvalue="on", offvalue="off", fg_color="red")
        show_toggle.place(relx=0.48, rely=0.5, anchor="center")
        set_button = CTkButton(reminder_window, text="Set Password", command=on_set_password, fg_color="white", hover_color="red", text_color="black", width=100, height=40, border_width=2, font=("Helvetica", 20, "bold"), cursor='hand2')
        set_button.place(relx=0.48, rely=0.62, anchor="center")

    # Function to schedule/check password reminder
    def schedule_random_password_check(self):
        now = datetime.datetime.now()
        check_day = datetime.timedelta(days=0)

        def random_check():
            if self.is_password_set():
                self.ask_for_password()
            self.master.after(int((check_day.total_seconds() * 1000)), random_check)

        next_check = now + datetime.timedelta(days=random.randint(1, 7))
        check_day = next_check - now
        self.master.after(int(check_day.total_seconds() * 1000), random_check)

    # Function to save preferences
    def save_preferences(self):
        config = configparser.ConfigParser()

        if os.path.exists('preferences.ini'):
            config.read('preferences.ini')
        else:
            if 'Security' not in config:
                config['Security'] = {}

        password_status = "on" if self.password == "on" else "off"
        hint_status = "on" if self.hint == "on" else "off"
        lock_status = "on" if self.lock == "on" else "off"
        twofa_status = "on" if self.twofa == "on" else "off"
        reminder_status = "on" if self.reminder == "on" else "off"
        
        config['Security'] = {
            'password': password_status,
            'hint': hint_status,
            'lock': lock_status,
            'reminder': reminder_status,
            'twofactor': twofa_status,
        }
        
        with open('preferences.ini', 'w') as configfile:
            config.write(configfile)

    # Function to load preferences
    def load_preferences(self):
        config = configparser.ConfigParser()
        if os.path.exists('preferences.ini'):
            config.read('preferences.ini')
            
            self.password = config.get('Security', 'password', fallback='off')
            self.hint = config.get('Security', 'hint', fallback='off')
            self.lock = config.get('Security', 'lock', fallback='off')
            self.twofa = config.get('Security', 'twofactor', fallback='off')
            self.reminder = config.get('Security', 'reminder', fallback='off')

