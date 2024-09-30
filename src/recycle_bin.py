import tkinter as tk
from customtkinter import *
from tkinter import messagebox
from ttkbootstrap.tooltip import ToolTip
from cryptography.fernet import InvalidToken
import backend, keys, json, os, time

class RecycleBinFunctions:
    def __init__(self, master, accounts, right_frame, update_labels):
        # Initialize the recycle bin manager
        self.master = master
        self.accounts = accounts
        self.right_frame = right_frame
        self.update_labels = update_labels

        self.key = backend.load_key() # Load encryption key
        self.deleted_accounts = {} # Store deleted accounts
        self.search_var = tk.StringVar() # For search functionality

        self.current_page = 1 # Track current page
        self.acc_per_page = 5 # Accounts per page
        self.frame_open = False # Check if the frame is open
        self.recycle_frame = None # Placeholder for recycle frame

    # Function to open help window
    def open_help_window(self):
        help_window = CTkToplevel(self.master)
        help_window.geometry("600x400")
        help_window.title("Recycle Bin Help")
        help_window.resizable(False, False)
        help_window.after(250, lambda: help_window.iconbitmap('images/VerifyVaultLogo.ico'))
        help_window.grab_set()

        help_text = (
            "- Restore: Restores the selected account\n\n"
            "- Delete: Permanently deletes the selected account\n\n"
            "- Restore All: Restores all accounts in recycle bin\n\n"
            "- Clear All: Permanently deletes all accounts in the recycle bin"
        )

        # Title and help text labels
        title_label = CTkLabel(help_window, text="Recycle Bin Help", font=("Helvetica", 30, "bold", "underline"))
        title_label.place(relx=0.5, rely=0.05, anchor="center")

        help_label = CTkLabel(help_window, text=help_text, font=("Helvetica", 20))
        help_label.place(relx=0.02, rely=0.15, anchor="nw")

    # Function to configure recycle bin frame
    def manage_recycle_bin(self):
        # Close existing frame if open
        if self.frame_open:
            self.recycle_frame.destroy()
        self.frame_open = True # Mark frame as open

        # Create recycle bin UI components
        self.recycle_frame = CTkFrame(self.right_frame, width=600, height=700)
        self.recycle_frame.place(relx=0.61, rely=0, anchor="n")

        # Function to close the frame
        def close_frame():
            self.recycle_frame.destroy() # Destroy the frame
            self.frame_open = False # Mark the frame as closed

        close_frame = CTkButton(self.recycle_frame, command=close_frame, text="❌", fg_color="white", border_color="black", text_color="black", hover_color="red", border_width=2, width=50, height=20, cursor="hand2")
        close_frame.place(relx=0.8, rely=0.03, anchor="ne")
        ToolTip(close_frame, text="Close")

        help_button = CTkButton(self.recycle_frame, text="❓", command=self.open_help_window, font=("Helvetica", 20, "bold"), fg_color="white", hover_color="red", width=30, height=10, border_width=2, corner_radius=2, text_color="black", cursor='hand2')
        help_button.place(relx=0.05, rely=0.03, anchor="n")
        ToolTip(help_button, text="Help")

        title_label = CTkLabel(self.recycle_frame, text="Recycle Bin", font=("Helvetica", 30, "bold"))
        title_label.place(relx=0.42, rely=0.1, anchor="center")

        # Search entry for filtering deleted accounts
        search_entry = CTkEntry(self.recycle_frame, width=300, height=40, textvariable=self.search_var, placeholder_text="🔍 Search Accounts", border_color="black")
        search_entry.place(relx=0.42, rely=0.17, anchor="center")
        search_entry.bind("<KeyRelease>", self.search_deleted_accounts)

        # Action buttons
        restore_all = CTkButton(self.recycle_frame, text="Restore All", fg_color="white", hover_color="red", text_color="black", width=100, height=40, border_width=2, font=("Helvetica", 16, "bold"), cursor='hand2', command=self.restore_all_accounts)
        restore_all.place(relx=0.32, rely=0.25, anchor="center")

        clear_button = CTkButton(self.recycle_frame, text="Clear All", fg_color="white", hover_color="red", text_color="black", width=100, height=40, border_width=2, font=("Helvetica", 16, "bold"), cursor='hand2', command=self.clear_all_accounts)
        clear_button.place(relx=0.52, rely=0.25, anchor="center")

        self.populate_recycle_bin() # Populate display

    # Function to display deleted accounts
    def populate_recycle_bin(self):
        self.load_deleted_accounts() # Load currently deleted accounts

        if self.recycle_frame is None:
            return # Exit if the recycle frame isn't initialized

        # Destroy old widgets, except for fixed widgets
        for widget in self.recycle_frame.winfo_children():
            if isinstance(widget, CTkFrame) and widget not in [self.recycle_frame.winfo_children()[0], self.recycle_frame.winfo_children()[1]]:
                widget.destroy()

        query = self.search_var.get().lower() # Get the search query
        filtered_accounts = {name: deletion_time for name, deletion_time in self.deleted_accounts.items() if query in name.lower()}

        # Remove existing "No Accounts Found" label if it exists
        for widget in self.recycle_frame.winfo_children():
            if isinstance(widget, CTkLabel) and widget.cget("text") == "❌ No Accounts Found":
                widget.destroy()
                break

        if not filtered_accounts:
            # Show message if no accounts match the search
            no_account_label = CTkLabel(self.recycle_frame, text="❌ No Accounts Found", font=("Helvetica", 20, "bold"), corner_radius=2)
            no_account_label.place(relx=0.42, rely=0.4, anchor="center")
        else:
            # Calculate pagination
            num_pages = (len(filtered_accounts) + self.acc_per_page - 1) // self.acc_per_page
            self.current_page = min(self.current_page, num_pages) # Ensure current page is valid

            start_index = (self.current_page - 1) * self.acc_per_page
            end_index = min(start_index + self.acc_per_page, len(filtered_accounts))

            filtered_accounts_list = list(filtered_accounts.items())[start_index:end_index]

            # Display the accounts
            for index, (account_name, deletion_time) in enumerate(filtered_accounts_list):
                account_frame = CTkFrame(self.recycle_frame)
                account_frame.place(relx=0.42, rely=0.35 + index * (0.1), anchor="center")
                
                #display_text = f"{account_name[:10]}..." if len(account_name) > 10 else account_name
                account_label = CTkLabel(account_frame, text=f"{account_name[:10]}..." if len(account_name) > 10 else account_name, width=250, height=50, anchor="w")
                account_label.pack(side="left", padx=10)

                # Restore button for each account
                restore_button = CTkButton(account_frame, text="Restore", fg_color="white", hover_color="red", text_color="black", width=80, height=30, border_width=2, font=("Helvetica", 12, "bold"), cursor='hand2', command=lambda name=account_name: self.restore_account(name))
                restore_button.pack(side="left", padx=5)
                
                # Delete button for each account
                delete_button = CTkButton(account_frame, text="Delete", fg_color="red", hover_color="white", text_color="black", width=80, height=30, border_width=2, font=("Helvetica", 12, "bold"), cursor='hand2', command=lambda name=account_name: self.permanent_delete_account(name))
                delete_button.pack(side="left", padx=5)

            self.add_pagination_controls(num_pages) # Add pagination controls

    # Function to display page number/buttons
    def add_pagination_controls(self, num_pages):
        # Remove old pagination buttons
        for widget in self.recycle_frame.winfo_children():
            if isinstance(widget, CTkButton) and widget.cget('text') in ("🢀", "🢂"):
                widget.destroy()

        def prev_page():
            if self.current_page > 1:
                self.current_page -= 1
                self.populate_recycle_bin() # Refresh the bin

        def next_page():
            if self.current_page < num_pages:
                self.current_page += 1
                self.populate_recycle_bin() # Refresh the bin

        # Create previous page button if not on the first page
        if self.current_page > 1:
            prev_button = CTkButton(self.recycle_frame, text="🢀", command=prev_page, fg_color="white", hover_color="red", text_color="black", width=100, height=40, border_width=2, font=("Helvetica", 25), cursor="hand2")
            prev_button.place(relx=0.15, rely=0.85, anchor="center")

        # Create next page button if not on the last page
        if self.current_page < num_pages:
            next_button = CTkButton(self.recycle_frame, text="🢂", command=next_page, fg_color="white", hover_color="red", text_color="black", width=100, height=40, border_width=2, font=("Helvetica", 25), cursor="hand2")
            next_button.place(relx=0.7, rely=0.85, anchor="center")

        # Page indicator label
        page_indicator = CTkLabel(self.recycle_frame, text=f"Page {self.current_page}/{num_pages}", font=("Helvetica", 14, "bold"))
        page_indicator.place(relx=0.4, rely=0.85, anchor="center")

    # Functions to search, load, and save deleted accounts
    def search_deleted_accounts(self, event):
        self.populate_recycle_bin() # Refresh the recycle bin based on search input

    def load_deleted_accounts(self):
        backend.unhide_file("deleted.json") # Make the file accessible
        key = backend.load_rec_key() # Load decryption key

        if os.path.exists("deleted.json"):
            with open("deleted.json", "rb") as file:
                try:
                    encrypted_data = file.read() # Read encrypted data
                    decrypted_data = backend.decrypt_message(encrypted_data, key) # Decrypt data
                    self.deleted_accounts = json.loads(decrypted_data) # Load accounts
                except (json.JSONDecodeError, InvalidToken):
                    messagebox.showerror("Error", "Error: Unable to decode or decrypt JSON file. Resetting accounts.")
                    self.deleted_accounts = {} # Reset if error occurs
        else:
            self.deleted_accounts = {} # No accounts found
            keys.delete_key("recycle_key") # Remove the recycle key if no file

        backend.mark_file_hidden("deleted.json") # Hide the file again
        return self.deleted_accounts

    def save_deleted_accounts(self):
        backend.unhide_file("deleted.json") # Make the file accessible
        key = backend.load_rec_key() # Load encryption key

        with open('deleted.json', 'wb') as file:
            json_data = json.dumps(self.deleted_accounts) # Convert accounts to JSON
            encrypted_data = backend.encrypt_message(json_data, key) # Encrypt data
            file.write(encrypted_data) # Save encrypted data

        backend.mark_file_hidden("deleted.json") # Hide the file again

    # Function to restore all accounts
    def restore_all_accounts(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to restore all accounts?"):
            if self.deleted_accounts:
                for account_name in list(self.deleted_accounts):
                    self.restore_account(account_name) # Restore each account
                messagebox.showinfo("Success", "All accounts have been restored.")
                self.populate_recycle_bin() # Refresh display
                self.update_labels() # Update UI labels
            else:
                messagebox.showerror("Error", "There are no accounts to restore.")

    # Function to clear all accounts
    def clear_all_accounts(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to permanently delete all accounts?"):
            if self.deleted_accounts:
                self.deleted_accounts.clear() # Clear the accounts
                self.save_deleted_accounts() # Save changes
                messagebox.showinfo("Success", "All accounts have been permanently deleted.")
                self.populate_recycle_bin() # Refresh display
            else:
                messagebox.showerror("Error", "There are no accounts to delete.")

    # Function to restore individual accounts with unique name
    def restore_account(self, account_name):
        if account_name in self.deleted_accounts:
            try:
                existing_accounts = backend.load_accounts(self.key) # Load current accounts
                account_info = self.deleted_accounts[account_name] # Get deleted account info

                # Ensure unique account name
                new_account_name = account_name
                suffix = 1
                while new_account_name in existing_accounts:
                    new_account_name = f"{account_name} ({suffix})" # Modify name for uniqueness
                    suffix += 1

                # Add restored account to existing accounts
                existing_accounts[new_account_name] = {
                    'secret': account_info.get('secret', ''),
                    'key': account_info.get('key', ''),
                    'group': account_info.get('group', ''),
                    'created': account_info.get('created', ''),
                    'modified': account_info.get('modified', ''),
                    'deleted': False # Mark as not deleted
                }

                backend.save_accounts(existing_accounts, self.key) # Save updated accounts
                del self.deleted_accounts[account_name] # Remove from deleted accounts
                self.save_deleted_accounts() # Save changes to deleted accounts
                self.populate_recycle_bin() # Refresh recycle bin display
                self.update_labels() # Update UI labels
            except Exception as e:
                messagebox.showerror("Error", f"Error restoring account: {str(e)}")
        else:
            messagebox.showerror("Error", f"Account '{account_name}' not found in deleted accounts.")

    # Function to permanently delete individual account
    def permanent_delete_account(self, account_name):
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this account permanently?"):
            if account_name in self.deleted_accounts:
                del self.deleted_accounts[account_name] # Remove account from deleted accounts
                self.save_deleted_accounts() # Save changes
                self.populate_recycle_bin() # Refresh recycle bin display
                messagebox.showinfo("Success", "Account deleted successfully.")
            else:
                messagebox.showerror("Error", f"Account '{account_name}' not found in deleted accounts.")
