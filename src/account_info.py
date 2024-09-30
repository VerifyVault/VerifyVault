from customtkinter import *
from groups import GroupsFunctions
from recycle_bin import RecycleBinFunctions
from PIL import Image
from tkinter import messagebox
from ttkbootstrap.tooltip import ToolTip
import backend, pyotp, time, pyperclip, qrcode, json, os, configparser

class AccountInfoFunctions:
   def __init__(self, master, groups, accounts, right_frame, update_labels):
      # Initialize with application components and user data
      self.master = master
      self.groups = groups
      self.accounts = accounts
      self.right_frame = right_frame
      self.update_labels = update_labels

      self.load_preferences()
      self.key = backend.load_key()
      self.recycle_bin = RecycleBinFunctions(master, accounts, right_frame, self.update_labels)

   # Function to open help window
   def open_help_window(self):
      # Create and configure the help window
      help_window = CTkToplevel(self.master)
      help_window.geometry("500x500")
      help_window.title("Account Information Help")
      help_window.resizable(False, False)
      help_window.after(250, lambda: help_window.iconbitmap('images/VerifyVaultLogo.ico'))
      help_window.grab_set()

      help_text = (
         # Help text providing important guidelines
         "- New name must be different\n\n"
         "- Name cannot contain: \\ / : * ? \" < > |\n\n"
         "- Invalid Key: Secret key isn't valid.\n\n"
         "- Groups cannot be created in the account window.\n\n"
         "- The QR code is for the account; you can also export it."
      )

      # Title and content for the help window
      title_label = CTkLabel(help_window, text="Account Information Help", font=("Helvetica", 30, "bold", "underline"))
      title_label.place(relx=0.5, rely=0.05, anchor="center")

      help_label = CTkLabel(help_window, text=help_text, font=("Helvetica", 20))
      help_label.place(relx=0.02, rely=0.1, anchor="nw")

   # Function to show a notification when TOTP is copied
   def show_copied_notification(self, popup_window):
      messagebox.showinfo("Success", "TOTP Copied!")

   # Function to display account information when an account is clicked
   def click_account(self, name):
      account_info = self.accounts[name] # Retrieve account information
      secret = account_info['secret'] # Get the secret key
      totp = pyotp.TOTP(secret) # Create a TOTP object

      # Create a frame to display account information
      info_frame = CTkFrame(self.right_frame, width=600, height=700)
      info_frame.place(relx=0.61, rely=0, anchor="n")

      # Function to close the information frame
      def close_frame():
         info_frame.destroy()

      # Close button to destroy the frame
      close_button = CTkButton(info_frame, command=close_frame, text="❌", fg_color="white", border_color="black", text_color="black", hover_color="red", border_width=2, width=50, height=20, cursor="hand2")
      close_button.place(relx=0.8, rely=0.03, anchor="ne")
      ToolTip(close_button, text="Close") # Tooltip for close button

      # Help button to open help window
      help_button = CTkButton(info_frame, text="❓",command=self.open_help_window, font=("Helvetica", 20, "bold"), fg_color="white", hover_color="red", width=30, height=10, border_width=2, corner_radius=2, text_color="black", cursor='hand2')
      help_button.place(relx=0.05, rely=0.03, anchor="n")
      ToolTip(help_button, text="Help") # Tooltip for help button

      # Title label for the account information
      title_label = CTkLabel(info_frame, text=f"Account Name - {name[:10]}..." if len(name) > 10 else name, font=("Helvetica", 30, "bold", "underline"))
      title_label.place(relx=0.42, rely=0.12, anchor="center")

      # Timer label for TOTP display
      timer_label = CTkLabel(info_frame, text="", font=("Helvetica", 24))
      timer_label.place(relx=0.42, rely=0.2, anchor="center")
      
      # Display current TOTP
      totp_label = CTkLabel(info_frame, text=f"TOTP: {totp.now()}", font=("Helvetica", 24))
      totp_label.place(relx=0.3, rely=0.25, anchor="center")

      # Copy button to copy TOTP to clipboard
      copy_button = CTkButton(info_frame, text="Copy", command=lambda: (pyperclip.copy(totp.now()), self.show_copied_notification(info_frame)), fg_color="white", hover_color="red", text_color="black", width=100, height=30, border_width=2, font=("Helvetica", 16, "bold"), cursor="hand2")
      copy_button.place(relx=0.55, rely=0.25, anchor="center")

      # Section for editing account information
      settings_label = CTkLabel(info_frame, text=f"Edit {name[:10]}..." if len(name) > 10 else name , font=("Helvetica", 30, "bold", "underline")).place(relx=0.42, rely=0.35, anchor="center")
      edit_name_label = CTkLabel(info_frame, text="Edit Name: ", font=("Helvetica", 18, "bold")).place(relx=0.05, rely=0.45, anchor="w")
      groups_label = CTkLabel(info_frame, text="Edit Group: ", font=("Helvetica", 18, "bold")).place(relx=0.05, rely=0.55, anchor="w")

      # Dropdown menu for selecting account groups
      group_options = ["None"] + [group for group in self.groups if group not in ["All Accounts", "Add Group"]]
      group_dropdown = CTkOptionMenu(info_frame, values=group_options, height=35, font=("Helvetica", 14), fg_color="white", text_color="black", dropdown_font=("Helvetica", 14), dropdown_text_color="black", corner_radius=2, button_color="red", button_hover_color="#EE4B2B", dropdown_fg_color="white", dropdown_hover_color="red", hover=True, anchor="center")
      group_dropdown.place(relx=0.25, rely=0.55, anchor="w")
      group_dropdown.set(account_info['group']) # Set the current group

      # Function to update the account group
      def update_group():
        new_group = group_dropdown.get() # Get selected group
        if new_group not in ["Add Group", "All Accounts"]:
         # Update account group and modified time
            account_info['group'] = new_group if new_group != "None" else ""
            account_info['modified'] = time.strftime("%B %d, %Y at %H:%M") if self.time_format == 'on' else time.strftime("%B %d, %Y at %I:%M%p")
            self.accounts[name] = account_info # Update accounts dictionary
            backend.save_accounts(self.accounts, self.key) # Save changes
            self.update_labels(self.accounts) # Refresh UI labels
            messagebox.showinfo("Success", "Account group updated successfully!") # Success message
            close_frame() # Close the info frame
        else:
            messagebox.showerror("Invalid Group", f"Cannot set group to {new_group}.") # Error message

      # Button to trigger group update
      update_group_button = CTkButton(info_frame, text="Update Group", command=update_group, fg_color="white", hover_color="red", text_color="black", width=150, height=30, border_width=2, font=("Helvetica", 12, "bold"), cursor="hand2")
      update_group_button.place(relx=0.5, rely=0.55, anchor="w")

      # Labels to display creation and last modified timestamps
      creation_time_label = CTkLabel(info_frame, text=f"Created At: {account_info['created']}", font=("Helvetica", 16)).place(relx=0.45, rely=0.84, anchor="center")
      last_edited_label = CTkLabel(info_frame, text=f"Last Modified: {account_info['modified']}", font=("Helvetica", 16)).place(relx=0.44, rely=0.88, anchor="center")

      # Function to validate and save the account name
      def validate_name(name):
         # Define invalid characters for the account name
         invalid_chars = "\\/:*?\"<>|"
         for char in invalid_chars:
            if char in name: # Check if any invalid character is in the name
               messagebox.showerror("Invalid Character", f"Name cannot contain '{char}'")
               return False  # Return false if invalid character is found
         return True  # Return true if name is valid

      # Register the validation function with the entry widget
      vcmd = (info_frame.register(validate_name), "%P")

      # Create an entry widget for editing the account name
      edit_name = CTkEntry(info_frame, validate="key", validatecommand=vcmd, width=220, height=40, border_width=2, border_color="red")
      edit_name.place(relx=0.22, rely=0.45, anchor="w")
      edit_name.insert(0, name) # Pre-fill with the current name

      # Function to save the new account name
      def save_name():
         new_name = edit_name.get().strip() # Get the entered name and remove surrounding whitespace

         if not new_name: # Check if the name is empty
            messagebox.showerror("Invalid Entry", "Name is required.")
            return # Exit if no name is provided

         # Validate the new name and ensure it differs from the old name
         if validate_name(new_name) and new_name != name:
            if new_name in self.accounts: # Check for name duplication
               messagebox.showerror("Invalid Entry", "Name already exists.")
            else:
               # Update the accounts dictionary with the new name
               self.accounts[new_name] = self.accounts.pop(name)
               account_info['modified'] = time.strftime("%B %d, %Y at %H:%M") if self.time_format == 'on' else time.strftime("%B %d, %Y at %I:%M%p")

               # Save updated accounts to storage
               backend.save_accounts(self.accounts, self.key)
               self.update_labels(self.accounts)  # Refresh UI labels
               messagebox.showinfo("Success", "Account Name edited successfully!")  # Success message
               close_frame()  # Close the edit frame
         else:
            messagebox.showerror("Invalid Entry", "Invalid Name.") # Error for invalid name

      # Bind the Enter key to the save_name function for quick saving
      edit_name.bind("<Return>", lambda event: save_name())

      # Create a button to save the new account name
      save_button = CTkButton(info_frame, text="Save", command=save_name, fg_color="white", hover_color="red", text_color="black", width=100, height=30, border_width=2, font=("Helvetica", 12, "bold"), cursor='hand2').place(relx=0.7, rely=0.45, anchor="center")

      # Function to export the QR code for the account
      def export_qr_code(name):
         account_info = self.accounts[name]  # Retrieve account information
         secret_key = account_info['secret']  # Get the secret key for TOTP
         provisioning_uri = pyotp.totp.TOTP(secret_key).provisioning_uri(name)  # Generate provisioning URI

         # Create a QR code
         qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=12,
            border=4,
         )
         qr.add_data(provisioning_uri) # Add the provisioning URI to the QR code
         qr.make(fit=True) # Fit the QR code to the data

         # Ask the user for a directory to save the QR code
         dest_folder = filedialog.askdirectory()
         if dest_folder:
            qr_code_file_path = os.path.join(dest_folder, f"{name}_QR_code.png")  # Set file path
            qr_img = qr.make_image(fill_color="black", back_color="white")  # Create the QR code image
            qr_img.save(qr_code_file_path)  # Save the QR code image
            messagebox.showinfo("Success", f"QR code exported successfully to {qr_code_file_path}")  # Success message
            
      # Function to display the QR code in a new window
      def show_qr_code(name):
         qr_window = CTkToplevel(self.master)
         qr_window.geometry("500x500")
         qr_window.title(f"{name} QR Code")
         qr_window.resizable(False, False)
         qr_window.after(250, lambda: qr_window.iconbitmap('images/VerifyVaultLogo.ico'))
         qr_window.grab_set()

         # Title label for the QR code window
         title_label = CTkLabel(qr_window, text=f"{name} QR Code", font=("Helvetica", 30, "bold", "underline")).place(relx=0.5, rely=0.1, anchor="center")

         # Generate the provisioning URI and create QR code
         provisioning_uri = totp.provisioning_uri(name)
         qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=3,
         )
         qr.add_data(provisioning_uri)  # Add provisioning URI to QR code
         qr.make(fit=True)  # Fit the QR code to the data
         qr_img = qr.make_image(fill_color="black", back_color="white")  # Create QR code image
        
         # Use BytesIO to handle the image in memory 
         from io import BytesIO
         qr_image_stream = BytesIO()
         qr_img.save(qr_image_stream, format='PNG') # Save the image to the stream
         qr_image_stream.seek(0) # Reset stream position
         
         # Create a PhotoImage from the image stream
         from tkinter import PhotoImage
         pil_image = Image.open(qr_image_stream)  # Open the BytesIO stream as a PIL image
         qr_image = CTkImage(pil_image, size=(300,300))  # Create CTkImage from the PIL image

         qr_code_label = CTkLabel(qr_window, image=qr_image, text="")
         qr_code_label.image = qr_image # Keep a reference to the image
         qr_code_label.place(relx=0.5, rely=0.5, anchor="center") # Position the QR code

         # Button to export the QR code
         export_qr_button = CTkButton(qr_window, text="Export QR Code", command=lambda: export_qr_code(name), fg_color="white", hover_color="red", text_color="black", width=130, height=40, border_width=2, font=("Helvetica", 16, "bold"), cursor="hand2")
         export_qr_button.place(relx=0.5, rely=0.9, anchor="center")

      # Function to delete an account
      def delete_account(name):
         confirm_delete = messagebox.askyesno("Delete Account", "Are you sure you would like to delete this account?")
         if not confirm_delete:
            return # Exit if the user cancels

         backend.unhide_file("data.json")  # Unhide the data file
         backend.unhide_file("deleted.json")  # Unhide the deleted accounts file
         try:
            # Load and decrypt account data
            with open('data.json', 'rb') as file:
               encrypted_data = file.read()
               decrypted_data = backend.decrypt_message(encrypted_data, self.key)
               accounts_data = json.loads(decrypted_data) # Parse JSON data

            if name not in accounts_data: # Check if account exists
               messagebox.showerror("Error", "Account not found.")
               return

            deleted_account_info = accounts_data.pop(name) # Remove account from active accounts
               
            # Encrypt and save updated accounts data
            encrypted_data = backend.encrypt_message(json.dumps(accounts_data), self.key)
            with open('data.json', 'wb') as file:
               file.write(encrypted_data)
            
            # Load existing deleted data or initialize it
            rkey = backend.load_rec_key()
            deleted_data = {}
            if os.path.exists('deleted.json') and os.path.getsize('deleted.json') > 0:
               with open('deleted.json', 'rb') as deleted_file:
                     encrypted_deleted_data = deleted_file.read()
                     decrypted_deleted_data = backend.decrypt_message(encrypted_deleted_data, rkey)
                     deleted_data = json.loads(decrypted_deleted_data) # Load deleted data

            # Ensure the deleted account name is unique
            unique_name = name
            counter = 1
            while unique_name in deleted_data:
               unique_name = f"{name} ({counter})" # Modify name if it exists
               counter += 1                                
            deleted_data[unique_name] = deleted_account_info # Add deleted account info

            # Encrypt and save updated deleted data
            encrypted_deleted_data = backend.encrypt_message(json.dumps(deleted_data), rkey)
            with open('deleted.json', 'wb') as deleted_file:
               deleted_file.write(encrypted_deleted_data)

            # Update in-memory accounts and refresh UI
            del self.accounts[name]  # Remove account from in-memory accounts
            self.update_labels(self.accounts)  # Update displayed account labels
            self.recycle_bin.populate_recycle_bin()  # Refresh recycle bin view
            info_frame.destroy() # Close account info frame
            messagebox.showinfo("Success", "Account deleted successfully.")

         except FileNotFoundError:
            messagebox.showerror("Error", "Data file not found.")
         except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}") # Handle unexpected errors
         finally:
            backend.mark_file_hidden("data.json")  # Hide the data file again
            backend.mark_file_hidden("deleted.json")  # Hide the deleted file again

      # Button to show the QR code
      show_qr_button = CTkButton(info_frame, text="Show QR Code", command=lambda: show_qr_code(name), fg_color="white", hover_color="red", text_color="black", width=130, height=40, border_width=2, font=("Helvetica", 16, "bold"), cursor="hand2")
      show_qr_button.place(relx=0.2, rely=0.75, anchor="w")
      
      # Button to delete the account
      delete_account_button = CTkButton(info_frame, text="Delete Account", command=lambda: delete_account(name), fg_color="red", hover_color="white", text_color="black", width=130, height=40, border_width=2, font=("Helvetica", 16, "bold"), cursor="hand2")
      delete_account_button.place(relx=0.45, rely=0.75, anchor="w")
      
      # Label for actions section
      actions_label = CTkLabel(info_frame, text="Actions", font=("Helvetica", 30, "bold", "underline"))
      actions_label.place(relx=0.42, rely=0.66, anchor="center")

      # Initialize progress bar for TOTP timer
      timer_bar = CTkProgressBar(info_frame, orientation="horizontal", width=300, height=20, border_width=0, border_color="red", fg_color="white", progress_color="red", mode="determinate")
      timer_bar.place(relx=0.42, rely=0.2, anchor="center")

      # Function to update the timer and TOTP display
      def update_timer():
         remaining_time = 30 - (time.time() % 30)  # Calculate time remaining in 30-second interval
         timer_bar.set(remaining_time / 30)  # Update progress bar
         info_frame.after(1000, update_timer)  # Call update_timer every second
         totp_label.configure(text=f"TOTP: {totp.now()}")  # Update displayed TOTP

      update_timer() # Start the timer

   # Function to load user preferences from a config file
   def load_preferences(self):
      config = configparser.ConfigParser()  # Create a config parser
      config.read('preferences.ini')  # Read the preferences file
      self.time_format = config.get('Preferences', 'time_format', fallback=None)  # Load time format preference