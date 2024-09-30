from customtkinter import *
from groups import GroupsFunctions
from account_info import AccountInfoFunctions
from ttkbootstrap.tooltip import ToolTip
import backend

class DisplayFunctions:
   def __init__(self, master, groups, accounts, top_frame, left_frame, right_frame):
      # Initialize display functions and UI components
      self.master = master
      self.groups = groups
      self.accounts = accounts
      self.top_frame = top_frame
      self.left_frame = left_frame
      self.right_frame = right_frame
      
      self.key = backend.load_key() # Load encryption key

      self.current_page = 1  # Track the current page of accounts
      self.acc_per_page = 20  # Number of accounts to display per page

      # Initialize account and group management functionalities
      self.account_info = AccountInfoFunctions(master, groups, accounts, right_frame, self.update_labels)
      self.groups_function = GroupsFunctions(master, accounts, top_frame, self.update_labels)
   
   # Function to update the displayed accounts
   def update_labels(self, accounts=None):
      # Load accounts if none are provided
      if accounts is None:
         accounts = backend.load_accounts(self.key)
         
      self.accounts = dict(sorted(accounts.items()))  # Sort accounts

      # Clear existing widgets in the left frame
      for widget in self.left_frame.winfo_children():
         widget.destroy()

      # Display message if no accounts are found
      if not self.accounts:
         no_accounts_label = CTkLabel(self.left_frame, text="❌ No Accounts Found", font=("Helvetica", 40, "bold"), corner_radius=2)
         no_accounts_label.place(relx=0.5, rely=0.4, anchor="center")
         return

      # Calculate the number of pages needed
      num_pages = (len(self.accounts) + self.acc_per_page - 1) // self.acc_per_page
      num_pages = max(num_pages, 1)

      # Ensure the current page is valid
      if self.current_page > num_pages:
         self.current_page = num_pages

      # Determine the range of accounts to display  
      start_index = (self.current_page - 1) * self.acc_per_page
      end_index = min(start_index + self.acc_per_page, len(self.accounts))

      x_offset = 0.01  # Horizontal positioning of buttons
      button_width = 0.2  # Width of each account button
      rely = 0.1  # Vertical position for the first row
      row_height = 0.2  # Height of each row

      # Display account buttons
      for name, info in list(self.accounts.items())[start_index:end_index]:
         if info.get("key") and info.get("secret"):
            display_text = f"{name[:10]}..." if len(name) > 10 else name # Text for the button

            # Create and place the button for the account
            button = CTkButton(self.left_frame, text=display_text, command=lambda name=name: self.account_info.click_account(name), fg_color="white", hover_color="red", text_color="black", width=145, height=100, border_width=2, corner_radius=2, font=("Helvetica", 20), cursor="hand2")
            button.place(relx=x_offset, rely=rely)
            x_offset += button_width # Move to the next button's position
            
            # Move to the next row if the row width exceeds limits
            if x_offset + button_width > 1.2:
               x_offset = 0.01
               rely += row_height

      # Functions to display page #'s and buttons
      def prev_page():
         if self.current_page > 1:
            self.current_page -= 1
            self.update_labels()
      def next_page():
         if self.current_page < num_pages:
            self.current_page += 1
            self.update_labels()

      # Remove navigation buttons if they already exist
      for widget in self.left_frame.winfo_children():
         if isinstance(widget, CTkButton) and widget.cget('text') in ("🢀", "🢂"):
               widget.destroy()

      # Create previous page button if not on the first page
      if self.current_page > 1:
         prev_button = CTkButton(self.left_frame, text="🢀", command=prev_page, fg_color="white", hover_color="red", text_color="black", width=100, height=40, border_width=2, font=("Helvetica", 25), cursor="hand2")
         prev_button.place(relx=0.1, rely=0.93, anchor="center")
         ToolTip(prev_button, text="Previous") # Tooltip for previous button

      # Create next page button if not on the last page
      if self.current_page < num_pages:
         next_button = CTkButton(self.left_frame, text="🢂", command=next_page, fg_color="white", hover_color="red", text_color="black", width=100, height=40, border_width=2, font=("Helvetica", 25), cursor="hand2")
         next_button.place(relx=0.9, rely=0.93, anchor="center")
         ToolTip(next_button, text="Next") # Tooltip for next button

      # Display current page information
      page_indicator = CTkLabel(self.left_frame, text=f"Page {self.current_page}/{num_pages}  - Number of Accounts: {len(self.accounts)}", font=("Helvetica", 14, "bold"), corner_radius=2)
      page_indicator.place(relx=0.5, rely=0.93, anchor="center")
