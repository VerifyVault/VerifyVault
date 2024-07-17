import tkinter as tk
from tkinter import ttk, messagebox
from search import SearchFunctions
from notifications import NotificationManager
from backend import load_accounts, save_accounts, load_key
import backend, json, os, time, datetime

class RecycleBinFunctions:
   # Initial recycle_bin configurations
   def __init__(self, master, accounts, notifications):
      self.master = master
      self.key = load_key()
      self.accounts = accounts
      self.notifications = notifications
      self.deleted_accounts = {}
      self.load_deleted_accounts()
      self.active_window = None

   # Function to close active window
   def close_active_window(self):
      if self.active_window:
            self.active_window.destroy()

   # Manage Recycle Bin Function
   def manage_recycle_bin(self):
      self.close_active_window()
      recycle_bin_window = tk.Toplevel(self.master)
      recycle_bin_window.title("Recycle Bin")
      recycle_bin_window.geometry("500x300")
      recycle_bin_window.resizable(False, False)
      recycle_bin_window.configure(bg="white")
      recycle_bin_window.iconbitmap('VerifyVaultLogo.ico')

      self.update_recycle_bin(recycle_bin_window)
      self.active_window = recycle_bin_window

   # Functions to load/save the accounts that have been marked deleted
   def load_deleted_accounts(self):
      try:
         with open('deleted.json', 'r') as f:
               self.deleted_accounts = json.load(f)
      except FileNotFoundError:
         self.deleted_accounts = {}
   def save_deleted_accounts(self):
      with open('deleted.json', 'w') as f:
         json.dump(self.deleted_accounts, f, indent=4)

   # Function to set/update the recycle bin window
   def update_recycle_bin(self, recycle_bin_window):
      if isinstance(recycle_bin_window, (tk.Toplevel, tk.Frame)):
         for widget in recycle_bin_window.winfo_children():
               widget.destroy()

         recycle_bin_frame = tk.Frame(recycle_bin_window, bg="white")
         recycle_bin_frame.pack(fill="both", expand=True)

         recycle_bin_label = tk.Label(recycle_bin_frame, text="Recycle Bin", font=("Helvetica", 16), bg="white")
         recycle_bin_label.pack(pady=(10, 5))

         button_frame = tk.Frame(recycle_bin_frame, bg="white")
         button_frame.pack(pady=5)

         clear_all_button = ttk.Button(button_frame, text="Clear All", command=self.clear_all_accounts)
         clear_all_button.pack(side=tk.LEFT, padx=5)

         restore_all_button = ttk.Button(button_frame, text="Restore All", command=self.restore_all_accounts)
         restore_all_button.pack(side=tk.LEFT, padx=5)

         search_frame = tk.Frame(recycle_bin_frame, bg="white")
         search_frame.pack(pady=5)

         search_entry = tk.Entry(search_frame, width=30, bd=5, highlightthickness=0)
         search_entry.pack(side=tk.LEFT, padx=5)
         search_entry.insert(0, "Search...")

         # Functions to configure search bar
         def on_search_focus_in(event):
               if search_entry.get() == "Search...":
                  search_entry.delete(0, tk.END)
                  search_entry.config(fg="black")
         def on_search_focus_out(event):
               if search_entry.get() == "":
                  search_entry.insert(0, "Search...")
                  search_entry.config(fg="black") 
         def on_search_update(event=None):
               search_term = search_entry.get().strip().lower()
               if search_term == "search...":
                  self.load_deleted_accounts = self.deleted_accounts.copy()
               else:
                  self.load_deleted_accounts = {name: info for name, info in self.deleted_accounts.items() if search_term in name.lower()}
               update_account_display()

         # Function to display accounts in recycle bin
         def update_account_display():
               for widget in recycle_bin_frame.winfo_children():
                  if widget not in [recycle_bin_label, button_frame, search_frame]:
                     widget.destroy()

               if not self.load_deleted_accounts:
                  no_accounts_label = tk.Label(recycle_bin_frame, text="No Accounts Found", bg="white")
                  no_accounts_label.pack(pady=20)
               else:
                  if len(self.load_deleted_accounts) >= 4:
                     recycle_bin_canvas = tk.Canvas(recycle_bin_frame, bg="white")
                     recycle_bin_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                     recycle_bin_scrollbar = tk.Scrollbar(recycle_bin_frame, orient=tk.VERTICAL, command=recycle_bin_canvas.yview)
                     recycle_bin_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

                     recycle_bin_canvas.configure(yscrollcommand=recycle_bin_scrollbar.set)
                     recycle_bin_canvas.bind("<Configure>", lambda e: recycle_bin_canvas.configure(scrollregion=recycle_bin_canvas.bbox("all")))

                     recycle_bin_scrollable_frame = tk.Frame(recycle_bin_canvas, bg="white")
                     recycle_bin_canvas.create_window((0, 0), window=recycle_bin_scrollable_frame, anchor=tk.NW)

                     for account_name in self.load_deleted_accounts:
                           account_frame = tk.Frame(recycle_bin_scrollable_frame, relief="ridge", bg="white", highlightbackground="black", highlightthickness=2)
                           account_frame.pack(fill="x", padx=50, pady=5)
                           account_label = tk.Label(account_frame, text=f"Account: {account_name}", bg="white")
                           account_label.pack(side=tk.LEFT, padx=10)

                           restore_button = ttk.Button(account_frame, text="Restore", command=lambda name=account_name: self.restore_account(name))
                           restore_button.pack(side=tk.RIGHT, padx=10)
                           permanent_delete_button = ttk.Button(account_frame, text="Permanently Delete", command=lambda name=account_name: self.permanent_delete_account(name))
                           permanent_delete_button.pack(side=tk.RIGHT, padx=10)

                           recycle_bin_canvas.update_idletasks()
                           recycle_bin_canvas.configure(scrollregion=recycle_bin_canvas.bbox("all"))

                     recycle_bin_canvas.bind_all("<MouseWheel>", lambda event: recycle_bin_canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
                  else:
                     for account_name in self.load_deleted_accounts:
                           account_frame = tk.Frame(recycle_bin_frame, relief="ridge", bg="white", highlightbackground="black", highlightthickness=2)
                           account_frame.pack(fill="x", padx=50, pady=5)
                           account_label = tk.Label(account_frame, text=f"Account: {account_name}", bg="white")
                           account_label.pack(side=tk.LEFT, padx=10)

                           restore_button = ttk.Button(account_frame, text="Restore", command=lambda name=account_name: self.restore_account(name))
                           restore_button.pack(side=tk.RIGHT, padx=10)
                           permanent_delete_button = ttk.Button(account_frame, text="Permanently Delete", command=lambda name=account_name: self.permanent_delete_account(name))
                           permanent_delete_button.pack(side=tk.RIGHT, padx=10)
         
         # Function that voids search bar selection
         def on_window_click(event):
               if not isinstance(event.widget, tk.Entry) or event.widget != search_entry:
                  search_entry.selection_clear()
                  search_entry.config(fg="black")
                  recycle_bin_window.focus_set()

         search_entry.bind("<FocusIn>", on_search_focus_in)
         search_entry.bind("<FocusOut>", on_search_focus_out)
         search_entry.bind("<KeyRelease>", on_search_update)
         recycle_bin_window.bind("<Button-1>", on_window_click)

         self.load_deleted_accounts = self.deleted_accounts.copy()
         update_account_display()

         # Function to close recycle bin
         def on_recycle_bin_close():
               from gui import TwoFactorAppGUI
               recycle_bin_window.destroy()
               self.master.destroy()
               TwoFactorAppGUI(tk.Tk(), self.key)

         recycle_bin_window.protocol("WM_DELETE_WINDOW", on_recycle_bin_close)
      else:
         messagebox.showerror("Window Type Error", "Unexpected window type encountered.")
      self.save_deleted_accounts()

   # FUnction to restore all accounts
   def restore_all_accounts(self):
      from gui import TwoFactorAppGUI
      if self.deleted_accounts:
         restored_accounts = []
         for account_name in list(self.deleted_accounts.keys()):
               self.restore_account(account_name)
               restored_accounts.append(account_name)

         if restored_accounts:
               restored_accounts_message = f"All accounts ({', '.join(restored_accounts)}) have been restored."
               messagebox.showinfo("All Accounts Restored", restored_accounts_message)
               self.update_recycle_bin(self.master.winfo_children()[1])
      else:
         messagebox.showinfo("No Accounts to Restore", "There are no accounts to restore.")

   # Function to clear all accounts
   def clear_all_accounts(self):
      confirmation = messagebox.askyesnocancel("Confirm Clear All", "Are you sure you want to permanently delete all accounts?")
      if confirmation is True:
         if not self.deleted_accounts:
               messagebox.showinfo("No Accounts to Delete", "There are no accounts to delete.")
         else:
               self.deleted_accounts = {}
               self.save_deleted_accounts()
               messagebox.showinfo("All Accounts Cleared", "All accounts have been permanently deleted.")
               self.update_recycle_bin(self.master.winfo_children()[1])

   # Function to automatically clear the recycle bin every month
   def monthly_cleanup(self):
      today = datetime.today()
      if today.day == 1:
         self.clear_recycle_bin()
   def clear_recycle_bin(self):
      self.deleted_accounts = {}
      self.save_deleted_accounts()
      messagebox.showinfo("Recycle Bin Cleared", "Recycle Bin has been cleared for the new month.")
      self.update_recycle_bin(self.master.winfo_children()[1])

   # Functions to delete/restore the account
   def mark_for_deletion(self, account_name):
      current_time = time.time()
      self.deleted_accounts[account_name] = current_time
   def restore_account(self, account_name):
      if account_name in self.deleted_accounts:
         try:
               existing_accounts = load_accounts(self.key)
               account_info = self.deleted_accounts[account_name]

               existing_accounts[account_name] = {
                  'secret': account_info['secret'],
                  'key': account_info['key'],
                  'deleted': False
               }
               save_accounts(existing_accounts, self.key)

               del self.deleted_accounts[account_name]
               self.save_deleted_accounts()
               self.update_recycle_bin(self.master.winfo_children()[1])

               self.notifications.show_notification("Account(s) restored successfully!")
               self.manage_recycle_bin()
         except Exception as e:
               messagebox.showerror("Error", f"Error restoring account: {str(e)}")
      else:
         messagebox.showerror("Account Not Found", f"Account '{account_name}' not found in deleted accounts.")

   # Function to permanently delete the account
   def permanent_delete_account(self, account_name):
      confirmation = messagebox.askyesnocancel("Confirm Permanent Delete", f"Are you sure you want to permanently delete account '{account_name}'?")
      if confirmation is True:
         del self.deleted_accounts[account_name]
         self.save_deleted_accounts()
         self.update_recycle_bin(self.master.winfo_children()[1])
         messagebox.showinfo("Permanent Delete", f"Account '{account_name}' permanently deleted.")
         self.manage_recycle_bin()