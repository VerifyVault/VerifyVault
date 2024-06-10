import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox, filedialog
import binascii, pyotp, qrcode, os, time, pyperclip, backend, sys, subprocess, json
from backend import load_key, encrypt_message, decrypt_message

class LabelsManager:
    def __init__(self, master, canvas, secframe, accounts, scrollbar, import_data, notifications, on_mousewheel, accounts_frame, add_account_tab):
        #Configuring labels_manager constructor
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
        self.key = load_key()
        self.edit_window_open = False
        self.edit_name_window_open = False

    #Retrieving accounts
    def get_accounts(self):
        return self.accounts

    #TOTP Copied notification
    def copy_totp(self, event, totp_text):
        pyperclip.copy(totp_text)
        self.notifications.show_notification("TOTP code copied to clipboard!")

    #Account display formatting
    def update_labels(self, accounts=None):
        if accounts is None:
            key = backend.load_key()
            accounts = backend.load_accounts(key)
        
        for widget in self.accounts_frame.winfo_children():
            widget.destroy()
            
        if not accounts:
            no_accounts_label = tk.Label(self.accounts_frame, text="No Accounts Found", font=("Helvetica", 18), bg="white")
            no_accounts_label.pack(pady=(200, 20), padx=(200, 300))
            add_account_button = ttk.Button(self.accounts_frame, text="Add Account", command=self.add_account_tab.add_account, style='Red.TButton')
            add_account_button.pack(pady=(0, 10), padx=(100, 200))
            import_button = ttk.Button(self.accounts_frame, text="Import Accounts", command=self.import_data, style='Red.TButton')
            import_button.pack(pady=(0, 10), padx=(100, 200))

            self.scrollbar.config(command=None)
            self.canvas.unbind_all("<MouseWheel>")
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
            self.scrollbar.pack_forget()
            self.canvas.config(yscrollcommand=None)

        else:
            if len(accounts) < 12:
                self.scrollbar.pack_forget()
                self.canvas.config(yscrollcommand=None)
            else:
                self.scrollbar.pack(side="right", fill="y")
                self.canvas.config(yscrollcommand=self.scrollbar.set)

            self.totp_labels = []

            def bind_copy_totp(label, totp_text):
                label.bind("<Button-1>", lambda event, totp_text=totp_text: self.copy_totp(event, totp_text))

            #Edit Account window
            def edit_account(name):
                #Closes Edit Account window
                def close_edit_window():
                    self.edit_window_open = False
                    edit_window.destroy()

                #Opens and configures Edit Account window
                if not self.edit_window_open:
                    self.edit_window_open = True
                    
                    edit_window = tk.Toplevel(self.master)
                    edit_window.title("Edit Account")
                    edit_window.geometry("150x150")
                    edit_window.resizable(False, False)
                    edit_window.configure(bg="white")

                    edit_frame = tk.Frame(edit_window, bg="white")
                    edit_frame.pack(fill="both", expand=True)

                    #Configures QR Exports
                    def export_qr_code():
                        if edit_window:
                            edit_window.destroy()
                        account_info = self.accounts[name]
                        secret_key = account_info['secret']
                        provisioning_uri = pyotp.totp.TOTP(secret_key).provisioning_uri(name)

                        qr = qrcode.QRCode(
                            version=1,
                            error_correction=qrcode.constants.ERROR_CORRECT_L,
                            box_size=10,
                            border=4,
                        )
                        qr.add_data(provisioning_uri)
                        qr.make(fit=True)

                        dest_folder = filedialog.askdirectory()

                        if dest_folder:
                            qr_code_file_path = os.path.join(dest_folder, f"{name}_QR_code.png")
                            qr_img = qr.make_image(fill_color="black", back_color="white")
                            qr_img.save(qr_code_file_path)
                            self.notifications.show_notification(f"QR code exported successfully to {qr_code_file_path}")
                        else:
                            self.notifications.show_notification("QR code export cancelled.")

                        close_edit_window()
                    
                    def edit_name():
                        #Closes Edit Name window
                        def close_edit_name_window():
                            self.edit_name_window_open = False
                            edit_name_window.destroy()

                        if not self.edit_name_window_open:
                            #Opens and configures Edit Name window
                            self.edit_name_window_open = True
                            close_edit_window()

                            edit_name_window = tk.Toplevel(self.master)
                            edit_name_window.title("Edit Name")
                            edit_name_window.geometry("150x200")
                            edit_name_window.resizable(False, False)
                            edit_name_window.configure(bg="white")

                            edit_name_frame = tk.Frame(edit_name_window, bg="white")
                            edit_name_frame.pack(fill="both", expand=True)

                            name_label = tk.Label(edit_name_frame, text="Enter New Name:", bg="white")
                            name_label.pack()
                            initial_character_count = len(name)

                            #Verifies that the account name is <30 characters
                            def validate_name(name):
                                if len(name) > 30:
                                    messagebox.showinfo("Error", "Character Limit is 30")
                                    edit_name_window.lift()
                                return True

                            vcmd = (edit_name_frame.register(validate_name), "%P")

                            name_entry = tk.Entry(edit_name_frame, validate="key", validatecommand=vcmd)
                            name_entry.pack()
                            name_entry.insert(0, name)
                            name_entry.focus_set()

                            def remove_focus(event):
                                name_entry.focus_set()
                                edit_name_frame.focus_set()
                            edit_name_frame.bind("<Button-1>", remove_focus)
                            
                            #Counting account name characters
                            def update_char_count(event):
                                char_count_label.config(text=f"Characters: {len(name_entry.get())}")

                            name_entry.bind("<KeyRelease>", update_char_count)
                            char_count_label = tk.Label(edit_name_frame, text=f"Characters: {initial_character_count}", bg="white")
                            char_count_label.pack()

                            #Saves new name
                            def save_name():
                                from gui import TwoFactorAppGUI
                                new_name = name_entry.get().strip()
                                if validate_name(new_name) and new_name != name:
                                    if new_name in self.accounts:
                                        error_label = tk.Label(edit_name_frame, text="Invalid Name", fg="red", bg="white")
                                        error_label.pack()
                                    else:
                                        self.accounts[new_name] = self.accounts.pop(name)
                                        key = backend.load_key()
                                        backend.save_accounts(self.accounts, key)
                                        messagebox.showinfo("Success", "Account Name edited successfully!")
                                        self.update_labels()
                                        close_edit_name_window()
                                        self.master.destroy()
                                        TwoFactorAppGUI(tk.Tk(), self.key)
                                else:
                                    error_label = tk.Label(edit_name_frame, text="Invalid Name", fg="red", bg="white")
                                    error_label.pack()
                                    self.master.after(3000, lambda: error_label.pack_forget())

                            name_entry.bind("<Return>", lambda event: save_name())

                            #Configures Edit Name window buttons
                            continue_button = ttk.Button(edit_name_frame, text="Save", command=save_name, style='Red.TButton')
                            continue_button.pack(pady=5)
                            cancel_button = ttk.Button(edit_name_frame, text="Cancel", command=edit_name_window.destroy, style='Red.TButton')
                            cancel_button.pack(pady=5)
                            edit_name_window.protocol("WM_DELETE_WINDOW", close_edit_name_window)

                    #Configures delete account functionaility
                    def delete_account(self, name):
                        from gui import TwoFactorAppGUI
                        try:
                            with open('data.json.vv', 'rb') as file:
                                encrypted_data = file.read()
                                decrypted_data = decrypt_message(encrypted_data, self.key)
                                accounts_data = json.loads(decrypted_data)
                        except FileNotFoundError:
                            accounts_data = {}

                        if name in accounts_data:
                            confirmed = messagebox.askyesno("Delete Account", "Are you sure you want to delete this account?")
                            if confirmed:
                                accounts_data[name]['deleted'] = True
                                del accounts_data[name]

                                with open('data.json.vv', 'wb') as file:
                                    encrypted_data = encrypt_message(json.dumps(accounts_data), self.key)
                                    file.write(encrypted_data)

                                messagebox.showinfo("Success", "Account deleted successfully.")
                                self.update_labels()
                                self.master.destroy()

                                TwoFactorAppGUI(tk.Tk(), self.key)

                    #Configures Edit Account window 
                    edit_name_button = ttk.Button(edit_frame, text="Edit Name", command=edit_name, style='Red.TButton')
                    edit_name_button.pack(pady=5, padx=10)
                    export_qr_button = ttk.Button(edit_frame, text="Export QR Code", command=export_qr_code, style='Red.TButton')
                    export_qr_button.pack(pady=5, padx=10)
                    delete_account_button = ttk.Button(edit_frame, text="Delete Account", command=lambda name=name: delete_account(self, name),
                                                                        style='Red.TButton')
                    delete_account_button.pack(pady=5, padx=10)

                    edit_window.protocol("WM_DELETE_WINDOW", close_edit_window)

            #Functions to close Edit/Edit Name windows
            def close_edit_window(self):
                if self.edit_window_open:
                    self.edit_window_open = False
                    self.edit_window.destroy()
                    self.close_edit_name_window()

            def close_edit_name_window(self):
                if self.edit_name_window_open:
                    self.edit_name_window_open = False
                    self.edit_name_window.destroy()

            self.secframe.update_idletasks()
            self.canvas.config(scrollregion=self.canvas.bbox("all"))

            #Displays accounts w/ working timer
            def update_timer(label, totp, name):
                if label.winfo_exists():
                    remaining_time = 30 - (time.time() % 30)
                    label.config(text=f"Name: {name} | TOTP: {totp.now()} | Remaining Time: {int(remaining_time)}s")
                    self.master.after(1000, lambda: update_timer(label, totp, name))

            for name, info in accounts.items():
                if not name.startswith("C:/") and info.get("key") and info.get("secret"):
                    secret = info['secret']
                    try:
                        totp = pyotp.TOTP(secret)
                        remaining_time = 30 - (time.time() % 30)
                        remaining_time = max(0, int(remaining_time))

                        account_frame = tk.Frame(self.accounts_frame, relief="ridge", bg="white",
                                                highlightbackground="black", highlightthickness=2)
                        account_frame.pack(pady=5, padx=10, fill="x")

                        display_text = f"Name: {name} | TOTP: {totp.now()} | Remaining Time: {int(remaining_time)}s"
                        label = tk.Label(account_frame, text=display_text, font=("Helvetica", 9), bg="white")
                        label.pack(side="left", fill="x", padx=5, pady=5)

                        label.update_idletasks()
                        label_width = label.winfo_width()
                        label.config(width=70)

                        self.totp_labels.append((label, totp.now()))
                        edit_button = ttk.Button(account_frame, text="Edit", command=lambda n=name: edit_account(n),
                                                style='Bubble.TButton')
                        edit_button.pack(side="right", padx=5, pady=5)
                        update_timer(label, totp, name)
                        bind_copy_totp(label, totp.now())

                    except binascii.Error as e:
                        print(f"Error generating TOTP for account '{name}': {e}")

            #Sets frames/scrollbar
            self.secframe.update_idletasks()
            self.canvas.config(scrollregion=self.canvas.bbox("all"))

            self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
            self.canvas.bind_all("<Button-4>", self.on_mousewheel)
            self.canvas.bind_all("<Button-5>", self.on_mousewheel)

            for child in self.accounts_frame.winfo_children():
                child.pack_configure(anchor="n", fill="x")

            if len(accounts) <= 10:
                self.scrollbar.config(command=None)
                self.canvas.unbind_all("<MouseWheel>")
                self.canvas.unbind_all("<Button-4>")
                self.canvas.unbind_all("<Button-5>")
                self.scrollbar.unbind_all("<MouseWheel>")
                self.scrollbar.unbind_all("<Button-4>")
                self.scrollbar.unbind_all("<Button-5>")
