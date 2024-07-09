import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
from pyzbar.pyzbar import decode
from notifications import NotificationManager
from backend import load_accounts, save_accounts, load_key
import backend, json, os, time

class ImportDataFunctions:
   # Initial import_data configurations
   def __init__(self, master, accounts, notifications):
        self.master = master
        self.accounts = accounts
        self.notifications = notifications
        self.key = backend.load_key()
        self.active_window = None

   # Function to close active window
   def close_active_window(self):
      if self.active_window:
            self.active_window.destroy()
    
   # Import Data function
   def import_data(self):
      from gui import TwoFactorAppGUI
      self.close_active_window()

      # Function to import accounts via .json
      def import_json():
            key = backend.load_key()
            self.close_active_window()
            file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
            if file_path:
               try:
                  existing_accounts = {}
                  if os.path.exists("data.vv"):
                        key = load_key()
                        existing_accounts = load_accounts(key)

                  with open(file_path, "r") as imported_file:
                        imported_data = json.load(imported_file)

                  duplicate_accounts = set(imported_data.keys()) & set(existing_accounts.keys())
                  if duplicate_accounts:
                        override = messagebox.askyesnocancel(
                           "Duplicate Account",
                           "At least one of your accounts already exists. Would you like to override them?"
                        )
                        if override is None:
                           return
                        if override is False:
                           for name in duplicate_accounts:
                              suffix = 1
                              new_name = f"{name} ({suffix})"
                              while new_name in existing_accounts:
                                    suffix += 1
                                    new_name = f"{name} ({suffix})"
                              existing_accounts[new_name] = existing_accounts.pop(name)
                        else:
                           pass

                  existing_accounts.update(imported_data)
                  save_accounts(existing_accounts, key)
                  messagebox.showinfo("Success", "Data imported successfully!")

                  self.master.destroy()
                  TwoFactorAppGUI(tk.Tk(), self.key)
               except (json.JSONDecodeError, ValueError):
                  messagebox.showerror("Invalid JSON format")
               except Exception as e:
                  print(f"An error occurred: {str(e)}")

      # Function to import accounts via QR Code
      def import_from_qr():
            from gui import TwoFactorAppGUI
            self.close_active_window()
            try:
               existing_accounts = {}
               if os.path.exists("data.vv"):
                  key = backend.load_key()
                  existing_accounts = backend.load_accounts(key)

               file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg;*.jpeg")])
               if file_path:
                  with open(file_path, 'rb') as img_file:
                        img = Image.open(img_file)
                        result = decode(img)
                        
                        if result:
                           for data in result:
                              qr_data = data.data.decode('utf-8')
                              parts = qr_data.split('secret=')
                              account_name = parts[0].split('/')[-1].rstrip('?').replace('%20', ' ')
                              secret_key = parts[1] if len(parts) > 1 else ''

                              while account_name in existing_accounts:
                                    messagebox.showerror("Duplicate Account", f"Account '{account_name}' already exists.")
                                    new_name = self.ask_for_account_name()
                                    account_name = new_name

                              if account_name:
                                    existing_accounts[account_name] = {'key': secret_key, 'secret': secret_key}
                                    messagebox.showinfo("Imported", f"Account '{account_name}' imported successfully!")
                                    backend.save_accounts(existing_accounts, self.key)
                                    self.master.destroy()
                                    TwoFactorAppGUI(tk.Tk(), self.key)
                        else:
                           messagebox.showerror("Error", "No QR code found in the image.")
            except Exception as e:
               messagebox.showerror("Error", f"An error occurred: {str(e)}")

      import_window = tk.Toplevel(self.master)
      import_window.title("Import Data")
      import_window.geometry("200x100")
      import_window.resizable(False, False)
      import_window.configure(bg="white")

      import_json_button = ttk.Button(import_window, text="Import via JSON", command=import_json, style='Red.TButton')
      import_json_button.pack(pady=5)
      import_qr_button = ttk.Button(import_window, text="Import via QR Code", command=import_from_qr, style='Red.TButton')
      import_qr_button.pack(pady=5)

      self.active_window = import_window

   # Ask for Account Name Function
   def ask_for_account_name(self):
      dialog_window = tk.Toplevel(self.master)
      dialog_window.title("Enter Account Name")
      dialog_window.geometry("300x150")
      dialog_window.resizable(False, False)
      dialog_window.configure(bg="white")

   # Function to validate and process the account name inputted
      def validate_name(name):
            if len(name) > 30:
               messagebox.showerror("Character Limit", "Character Limit is 30")
               return False
            invalid_chars = "\\/:*?\"<>|"
            for char in invalid_chars:
               if char in name:
                  messagebox.showerror("Invalid Character", f"Name cannot contain '{char}'")
                  return False
            return True
      def confirm(event=None):
            account_name = account_name_var.get()
            if account_name:
               if validate_name(account_name):
                  dialog_window.destroy()
               else:
                  account_name_var.set("")
            else:
               messagebox.showerror("Error", "Account name cannot be empty.")
      
      label = tk.Label(dialog_window, text="Enter a unique account name:", bg="white")
      label.pack(pady=10)

      account_name_var = tk.StringVar()
      entry = tk.Entry(dialog_window, textvariable=account_name_var)
      entry.pack(pady=10)

      vcmd = (dialog_window.register(validate_name), "%P")
      entry.config(validate="key", validatecommand=vcmd)
      dialog_window.bind("<Return>", confirm)
      entry.focus_set()

      confirm_button = ttk.Button(dialog_window, text="Confirm", command=confirm, style='Red.TButton')
      confirm_button.pack(pady=10)
      char_count_label = tk.Label(dialog_window, text="Characters: 0", bg="white")
      char_count_label.pack()

      #Function to count the character length of the name
      def update_char_count(event):
            char_count_label.config(text=f"Characters: {len(account_name_var.get())}")

      entry.bind("<KeyRelease>", update_char_count)
      dialog_window.transient(self.master)
      dialog_window.grab_set()
      return account_name_var.get()
