import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from gui import TwoFactorAppGUI
from password import PasswordManager
from manage_password import ManagePassword
import backend, os

# Main Function
def main():
    # Password window configurations
    root = tk.Tk()
    key = backend.load_key()
    root.title("Enter Your Password")
    root.geometry("300x200")
    root.resizable(False, False)
    root.configure(bg="white")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, "VerifyVault Logo.png")

    # Function to verify the entered password
    def verify_password():
        entered_password = password_entry.get()
        password_manager = PasswordManager()
        if password_manager.verify_password(entered_password):
            password_frame.pack_forget()
            TwoFactorAppGUI(root, key)
        else:
            messagebox.showerror("Incorrect Password", "The password you entered is incorrect.")
            password_entry.delete(0, "end")

    # Function to toggle password visibility
    def toggle_password_visibility():
        if show_password_var.get():
            password_entry.config(show="")
        else:
            password_entry.config(show="*")

    # Function to display the password hint
    def show_password_hint():
        manage_password = ManagePassword(root)
        password_hint = manage_password.decrypt_hint()
        if password_hint:
            messagebox.showinfo("Password Hint", f"Your password hint is:\n\n{password_hint}")

    # Function to handle Enter key press
    def on_enter(event):
        verify_password()

    # Password window configurations
    if os.path.exists(".secure"):
        password_frame = tk.Frame(root, bg="white")
        password_frame.pack()
        tk.Label(password_frame, text="Enter your password:", bg="white").pack(pady=5)

        password_entry = tk.Entry(password_frame, show="*")
        password_entry.pack(pady=5)

        style = ttk.Style()
        style.configure("White.TCheckbutton", foreground="black", background="white", font=("Helvetica", 10))

        show_password_var = tk.BooleanVar()
        show_password_var.set(False)
        show_password_button = ttk.Checkbutton(password_frame, text="Show Password", var=show_password_var, command=toggle_password_visibility,
                                            style="White.TCheckbutton")
        show_password_button.pack()

        password_entry.bind("<Return>", on_enter)
        password_entry.focus_set()

        button_style = ttk.Style()
        button_style.configure('Custom.TButton', background='white', padding=5, relief="flat", borderwidth=0, bordercolor="red")
        ttk.Button(password_frame, text="Enter", command=verify_password, style='Custom.TButton').pack(pady=5)

        if os.path.exists(image_path):
            img = Image.open(image_path)
            icon = ImageTk.PhotoImage(img)
            root.iconphoto(True, icon)
        
        # Verifies if password hint is enabled
        manage_password = ManagePassword(root)
        if manage_password.password_hint_status == "On":
            ttk.Button(password_frame, text="Password Hint", command=show_password_hint, style='Custom.TButton').pack(pady=5)

    else:
        TwoFactorAppGUI(root, key)
    
    root.mainloop()

# Calls main function
if __name__ == "__main__":
    main()
