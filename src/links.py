from customtkinter import *
from PIL import Image
from tkinter import messagebox
from ttkbootstrap.tooltip import ToolTip
import pyperclip, webbrowser

class LinksManager:
    def __init__(self, master, right_frame):
        # Initialize menu configurations
        self.master = master
        self.right_frame = right_frame

    # Function to display VerifyVault social media
    def socials(self):
        social_frame = CTkFrame(self.right_frame, width=600, height=700)
        social_frame.place(relx=0.61, rely=0, anchor="n")

        def close_frame():
            social_frame.destroy() # Close the social frame

        close_button = CTkButton(social_frame, command=close_frame, text="❌", fg_color="white", border_color="black", text_color="black", hover_color="red", border_width=2, width=50, height=20, cursor="hand2")
        close_button.place(relx=0.8, rely= 0.03, anchor="ne")
        ToolTip(close_button, text="Close")  # Add tooltip to close button

        title_label = CTkLabel(social_frame, text="VerifyVault Socials", font=("Helvetica", 30, "bold"))
        title_label.place(relx=0.4, rely=0.1, anchor="center")

        # Function to prevent input in the text field
        def prevent_input(event):
            messagebox.showerror("Error", "To copy, click the Copy button.")
            return "break" # Prevent further processing of the event

        # Function to copy social media link to clipboard
        def copy_url(event):
            url = event.widget.get()  # Get the URL from the widget
            pyperclip.copy(url)  # Copy the URL to the clipboard
            messagebox.showinfo("Success", "The URL has been copied to the clipboard!") # Notify user

        # Function to open the social media link in a web browser
        def open_url(event):
            url = event.widget.get() # Get the URL from the widget
            webbrowser.open(url) # Open the URL in the default web browser

        # Function to create a social media entry with an icon and URL
        def create_social_entry(image_path, url, y_position, border_color, tooltip_text):
            img = CTkImage(Image.open(image_path), size=(30, 25)) # Load the icon image
            CTkLabel(social_frame, text="", image=img).place(relx=0.02, rely=y_position, anchor="w") # Place the icon
            
            entry = CTkEntry(social_frame, font=("Helvetica", 18, "bold"), border_width=2, border_color=border_color, corner_radius=5, width=400) # Create entry for URL
            entry.place(relx=0.08, rely=y_position - 0.02, anchor="nw") # Insert the URL into the entry
            
            entry.insert(0, url) # Insert the URL into the entry
            entry.bind("<Key>", prevent_input) # Prevent user input
            entry.bind("<Button-3>", open_url) # Right-click to open URL
            entry.bind("<Button-1>", copy_url) # Left-click to copy URL
            ToolTip(entry, text=tooltip_text) # Add tooltip for the entry

        # Create entries for each social media platform
        create_social_entry("images/icons/Socials/Github.png", "https://github.com/VerifyVault", 0.19, "#181717", "GitHub")
        create_social_entry("images/icons/Socials/SourceForge.png", "https://sourceforge.net/projects/verifyvault/", 0.27, "#FF6600", "SourceForge")
        create_social_entry("images/icons/Socials/Mastodon.png", "https://mastodon.social/@verifyvault", 0.35, "#6364FF", "Mastodon")
        create_social_entry("images/icons/Socials/Twitter.png", "https://x.com/VerifyVault", 0.43, "#000000", "Twitter")
        create_social_entry("images/icons/Socials/YouTube.png", "https://www.youtube.com/@OffVerifyVault", 0.51, "#FF0000", "YouTube")
        create_social_entry("images/icons/Socials/Medium.png", "https://medium.com/@offverifyvault", 0.59, "#000000", "Medium")
        create_social_entry("images/icons/Socials/Matrix.png", "https://matrix.to/#/#official-verifyvault:matrix.org", 0.67, "#0DBD8B", "Matrix")

    # Function to display donation addresses
    def donations(self):
        donation_frame = CTkFrame(self.right_frame, width=600, height=700) # Create a frame for donations
        donation_frame.place(relx=0.61, rely=0, anchor="n")

        def close_frame():
            donation_frame.destroy() # Function to close the donation frame

        close_button = CTkButton(donation_frame, command=close_frame, text="❌", fg_color="white", border_color="black", text_color="black", hover_color="red", border_width=2, width=50, height=20, cursor="hand2")
        close_button.place(relx=0.8, rely= 0.03, anchor="ne") # Position the close button
        ToolTip(close_button, text="Close") # Add tooltip to the close button

        title_label = CTkLabel(donation_frame, text="Contribute to VerifyVault", font=("Helvetica", 30, "bold"))
        title_label.place(relx=0.4, rely=0.1, anchor="center") # Position the title label

        # Function to prevent input in the donation address entry
        def prevent_input(event):
            messagebox.showerror("Error", "To copy, click the Copy button.")
            return "break" # Block input

        # Function to create a donation entry
        def copy_address(event):
            address = event.widget.get()
            pyperclip.copy(address) # Copy the address to clipboard
            messagebox.showinfo("Success", "The address has been copied to the clipboard!")

        # Function to create donation entry
        def create_donation_entry(address, icon_path, y_position, border_color, label_text):
            img = CTkImage(Image.open(icon_path), size=(30, 25)) # Load the icon image
            CTkLabel(donation_frame, text="", image=img).place(relx=0.02, rely=y_position + 0.03, anchor="w") # Place the icon
            
            entry = CTkEntry(donation_frame, font=("Helvetica", 18, "bold"), border_width=2, border_color=border_color, corner_radius=5, width=400) # Create the entry field
            entry.place(relx=0.1, rely=y_position + 0.03, anchor="w") # Position the entry field
            
            entry.insert(0, address) # Insert the donation address into the entry
            entry.bind("<Key>", prevent_input) # Bind key event to prevent input
            entry.bind("<Button-1>", copy_address) # Bind left-click to copy address
            ToolTip(entry, text=label_text)  # Set tooltip with label text

        # Create donation entries for various cryptocurrencies
        create_donation_entry("43YvGR6aUTTG6sAf5Ain8WeJ2fUq6iraUV7VWt9UwsBA8bNctzsndUn1b39asA6Eb1MSpRTjeddwuX4nHQqKnwa7EcCHX9Q", "images/icons/Donate/Monero.png", 0.19, "#FF6600", "Monero")
        create_donation_entry("bc1q3zqeh99p8efuldmn27e44tpajzymafvfyfaqus", "images/icons/Donate/Bitcoin.png", 0.27, "#F7931A", "Bitcoin")
        create_donation_entry("0x7Af3ee1251c0428b7ba6E1dEaB913ac029e58E1e", "images/icons/Donate/Ethereum.png", 0.35, "#3C3C3D", "Ethereum")
        create_donation_entry("LQakrnCZoSDWioe7qp7SPB9dkP4Tdx4oJd", "images/icons/Donate/Litecoin.png", 0.43, "#A6A9AA", "LItecoin")