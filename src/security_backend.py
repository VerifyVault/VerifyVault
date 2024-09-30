import tkinter as tk
from customtkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import backend, keys, os, time, configparser, qrcode, pyotp, pyperclip, datetime, random, bcrypt

class SecurityBackendFunctions:
   def __init__(self, master, update_labels):
      # Initial configurations for security management
      self.master = master
      self.update_labels = update_labels
      self.minimize_time = None
      self.minimize_timer = None

      self.password = None
      self.hint = None
      self.lock = None
      self.twofa = None
      self.reminder = None

      self.load_preferences()  # Load user preferences
      self.start_password_reminders()  # Start password reminders

   # Generate a secret key for 2FA
   def generate_secret_key(self):
      return pyotp.random_base32()

   # Create a QR code for 2FA setup
   def generate_qr_code(self, secret_key):
      qr_data = pyotp.totp.TOTP(secret_key).provisioning_uri() # Prepare QR data
      qr = qrcode.QRCode(
         version=1,
         error_correction=qrcode.constants.ERROR_CORRECT_L,
         box_size=7,
         border=4,
      )
      qr.add_data(qr_data)
      qr.make(fit=True)
      qr_img = qr.make_image(fill_color="black", back_color="white")
      return ImageTk.PhotoImage(qr_img) # Return as PhotoImage

   # Check if a password is set
   def is_password_set(self):
      stored_hash = keys.retrieve_key('pw_hash')  # Retrieve stored password hash
      return stored_hash is not None  # Return True if a hash exists

   def set_password(self):
      # Create a new window for setting the password
      password_window = CTkToplevel(self.master)
      password_window.geometry("500x300")
      password_window.title("Set Password")
      password_window.resizable(False, False)
      password_window.after(250, lambda: password_window.iconbitmap('images/VerifyVaultLogo.ico'))
      password_window.grab_set()
      password_window.focus_set()

      # Title and labels for password entry
      title_label = CTkLabel(password_window, text="Set Password", font=("Helvetica", 30, "bold", "underline"))
      title_label.place(relx=0.5, rely=0.15, anchor="center")

      enter_label = CTkLabel(password_window, text="Enter Password:", font=("Helvetica", 18, "bold"))
      enter_label.place(relx=0.04, rely=0.31, anchor="nw")
      reenter_label = CTkLabel(password_window, text="Re-Enter:", font=("Helvetica", 18, "bold"))
      reenter_label.place(relx=0.16, rely=0.46, anchor="nw")

      # Entry fields for password
      password_entry = CTkEntry(password_window, show="*", width=275, height=40, border_width=2, border_color="black")
      password_entry.place(relx=0.35, rely=0.3, anchor="nw")
      reenter_entry = CTkEntry(password_window, show="*", width=275, height=40, border_width=2, border_color="black")
      reenter_entry.place(relx=0.35, rely=0.45, anchor="nw")

      # Verify and set the password
      def on_set_password(event=None):         
         password = password_entry.get()
         reentered_password = reenter_entry.get()

         if not password or not reentered_password:
               messagebox.showerror("Error", "Both password fields must be filled in.")
               return
         if password != reentered_password:
               messagebox.showerror("Error", "Passwords do not match. Please try again.")
               return

         try:
            # Hash the password and save it
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            keys.insert_key('pw_hash', password_hash)
            messagebox.showinfo("Success", "Password has been successfully set.")
            
            self.password = 'on'
            self.save_preferences()
            password_window.destroy()
         except Exception as e:
            messagebox.showerror("Error", f"Failed to set password: {str(e)}")
      reenter_entry.bind("<Return>", on_set_password)  # Bind Enter key to password setting

      # Toggle password visibility
      def toggle_password_visibility():
         show_char = "" if show_password_var.get() else "*"
         password_entry.configure(show=show_char)
         reenter_entry.configure(show=show_char)

      # Show password toggle switch
      show_password_var = tk.BooleanVar(value=False)
      show_toggle = CTkSwitch(password_window, text="Show Password", variable=show_password_var, command=toggle_password_visibility, cursor="hand2", onvalue="on", offvalue="off", fg_color="red")
      show_toggle.place(relx=0.48, rely=0.65, anchor="center")

      # Button to set the password
      set_button = CTkButton(password_window, text="Set Password", command=on_set_password, fg_color="white", hover_color="red", text_color="black", width=100, height=40, border_width=2, font=("Helvetica", 20, "bold"), cursor='hand2')
      set_button.place(relx=0.48, rely=0.77, anchor="center")

      # Handle window close event
      def on_close():
         self.password = 'off'
         self.save_preferences()
         password_window.destroy()

      password_window.protocol("WM_DELETE_WINDOW", on_close) # Set close protocol

   def set_2fa(self):
      # Create a new window for 2FA setup
      twofa_window = CTkToplevel(self.master)
      twofa_window.geometry("500x700")
      twofa_window.title("2 Factor Authentication")
      twofa_window.resizable(False, False)
      twofa_window.after(250, lambda: twofa_window.iconbitmap('images/VerifyVaultLogo.ico'))
      twofa_window.grab_set()
      twofa_window.focus_set()

      # Title for the 2FA window
      title_label = CTkLabel(twofa_window, text="Enable 2 Factor Authentication", font=("Helvetica", 30, "bold", "underline"))
      title_label.place(relx=0.5, rely=0.1, anchor="center")

      # Generate secret key and QR code
      secret_key = self.generate_secret_key()
      qr_code = self.generate_qr_code(secret_key)
      key_label = CTkLabel(twofa_window, text=f"Secret Key: {secret_key}", font=("Helvetica", 14))
      key_label.place(relx=0.5, rely=0.15, anchor="center")

      # Copy secret key to clipboard
      def copy_secret_key():
         pyperclip.copy(secret_key)
         messagebox.showinfo("Success", "Secret key copied to clipboard.")
      
      copy_key = CTkButton(twofa_window, text="Copy Secret Key", command=copy_secret_key, fg_color="white", hover_color="red", text_color="black", width=80, height=30, border_width=2, font=("Helvetica", 16, "bold"), cursor='hand2')
      copy_key.place(relx=0.5, rely=0.2, anchor="center")

      # Display QR code
      qr_label = CTkLabel(twofa_window, text="", image=qr_code)
      qr_label.place(relx=0.5, rely=0.45, anchor="center")

      # Entry field for code verification
      twofa_entry = CTkEntry(twofa_window, placeholder_text="Verify Code", width=200, height=30, border_width=2, border_color="black")
      twofa_entry.place(relx=0.5, rely=0.7, anchor="center")

      twofa_window.grab_set()
      twofa_window.focus_set()

      # Verify the 2FA code
      def verify_2fa():
         code = twofa_entry.get().strip()
         totp = pyotp.TOTP(secret_key)
         
         if code and totp.verify(code):
               keys.insert_key('secret_key', secret_key)
               messagebox.showinfo("Success", "Two-Factor Authentication has been enabled successfully.")
               
               self.twofa = 'on'
               self.save_preferences()
               twofa_window.destroy()
         else:
               messagebox.showerror("Error", "Invalid 2FA code. Please try again.")

      # Button to verify the entered code
      verify_2fa_button = CTkButton(twofa_window, text="Verify Code", command=verify_2fa, fg_color="white", hover_color="red", text_color="black", width=100, height=40, border_width=2, font=("Helvetica", 16, "bold"), cursor='hand2')
      verify_2fa_button.place(relx=0.5, rely=0.77, anchor="center")

      # Handle window close event
      def on_close():
         self.twofa = 'off'
         self.save_preferences()
         twofa_window.destroy()
         
      twofa_window.protocol("WM_DELETE_WINDOW", on_close) # Set close protocol

   # Function to cancel the inactive timer
   def on_restore(self, event):
      if self.minimize_timer is not None:
         self.master.after_cancel(self.minimize_timer)
         self.minimize_timer = None
      self.minimize_time = None
      if hasattr(self, 'lock_warning'):
         self.lock_warning.destroy()

   # Function to check how long the program has been minimized
   def on_minimize(self, event):
      if self.lock == 'on':
         if self.minimize_timer is None:
               self.minimize_time = time.time()
               self.check_minimize_time()

   # Function to check the amount of time the program has been minimized
   def check_minimize_time(self):
      import main # Import main module for relaunching

      if self.lock == 'on':
         if self.master.wm_state() in ('iconic', 'withdrawn'):
               if time.time() - self.minimize_time >= 600: # 10 minutes
                  messagebox.showwarning("Inactivity", "Program will be closed due to inactivity.")
                  self.master.destroy()
                  main.main() # Relaunch login window
               else:
                  self.minimize_timer = self.master.after(1000, self.check_minimize_time)
         else:
            self.minimize_timer = self.master.after(1000, self.check_minimize_time)

   # Function to start password reminders based on user settings
   def start_password_reminders(self):
      if self.reminder == 'on':
         now = datetime.datetime.now()
         next_check = now + datetime.timedelta(days=random.randint(1, 7))
         check_day = next_check - now

         def random_check():
            if keys.retrieve_key('pw_hash'):
                  self.ask_for_reminder() # Prompt for reminder if password is set
            self.master.after(int((check_day.total_seconds() * 1000)), random_check)

         self.master.after(int((check_day.total_seconds() * 1000)), random_check)

   # Function to ask for password reminder
   def ask_for_reminder():
      # Create reminder window
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

      reminder_window.grab_set()
      reminder_window.focus_set()

      # Function to verify the entered password
      def reminder_verification(event=None):
         password = reminder_entry.get()
         if not password:
            messagebox.showerror("Error", "Please enter your password.")
            return

         stored_hash = keys.retrieve_key('pw_hash')  # Get stored password hash
         if bcrypt.checkpw(password.encode(), stored_hash):
               messagebox.showinfo("Success", "Password has been verified successfully.")
               reminder_window.destroy()
         else:
               messagebox.showerror("Error", "Password verification failed. Please try again.")

      reminder_entry.bind("<Return>", reminder_verification)

      # Function to toggle password visibility
      def toggle_reminder_visibility():
         reminder_entry.configure(show="" if show_password_var.get() else "*")

      show_password_var = tk.BooleanVar(value=False)

      # Show/Set password toggle
      show_toggle = CTkSwitch(reminder_window, text="Show Password", variable=show_password_var, command=toggle_reminder_visibility, cursor="hand2", onvalue="on", offvalue="off", fg_color="red")
      show_toggle.place(relx=0.48, rely=0.5, anchor="center")
      verify_button = CTkButton(reminder_window, text="Verify Password", command=reminder_verification, fg_color="white", hover_color="red", text_color="black", width=100, height=40, border_width=2, font=("Helvetica", 20, "bold"), cursor='hand2')
      verify_button.place(relx=0.48, rely=0.62, anchor="center")

   def reset_preferences(self):
      # Prompt user for confirmation before resetting preferences
      if messagebox.askyesno("WARNING", "This action is irreversible. Are you sure you want to proceed?"):
         # Remove preferences file if it exists
         if os.path.exists('preferences.ini'):
            backend.unhide_file('preferences.ini')
            with open('preferences.ini', 'w') as file:
               file.write('')
            backend.mark_file_hidden('preferences.ini')
         
         # Delete specific keys from storage
         for key in ['pw_hash', 'hint', 'hint_key', 'secret_key']:
            if keys.retrieve_key(key):
               keys.delete_key(key)

         messagebox.showinfo("Success", "Preferences reset, please restart.")

   def purge_accounts(self):
      # Confirm with user before purging accounts
      if messagebox.askyesno("WARNING", "This action is irreversible. Are you sure you want to proceed?"):
         # Remove account data files
         for file_name in ['data.json', 'deleted.json']:
            if os.path.exists(file_name):
               backend.unhide_file(file_name)
               
               with open(file_name, 'w') as file:
                  file.truncate()  # Clear the contents of the file
               backend.mark_file_hidden(file_name)

         messagebox.showinfo("Success", "Accounts purged successfully.")

         # Reload accounts after purging
         self.accounts = backend.load_accounts(backend.load_key())  # Reload accounts from storage
         self.update_labels()  # Update the displayed accounts

   def save_preferences(self):
      # Unhide preferences file for writing
      backend.unhide_file('preferences.ini')
      config = configparser.ConfigParser()

      # Read existing preferences if file exists
      if os.path.exists('preferences.ini'):
         config.read('preferences.ini')
   
      # Initialize 'Security' section if not present
      if 'Security' not in config:
         config['Security'] = {}

      # Set security preferences based on current state
      config['Security'] = {
         'password': "on" if self.password == "on" else "off",
         'hint': "on" if self.hint == "on" else "off",
         'lock': "on" if self.lock == "on" else "off",
         'reminder': "on" if self.reminder == "on" else "off",
         'twofactor': "on" if self.twofa == "on" else "off",
      }
      
      # Write preferences back to file
      with open('preferences.ini', 'w') as configfile:
         config.write(configfile)
         
      # Hide the preferences file after saving
      backend.mark_file_hidden('preferences.ini')

   # Function to load preferences
   def load_preferences(self):
      # Unhide preferences file for reading
      backend.unhide_file('preferences.ini')
      config = configparser.ConfigParser()

      # Load preferences if file exists
      if os.path.exists('preferences.ini'):
         config.read('preferences.ini')
         
         # Set instance variables from loaded preferences
         self.password = config.get('Security', 'password', fallback='off')
         self.hint = config.get('Security', 'hint', fallback='off')
         self.lock = config.get('Security', 'lock', fallback='off')
         self.twofa = config.get('Security', 'twofactor', fallback='off')
         self.reminder = config.get('Security', 'reminder', fallback='off')

      # Hide the preferences file after loading
      backend.mark_file_hidden('preferences.ini')