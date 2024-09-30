from customtkinter import *
from tkinter import messagebox
from ttkbootstrap.tooltip import ToolTip
import backend, json, os

class GroupsFunctions:
   def __init__(self, master, accounts, top_frame, update_labels):
      # Initialize the main attributes and load existing groups
      self.master = master
      self.accounts = accounts
      self.top_frame = top_frame
      self.update_labels = update_labels

      self.key = backend.load_key()  #Load decryption key
      self.groups = self.load_groups() # Load groups from a data source
      self.setup_dropdown() # Set up the dropdown menu for group selection
      ToolTip(self.groups_dropdown, text="Groups") # Add tooltip for the dropdown

   # Function to setup groups dropdown
   def setup_dropdown(self):
      # Create a new list with truncated group names
      truncated_groups = [group if len(group) <= 12 else group[:12] + "..." for group in self.groups]

      # Create the dropdown menu for group selection
      self.groups_dropdown = CTkOptionMenu(self.top_frame, command=self.group_selection, values=truncated_groups, height=35, font=("Helvetica", 14), fg_color="white", text_color="black", dropdown_font=("Helvetica", 14), dropdown_text_color="black", corner_radius=2, button_color="red", button_hover_color="#EE4B2B", dropdown_fg_color="white", dropdown_hover_color="red", hover=True, anchor="center", state="normal")
      # Place the dropdown in the specified location
      self.groups_dropdown.place(relx=0.72, rely=0.5, anchor="center")
      self.groups_dropdown.set("All Accounts") # Default selection
      self.groups_dropdown.bind("<Button-3>", self.delete_group) # Bind right-click for deletion

   # Function to return selected groups
   def get_group(self):
      # Return the currently selected group from the dropdown
      return self.groups_dropdown.get()

   # Function to handle group selection and perform actions based on the selected group
   def group_selection(self, selected):
      if selected == "Add Group":
         self.add_group() # Call method to add a new group
         self.groups_dropdown.set("All Accounts") # Reset to default after adding
      elif selected == "All Accounts":
         self.update_labels() # Update labels to show all accounts
      else:
         # Filter accounts based on the selected group and update labels
         filtered_accounts = {name: data for name, data in self.accounts.items() if data['group'] == selected}
         self.update_labels(filtered_accounts)

   # Function to add a group
   def add_group(self):
      # Prompt user for a new group name using an input dialog
      group_entry = CTkInputDialog(text="Create New Group", font=("Helvetica", 16, "bold"), title="Create New Group", button_fg_color="white", button_hover_color="red", button_text_color="black", entry_border_color="black")
      # Set an icon for the dialog after a short delay
      group_entry.after(250, lambda: group_entry.iconbitmap('images/VerifyVaultLogo.ico'))
      group_name = group_entry.get_input()

      # Validate the group name
      if group_name is None:
         return  # User closed the dialog without input

      group_name = group_name.strip()
      if group_name == "" or group_name.lower() == "none":
         messagebox.showerror("Error", "The Group Name you set is invalid.")
         return

      # Ensure the group name is unique
      original_group_name = group_name
      count = 1
      while group_name in self.groups:
            group_name = f"{original_group_name} ({count})"
            count += 1

      # Update the group list, ensuring "All Accounts" and "Add Group" are correctly positioned
      self.groups = [group for group in self.groups if group not in ["All Accounts", "Add Group"]]
      self.groups.append(group_name)
      self.groups.sort()
      self.groups = ["All Accounts"] + self.groups + ["Add Group"]

      # Update the dropdown menu with the new list of groups
      self.groups_dropdown.configure(values=[group if len(group) <= 12 else group[:12] + "..." for group in self.groups])
      self.save_groups() # Save the updated groups to persistent storage
      messagebox.showinfo("Success", f"Group '{group_name}' created successfully")

   # Function to initialize groups and reset all accounts to "None"
   def create_groups(self):
      with open('groups.json', 'wb') as file:
         # Create an initial group list and encrypt it
         encrypted_data = backend.encrypt_message(json.dumps(["All Accounts", "Add Group"]), backend.load_groups_key())
         file.write(encrypted_data)

      # Reset all accounts to have no associated group
      for name, info in self.accounts.items():
         info['group'] = "None"
      backend.save_accounts(self.accounts, self.key)
      print("All accounts' groups have been reset to 'None'")
      backend.mark_file_hidden("groups.json")

   # Function to load existing groups from a file
   def load_groups(self):
      # Check if the groups file exists; create it if not
      if not os.path.exists('groups.json'):
         self.create_groups()
         return ["All Accounts", "Add Group"]
      else:
         backend.unhide_file("groups.json")
         key = backend.load_groups_key()

         try:
            # Read and decrypt the group data
            with open('groups.json', 'rb') as file:
               encrypted_data = file.read()
               decrypted_data = backend.decrypt_message(encrypted_data, key)
               groups = json.loads(decrypted_data) # Return the list of groups
               return [group if len(group) <= 12 else group[:12] + "..." for group in groups]
         except json.JSONDecodeError:
            return ["All Accounts", "Add Group"] # Default return on error
         finally:
            backend.mark_file_hidden("groups.json") # Hide the file after access

   # Function to save the current list of groups to a file
   def save_groups(self):
      backend.unhide_file("groups.json") # Make the file accessible
      gkey = backend.load_groups_key() # Load the encryption key
      encrypted_data = backend.encrypt_message(json.dumps(self.groups), gkey) # Encrypt the group data

      # Write the encrypted data to the file
      with open('groups.json', 'wb') as file:
         file.write(encrypted_data)

      backend.mark_file_hidden("groups.json") # Hide the file again after saving

   # Function to delete a selected group
   def delete_group(self, event=None):
      selected_group = self.groups_dropdown.get() # Get the currently selected group

      # Prevent deletion of the default group
      if selected_group == "All Accounts":
         messagebox.showerror("Error", "You cannot delete 'All Accounts'.")
         return

      # Confirm deletion from the user
      if messagebox.askyesno("Confirm", f"Are you sure you want to delete the group '{selected_group}'?"):
         if selected_group in self.groups:
            self.groups.remove(selected_group) # Remove the selected group
            
            # Ensure at least the default group remains
            if not self.groups:
               self.groups.append("All Accounts")      

            self.save_groups() # Save the updated groups list
            self.groups_dropdown.configure(values=[group if len(group) <= 12 else group[:12] + "..." for group in self.groups]) # Update dropdown options
                        
            # Set the dropdown to the first available group or reset to default
            if self.groups:
               self.groups_dropdown.set(self.groups[0])
            else:
               self.groups_dropdown.set("All Accounts")

            self.update_labels() # Refresh labels to reflect changes
         else:
               messagebox.showerror("Error", "Group not found.") # Show error if the group does not exist

