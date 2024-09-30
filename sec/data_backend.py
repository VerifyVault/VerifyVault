from tkinter import messagebox
import backend, json, os, shutil, time, configparser, glob, qrcode, pyotp, zipfile, io

class DataBackendFunctions:
   def __init__(self):
      self.load_preferences() # Load user preferences at startup

   # Function to perform automatic backups
   def perform_automatic_backup(self):
      if self.autobackups == 'on' and self.backup_folder_path:
         # Manage existing backup files, keeping only the latest 4
         backup_files = glob.glob(os.path.join(self.backup_folder_path, "vv_automatic_export_*"))
         if len(backup_files) > 4:
               backup_files.sort(key=os.path.getmtime) # Sort files by modification time
               while len(backup_files) > 4:
                  os.remove(backup_files.pop(0)) # Remove oldest backups

         # Create a new backup file
         current_time = time.strftime("%Y-%m-%d_%H%M", time.localtime())
         src_file = "data.json"
         file_base = f"vv_automatic_export_{self.backup_file_format}_{current_time}"
         
         try:
               # Call appropriate backup function based on selected format
               if "Encrypted JSON" in self.backup_file_format:
                  self.backup_encrypted_json(src_file, file_base)
               elif "Unencrypted JSON" in self.backup_file_format:
                  self.backup_unencrypted_json(src_file, file_base)
               elif "Encrypted TXT" in self.backup_file_format:
                  self.backup_encrypted_txt(src_file, file_base)
               elif "Unencrypted TXT" in self.backup_file_format:
                  self.backup_unencrypted_txt(src_file, file_base)
               elif "Secrets" in self.backup_file_format:
                  self.backup_secrets(file_base)
               elif "QR Code(s)" in self.backup_file_format:
                  self.backup_qr_codes(file_base)

         except Exception as e:
               messagebox.showerror("Error", f"Error performing backup: {str(e)}")

   def backup_encrypted_json(self, src_file, file_base):
      json_file_path = os.path.join(self.backup_folder_path, f"{file_base}.json")
      shutil.copy(src_file, json_file_path) # Copy source file to backup path

   def backup_unencrypted_json(self, src_file, file_base):
      json_file_path = os.path.join(self.backup_folder_path, f"{file_base}.json")
      key = backend.load_key() # Load encryption key
      accounts = backend.load_accounts(key) # Load account data
      with open(json_file_path, 'w') as file_path:
         json.dump(accounts, file_path, indent=4) # Write accounts to file

   def backup_encrypted_txt(self, src_file, file_base):
      txt_file_path = os.path.join(self.backup_folder_path, f"{file_base}.txt")
      shutil.copy(src_file, txt_file_path) # Copy source file to backup path

   def backup_unencrypted_txt(self, src_file, file_base):
      txt_file_path = os.path.join(self.backup_folder_path, f"{file_base}.txt")
      with open(src_file, 'rb') as src_file_path:
         encrypted_data = src_file_path.read() # Read encrypted data
      key = backend.load_key() # Load encryption key
      decrypted_data = backend.decrypt_message(encrypted_data, key) # Decrypt data
      accounts = json.loads(decrypted_data) # Load account data from decrypted JSON
      with open(txt_file_path, 'w') as file_path:
         json.dump(accounts, file_path, indent=4) # Write accounts to file

   def backup_secrets(self, file_base):
      txt_file_path = os.path.join(self.backup_folder_path, f"{file_base}.txt")
      with open(txt_file_path, 'w') as file_path:
         accounts = backend.load_accounts(backend.load_key()) # Load account data
         for name, info in accounts.items():
               file_path.write(f"Name: {name}\nSecret: {info['secret']}\n\n") # Write each secret

   def backup_qr_codes(self, file_base):
      zip_file_path = os.path.join(self.backup_folder_path, f"{file_base}.zip")
      with zipfile.ZipFile(zip_file_path, 'w') as zipf:
         accounts = backend.load_accounts(backend.load_key()) # Load account data
         for name, info in accounts.items():
               if 'secret' in info: # Check if secret exists
                  secret_key = info['secret']
                  provisioning_uri = pyotp.totp.TOTP(secret_key).provisioning_uri(name) # Generate provisioning URI
                  qr = qrcode.QRCode(
                     version=1,
                     error_correction=qrcode.constants.ERROR_CORRECT_L,
                     box_size=10,
                     border=4,
                  )
                  qr.add_data(provisioning_uri) # Add URI data to QR code
                  qr.make(fit=True)
                  qr_code_img = qr.make_image(fill_color="black", back_color="white")

                  qr_code_file_path = f"{name}_QR_code.png"
                  with io.BytesIO() as qr_code_io:
                     qr_code_img.save(qr_code_io, format='PNG') # Save QR code to bytes
                     zipf.writestr(qr_code_file_path, qr_code_io.getvalue()) # Write to ZIP

   # Function to load preferences
   def load_preferences(self):
      backend.unhide_file('preferences.ini') # Unhide the preferences file for reading
      config = configparser.ConfigParser()
      if os.path.exists('preferences.ini'):
         config.read('preferences.ini') # Read existing preferences

      # Load settings from the config file
      self.autobackups = config.get('Automatic Backups', 'backups', fallback=None)
      self.backup_folder_path = config.get('Automatic Backups', 'folder', fallback=None)
      self.backup_file_format = config.get('Automatic Backups', 'format', fallback="Encrypted JSON")
      
      # Re-hide the preferences file
      backend.mark_file_hidden('preferences.ini')




