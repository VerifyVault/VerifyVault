import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from gui import TwoFactorAppGUI
from password import PasswordManager
import backend, os

# Main Function
def main():
    # Password window configurations
    root = tk.Tk()
    key = backend.load_key()
    root.title("Enter Your Password")
    root.geometry("200x100")
    root.resizable(False, False)
    root.configure(bg="white")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, "VerifyVault Logo.png")

    # Verifies the password
    def verify_password():
        entered_password = password_entry.get()
        password_manager = PasswordManager()
        if password_manager.verify_password(entered_password):
            password_frame.pack_forget()
            TwoFactorAppGUI(root, key)
        else:
            messagebox.showerror("Incorrect Password", "The password you entered is incorrect.")
            password_entry.delete(0, "end")
    def on_enter(event):
        verify_password()

    # Checks if the password is set
    if os.path.exists(".secure"):
        password_frame = tk.Frame(root, bg="white")
        password_frame.pack()

        # Password window configurations
        tk.Label(password_frame, text="Enter your password:", bg="white").pack(pady=5)
        password_entry = tk.Entry(password_frame, show="*")
        password_entry.pack(pady=5)
        password_entry.bind("<Return>", on_enter)
        password_entry.focus_set()

        button_style = ttk.Style()
        button_style.configure('Custom.TButton', background='white', padding=5, relief="flat", borderwidth=0, bordercolor="red")
        ttk.Button(password_frame, text="Enter", command=verify_password, style='Custom.TButton').pack(pady=5)

        if os.path.exists(image_path):
            img = Image.open(image_path)
            icon = ImageTk.PhotoImage(img)
            root.iconphoto(True, icon) 
    else:
        TwoFactorAppGUI(root, key)
    root.mainloop()

# Calls main function
if __name__ == "__main__":
    main()
