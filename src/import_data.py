from tkinter import filedialog, messagebox
from PIL import Image
from pyzbar.pyzbar import decode
from backend import load_accounts, save_accounts, load_key
import backend, json, os, shutil

class ImportDataFunctions:
   # Initial import_data configurations
   def __init__(self, master):
        self.master = master
        self.key = backend.load_key()

   # Function to import accounts via JSON
   def import_json(self):
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

            existing_accounts.update(imported_data)
            save_accounts(existing_accounts, key)
            messagebox.showinfo("Success", "Data imported successfully!")
            
         except (json.JSONDecodeError, ValueError):
            messagebox.showerror("Invalid JSON format")
         except Exception as e:
            print(f"An error occurred: {str(e)}")

   # Function to import accounts via QR Code
   def import_from_qr(self):
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
                  else:
                     messagebox.showerror("Error", "No QR code found in the image.")
      except Exception as e:
         messagebox.showerror("Error", f"An error occurred: {str(e)}")

   # Function to import preferences
   def import_preferences(event=None):
      file_path = filedialog.askopenfilename(
         title="Select preferences.ini",
         filetypes=[("INI files", "*.ini")],
         initialdir=os.getcwd()
      )

      if os.path.basename(file_path) != 'preferences.ini':
         messagebox.showerror("Error", "You did not select a valid preferences file.")
         return

      current_preferences_path = os.path.join(os.getcwd(), "preferences.ini")

      try:
         shutil.copyfile(file_path, current_preferences_path)
         messagebox.showinfo("Success", f"Preferences successfully updated from {file_path}")
      except Exception as e:
         messagebox.showerror("Error", f"Error replacing preferences.ini: {e}")

