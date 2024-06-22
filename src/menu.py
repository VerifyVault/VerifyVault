import tkinter as tk
import tkinter as ttk
import pyperclip, webbrowser
from notifications import NotificationFrame

class MenuManager:
    def __init__(self, master):
        #Setting objects
        self.master = master
        self.menubar = tk.Menu(master)
        self.notifications = NotificationFrame(master)

        # Guide Menu
        self.guide_menu = tk.Menu(self.menubar, tearoff=0)
        self.guide_menu.add_command(label="Basic Functionality", command=self.guide_menu_functionality)
        self.guide_menu.add_command(label="Add Account", command=self.guide_menu_account)
        self.guide_menu.add_command(label="Settings", command=self.guide_menu_settings)
        self.guide_menu.add_command(label="Edit", command=self.guide_menu_edit)
        self.guide_menu.add_command(label="Common Errors", command=self.guide_menu_errors)
        self.menubar.add_cascade(label="Guide", menu=self.guide_menu)

        # Social Menu
        self.social_menu = tk.Menu(self.menubar, tearoff=0)
        self.social_menu.add_command(label="GitHub", command=self.copy_github_url)
        self.social_menu.add_command(label="Reddit", command=self.copy_reddit_url)
        self.social_menu.add_command(label="Mastodon", command=self.copy_mastodon_url)
        self.social_menu.add_command(label="Matrix", command=self.copy_matrix_url)
        self.social_menu.add_command(label="Twitter", command=self.copy_twitter_url)
        self.menubar.add_cascade(label="Socials", menu=self.social_menu)

        # Donate Menu
        self.donate_menu = tk.Menu(self.menubar, tearoff=0)
        self.donate_menu.add_command(label="Monero", command=lambda: self.copy_donation_address("Monero"))
        self.donate_menu.add_command(label="Bitcoin", command=lambda: self.copy_donation_address("Bitcoin"))
        self.donate_menu.add_command(label="Ethereum", command=lambda: self.copy_donation_address("Ethereum"))
        self.donate_menu.add_command(label="Litecoin", command=lambda: self.copy_donation_address("Litecoin"))
        self.menubar.add_cascade(label="Donate", menu=self.donate_menu)
        
        master.config(menu=self.menubar)

    #Open Social URLs
    def copy_github_url(self):
        url = "https://github.com/VerifyVault"
        webbrowser.open(url)

    def copy_reddit_url(self):
        url = "https://www.reddit.com/user/OffVerifyVault-/"
        webbrowser.open(url)

    def copy_mastodon_url(self):
        url = "https://mastodon.social/@verifyvault"
        webbrowser.open(url)

    def copy_matrix_url(self):
        url = "https://matrix.to/#/#official-verifyvault:matrix.org"
        webbrowser.open(url)

    def copy_twitter_url(self):
        url = "https://x.com/VeryfyVault"
        webbrowser.open(url)

    #Copy Donation Addresses
    def copy_donation_address(self, currency):
        donation_addresses = {
            "Monero": "43YvGR6aUTTG6sAf5Ain8WeJ2fUq6iraUV7VWt9UwsBA8bNctzsndUn1b39asA6Eb1MSpRTjeddwuX4nHQqKnwa7EcCHX9Q",
            "Bitcoin": "bc1q3zqeh99p8efuldmn27e44tpajzymafvfyfaqus",
            "Ethereum": "0x7Af3ee1251c0428b7ba6E1dEaB913ac029e58E1e",
            "Litecoin": "LQakrnCZoSDWioe7qp7SPB9dkP4Tdx4oJd"
        }
        address = donation_addresses.get(currency, "Address not found")
        pyperclip.copy(address)
        self.notifications.show_notification(f"{currency} donation address copied to clipboard!")

    #Guides - Sets configurations, adds closing functionality
    def show_basic_functionality(self):
        basic_functionality_window = tk.Toplevel(self.master)
        basic_functionality_window.title("Basic Functionality")
        basic_functionality_window.geometry("800x400")
        basic_functionality_window.resizable(False, False)
        basic_functionality_window.configure(bg="white")

        frame = tk.Frame(basic_functionality_window, bg="white", bd=0)
        frame.pack(fill="both", expand=True)

        text = """
        • To copy a 2FA code, click on the frame of the account you want to copy.\n\n
        • To copy any Crypto Addresses, click the option, it will automatically copy to your clipboard.\n\n
        • To open any Social Media pages click the option, it will automatically open in your browser.\n\n
        • Add Account - Add a new account.\n\n
        • Settings - Import/Export.\n\n
        • Search - Search for an account.\n\n
        • Edit - Edit name/Export account/Delete account."""

        label = tk.Label(frame, text=text, justify="left", font=("Helvetica", 12), bg="white", padx=10, pady=10, highlightthickness=0, highlightbackground="white")
        label.pack()

        def close_window():
            basic_functionality_window.destroy()

    def guide_menu_functionality(self):
        self.show_basic_functionality()

    def add_account_help(self):
        add_account_help = tk.Toplevel(self.master)
        add_account_help.title("Add Account Help")
        add_account_help.geometry("800x400")
        add_account_help.resizable(False, False)
        add_account_help.configure(bg="white")

        frame = tk.Frame(add_account_help, bg="white", bd=0)
        frame.pack(fill="both", expand=True)

        text = """
        1) Click the "Add Account" button on the top left\n
        2) Enter in the name of the account, press "Continue" or hit "Enter" on your keyboard\n
        3) Enter the Secert Key provided by the service, press "Confirm" or hit "Enter" on your keyboard\n
        4) Added!"""

        label = tk.Label(frame, text=text, justify="left", font=("Helvetica", 12), bg="white", padx=10, pady=10, highlightthickness=0, highlightbackground="white")
        label.pack(padx=10, pady=10)

        def close_window():
            add_account_help.destroy()

    def guide_menu_account(self):
        self.add_account_help()

    def settings_help(self):
        settings_help = tk.Toplevel(self.master)
        settings_help.title("Settings Help")
        settings_help.geometry("800x400")
        settings_help.resizable(False, False)
        settings_help.configure(bg="white")
        
        frame = tk.Frame(settings_help, bg="white", bd=0)
        frame.pack(fill="both", expand=True)

        text = """
        • Import Data - File type must be .json, all new accounts will be added.\n\n
        • Export Data - To export accounts to a new app choose JSON, to export specific accounts choose QR Codes"""

        label = tk.Label(frame, text=text, justify="left", font=("Helvetica", 12), bg="white", padx=10, pady=10, highlightthickness=0, highlightbackground="white")
        label.pack(padx=10, pady=10)

        def close_window():
            settings_help.destroy()

    def guide_menu_settings(self):
        self.settings_help()

    def edit_help(self):
        edit_help = tk.Toplevel(self.master)
        edit_help.title("Edit Account Help")
        edit_help.geometry("800x400")
        edit_help.resizable(False, False)
        edit_help.configure(bg="white")

        frame = tk.Frame(edit_help, bg="white", bd=0)
        frame.pack(fill="both", expand=True)

        text = """
        • Edit Name - Name must be different, click "Confirm" or hit "Enter" on your keyboard to confirm.\n\n
        • Export QR Code - Exports QR Code for the specific account, pick the path.\n\n
        • Delete Account - Warning popup will appear, hitting "Enter" on your keyboard WILL delete the account."""

        label = tk.Label(frame, text=text, justify="left", font=("Helvetica", 12), bg="white", padx=10, pady=10, highlightthickness=0, highlightbackground="white")
        label.pack(padx=10, pady=10)

        def close_window():
            edit_help.destroy()

    def guide_menu_edit(self):
        self.edit_help()

    def common_errors(self):
        common_errors = tk.Toplevel(self.master)
        common_errors.title("Common Errors")
        common_errors.geometry("800x400")
        common_errors.resizable(False, False)
        common_errors.configure(bg="white")

        frame = tk.Frame(common_errors, bg="white", bd=0)
        frame.pack(fill="both", expand=True)

        text = """
        • Name Required - You haven't entered a name.\n\n
        • Character limit is 30 - Your name has reached the limit of 30 characters\n\n
        • Override account - An account with the same name already exist, choosing to override will replace your old 
        account\n\n
        • Please enter a valid key - Your secert key is invalid, verify its correct.\n\n
        • Invalid TOTP Key - Please enter a valid key - Your secert key is invalid, verify its correct.\n\n
        • Invalid format - File/input format incorrect.\n\n
        • Invalid Name - No name inputted or name is already in use.
        """

        label = tk.Label(frame, text=text, justify="left", font=("Helvetica", 12), bg="white", padx=10, pady=10, highlightthickness=0, highlightbackground="white")
        label.pack(padx=10, pady=10)

        def close_window():
            common_errors.destroy()

    def guide_menu_errors(self):
        self.common_errors()
