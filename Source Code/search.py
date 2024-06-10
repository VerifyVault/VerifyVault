import tkinter as tk
import backend
from labels import LabelsManager

class SearchFunctions:
    def __init__(self, master, search_var, update_labels, top_button_frame, key):
        #Configuring search_functions constructor
        self.master = master
        self.search_var = search_var
        self.update_labels = update_labels
        self.top_button_frame = top_button_frame
        self.accounts = backend.load_accounts(key)

        #Configures search bar
        self.search_entry = tk.Entry(self.top_button_frame, textvariable=self.search_var, width=60, bd=7,
                                     highlightthickness=0)
        self.search_entry.pack(side="right", padx=5, pady=10)
        self.search_entry.insert(0, "Search...")
        self.search_entry.bind("<FocusIn>", lambda event: self.remove_placeholder(event))
        self.search_entry.bind("<KeyRelease>", self.search_accounts)

        self.master.bind("<Button-1>", self.reset_search_bar)
        self.update_labels = update_labels
        self.accounts = backend.load_accounts(key)
        
    #Removes search bar placeholder
    def remove_placeholder(self, event):
        if self.search_var.get() == "Search...":
            self.search_var.set("")

    #Search funtionality
    def search_accounts(self, event):
        query = self.search_var.get().lower()
        if query and query != "search...":
            filtered_accounts = {name: info for name, info in self.accounts.items() 
                                 if query in name.lower() and not info.get("deleted")}
            self.update_labels(filtered_accounts)
        else:
            self.update_labels()

    #Adds placeholder back
    def reset_search_bar(self, event):
        if not self.search_var.get():
            self.search_var.set("Search...")
            self.master.focus_set()

    #Goes back to main menu
    def exit_search_mode(self):
        self.search_var.set("")
        self.update_labels(self.accounts)

    #Dsiplays relevant accounts
    def update_accounts(self, updated_accounts):
        self.accounts = updated_accounts
        query = self.search_var.get().lower()

        if query and query != "search...":
            filtered_accounts = {name: info for name, info in updated_accounts.items() 
                                if query in name.lower() and not info.get("deleted")}
            self.update_labels(filtered_accounts)
        else:
            self.update_labels(updated_accounts)
