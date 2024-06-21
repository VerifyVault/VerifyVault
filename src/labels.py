import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import backend, pyotp, time, pyperclip
from edit_account_tab import EditAccount
from backend import load_key

class LabelsManager:
    def __init__(self, master, canvas, secframe, accounts, scrollbar, import_data, notifications, on_mousewheel, accounts_frame, add_account_tab, edit_account_tab):
        # Initial labels configurations
        self.master = master
        self.canvas = canvas
        self.secframe = secframe
        self.accounts = accounts
        self.scrollbar = scrollbar
        self.import_data = import_data
        self.notifications = notifications
        self.on_mousewheel = on_mousewheel
        self.accounts_frame = accounts_frame
        self.add_account_tab = add_account_tab
        self.edit_account_tab = edit_account_tab
        self.key = load_key()
        self.edit_window_open = False
        self.edit_name_window_open = False

    # Retrievs accounts
    def get_accounts(self):
        return self.accounts
    # Displays TOTP Copied notification
    def copy_totp(self, event, totp_text):
        pyperclip.copy(totp_text)
        self.notifications.show_notification("TOTP code copied to clipboard!")

    # Account display formatting
    def update_labels(self, accounts=None):
        if accounts is None:
            key = backend.load_key()
            accounts = backend.load_accounts(key)
        for widget in self.accounts_frame.winfo_children():
            widget.destroy()
            
        if not accounts:
            #If there are no accounts, "No Accounts Found" will be displayed
            no_accounts_label = tk.Label(self.accounts_frame, text="No Accounts Found", font=("Helvetica", 18), bg="white")
            no_accounts_label.pack(pady=(150, 20), padx=(85, 150))
            add_account_button = ttk.Button(self.accounts_frame, text="Add Account", command=self.add_account_tab.add_account, style='Red.TButton')
            add_account_button.pack(pady=(0, 10), padx=(85, 150))
            import_button = ttk.Button(self.accounts_frame, text="Import Accounts", command=self.import_data, style='Red.TButton')
            import_button.pack(pady=(0, 20), padx=(85, 150))

            self.scrollbar.config(command=None)
            self.canvas.unbind_all("<MouseWheel>")
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
            self.scrollbar.pack_forget()
            self.canvas.config(yscrollcommand=None)
        else:
            #Accounts are printed here
            if len(accounts) < 6:
                self.scrollbar.pack_forget()
                self.canvas.config(yscrollcommand=None)
            else:
                self.scrollbar.pack(side="right", fill="y")
                self.canvas.config(yscrollcommand=self.scrollbar.set)

            self.totp_labels = {}

            # Handles clicking an account
            def click_account(name):
                account_info = self.accounts[name]
                secret = account_info['secret']
                totp = pyotp.TOTP(secret)

                # Configures Account Details window
                popup_window = tk.Toplevel(self.master)
                popup_window.title(f"Account Details - {name}")
                popup_window.geometry("300x200")
                popup_window.resizable(False, False)
                popup_window.configure(bg="white")

                account_name_label = tk.Label(popup_window, text=f"Account Name: {name}", font=("Helvetica", 12), bg="white")
                account_name_label.pack(pady=5)
                timer_label = tk.Label(popup_window, text="", font=("Helvetica", 16), bg="white")
                timer_label.pack()
                totp_label = tk.Label(popup_window, text=f"TOTP: {totp.now()}", font=("Helvetica", 12), bg="white")
                totp_label.pack()

                copy_button = ttk.Button(popup_window, text="Copy TOTP", command=lambda: self.copy_totp(None, totp.now()), style='Red.TButton')
                copy_button.pack(pady=5)
                edit_button = ttk.Button(popup_window, text="Edit", command=lambda: self.edit_account_tab.edit_account(name), style='Red.TButton')  # Call edit_account method from EditAccount instance
                edit_button.pack(pady=5)

                # Updates TOTP Code and Timer
                def update_timer():
                    remaining_time = 30 - (time.time() % 30)
                    timer_label.config(text=f"Time until next TOTP: {int(remaining_time)}s")
                    popup_window.after(1000, update_timer)
                    totp_label.config(text=f"TOTP: {totp.now()}")

                update_timer()

            # Handles mouse enter and leave events
            def on_enter(event):
                account_frame.config(cursor="watch")
            def on_leave(event):
                account_frame.config(cursor="")

            # Displays accounts
            for name, info in accounts.items():
                if not name.startswith("C:/") and info.get("key") and info.get("secret"):
                    account_frame = tk.Frame(self.accounts_frame, relief="ridge", bg="white", highlightbackground="black", highlightthickness=2)
                    account_frame.pack(pady=10, padx=(0, 10), fill="x", anchor="w")

                    display_text = f"Name: {name}"
                    label = tk.Label(account_frame, text=display_text, font=("Helvetica", 9), bg="white", width=50)
                    label.pack(side="left", fill="x", padx=10, pady=10)

                    label.bind("<Enter>", lambda event, frame=account_frame: frame.config(cursor="hand2"))
                    label.bind("<Leave>", lambda event, frame=account_frame: frame.config(cursor=""))
                    label.bind("<Button-1>", lambda event, name=name: click_account(name))

            # Sets frames/scrollbar
            self.secframe.update_idletasks()
            self.canvas.config(scrollregion=self.canvas.bbox("all"))

            self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
            self.canvas.bind_all("<Button-4>", self.on_mousewheel)
            self.canvas.bind_all("<Button-5>", self.on_mousewheel)

            for child in self.accounts_frame.winfo_children():
                child.pack_configure(anchor="n", fill="x")

            if len(accounts) <= 8:
                self.scrollbar.config(command=None)
                self.canvas.unbind_all("<MouseWheel>")
                self.canvas.unbind_all("<Button-4>")
                self.canvas.unbind_all("<Button-5>")
                self.scrollbar.unbind_all("<MouseWheel>")
                self.scrollbar.unbind_all("<Button-4>")
                self.scrollbar.unbind_all("<Button-5>")
