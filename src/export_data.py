import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
from notifications import NotificationManager
import json, pyotp, os, shutil, qrcode

class ExportDataFunctions:
   # Initial export_data configurations
   def __init__(self, master, accounts, notifications):
      self.master = master
      self.accounts = accounts
      self.notifications = notifications
      self.active_window = None

   # Function to close the active window
   def close_active_window(self):
      if self.active_window:
            self.active_window.destroy()

   # Function to configure Export Data window configurations
   def export_and_close(self):
      self.close_active_window()
      export_window = tk.Toplevel(self.master)
      export_window.title("Export Data")
      export_window.geometry("200x100")
      export_window.resizable(False, False)
      export_window.configure(bg="white")

      json_button = ttk.Button(export_window, text="Export via File", command=self.export_file, style='Red.TButton')
      json_button.pack(pady=5)
      qr_button = ttk.Button(export_window, text="Export via QR Code(s)", command=self.export_qr_codes, style='Red.TButton')
      qr_button.pack(pady=5)

      self.active_window = export_window

   # Function to export accounts via .json window
   def export_file(self):
      self.close_active_window()
      export_window = tk.Toplevel(self.master)
      export_window.title("Export via File Options")
      export_window.geometry("250x250")
      export_window.resizable(False, False)
      export_window.configure(bg="white")
      self.active_window = export_window

      # Function to export accounts via .json encrypted
      def export_encrypted():
            self.close_active_window()
            dest_dir = filedialog.askdirectory()
            if dest_dir:
               dest_file = os.path.join(dest_dir, "exported_data_encrypted.json")
               shutil.copy("data.vv", dest_file)
               os.chmod(dest_file, 0o700)
               messagebox.showinfo("Exported", f"Encrypted JSON file exported to {dest_file}")

      # Function to export accounts via .json unencrypted
      def export_unencrypted():
            self.close_active_window()
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

      # Function to export accounts via txt
      def export_txt():
            self.close_active_window()
            file_path = filedialog.asksaveasfile(defaultextension=".txt", filetypes=[("Text files", "*.txt")],
                                                mode="w", initialfile="exported_data.txt")
            if file_path:
               try:
                  for name, info in self.accounts.items():
                        file_path.write(f"Name: {name}\n")
                        file_path.write(f"Key: {info['key']}\n")
                        file_path.write(f"Secret: {info['secret']}\n\n")
                  messagebox.showinfo("Exported", "Data exported successfully as TXT.")
               except Exception as e:
                  messagebox.showerror("Error", f"Error exporting TXT: {str(e)}")
               finally:
                  file_path.close()

      # Function to export accounts via txt encrypted
      def export_txt_encrypted():
            self.close_active_window()
            dest_dir = filedialog.askdirectory()
            if dest_dir:
               dest_file = os.path.join(dest_dir, "data.txt")
               shutil.copy("data.vv", dest_file)
               os.chmod(dest_file, 0o700)
               messagebox.showinfo("Exported", f"Encrypted TXT file exported to {dest_file}")

      # Function to export account secerts via txt
      def export_secrets():
            self.close_active_window()
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

      export_encrypted_button = ttk.Button(export_window, text="Export via JSON Encrypted", command=export_encrypted, style='Red.TButton')
      export_encrypted_button.pack(pady=5)
      export_unencrypted_button = ttk.Button(export_window, text="Export via JSON Unencrypted", command=export_unencrypted, style='Red.TButton')
      export_unencrypted_button.pack(pady=5)
      export_txt_button = ttk.Button(export_window, text="Export via TXT", command=export_txt, style='Red.TButton')
      export_txt_button.pack(pady=5)
      export_txt_encrypted_button = ttk.Button(export_window, text="Export via TXT Encrypted", command=export_txt_encrypted, style='Red.TButton')
      export_txt_encrypted_button.pack(pady=5)
      export_secrets_button = ttk.Button(export_window, text="Export Secrets via TXT", command=export_secrets, style='Red.TButton')
      export_secrets_button.pack(pady=5)

   # Function to export accounts via QR Code configuration
   def export_qr_codes(self):
      self.close_active_window()

      def export_from_qr():
            dest_folder = filedialog.askdirectory()
            if dest_folder:
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
                        qr_code_file_path = os.path.join(dest_folder, f"{name}_QR_code.png")
                        qr_img = qr.make_image(fill_color="black", back_color="white")
                        qr_img.save(qr_code_file_path)
               messagebox.showinfo("Exported", "QR codes exported successfully.")
      export_from_qr()