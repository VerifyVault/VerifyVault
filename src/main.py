import tkinter as tk
from customtkinter import *
from keys import retrieve_key
from gui import TwoFactorAppGUI
from PIL import Image
from tkinter import messagebox
from cryptography.fernet import Fernet
import backend, keys, pyotp, bcrypt, configparser

# Main Function
def main():
    # Password window configurations
    keys.create_database_if_not_exists()
    
    root = CTk()
    root.title("Login to VerifyVault")
    root.geometry("500x300")
    root.resizable(False, False)
    root.iconbitmap('images/VerifyVaultLogo.ico')

    config = configparser.ConfigParser()
    config.read('preferences.ini')
    dark_mode = config.get('Preferences', 'dark_mode', fallback=None)

    if dark_mode == 'on':
        set_appearance_mode("dark")
    else:
        set_appearance_mode("light")

    password_frame = CTkFrame(root, width=500, height=300)
    password_frame.pack()
    
    img = CTkImage(light_image=Image.open("images/VVLogo.png"), dark_image=Image.open("images/VVDarkLogo.png"), size=(100,100))
    img_label = CTkLabel(password_frame, text="", image=img).place(relx=0.5, rely=0.18, anchor="center")

    password_text = CTkLabel(password_frame, text="Enter Password", font=("Helvetica", 24, "bold"))
    password_text.place(relx=0.5, rely=0.4, anchor="center")
    password_entry = CTkEntry(password_frame, placeholder_text="🔒 Password", width=200, height=40, show="*", border_width=2, border_color="red")
    password_entry.place(relx=0.5, rely=0.55, anchor="center")

    # Function to set focus to password entry
    def set_focus():
        password_entry.focus_set()
    root.after(1000, set_focus)

    # Function to toggle password visibility
    def toggle_password_visibility():
        if show_password_var.get():
            password_entry.configure(show="")
        else:
            password_entry.configure(show="*")
    show_password_var = tk.BooleanVar()
    show_password_var.set(False)

    # Configures the show password toggle
    show_toggle = CTkSwitch(password_frame, text="Show Password", variable=show_password_var, command=toggle_password_visibility, cursor="hand2", onvalue="on", offvalue="off", fg_color="red")
    show_toggle.place(relx=0.5, rely=0.7, anchor="center")

    # Function to update the label text
    def update_label_text(text):
        password_text.configure(text=text)
    
    # Function to verify the entered password and check for 2FA
    def verify_password(event=None):
        stored_hash = keys.retrieve_key('pw_hash')
        stored_secret_key = keys.retrieve_key('secret_key')

        # Configures 2FA elements
        if stored_hash:
            entered_password = password_entry.get()
            if bcrypt.checkpw(entered_password.encode(), stored_hash):
                password_entry.place_forget()
                show_toggle.place_forget()
                enter_button.place_forget()
                show_hint.place_forget()

                if stored_secret_key:
                    update_label_text("Enter 2FA Code")
                    code_entry = CTkEntry(password_frame, placeholder_text="🔑 2FA Code", width=200, height=40, border_width=2, border_color="red")
                    code_entry.place(relx=0.5, rely=0.55, anchor="center")
                    code_entry.focus_set()

                    def verify_code():
                        totp = pyotp.TOTP(stored_secret_key)
                        if totp.verify(code_entry.get().strip()):
                            password_frame.destroy()
                            key = backend.load_key()
                            TwoFactorAppGUI(root, key)
                        else:
                            messagebox.showerror("Invalid Code", "Invalid 2FA code. Please try again.")
                            code_entry.delete(0, "end")
                            code_entry.focus_set()
                    enter_code_button = CTkButton(master=password_frame, text="Verify Code", command=verify_code, fg_color="white", hover_color="red", text_color="black", cursor="hand2", width=100, height=30, border_width=2, font=("Helvetica", 12, "bold"))
                    enter_code_button.place(relx=0.5, rely=0.7, anchor="center")
                    
                    def on_enter_code(event=None):
                        verify_code()
                    code_entry.bind("<Return>", on_enter_code)
                else:
                    password_frame.destroy()
                    key = backend.load_key()
                    TwoFactorAppGUI(root, key)
            else:
                messagebox.showerror("Incorrect Password", "The password you entered is incorrect.")
                password_entry.delete(0, "end")
        else:
            password_frame.destroy()
            key = backend.load_key()
            TwoFactorAppGUI(root, key)

    # Function to display the password hint
    def show_password_hint():
        try:
            key = retrieve_key('hint_key')
            if key:
                fernet = Fernet(key.encode())
                if retrieve_key('hint'):
                    encrypted_hint = retrieve_key('hint')
                    decrypted_hint = fernet.decrypt(encrypted_hint).decode()
                    messagebox.showinfo("Password Hint", f"Your password hint is:\n{decrypted_hint}")
                else:
                    messagebox.showerror("No Password Hint Found", "No password hint file found.")
            else:
                messagebox.showerror("No Password Hint Found", "No password hint file found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read hint: {str(e)}")
    show_hint = CTkButton(master=password_frame, text="Need Help?", command=show_password_hint, fg_color="white", hover_color="red", text_color="black", cursor="hand2", width=50, height=30, border_width=2, font=("Helvetica", 12, "bold"))
    show_hint.place(relx=0.5, rely=0.8, anchor="center")

    # Checks if password is set
    stored_hash = keys.retrieve_key('pw_hash')
    if stored_hash:
        enter_button = CTkButton(master=password_frame, text="➜", command=verify_password, fg_color="white", hover_color="red", text_color="black", cursor="hand2", width=50, height=30, border_width=2, font=("Helvetica", 12, "bold"))
        enter_button.place(relx=0.8, rely=0.55, anchor="center")

        def on_enter_root(event=None):
            verify_password()
        root.bind("<Return>", on_enter_root)
    else:
        password_frame.destroy()
        key = backend.load_key()
        TwoFactorAppGUI(root, key)
    root.mainloop()

# Calls main function
if __name__ == "__main__":
    main()