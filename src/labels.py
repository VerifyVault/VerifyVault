from customtkinter import *
from tkinter import messagebox
from recycle_bin import RecycleBinFunctions
from backend import load_key, encrypt_message, decrypt_message
import backend, pyotp, time, pyperclip, qrcode, json

class LabelsManager:
    def __init__(self, master, accounts, middle_frame, right_frame, top_button_frame):
        # Initial labels configurations
        self.master = master
        self.accounts = accounts
        self.middle_frame = middle_frame
        self.right_frame = right_frame
        self.top_button_frame = top_button_frame
        
        self.key = load_key()
        self.open_popups = {}

        self.groups = self.load_groups()
        if not self.groups:
            self.groups = ["All Accounts", "Add Group"]

        self.current_page = 1
        self.accounts_per_page = 20
        self.groups_dropdown = None

        self.groups_dropdown = CTkOptionMenu(self.top_button_frame, command=self.handle_group_selection, values=self.groups, height=35, font=("Helvetica", 14), fg_color="white", text_color="black", dropdown_font=("Helvetica", 14), dropdown_text_color="black", corner_radius=2, button_color="red", button_hover_color="#EE4B2B", dropdown_fg_color="white", dropdown_hover_color="red", hover=True, anchor="center", state="normal")
        self.groups_dropdown.place(relx=0.72, rely=0.5, anchor="center")
        self.groups_dropdown.set("All Accounts")
        self.groups_dropdown.bind("<Button-3>", self.delete_group)

        self.recycle_bin = RecycleBinFunctions(master, self.accounts, self.update_labels, self.right_frame)

    # Function to save groups
    def save_groups(self):
        with open('groups.json', 'w') as file:
            json.dump(self.groups, file, indent=4)

    # Function to load groups
    def load_groups(self):
        if not os.path.exists('groups.json'):
            with open('groups.json', 'w') as file:
                json.dump(["All Accounts"], file)
            return ["All Accounts", "Add Group"]
        else:
            try:
                with open('groups.json', 'r') as file:
                    return json.load(file)
            except json.JSONDecodeError:
                return ["All Accounts", "Add Group"]

    # Function to delete groups
    def delete_group(self, event=None):
        selected_group = self.groups_dropdown.get()

        if selected_group == "All Accounts":
            messagebox.showerror("Info", "You cannot delete the 'All Accounts' bar.")
            return

        delete = messagebox.askyesno("Confirm", f"Are you sure you want to delete the group '{selected_group}'?")
        if delete:
            if selected_group in self.groups:
                self.groups.remove(selected_group)
                
                if not self.groups:
                    self.groups.append("All Accounts")                
                self.save_groups()

                self.groups_dropdown.configure(values=self.groups)
                if self.groups:
                    self.groups_dropdown.set(self.groups[0])
                else:
                    self.groups_dropdown.set("All Accounts")

                self.update_labels()
            else:
                messagebox.showwarning("Warning", "Group not found.")

    # Function to get accounts
    def get_accounts(self):
        return self.accounts

    # Function to show TOTP Copied notification
    def show_copied_notification(self, popup_window):
        messagebox.showinfo("Success", "TOTP Copied!")

    # Function to get the number of accounts
    def get_number_of_accounts(self):
        return len(self.accounts)

    # Function to handle group selection
    def handle_group_selection(self, selected_option):
        if selected_option == "Add Group":
            self.add_group()
            self.groups_dropdown.set("All Accounts")
        elif selected_option == "All Accounts":
            self.update_labels()
        else:
            self.filter_accounts_by_group(selected_option)

    # Function to filter accounts by group
    def filter_accounts_by_group(self, group_name):
        filtered_accounts = {name: data for name, data in self.accounts.items() if data['group'] == group_name}
        self.update_labels(filtered_accounts)

    # Function to add a group
    def add_group(self):
        group_entry = CTkInputDialog(text="Create New Group", font=("Helvetica", 16, "bold"), title="Create New Group", button_fg_color="white", button_hover_color="red", button_text_color="black", entry_border_color="black")
        group_name = group_entry.get_input()

        if group_name:
            if group_name in self.groups:
                messagebox.showerror("Group Exists", f"Group '{group_name}' already exists.")
                return
            if group_name == "None" or group_name == "none":
                messagebox.showerror("Invalid Name", "The Group Name you set is invalid.")
                return

            self.groups.append(group_name)
            self.groups.sort()

            if "Add Group" in self.groups:
                self.groups.remove("Add Group")
            self.groups.append("Add Group")
            self.groups_dropdown.configure(values=self.groups)
            self.save_groups()
            messagebox.showinfo("Success", "Group created successfully")

    # Function to display accounts
    def update_labels(self, accounts=None):
        if accounts is None:
            key = backend.load_key()
            accounts = backend.load_accounts(key)
        accounts = dict(sorted(accounts.items()))

        for widget in self.middle_frame.winfo_children():
            widget.destroy()

        if not accounts:
            no_accounts_label = CTkLabel(self.middle_frame, text="❌ No Accounts Found", font=("Helvetica", 40, "bold"), corner_radius=2)
            no_accounts_label.place(relx=0.5, rely=0.4, anchor="center")
        else:
            num_pages = (len(accounts) + self.accounts_per_page - 1) // self.accounts_per_page
            start_index = (self.current_page - 1) * self.accounts_per_page
            end_index = min(start_index + self.accounts_per_page, len(accounts))

            # Funcion to display account information
            def click_account(name):
                if name in self.open_popups and not self.open_popups[name].winfo_exists():
                    del self.open_popups[name]
                if name in self.open_popups:
                    self.open_popups[name].lift()
                    return
                account_info = self.accounts[name]
                secret = account_info['secret']
                totp = pyotp.TOTP(secret)

                info_frame = CTkFrame(self.right_frame, width=600, height=700)
                info_frame.place(relx=0.61, rely=0, anchor="n")

                def close_frame():
                    info_frame.destroy()

                x_button = CTkButton(info_frame, command=close_frame, text="❌", fg_color="white", border_color="black", text_color="black", hover_color="red", border_width=2, width=50, height=20, cursor="hand2")
                x_button.place(relx=0.8, rely=0.03, anchor="ne")

                title_label = CTkLabel(info_frame, text=f"Account Name - {name}", font=("Helvetica", 30, "bold", "underline"))
                title_label.place(relx=0.42, rely=0.12, anchor="center")

                timer_label = CTkLabel(info_frame, text="", font=("Helvetica", 24))
                timer_label.place(relx=0.42, rely=0.2, anchor="center")
                totp_label = CTkLabel(info_frame, text=f"TOTP: {totp.now()}", font=("Helvetica", 24))
                totp_label.place(relx=0.42, rely=0.25, anchor="center")

                copy_button = CTkButton(info_frame, text="Copy", command=lambda: (pyperclip.copy(totp.now()), self.show_copied_notification(info_frame)), fg_color="white", hover_color="red", text_color="black", width=100, height=30, border_width=2, font=("Helvetica", 16, "bold"), cursor="hand2")
                copy_button.place(relx=0.42, rely=0.3, anchor="center")

                settings_label = CTkLabel(info_frame, text="Settings", font=("Helvetica", 30, "bold", "underline"))
                settings_label.place(relx=0.42, rely=0.4, anchor="center")

                edit_name_label = CTkLabel(info_frame, text="Edit Name: ", font=("Helvetica", 18, "bold"))
                edit_name_label.place(relx=0.05, rely=0.48, anchor="w")

                group_options = ["None"] + [group for group in self.groups if group not in ["All Accounts", "Add Group"]]
                group_dropdown = CTkOptionMenu(info_frame, values=group_options, height=35, font=("Helvetica", 14), fg_color="white", text_color="black", dropdown_font=("Helvetica", 14), dropdown_text_color="black", corner_radius=2, button_color="red", button_hover_color="#EE4B2B", dropdown_fg_color="white", dropdown_hover_color="red", hover=True, anchor="center")
                group_dropdown.place(relx=0.12, rely=0.58, anchor="w")
                group_dropdown.set(account_info['group'])

                # Function to update group
                def update_group():
                    new_group = group_dropdown.get()
                    if new_group != account_info['group']:
                        if new_group == "Add Group" or new_group == "All Accounts":
                            messagebox.showerror("Invalid Group", f"Cannot set group to {new_group}.")
                            return
                        account_info['group'] = new_group
                        if new_group == "None":
                            account_info['group'] = ""
                        self.accounts[name] = account_info
                        key = backend.load_key()
                        backend.save_accounts(self.accounts, key)
                        self.update_labels(self.accounts)
                        messagebox.showinfo("Success", "Account group updated successfully!")

                update_group_button = CTkButton(info_frame, text="Update Group", command=update_group, fg_color="white", hover_color="red", text_color="black", width=150, height=30, border_width=2, font=("Helvetica", 16, "bold"), cursor="hand2")
                update_group_button.place(relx=0.11, rely=0.64, anchor="w")

                provisioning_uri = totp.provisioning_uri(name)
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=5,
                    border=4,
                )
                qr.add_data(provisioning_uri)
                qr.make(fit=True)
                qr_img = qr.make_image(fill_color="black", back_color="white")
                
                from io import BytesIO
                qr_image_stream = BytesIO()
                qr_img.save(qr_image_stream, format='PNG')
                qr_image_stream.seek(0)
                
                from tkinter import PhotoImage
                qr_image = PhotoImage(data=qr_image_stream.getvalue())
                qr_code_label = CTkLabel(info_frame, image=qr_image, text="")
                qr_code_label.image = qr_image
                qr_code_label.place(relx=0.6, rely=0.7, anchor="center")

                creation_time_label = CTkLabel(info_frame, text=f"Created At: {account_info['created']}", font=("Helvetica", 16))
                creation_time_label.place(relx=0.4, rely=0.88, anchor="center")

                # Functions to validate/save account name
                def validate_name(name):
                    invalid_chars = "\\/:*?\"<>|"
                    for char in invalid_chars:
                        if char in name:
                            messagebox.showerror("Invalid Character", f"Name cannot contain '{char}'")
                            return False
                    return True
                vcmd = (info_frame.register(validate_name), "%P")
                edit_name = CTkEntry(info_frame, validate="key", validatecommand=vcmd, width=220, height=40, border_width=2, border_color="red")
                edit_name.place(relx=0.22, rely=0.48, anchor="w")
                edit_name.insert(0, name)

                def save_name():
                    new_name = edit_name.get().strip()

                    if len(new_name) == 0:
                        messagebox.showerror("Invalid Entry", "Name is required.")
                        return
                    if validate_name(new_name) and new_name != name:
                        if new_name in self.accounts:
                            messagebox.showerror("Invalid Entry", "Name already exists.")
                        else:
                            self.accounts[new_name] = self.accounts.pop(name)
                            key = backend.load_key()
                            backend.save_accounts(self.accounts, key)
                            self.update_labels(self.accounts)
                            messagebox.showinfo("Success", "Account Name edited successfully!")
                            close_frame()
                    else:
                        messagebox.showerror("Invalid Entry", "Invalid Name.")
                edit_name.bind("<Return>", lambda event: save_name())

                save_button = CTkButton(info_frame, text="Save", command=save_name, fg_color="white", hover_color="red", text_color="black", width=100, height=30, border_width=2, font=("Helvetica", 12, "bold"), cursor='hand2')
                save_button.place(relx=0.7, rely=0.48, anchor="center")

                # Function to export QR code
                def export_qr_code(name):
                    account_info = self.accounts[name]
                    secret_key = account_info['secret']
                    provisioning_uri = pyotp.totp.TOTP(secret_key).provisioning_uri(name)

                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=15,
                        border=4,
                    )
                    qr.add_data(provisioning_uri)
                    qr.make(fit=True)

                    dest_folder = filedialog.askdirectory()

                    if dest_folder:
                        qr_code_file_path = os.path.join(dest_folder, f"{name}_QR_code.png")
                        qr_img = qr.make_image(fill_color="black", back_color="white")
                        qr_img.save(qr_code_file_path)
                        messagebox.showinfo("Success", f"QR code exported successfully to {qr_code_file_path}")

                # Function to delete account
                def delete_account(name):
                    confirm_delete = messagebox.askyesno("Delete Account", "Are you sure you would like to delete this account?")
                    if confirm_delete:
                        try:
                            with open('data.vv', 'rb') as file:
                                encrypted_data = file.read()
                                decrypted_data = decrypt_message(encrypted_data, self.key)
                                accounts_data = json.loads(decrypted_data)

                            if name in accounts_data:
                                deleted_account_info = accounts_data.pop(name)
                                
                                encrypted_data = encrypt_message(json.dumps(accounts_data), self.key)
                                with open('data.vv', 'wb') as file:
                                    file.write(encrypted_data)

                                if os.path.exists('deleted.json') and os.path.getsize('deleted.json') > 0:
                                    with open('deleted.json', 'r') as deleted_file:
                                        deleted_data = json.load(deleted_file)
                                else:
                                    deleted_data = {}

                                deleted_data[name] = deleted_account_info

                                with open('deleted.json', 'w') as deleted_file:
                                    json.dump(deleted_data, deleted_file, indent=4)

                                if name in self.accounts:
                                    del self.accounts[name]

                                self.update_labels(self.accounts)
                                messagebox.showinfo("Success", "Account deleted successfully.")
                                close_frame()
                            else:
                                messagebox.showerror("Error", "Account not found.")
                        except FileNotFoundError:
                            messagebox.showerror("Error", "Data file not found.")
                        except Exception as e:
                            messagebox.showerror("Error", f"An error occurred: {str(e)}")

                export_qr_button = CTkButton(info_frame, text="Export via QR Code", command=lambda: export_qr_code(name), fg_color="white", hover_color="red", text_color="black", width=150, height=40, border_width=2, font=("Helvetica", 16, "bold"), cursor="hand2")
                export_qr_button.place(relx=0.1, rely=0.75, anchor="w")
                delete_account_button = CTkButton(info_frame, text="Delete Account", command=lambda: delete_account(name), fg_color="red", hover_color="white", text_color="black", width=150, height=40, border_width=2, font=("Helvetica", 16, "bold"), cursor="hand2")
                delete_account_button.place(relx=0.11, rely=0.82, anchor="w")

                # Function to update TOTP timer
                def update_timer():
                    remaining_time = 30 - (time.time() % 30)
                    timer_label.configure(text=f"Time until next TOTP: {int(remaining_time)}s")
                    info_frame.after(1000, update_timer)
                    totp_label.configure(text=f"TOTP: {totp.now()}")
                update_timer()
                self.open_popups[name] = info_frame

            x_offset = 0.01
            button_width = 0.2
            rely = 0.1
            row_height = 0.2

            # Display accounts
            for name, info in list(accounts.items())[start_index:end_index]:
                if not name.startswith("C:/") and info.get("key") and info.get("secret"):
                    display_text = f"{name}"

                    button = CTkButton(self.middle_frame, text=display_text, command=lambda n=name: click_account(n), fg_color="white", hover_color="red", text_color="black", width=145, height=100, border_width=2, corner_radius=2, font=("Helvetica", 20), cursor="hand2")
                    button.place(relx=x_offset, rely=rely)
                    x_offset += button_width
                    
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

            for widget in self.middle_frame.winfo_children():
                if isinstance(widget, CTkButton) and widget.cget('text') in ("Previous", "Next"):
                    widget.destroy()
            if self.current_page > 1:
                prev_button = CTkButton(self.middle_frame, text="Previous", command=prev_page, fg_color="white", hover_color="#EE4B2B", text_color="black", width=100, height=40, border_width=2, font=("Helvetica", 14, "bold"), cursor="hand2")
                prev_button.place(relx=0.35, rely=0.93, anchor="center")
            if self.current_page < num_pages:
                next_button = CTkButton(self.middle_frame, text="Next", command=next_page, fg_color="white", hover_color="#EE4B2B", text_color="black", width=100, height=40, border_width=2, font=("Helvetica", 14, "bold"), cursor="hand2")
                next_button.place(relx=0.65, rely=0.93, anchor="center")
            page_indicator = CTkLabel(self.middle_frame, text=f"Page {self.current_page}/{num_pages}  - Total Accounts: {len(accounts)}", font=("Helvetica", 14, "bold"), corner_radius=2)
            page_indicator.place(relx=0.5, rely=0.93, anchor="center")