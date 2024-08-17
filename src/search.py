from customtkinter import *
from labels import LabelsManager
import backend

class SearchFunctions:
    def __init__(self, master, search_var, update_labels, top_button_frame, key):
        # Configures search_functions constructor
        self.master = master
        self.search_var = search_var
        self.update_labels = update_labels
        self.top_button_frame = top_button_frame
        self.accounts = backend.load_accounts(key)

        # Configures search bar
        self.search_entry = CTkEntry(self.top_button_frame, width=550, height=40, corner_radius=2, textvariable=self.search_var, placeholder_text="🔍 Search Accounts", border_color="black")
        self.search_entry.place(relx=0.43, rely=0.5, anchor="center")
        self.search_entry.bind("<KeyRelease>", self.search_accounts)

    # Function to set the search funtionality
    def search_accounts(self, event):
        query = self.search_var.get().lower()
        if query:
            filtered_accounts = {name: info for name, info in self.accounts.items()
                                 if query in name.lower() and not info.get("deleted")}
        else:
            filtered_accounts = self.accounts
        self.update_labels(filtered_accounts)

    # Function to return to main menu
    def exit_search_mode(self):
        self.search_var.set("")
        self.update_labels(self.accounts)

    # Function to display relevant accounts
    def update_accounts(self, updated_accounts):
        self.accounts = updated_accounts
        query = self.search_var.get().lower()

        if query and query != "search...":
            filtered_accounts = {name: info for name, info in updated_accounts.items()
                                if query in name.lower() and not info.get("deleted")}
        else:
            filtered_accounts = updated_accounts
        self.update_labels(filtered_accounts)
