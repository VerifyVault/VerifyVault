import tkinter as tk
import tkinter.ttk as ttk
from edit_account_tab import EditAccount
from import_data import ImportDataFunctions
from backend import load_key
import backend, pyotp, time, pyperclip

class LabelsManager:
    def __init__(self, master, canvas, secframe, accounts, scrollbar, import_data, on_mousewheel, accounts_frame, add_account_tab, edit_account_tab):
        # Initial labels configurations
        self.master = master
        self.canvas = canvas
        self.secframe = secframe
        self.accounts = accounts
        self.scrollbar = scrollbar
        self.import_data = import_data
        self.on_mousewheel = on_mousewheel
        self.accounts_frame = accounts_frame
        self.add_account_tab = add_account_tab
        self.edit_account_tab = edit_account_tab
        self.key = load_key()
        self.open_popups = {}

    # Function to retrieve accounts
    def get_accounts(self):
        return self.accounts
        
    # Function to display the TOTP Copied notification
    def show_copied_notification(self, popup_window):
        copied_label = tk.Label(popup_window, text="TOTP Copied!", fg="green", font=("Helvetica", 12), bg="white")
        copied_label.pack(pady=5)
        popup_window.after(3000, lambda: copied_label.pack_forget())

    # Function to display accounts
    def update_labels(self, accounts=None):
        if accounts is None:
            key = backend.load_key()
            accounts = backend.load_accounts(key)
        for widget in self.accounts_frame.winfo_children():
            widget.destroy()
            
        # If no accounts are found
        if not accounts:
            no_accounts_label = tk.Label(self.accounts_frame, text="No Accounts Found", font=("Helvetica", 18), bg="white")
            no_accounts_label.pack(pady=(150, 20), padx=(85, 150))
            add_account_button = ttk.Button(self.accounts_frame, text="Add Account", command=self.add_account_tab.add_account, style='Red.TButton')
            add_account_button.pack(pady=(0, 10), padx=(85, 150))
            import_button = ttk.Button(self.accounts_frame, text="Import Accounts", command=self.import_data.import_data, style='Red.TButton')
            import_button.pack(pady=(0, 20), padx=(85, 150))

            self.scrollbar.config(command=None)
            self.canvas.unbind_all("<MouseWheel>")
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
            self.scrollbar.pack_forget()
            self.canvas.config(yscrollcommand=None)
        else:
            # Initializes the scrollbar
            if len(accounts) < 9:
                self.scrollbar.pack_forget()
                self.canvas.config(yscrollcommand=None)
            else:
                self.scrollbar.pack(side="right", fill="y")
                self.canvas.config(yscrollcommand=self.scrollbar.set)
            self.totp_labels = {}

            # Function to open the account information when clicked
            def click_account(name):
                if name in self.open_popups and not self.open_popups[name].winfo_exists():
                    del self.open_popups[name]
                if name in self.open_popups:
                    self.open_popups[name].lift()
                    return
                account_info = self.accounts[name]
                secret = account_info['secret']
                totp = pyotp.TOTP(secret)

                # Account Details window configurations
                popup_window = tk.Toplevel(self.master)
                popup_window.title(f"Account Details - {name}")
                popup_window.geometry("400x200")
                popup_window.resizable(False, False)
                popup_window.configure(bg="white")
                popup_window.iconbitmap('VerifyVaultLogo.ico')

                account_name_label = tk.Label(popup_window, text=f"Account Name: {name}", font=("Helvetica", 12), bg="white")
                account_name_label.pack(pady=5)
                timer_label = tk.Label(popup_window, text="", font=("Helvetica", 16), bg="white")
                timer_label.pack()
                totp_label = tk.Label(popup_window, text=f"TOTP: {totp.now()}", font=("Helvetica", 12), bg="white")
                totp_label.pack()

                copy_button = ttk.Button(popup_window, text="Copy TOTP", command=lambda: (pyperclip.copy(totp.now()), self.show_copied_notification(popup_window)), style='Red.TButton')
                copy_button.pack(pady=5)
                edit_button = ttk.Button(popup_window, text="Edit", command=lambda: self.edit_account_tab.edit_account(name), style='Red.TButton')
                edit_button.pack(pady=5)

                # Function to update TOTP Code and timer
                def update_timer():
                    remaining_time = 30 - (time.time() % 30)
                    timer_label.config(text=f"Time until next TOTP: {int(remaining_time)}s")
                    popup_window.after(1000, update_timer)
                    totp_label.config(text=f"TOTP: {totp.now()}")
                update_timer()
                self.open_popups[name] = popup_window

            # Function to handle mouse enter and leave events
            def on_enter(event):
                account_frame.config(cursor="watch")
            def on_leave(event):
                account_frame.config(cursor="")

            # Displays accounts on main window
            for name, info in accounts.items():
                if not name.startswith("C:/") and info.get("key") and info.get("secret"):
                    account_frame = tk.Frame(self.accounts_frame, relief="ridge", bg="white", highlightbackground="black", highlightthickness=2)
                    account_frame.pack(pady=10, padx=(0, 10), fill="x", anchor="w")

                    display_text = f"{name}"
                    label = tk.Label(account_frame, text=display_text, font=("Helvetica", 12), bg="white", width=40)
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
            #else:
                self.scrollbar.config(command=self.canvas.yview)