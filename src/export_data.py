from tkinter import filedialog, messagebox
from PIL import Image
import json, pyotp, os, shutil, qrcode

class ExportDataFunctions:
   # Initial export_data configurations
   def __init__(self, master, accounts):
      self.master = master
      self.accounts = accounts

   # Function to export accounts via .json encrypted
   def export_encrypted(self):
      file_path = filedialog.askdirectory()
      if file_path:
         try:
            dest_file = os.path.join(file_path, "exported_data_encrypted.json")
            shutil.copy("data.vv", dest_file)
            os.chmod(dest_file, 0o700)
            messagebox.showinfo("Exported", f"Encrypted JSON file exported to {dest_file}")
         except Exception as e:
            messagebox.showerror("Error", f"Error exporting encrypted JSON: {str(e)}")
         finally:
            file_path.close()

   # Function to export accounts via .json unencrypted
   def export_unencrypted(self):
      file_path = filedialog.asksaveasfile(defaultextension=".json", filetypes=[("JSON files", "*.json")],
                                          mode="w", initialfile="exported_data_unencrypted.json")
      if file_path:
         try:
            json.dump(self.accounts, file_path, indent=4)
            messagebox.showinfo("Exported", "Data exported successfully as unencrypted JSON.")
         except Exception as e:
            messagebox.showerror("Error", f"Error exporting unencrypted JSON: {str(e)}")
         finally:
            file_path.close()

   # Function to export accounts via txt unencrypted
   def export_txt(self):
      file_path = filedialog.asksaveasfile(defaultextension=".txt", filetypes=[("Text files", "*.txt")],
                                          mode="w", initialfile="exported_data.txt")
      if file_path:
         try:
            for name, info in self.accounts.items():
                  file_path.write(f"Name: {name}\n")
                  file_path.write(f"Key: {info['key']}\n")
                  file_path.write(f"Secret: {info['secret']}\n")
                  file_path.write(f"Group: {info.get('group', 'No Group')}\n")
                  file_path.write(f"Created at: {info.get('created')}\n\n")
            messagebox.showinfo("Exported", "Data exported successfully as TXT.")
         except Exception as e:
            messagebox.showerror("Error", f"Error exporting unencrypted TXT: {str(e)}")
         finally:
            file_path.close()

   # Function to export accounts via txt encrypted
   def export_txt_encrypted(self):
      file_path = filedialog.askdirectory()
      if file_path:
         try:
            dest_file = os.path.join(file_path, "data.txt")
            shutil.copy("data.vv", dest_file)
            os.chmod(dest_file, 0o700)
            messagebox.showinfo("Exported", f"Encrypted TXT file exported to {dest_file}")
         except Exception as e:
            messagebox.showerror("Error", f"Error exporting encrypted TXT: {str(e)}")
         finally:
            file_path.close()

   # Function to export account secerts via txt
   def export_secrets(self):
      file_path = filedialog.asksaveasfile(defaultextension=".txt", filetypes=[("Text files", "*.txt")],
                                          mode="w", initialfile="exported_secrets.txt")
      if file_path:
         try:
            for name, info in self.accounts.items():
                  file_path.write(f"Name: {name}\n")
                  file_path.write(f"Secret: {info['secret']}\n\n")
            messagebox.showinfo("Exported", "Secrets exported successfully as TXT.")
         except Exception as e:
            messagebox.showerror("Error", f"Error exporting secrets as TXT: {str(e)}")
         finally:
            file_path.close()

   # Function to export accounts via QR Code 
   def export_from_qr(self):
      file_path = filedialog.askdirectory()
      if file_path:
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
                  qr_code_file_path = os.path.join(file_path, f"{name}_QR_code.png")
                  qr_img = qr.make_image(fill_color="black", back_color="white")
                  qr_img.save(qr_code_file_path)
                  messagebox.showinfo("Exported", "QR codes exported successfully.")
      else:
         messagebox.showerror("Error", f"Error exporting QR Code(s): {str(e)}")

   # Function to export VerifyVault preferences
   def export_preferences(self):
      current_preferences_path = os.path.join(os.getcwd(), "preferences.ini")

      if not os.path.exists(current_preferences_path):
         messagebox.showerror("Error", "The preferences.ini file does not exist.")
         return

      save_path = filedialog.asksaveasfilename(
         title="Save preferences.ini",
         defaultextension=".ini",
         filetypes=[("INI files", "*.ini")],
         initialfile="preferences.ini",
         initialdir=os.getcwd()
      )

      try:
         shutil.copyfile(current_preferences_path, save_path)
         messagebox.showinfo("Success", f"Preferences successfully exported to {save_path}")
      except Exception as e:
         messagebox.showerror("Error", f"Error exporting preferences.ini: {e}")


