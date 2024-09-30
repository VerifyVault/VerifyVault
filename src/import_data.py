from backend import load_key, load_accounts, save_accounts, mark_file_hidden, unhide_file
from PIL import Image
from pyzbar.pyzbar import decode
from tkinter import filedialog, messagebox
import backend, json, os, shutil

class ImportDataFunctions:
   # Initial file configurations
   def __init__(self, master, accounts, update_labels):
        self.master = master
        self.accounts = accounts
        self.update_labels = update_labels
        self.key = load_key() # Load the encryption key for data handling

   # Function to import accounts via JSON
   def import_json(self):
      # Prompt user to select a JSON file for import
      file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])

      # Exit if no file was selected
      if not file_path:
         return

      try:
         # Load existing accounts from the encrypted storage
         existing_accounts = load_accounts(self.key)

         # Open the selected JSON file for reading
         with open(file_path, "r") as imported_file:
               imported_data = json.load(imported_file) # Load data from the JSON file

         # Validate the imported data structure
         self.validate_data(imported_data)

         # Check for duplicates between existing accounts and imported data
         self.check_duplicates(existing_accounts, imported_data)

         # Check for duplicates between existing accounts and imported data
         existing_accounts.update(imported_data)

         # Save the updated accounts back to the storage
         save_accounts(existing_accounts, self.key)

         # Update the UI labels to reflect the new account data
         self.update_labels()

         # Notify user of successful import
         messagebox.showinfo("Success", "Data imported successfully!")
         
      except (json.JSONDecodeError, ValueError):
         # Handle invalid JSON format errors
         messagebox.showerror("Error", "Invalid JSON format")
      except Exception as e:
         # Handle any other errors that may occur
         messagebox.showerror("Error", f"An error occurred: {str(e)}")

   # Ensures all imported accounts have the required fields
   def validate_data(self, imported_data):
      invalid_accounts = [] # Invalid accounts are removed from the imported data

      for account_name, account_data in imported_data.items():
         # Check for required fields in each account
         if 'key' not in account_data or 'secret' not in account_data:
            invalid_accounts.append(account_name) # Collect names of invalid accounts
         else:
            # Set default values for optional fields
            account_data.setdefault('group', "None")
            account_data.setdefault('created', "Unknown")
            account_data.setdefault('modified', "Not Modified")

      # Remove invalid accounts from the imported data and notify the user
      for account_name in invalid_accounts:
         del imported_data[account_name]
         messagebox.showerror("Error", f"The account '{account_name}' won't be added due to invalid format.")

   # Checks for duplicate accounts between existing and imported data.
   def check_duplicates(self, existing_accounts, imported_data):
      # Identify duplicate account names
      duplicate_accounts = set(imported_data.keys()) & set(existing_accounts.keys())

      if duplicate_accounts:
         # Prompt user about the existence of duplicates
         override = messagebox.askyesnocancel(
            "Duplicate Account",
            "At least one of your accounts already exists. Would you like to override them?"
         )

         if override is None:
            return # User canceled the operation
            
         if override is False:
            # Rename duplicates instead of overriding
            for name in duplicate_accounts:
               suffix = 1
               new_name = f"{name} ({suffix})"

               # Generate a unique name for the duplicate
               while new_name in existing_accounts:
                     suffix += 1
                     new_name = f"{name} ({suffix})"

               # Move the existing account data to the new name
               existing_accounts[new_name] = existing_accounts.pop(name)

   # Function to import accounts via QR Code
   def import_from_qr(self):
      # Open a file dialog to select a QR code image
      file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg;*.jpeg")])
      if not file_path:
         return # Exit if no file was selected

      try:
         # Load existing accounts
         existing_accounts = load_accounts(self.key)

         # Open the selected image file
         with open(file_path, 'rb') as img_file:
            img = Image.open(img_file)
            qr_info = decode(img) # Decode the QR code from the image

            if qr_info:
               # Process each QR code found in the image
               for data in qr_info:
                  self.create_qrcode(data, existing_accounts)
            else:
               messagebox.showerror("Error", "No QR code found in the image.")
      except Exception as e:
         # Handle any errors that occur during the import process
         messagebox.showerror("Error", f"An error occurred: {str(e)}")

   # Function to create an account from the decoded QR code data
   def create_qrcode(self, data, existing_accounts):
      # Decode the QR code data
      qr_data = data.data.decode('utf-8')
      parts = qr_data.split('secret=')

      # Extract the account name and secret key
      account_name = parts[0].split('/')[-1].rstrip('?').replace('%20', ' ')
      secret_key = parts[1] if len(parts) > 1 else ''

      # Check for duplicate accounts and create a unique name if necessary
      original_name = account_name
      suffix = 1
      while account_name in existing_accounts:
         account_name = f"{original_name} ({suffix})" # Generate new name with suffix
         suffix += 1

      # Add the new account to the existing accounts
      existing_accounts[account_name] = {'key': secret_key, 'secret': secret_key, 'group': "None", 'created': "Unknown", 'modified': "Not Modified"}
      
      # Save the updated accounts
      save_accounts(existing_accounts, self.key)

      # Update UI labels and notify the user
      self.update_labels()
      messagebox.showinfo("Success", f"Account '{account_name}' imported successfully.")

   # Function to import preferences
   def import_preferences(event=None):
      # Open a file dialog to select the preferences.ini file
      file_path = filedialog.askopenfilename(title="Select preferences.ini", filetypes=[("INI files", "*.ini")], initialdir=os.getcwd())
      
      # Unhide the original preferences.ini file before importing
      unhide_file('preferences.ini')

      # Validate that the selected file is named 'preferences.ini'
      if os.path.basename(file_path) != 'preferences.ini':
         messagebox.showerror("Error", "You did not select a valid preferences file.")
         mark_file_hidden('preferences.ini') # Re-hide the original file in case of an error
         return

      current_preferences_path = os.path.join(os.getcwd(), "preferences.ini")

      try:
         # Copy the selected preferences file to the current directory
         shutil.copyfile(file_path, current_preferences_path)
         messagebox.showinfo("Success", f"Preferences successfully imported. PLease restart.")
      except Exception as e:
         # Handle any errors during the file copy process
         messagebox.showerror("Error", f"Error replacing preferences.ini: {e}")
         mark_file_hidden('preferences.ini') # Re-hide the original file in case of an error
