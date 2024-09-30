import tkinter as tk
from customtkinter import *
from homepage import HomepageFunctions
from PIL import Image
from tkinter import messagebox
from cryptography.fernet import Fernet
import backend, keys, pyotp, bcrypt, configparser

# Initialize the password window
def login():
    # Ensure the database exists
    keys.create_database_if_not_exists()

    # Load configuration settings
    config = configparser.ConfigParser()
    
    # Create the main window for login
    root = CTk()
    root.title("Login to VerifyVault")
    root.geometry("500x300")
    root.resizable(False, False)
    root.iconbitmap('images/VerifyVaultLogo.ico')

    # Check and set dark mode preferences
    backend.unhide_file('preferences.ini')
    config.read('preferences.ini')
    dark_mode = config.get('Preferences', 'dark_mode', fallback=None)
    backend.mark_file_hidden('preferences.ini')
    set_appearance_mode("dark" if dark_mode == 'on' else "light")

    # Create frame for password entry
    password_frame = CTkFrame(root, width=500, height=300)
    password_frame.pack()

    # Load and display the logo
    logo = CTkImage(light_image=Image.open("images/VVLogo.png"), dark_image=Image.open("images/VVDarkLogo.png"), size=(100,100))
    logo_label = CTkLabel(password_frame, text="", image=logo).place(relx=0.5, rely=0.18, anchor="center")

    # Label for password entry
    password_text = CTkLabel(password_frame, text="Enter Password", font=("Helvetica", 24, "bold")).place(relx=0.5, rely=0.4, anchor="center")
    password_entry = CTkEntry(password_frame, placeholder_text="🔒 Password", width=200, height=40, show="*", border_width=2, border_color="red")
    password_entry.place(relx=0.5, rely=0.55, anchor="center")

    # Focus on the password entry if a password is set
    root.after(1000, lambda: password_entry.focus_set() if keys.retrieve_key('pw_hash') else None)

    # Retrieve the password hash for verification
    pw_hash = keys.retrieve_key('pw_hash')

    # Function to toggle password visibility
    def toggle_password_visibility():
        password_entry.configure(show="" if show_password_var.get() else "*")

    # Boolean variable to track password visibility
    show_password_var = tk.BooleanVar(value=False)

    # Toggle switch for showing/hiding the password
    show_toggle = CTkSwitch(password_frame, text="Show Password", variable=show_password_var, command=toggle_password_visibility, cursor="hand2", onvalue="on", offvalue="off", fg_color="red")
    show_toggle.place(relx=0.5, rely=0.7, anchor="center")
    
    # Function to verify the entered password and optional 2FA code
    def verify_password(event=None):
        secret_key = keys.retrieve_key('secret_key')

        # Check if a password hash exists
        if pw_hash:
            entered_password = password_entry.get()

            # Verify the entered password
            if bcrypt.checkpw(entered_password.encode(), pw_hash):

                # Hide password entry elements
                for widget in [password_entry, show_toggle, enter_button, show_hint]:
                    widget.place_forget()

                # Check for 2FA requirement
                if secret_key:
                    password_text.configure("Enter 2FA Code") # Update label for 2FA
                    code_entry = CTkEntry(password_frame, placeholder_text="🔑 2FA Code", width=200, height=40, border_width=2, border_color="red")
                    code_entry.place(relx=0.5, rely=0.55, anchor="center")
                    code_entry.focus_set()

                    # Function to verify 2FA code
                    def verify_code():
                        totp = pyotp.TOTP(secret_key)
                        if totp.verify(code_entry.get().strip()):
                            to_homepage() # Proceed to homepage if 2FA is valid
                        else:
                            messagebox.showerror("Error", "The 2FA Code you entered is invalid. Please try again.")
                            code_entry.delete(0, "end") # Clear entry
                            code_entry.focus_set() # Focus back on the entry

                    # Button to verify the 2FA code
                    enterc_button = CTkButton(master=password_frame, text="Verify Code", command=verify_code, fg_color="white", hover_color="red", text_color="black", cursor="hand2", width=100, height=30, border_width=2, font=("Helvetica", 12, "bold"))
                    enterc_button.place(relx=0.5, rely=0.7, anchor="center")
                    code_entry.bind("<Return>", lambda event: verify_code()) # Bind Enter key

                else:
                    to_homepage() # Proceed to homepage if no 2FA required
            else:
                messagebox.showerror("Error", "The password you entered is invalid. Please try again.")
                password_entry.delete(0, "end") # Clear entry if incorrect
        else:
            to_homepage() # Directly proceed if no password is set

    # Function to navigate to the homepage
    def to_homepage():
        password_frame.destroy()  # Close password frame
        key = backend.load_key()  # Load the encryption key
        HomepageFunctions(root, key)  # Go to homepage

    # Function to display the password hint
    def show_pwhint():
        try:
            # Retrieve the hint key and encrypted hint from storage
            key = keys.retrieve_key('hint_key')
            encrypted_hint = keys.retrieve_key('hint')
            
            # Check if the key or hint exists
            if not key or not encrypted_hint:
                messagebox.showerror("Error", "No password hint found.")
                return
            
            # Decrypt the hint using the key
            fernet = Fernet(key.encode())
            decrypted_hint = fernet.decrypt(encrypted_hint).decode()
            # Display the decrypted hint in a message box
            messagebox.showinfo("Password Hint", f"Your password hint is:\n{decrypted_hint}")
        
        except Exception as e:
            # Handle any exceptions and display an error message
            messagebox.showerror("Error", f"Failed to read hint: {str(e)}")

    # Button to show the password hint
    show_hint = CTkButton(master=password_frame, text="Need Help?", command=show_pwhint, fg_color="white", hover_color="red", text_color="black", cursor="hand2", width=50, height=30, border_width=2, font=("Helvetica", 12, "bold"))
    show_hint.place(relx=0.5, rely=0.8, anchor="center") # Position the button

    # Check if a password hash is set
    pw_hash = keys.retrieve_key('pw_hash')
    if pw_hash:
        # Create the button to enter the password
        enter_button = CTkButton(master=password_frame, text="➜", command=verify_password, fg_color="white", hover_color="red", text_color="black", cursor="hand2", width=50, height=30, border_width=2, font=("Helvetica", 12, "bold"))
        enter_button.place(relx=0.8, rely=0.55, anchor="center") # Position the button

        # Bind the Enter key to the verify password function
        root.bind("<Return>", lambda event: verify_password())
    else:
        # If no password is set, go directly to the homepage
        password_frame.destroy()
        HomepageFunctions(root, backend.load_key())
    
    # Start the main application loop
    root.mainloop()

# Call the login function when the script runs
if __name__ == "__main__":
    login()