from tkinter import filedialog, messagebox
import json, pyotp, os, shutil, qrcode, zipfile, io

class ExportDataFunctions:
   # Initial file configurations
   def __init__(self, master, accounts):
      self.master = master
      self.accounts = accounts

   # Function to export accounts via encrypted .json file
   def export_encrypted(self):
      try:
         # Prompt user to select a directory for export
         file_path = filedialog.askdirectory()
         if not file_path:
            return # Exit if no directory was selected

         # Define the destination file path
         dest_file = os.path.join(file_path, "exported_data_encrypted.json")
         # Copy the data file to the destination
         shutil.copy("data.json", dest_file)

         # Notify user of success
         messagebox.showinfo("Success", f"Encrypted JSON file exported to {dest_file}")
      except Exception as e:
         # Handle any errors that occur during the export
         print(f"Error exporting encrypted JSON: {str(e)}")

   # Function to export accounts via unencrypted .json file
   def export_unencrypted(self):
      try:
         # Prompt user to choose a file location for export
         with filedialog.asksaveasfile(defaultextension=".json", filetypes=[("JSON files", "*.json")], mode="w", initialfile="exported_data_unencrypted.json") as file_path:
            if file_path:
               json.dump(self.accounts, file_path, indent=4) # Write accounts to the file

               # Notify user of success
               messagebox.showinfo("Success", f"Unencrypted JSON file exported to {file_path.name}")
      except Exception as e:
         # Handle any errors that occur during the export
         print(f"Error exporting unencrypted JSON: {str(e)}")

   # Function to export accounts via encrypted .txt file
   def export_txt_encrypted(self):
      try:
         # Prompt user to select a directory for export
         file_path = filedialog.askdirectory()
         if not file_path:
            return # Exit if no directory was selected

         # Define the destination file path for the TXT file
         dest_file = os.path.join(file_path, "exported_data_encrypted.txt")
         shutil.copy("data.json", dest_file) # Copy the data file to the destination

         # Notify user of success
         messagebox.showinfo("Success", f"Encrypted TXT file exported to {file_path.name}")
      except Exception as e:
         # Handle any errors that occur during the export
         print(f"Error exporting encrypted TXT: {str(e)}")

   # Function to export accounts via txt unencrypted
   def export_txt_unencrypted(self):
      try:
         # Prompt user to choose a file location for export
         with filedialog.asksaveasfile(defaultextension=".txt", filetypes=[("Text files", "*.txt")], mode="w", initialfile="exported_data_unencrypted.txt") as file_path:
            # Iterate through the accounts and write their details to the file
            for name, info in self.accounts.items():
               file_path.write(f"Name: {name}\nKey: {info['key']}\nSecret: {info['secret']}\nGroup: {info.get('group', 'No Group')}\nCreated at: {info.get('created')}\nModified at: {info.get('modified')}\n\n")
            # Notify the user of success
            messagebox.showinfo("Success", f"Unencrypted TXT file exported to {file_path.name}")
      except Exception as e:
         # Handle any errors that occur during the export
         print(f"Error exporting unencrypted TXT: {str(e)}")

   # Function to export account secerts via txt
   def export_secrets(self):
      try:
         # Prompt user to choose a file location for export
         with filedialog.asksaveasfile(defaultextension=".txt", filetypes=[("Text files", "*.txt")], mode="w", initialfile="exported_secrets.txt") as file_path:
               # Write each account's name and secret to the file
               for name, info in self.accounts.items():
                  file_path.write(f"Name: {name}\nSecret: {info['secret']}\n\n")

               # Notify user of success
               messagebox.showinfo("Success", f"Secrets exported as TXT file to {file_path.name}")
      except Exception as e:
         # Handle any errors that occur during the export
         print(f"Error exporting secrets as TXT: {str(e)}")

   # Function to export accounts via QR Code 
   def export_qr_codes(self):
      file_path = filedialog.askdirectory()

      if file_path:
         zip_file_path = os.path.join(file_path, "exported_qr_codes.zip")
         with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            # Generate QR codes for each account with a secret
            for name, info in self.accounts.items():
                  if 'secret' in info:
                     secret_key = info['secret']
                     provisioning_uri = pyotp.totp.TOTP(secret_key).provisioning_uri(name)
                     qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                     )
                     qr.add_data(provisioning_uri)
                     qr.make(fit=True)
                     qr_code_img = qr.make_image(fill_color="black", back_color="white")
                     
                     # Save QR code to a bytes buffer and add to ZIP
                     qr_code_file_path = f"{name}_QR_code.png"
                     with io.BytesIO() as qr_code_io:
                        qr_code_img.save(qr_code_io, format='PNG')
                        zipf.writestr(qr_code_file_path, qr_code_io.getvalue())

            # Notify user of success
            messagebox.showinfo("Success", f"QR Codes exported to {zip_file_path}")

   # Function to export VerifyVault preferences
   def export_preferences(self):
      current_path = os.path.join(os.getcwd(), "preferences.ini")

      # Check if the preferences file exists
      if not os.path.exists(current_path):
         messagebox.showerror("Error", "The preferences.ini file does not exist.")
         return

      # Prompt user to choose a save location for the exported file
      save_path = filedialog.asksaveasfilename(title="Save preferences.ini", defaultextension=".ini", filetypes=[("INI files", "*.ini")], initialfile="preferences.ini", initialdir=os.getcwd())

      try:
         # Copy the preferences file to the chosen location
         shutil.copyfile(current_path, save_path)
         messagebox.showinfo("Success", f"Preferences exported to {save_path}")
      except Exception as e:
         # Handle any errors that occur during the export
         print(f"Error exporting preferences.ini: {e}")


