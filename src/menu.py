import tkinter as tk
import tkinter as ttk
from customtkinter import *
from PIL import Image
from tkinter import messagebox
from ttkbootstrap.tooltip import ToolTip
import pyperclip, webbrowser

class MenuManager:
    def __init__(self, master, right_frame):
        # Menu bar configurations
        self.master = master
        self.right_frame = right_frame
        self.menubar = tk.Menu(master)

    # Function to display VerifyVault social media
    def socials(self):
        social_frame = CTkFrame(self.right_frame, width=600, height=700)
        social_frame.place(relx=0.61, rely=0, anchor="n")

        def close_frame():
            social_frame.destroy()

        x_button = CTkButton(social_frame, command=close_frame, text="❌", fg_color="white", border_color="black", text_color="black", hover_color="red", border_width=2, width=50, height=20, cursor="hand2")
        x_button.place(relx=0.8, rely= 0.03, anchor="ne")

        title_label = CTkLabel(social_frame, text="VerifyVault Socials", font=("Helvetica", 30, "bold"))
        title_label.place(relx=0.4, rely=0.1, anchor="center")

        # Function to prevent input
        def prevent_input(event):
            messagebox.showerror("Use Copy Button", "To copy, click the Copy button.")
            return "break"

        # Function to copy social media link
        def copy_to_clipboard(event):
            widget = event.widget
            url = widget.get()
            pyperclip.copy(url)
            messagebox.showinfo("Copied", "The URL has been copied to the clipboard!")

        # Function to open social media link
        def open_url(event):
            widget = event.widget
            url = widget.get()
            webbrowser.open(url)

        # Social Media initialization
        git_img = CTkImage(Image.open("images/icons/Socials/Github.png"), size=(30,25))
        img_label = CTkLabel(social_frame, text="", image=git_img).place(relx=0.02, rely=0.19, anchor="w")
        github_url = "https://github.com/VerifyVault"
        github_entry = CTkEntry(social_frame, font=("Helvetica", 18, "bold"), border_width=2, border_color="#181717", corner_radius=5, width=400)
        github_entry.place(relx=0.08, rely=0.17, anchor="nw")

        github_entry.insert(0, github_url)
        github_entry.bind("<Key>", prevent_input)
        github_entry.bind("<Button-3>", open_url)
        github_entry.bind("<Button-1>", copy_to_clipboard)
        ToolTip(github_entry, text="GitHub")

        source_img = CTkImage(Image.open("images/icons/Socials/SourceForge.png"), size=(30,25))
        img_label = CTkLabel(social_frame, text="", image=source_img).place(relx=0.02, rely=0.27, anchor="w")
        sourceforge_url = "https://sourceforge.net/projects/verifyvault/"
        sourceforge_entry = CTkEntry(social_frame, font=("Helvetica", 18, "bold"), border_width=2, border_color="#FF6600", corner_radius=5, width=400)
        sourceforge_entry.place(relx=0.08, rely=0.25, anchor="nw")
        
        sourceforge_entry.insert(0, sourceforge_url)
        sourceforge_entry.bind("<Key>", prevent_input)
        sourceforge_entry.bind("<Button-3>", open_url)
        sourceforge_entry.bind("<Button-1>", copy_to_clipboard)
        ToolTip(sourceforge_entry, text="SourceForge")

        masto_img= CTkImage(Image.open("images/icons/Socials/Mastodon.png"), size=(30,25))
        img_label = CTkLabel(social_frame, text="", image=masto_img).place(relx=0.02, rely=0.35, anchor="w")
        mastodon_url = "https://mastodon.social/@verifyvault"
        mastodon_entry = CTkEntry(social_frame, font=("Helvetica", 18, "bold"), border_width=2, border_color="#6364FF", corner_radius=5, width=400)
        mastodon_entry.place(relx=0.08, rely=0.33, anchor="nw")

        mastodon_entry.insert(0, mastodon_url)
        mastodon_entry.bind("<Key>", prevent_input)
        mastodon_entry.bind("<Button-3>", open_url)
        mastodon_entry.bind("<Button-1>", copy_to_clipboard)
        ToolTip(mastodon_entry, text="Mastodon")

        x_img = CTkImage(Image.open("images/icons/Socials/Twitter.png"), size=(30,25))
        img_label = CTkLabel(social_frame, text="", image=x_img).place(relx=0.02, rely=0.43, anchor="w")
        twitter_url = "https://x.com/VeryfyVault"
        twitter_entry = CTkEntry(social_frame, font=("Helvetica", 18, "bold"), border_width=2, border_color="#000000", corner_radius=5, width=400)
        twitter_entry.place(relx=0.08, rely=0.41, anchor="nw")

        twitter_entry.insert(0, twitter_url)
        twitter_entry.bind("<Key>", prevent_input)
        twitter_entry.bind("<Button-3>", open_url)
        twitter_entry.bind("<Button-1>", copy_to_clipboard)
        ToolTip(twitter_entry, text="Twitter")

        med_img = CTkImage(Image.open("images/icons/Socials/Medium.png"), size=(30,25))
        img_label = CTkLabel(social_frame, text="", image=med_img).place(relx=0.02, rely=0.51, anchor="w")
        medium_url = "https://medium.com/@offverifyvault"
        medium_entry = CTkEntry(social_frame, font=("Helvetica", 18, "bold"), border_width=2, border_color="#000000", corner_radius=5, width=400)
        medium_entry.place(relx=0.08, rely=0.49, anchor="nw")

        medium_entry.insert(0, medium_url)
        medium_entry.bind("<Key>", prevent_input)
        medium_entry.bind("<Button-3>", open_url)
        medium_entry.bind("<Button-1>", copy_to_clipboard)
        ToolTip(medium_entry, text="Medium")

        mat_img = CTkImage(Image.open("images/icons/Socials/Matrix.png"), size=(30,25))
        img_label = CTkLabel(social_frame, text="", image=mat_img).place(relx=0.02, rely=0.58, anchor="w")
        matrix_url = "https://matrix.to/#/#official-verifyvault:matrix.org"
        matrix_entry = CTkEntry(social_frame, font=("Helvetica", 18, "bold"), border_width=2, border_color="#0DBD8B", corner_radius=5, width=400)
        matrix_entry.place(relx=0.08, rely=0.56, anchor="nw")

        matrix_entry.insert(0, matrix_url)
        matrix_entry.bind("<Key>", prevent_input)
        matrix_entry.bind("<Button-3>", open_url)
        matrix_entry.bind("<Button-1>", copy_to_clipboard)
        ToolTip(matrix_entry, text="Matrix")

    # Function to display donation addresses
    def donations(self):
        donation_frame = CTkFrame(self.right_frame, width=600, height=700)
        donation_frame.place(relx=0.61, rely=0, anchor="n")

        def close_frame():
            donation_frame.destroy()

        x_button = CTkButton(donation_frame, command=close_frame, text="❌", fg_color="white", border_color="black", text_color="black", hover_color="red", border_width=2, width=50, height=20, cursor="hand2")
        x_button.place(relx=0.8, rely= 0.03, anchor="ne")

        title_label = CTkLabel(donation_frame, text="Contribute to VerifyVault", font=("Helvetica", 30, "bold"))
        title_label.place(relx=0.4, rely=0.1, anchor="center")

        # Function to prevent input
        def prevent_input(event):
            messagebox.showerror("Use Copy Button", "To copy, click the Copy button.")
            return "break"

        # Function to copy donate address
        def copy_to_clipboard(event):
            widget = event.widget
            add = widget.get()
            pyperclip.copy(add)
            messagebox.showinfo("Copied", "The address has been copied to the clipboard!")

        # Donation address initialization
        mon_img = CTkImage(Image.open("images/icons/Donate/Monero.png"), size=(30,25))
        img_label = CTkLabel(donation_frame, text="", image=mon_img).place(relx=0.05, rely=0.19, anchor="w")
        monero_add = "43YvGR6aUTTG6sAf5Ain8WeJ2fUq6iraUV7VWt9UwsBA8bNctzsndUn1b39asA6Eb1MSpRTjeddwuX4nHQqKnwa7EcCHX9Q"
        monero_entry = CTkEntry(donation_frame, font=("Helvetica", 18, "bold"), border_width=2, border_color="#FF6600", corner_radius=5, width=400)
        monero_entry.place(relx=0.15, rely=0.17, anchor="nw")
        
        monero_entry.insert(0, monero_add)
        monero_entry.bind("<Key>", prevent_input)
        monero_entry.bind("<Button-1>", copy_to_clipboard)
        ToolTip(monero_entry, text="Monero")

        btc_img = CTkImage(Image.open("images/icons/Donate/Bitcoin.png"), size=(30,25))
        img_label = CTkLabel(donation_frame, text="", image=btc_img).place(relx=0.05, rely=0.27, anchor="w")
        bitcoin_add = "bc1q3zqeh99p8efuldmn27e44tpajzymafvfyfaqus"
        bitcoin_entry = CTkEntry(donation_frame, font=("Helvetica", 18, "bold"), border_width=2, border_color="#F7931A", corner_radius=5, width=400)
        bitcoin_entry.place(relx=0.15, rely=0.25, anchor="nw")

        bitcoin_entry.insert(0, bitcoin_add)
        bitcoin_entry.bind("<Key>", prevent_input)
        bitcoin_entry.bind("<Button-1>", copy_to_clipboard)
        ToolTip(bitcoin_entry, text="Bitcoin")

        eth_img = CTkImage(Image.open("images/icons/Donate/Ethereum.png"), size=(30,25))
        img_label = CTkLabel(donation_frame, text="", image=eth_img).place(relx=0.05, rely=0.35, anchor="w")
        ether_add = "0x7Af3ee1251c0428b7ba6E1dEaB913ac029e58E1e"
        ether_entry = CTkEntry(donation_frame, font=("Helvetica", 18, "bold"), border_width=2, border_color="#3C3C3D", corner_radius=5, width=400)
        ether_entry.place(relx=0.15, rely=0.33, anchor="nw")
        
        ether_entry.insert(0, ether_add)
        ether_entry.bind("<Key>", prevent_input)
        ether_entry.bind("<Button-1>", copy_to_clipboard)
        ToolTip(ether_entry, text="Ethereum")

        lit_img = CTkImage(Image.open("images/icons/Donate/Litecoin.png"), size=(30,25))
        img_label = CTkLabel(donation_frame, text="", image=lit_img).place(relx=0.05, rely=0.43, anchor="w")
        litecoin_add = "LQakrnCZoSDWioe7qp7SPB9dkP4Tdx4oJd"
        litecoin_entry = CTkEntry(donation_frame, font=("Helvetica", 18, "bold"), border_width=2, border_color="#A6A9AA", corner_radius=5, width=400)
        litecoin_entry.place(relx=0.15, rely=0.41, anchor="nw")

        litecoin_entry.insert(0, litecoin_add)
        litecoin_entry.bind("<Key>", prevent_input)
        litecoin_entry.bind("<Button-1>", copy_to_clipboard)
        ToolTip(litecoin_entry, text="Litecoin")
