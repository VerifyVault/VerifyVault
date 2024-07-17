import tkinter as tk
from tkinter import ttk, messagebox
import backend, keys
from gui import TwoFactorAppGUI
from manage_password import ManagePassword
import pyotp, bcrypt

# Main Function
def main():
    # Password window configurations
    keys.create_database_if_not_exists()

    root = tk.Tk()
    root.title("Enter Your Password")
    root.geometry("300x300")
    root.resizable(False, False)
    root.configure(bg="white")
    root.iconbitmap('VerifyVaultLogo.ico')

    password_frame = tk.Frame(root, bg="white")
    password_frame.pack(pady=20)

    tk.Label(password_frame, text="Enter your password:", bg="white").pack(pady=5)
    password_entry = tk.Entry(password_frame, show="*")
    password_entry.pack(pady=5)
    
    style = ttk.Style()
    style.configure("White.TCheckbutton", foreground="black", background="white", font=("Helvetica", 10))

    # Function to toggle password visibility
    def toggle_password_visibility():
        if show_password_var.get():
            password_entry.config(show="")
        else:
            password_entry.config(show="*")

    show_password_var = tk.BooleanVar()
    show_password_var.set(False)
    show_password_button = ttk.Checkbutton(password_frame, text="Show Password", var=show_password_var, command=toggle_password_visibility,
                                          style="White.TCheckbutton")
    show_password_button.pack()

    # Function to verify the entered password
    def verify_password(event=None):
        stored_hash = keys.retrieve_key('pw_hash')

        if stored_hash:
            entered_password = password_entry.get()
            if bcrypt.checkpw(entered_password.encode(), stored_hash):
                manage_password = ManagePassword(root)
                if manage_password.two_factor_status == "ON":
                    render_2fa_input()
                else:
                    password_frame.pack_forget()
                    key = backend.load_key()
                    TwoFactorAppGUI(root, key)
            else:
                messagebox.showerror("Incorrect Password", "The password you entered is incorrect.")
                password_entry.delete(0, "end")
        else:
            password_frame.pack_forget()
            key = backend.load_key()
            TwoFactorAppGUI(root, key)

    # Function to display the password hint
    def show_password_hint():
        manage_password = ManagePassword(root)
        password_hint = manage_password.decrypt_hint()
        if password_hint:
            messagebox.showinfo("Password Hint", f"Your password hint is:\n\n{password_hint}")

    # Function to handle Enter key press
    def render_2fa_input():
        code_label.pack(pady=5)
        code_entry.pack(pady=5)
        code_entry.focus_set()
        enter_button.config(command=verify_2fa)
        code_entry.bind("<Return>", lambda event: verify_2fa())
    
    # Function to verify the 2FA Code
    def verify_2fa(event=None):
        stored_hash = keys.retrieve_key('pw_hash')
        stored_secret_key = keys.retrieve_key('secret_key')

        if stored_hash and bcrypt.checkpw(password_entry.get().encode(), stored_hash) and stored_secret_key:
            totp = pyotp.TOTP(stored_secret_key)
            if totp.verify(code_entry.get().strip()):
                password_frame.pack_forget()
                key = backend.load_key()
                TwoFactorAppGUI(root, key)
            else:
                messagebox.showerror("Invalid Code", "Invalid 2FA code. Please try again.")
                code_entry.delete(0, "end")
                code_entry.focus_set()
        else:
            messagebox.showerror("Authentication Failed", "Password or 2FA code incorrect. Please try again.")
            password_entry.delete(0, "end")
            code_entry.delete(0, "end")
            password_entry.focus_set()

    # Password window configurations
    stored_hash = keys.retrieve_key('pw_hash')
    if stored_hash:
        manage_password = ManagePassword(root)
        if manage_password.two_factor_status == "ON":
            code_label = tk.Label(password_frame, text="Enter your 2FA code:", bg="white")
            code_label.pack(pady=5)
            
            code_entry = tk.Entry(password_frame)
            code_entry.pack(pady=5)
            code_entry.bind("<Return>", verify_2fa)

        password_entry.bind("<Return>", verify_password)
        password_entry.focus_set()

        button_style = ttk.Style()
        button_style.configure('Custom.TButton', background='white', padding=5, relief="flat", borderwidth=0, bordercolor="red")
        enter_button = ttk.Button(password_frame, text="Enter", command=verify_password, style='Custom.TButton')
        enter_button.pack(pady=5)
    else:
        password_frame.pack_forget()
        key = backend.load_key()
        TwoFactorAppGUI(root, key)

    root.mainloop()

if __name__ == "__main__":
    main()
