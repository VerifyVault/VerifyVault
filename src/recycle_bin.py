import tkinter as tk
from customtkinter import *
from tkinter import messagebox
from backend import load_accounts, save_accounts, load_key
import json, os, time, datetime

class RecycleBinFunctions:
    def __init__(self, master, accounts, update_labels, right_frame):
        # Initial recycle bin configurations
        self.master = master
        self.accounts = accounts
        self.update_labels = update_labels
        self.right_frame = right_frame

        self.key = load_key()
        self.deleted_accounts = {}
        self.load_deleted_accounts()

        self.recycle_frame = None
        self.search_var = tk.StringVar()
        self.selected_accounts = set()

        self.current_page = 1
        self.accounts_per_page = 5

    # Function to configure recycle bin frame
    def manage_recycle_bin(self):
        if self.recycle_frame is None:
            self.recycle_frame = CTkFrame(self.right_frame, width=600, height=700)
            self.recycle_frame.place(relx=0.61, rely=0, anchor="n")

            def close_frame():
                self.recycle_frame.destroy()
                self.recycle_frame = None

            x_button = CTkButton(self.recycle_frame, command=close_frame, text="❌", fg_color="white", border_color="black", text_color="black", hover_color="red", border_width=2, width=50, height=20, cursor="hand2")
            x_button.place(relx=0.8, rely=0.03, anchor="ne")

            title_label = CTkLabel(self.recycle_frame, text="Recycle Bin", font=("Helvetica", 30, "bold"))
            title_label.place(relx=0.42, rely=0.1, anchor="center")

            search_entry = CTkEntry(self.recycle_frame, width=300, height=40, textvariable=self.search_var, placeholder_text="🔍 Search Accounts", border_color="black")
            search_entry.place(relx=0.42, rely=0.17, anchor="center")
            search_entry.bind("<KeyRelease>", self.search_deleted_accounts)

            restore_all = CTkButton(self.recycle_frame, text="Restore All", fg_color="white", hover_color="red", text_color="black", width=100, height=40, border_width=2, font=("Helvetica", 16, "bold"), cursor='hand2', command=self.restore_all_accounts)
            restore_all.place(relx=0.32, rely=0.25, anchor="center")
            clear_button = CTkButton(self.recycle_frame, text="Clear All", fg_color="white", hover_color="red", text_color="black", width=100, height=40, border_width=2, font=("Helvetica", 16, "bold"), cursor='hand2', command=self.clear_all_accounts)
            clear_button.place(relx=0.52, rely=0.25, anchor="center")

        self.populate_recycle_bin()

    # Function to display deleted accounts
    def populate_recycle_bin(self):
        if self.recycle_frame is None:
            self.manage_recycle_bin()
            
        for widget in self.recycle_frame.winfo_children():
            if isinstance(widget, CTkFrame) and widget not in [self.recycle_frame.winfo_children()[0], self.recycle_frame.winfo_children()[1]]:
                widget.destroy()

        query = self.search_var.get().lower()
        filtered_accounts = {name: deletion_time for name, deletion_time in self.deleted_accounts.items()
                             if query in name.lower()}

        if not self.deleted_accounts:
            no_account_label = CTkLabel(self.recycle_frame, text="❌ No Accounts Found", font=("Helvetica", 20, "bold"), corner_radius=2)
            no_account_label.place(relx=0.42, rely=0.4, anchor="center")

        else:
            num_pages = (len(filtered_accounts) + self.accounts_per_page - 1) // self.accounts_per_page
            start_index = (self.current_page - 1) * self.accounts_per_page
            end_index = min(start_index + self.accounts_per_page, len(filtered_accounts))

            filtered_accounts_list = list(filtered_accounts.items())[start_index:end_index]

            spacing = 0.05
            for index, (account_name, deletion_time) in enumerate(filtered_accounts_list):
                account_frame = CTkFrame(self.recycle_frame)
                account_frame.place(relx=0.42, rely=0.35 + index * (spacing + 0.05), anchor="center")
                account_label = CTkLabel(account_frame, text=account_name, width=250, height=50, anchor="w")
                account_label.pack(side="left", padx=10)

                restore_button = CTkButton(account_frame, text="Restore", fg_color="white", hover_color="red", text_color="black", width=80, height=30, border_width=2, font=("Helvetica", 12, "bold"), cursor='hand2', command=lambda name=account_name: self.restore_account(name))
                restore_button.pack(side="left", padx=5)
                delete_button = CTkButton(account_frame, text="Delete", fg_color="red", hover_color="white", text_color="black", width=80, height=30, border_width=2, font=("Helvetica", 12, "bold"), cursor='hand2', command=lambda name=account_name: self.permanent_delete_account(name))
                delete_button.pack(side="left", padx=5)

            self.add_pagination_controls(num_pages)

    # Function to display page number/buttons
    def add_pagination_controls(self, num_pages):
        for widget in self.recycle_frame.winfo_children():
            if isinstance(widget, CTkButton) and widget.cget('text') in ("Previous", "Next"):
                widget.destroy()

        def prev_page():
            if self.current_page > 1:
                self.current_page -= 1
                self.populate_recycle_bin()

        def next_page():
            if self.current_page < num_pages:
                self.current_page += 1
                self.populate_recycle_bin()

        if self.current_page > 1:
            prev_button = CTkButton(self.recycle_frame, text="Previous", command=prev_page, fg_color="white", hover_color="red", text_color="black", width=100, height=40, border_width=2, font=("Helvetica", 14, "bold"), cursor="hand2")
            prev_button.place(relx=0.15, rely=0.85, anchor="center")

        if self.current_page < num_pages:
            next_button = CTkButton(self.recycle_frame, text="Next", command=next_page, fg_color="white", hover_color="red", text_color="black", width=100, height=40, border_width=2, font=("Helvetica", 14, "bold"), cursor="hand2")
            next_button.place(relx=0.7, rely=0.85, anchor="center")

        page_indicator = CTkLabel(self.recycle_frame, text=f"Page {self.current_page}/{num_pages}", font=("Helvetica", 14, "bold"))
        page_indicator.place(relx=0.4, rely=0.85, anchor="center")

    #Functions to search, load, and save deleted accounts
    def search_deleted_accounts(self, event):
        self.populate_recycle_bin()
    def load_deleted_accounts(self):
        try:
            with open('deleted.json', 'r') as f:
                self.deleted_accounts = json.load(f)
        except FileNotFoundError:
            self.deleted_accounts = {}
    def save_deleted_accounts(self):
        with open('deleted.json', 'w') as f:
            json.dump(self.deleted_accounts, f, indent=4)

    # Fucntions to restore all accounts
    def restore_all_accounts(self):
        confirmation = messagebox.askyesno("Confirm Restore All", "No accounts are selected. Do you want to restore all accounts?")
        if confirmation:
            self.restore_all_accounts_from_list()
    def restore_all_accounts_from_list(self):
        if self.deleted_accounts:
            for account_name in list(self.deleted_accounts):
                self.restore_account(account_name)
            messagebox.showinfo("All Accounts Restored", "All accounts have been restored.")
            self.populate_recycle_bin()
            self.update_labels()
        else:
            messagebox.showinfo("No Accounts to Restore", "There are no accounts to restore.")

    # Functons to delete all accounts
    def clear_all_accounts(self):
        confirmation = messagebox.askyesno("Confirm Clear All", "No accounts are selected. Do you want to permanently delete all accounts?")
        if confirmation:
            self.clear_all_accounts_from_list()
    def clear_all_accounts_from_list(self):
        if self.deleted_accounts:
            self.deleted_accounts = {}
            self.save_deleted_accounts()
            messagebox.showinfo("All Accounts Cleared", "All accounts have been permanently deleted.")
            self.populate_recycle_bin()
        else:
            messagebox.showinfo("No Accounts to Delete", "There are no accounts to delete.")
            
    # Function to restore individual accounts
    def restore_account(self, account_name):
        if account_name in self.deleted_accounts:
            try:
                existing_accounts = load_accounts(self.key)
                account_info = self.deleted_accounts[account_name]

                existing_accounts[account_name] = {
                    'secret': account_info.get('secret', ''),
                    'key': account_info.get('key', ''),
                    'deleted': False
                }
                save_accounts(existing_accounts, self.key)

                del self.deleted_accounts[account_name]
                self.save_deleted_accounts()
                self.populate_recycle_bin()
                self.update_labels()
            except Exception as e:
                messagebox.showerror("Error", f"Error restoring account: {str(e)}")
        else:
            messagebox.showerror("Account Not Found", f"Account '{account_name}' not found in deleted accounts.")

    # Function to delete individual account
    def permanent_delete_account(self, account_name):
        confirm_delete = messagebox.askyesno("Confirm", "Are you sure you want to delete this account permanently?")
        if confirm_delete:
            if account_name in self.deleted_accounts:
                del self.deleted_accounts[account_name]
                self.save_deleted_accounts()
                self.populate_recycle_bin()

                messagebox.showinfo("Success", "Account deleted sucessfully.")
            else:
                messagebox.showerror("Account Not Found", f"Account '{account_name}' not found in deleted accounts.")

