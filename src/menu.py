import tkinter as tk
import tkinter as ttk
import pyperclip, webbrowser
from notifications import NotificationFrame

class MenuManager:
    def __init__(self, master):
        # Menu.py configurations
        self.master = master
        self.menubar = tk.Menu(master)
        self.notifications = NotificationFrame(master)

        # Guide Menu
        self.guide_menu = tk.Menu(self.menubar, tearoff=0, bg="white")

        self.basics_menu = tk.Menu(self.guide_menu, tearoff=0, bg="white")
        self.basics_menu.add_command(label="Basic Functionality", command=self.guide_menu_functionality)
        self.basics_menu.add_command(label="Common Errors", command=self.guide_menu_errors)
        self.account_menu = tk.Menu(self.guide_menu, tearoff=0, bg="white")
        self.account_menu.add_command(label="Add Account", command=self.guide_menu_account)
        self.account_menu.add_command(label="Edit Account", command=self.guide_menu_edit)
        self.settings_menu = tk.Menu(self.guide_menu, tearoff=0, bg="white")
        self.settings_menu.add_command(label="Manage Password", command=self.guide_menu_password)
        self.settings_menu.add_command(label="Manage Data", command=self.guide_menu_data)
        self.settings_menu.add_command(label="Manage Preferences", command=self.guide_menu_pref)

        self.guide_menu.add_cascade(label="Basics", menu=self.basics_menu)
        self.guide_menu.add_cascade(label="Account", menu=self.account_menu)
        self.guide_menu.add_cascade(label="Settings", menu=self.settings_menu)
        self.menubar.add_cascade(label="Guide", menu=self.guide_menu)
        master.config(menu=self.menubar)

        # Social Menu
        self.socials_menu = tk.Menu(self.menubar, tearoff=0, bg="white")

        self.development_menu = tk.Menu(self.socials_menu, tearoff=0, bg="white")
        self.social_menu = tk.Menu(self.socials_menu, tearoff=0, bg="white")
        self.chat_menu = tk.Menu(self.socials_menu, tearoff=0, bg="white")
        self.blogs_menu = tk.Menu(self.socials_menu, tearoff=0, bg="white")

        self.development_menu.add_command(label="GitHub", command=self.copy_github_url)
        self.development_menu.add_command(label="SourceForge", command=self.copy_sourceforge_url)
        self.social_menu.add_command(label="Mastodon", command=self.copy_mastodon_url)
        self.social_menu.add_command(label="Twitter", command=self.copy_twitter_url)
        self.chat_menu.add_command(label="Discord", command=self.copy_discord_url)
        self.chat_menu.add_command(label="Matrix", command=self.copy_matrix_url)
        self.blogs_menu.add_command(label="Hashnode", command=self.copy_hashnode_url)
        self.blogs_menu.add_command(label="DEV.TO", command=self.copy_devto_url)

        self.socials_menu.add_cascade(label="Development", menu=self.development_menu)
        self.socials_menu.add_cascade(label="Socials", menu=self.social_menu)
        self.socials_menu.add_cascade(label="Chat", menu=self.chat_menu)
        self.socials_menu.add_cascade(label="Blogs", menu=self.blogs_menu)
        self.menubar.add_cascade(label="Socials", menu=self.socials_menu)
        master.config(menu=self.menubar)

        # Donate Menu
        self.donate_menu = tk.Menu(self.menubar, tearoff=0, bg="white")
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
    def copy_sourceforge_url(self):
        url = "https://sourceforge.net/projects/verifyvault/"
        webbrowser.open(url)
    def copy_mastodon_url(self):
        url = "https://mastodon.social/@verifyvault"
        webbrowser.open(url)
    def copy_twitter_url(self):
        url = "https://x.com/VeryfyVault"
        webbrowser.open(url)
    def copy_discord_url(self):
        url = "https://discord.gg/ckpKXmPe"
        webbrowser.open(url)
    def copy_matrix_url(self):
        url = "https://matrix.to/#/#official-verifyvault:matrix.org"
        webbrowser.open(url)
    def copy_hashnode_url(self):
        url = "https://verifyvault.hashnode.dev/"
        webbrowser.open(url)
        webbrowser.open(url)
    def copy_devto_url(self):
        url = "https://dev.to/verifyvault"
        webbrowser.open(url)

    # Function which copies the donation dddresses
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

    # Function which configures the Guides tab
    def show_basic_functionality(self):
        basic_functionality_window = tk.Toplevel(self.master)
        basic_functionality_window.title("Basic Functionality")
        basic_functionality_window.geometry("1000x400")
        basic_functionality_window.resizable(False, False)
        basic_functionality_window.configure(bg="white")

        frame = tk.Frame(basic_functionality_window, bg="white", bd=0)
        frame.pack(fill="both", expand=True)

        text = """
        • To access an account's TOTP and settings, click on the account.\n\n
        • To copy a crypto dddresses, click the name of the crypto and it will automatically copy to your clipboard.\n\n
        • To open any social Mmedia pages, hover over the category and click the name, it will automatically open in your browser.\n\n
        • Add Account - Add a new account.\n\n
        • Settings - Manage Password, Import/Export Data, Set Preferences.\n\n
        • Search - Search for an account.\n\n"""

        label = tk.Label(frame, text=text, justify="left", font=("Helvetica", 12), bg="white", padx=10, pady=10, highlightthickness=0, highlightbackground="white")
        label.pack()
        def close_window():
            basic_functionality_window.destroy()
    def guide_menu_functionality(self):
        self.show_basic_functionality()

    # Function which configures the Add Account Help tab
    def add_account_help(self):
        add_account_help = tk.Toplevel(self.master)
        add_account_help.title("Add Account Help")
        add_account_help.geometry("800x200")
        add_account_help.resizable(False, False)
        add_account_help.configure(bg="white")

        frame = tk.Frame(add_account_help, bg="white", bd=0)
        frame.pack(fill="both", expand=True)

        text = """
        1) Click the "Add Account" button on the top left.\n
        2) Enter in the name of the account, press "Continue" or hit "Enter" on your keyboard.\n
        3) Enter the Secret Key provided by the service, then press "Confirm" or hit "Enter" on your keyboard\n
        4) Added!"""

        label = tk.Label(frame, text=text, justify="left", font=("Helvetica", 12), bg="white", padx=10, pady=10, highlightthickness=0, highlightbackground="white")
        label.pack(padx=10, pady=10)
        def close_window():
            add_account_help.destroy()
    def guide_menu_account(self):
        self.add_account_help()

    # Function which configures the Edit Account Help tab
    def edit_help(self):
        edit_help = tk.Toplevel(self.master)
        edit_help.title("Edit Account Help")
        edit_help.geometry("1000x200")
        edit_help.resizable(False, False)
        edit_help.configure(bg="white")

        frame = tk.Frame(edit_help, bg="white", bd=0)
        frame.pack(fill="both", expand=True)

        text = """
        • Edit Name - Name must be different, click "Confirm" or hit "Enter" on your keyboard to confirm.\n\n
        • Export QR Code - Exports QR Code for the specific account, choose the path you would like it to be saved to.\n\n
        • Delete Account - Warning popup will appear, clicking "Yes" will move your account to the recycle bin until the end of the month."""

        label = tk.Label(frame, text=text, justify="left", font=("Helvetica", 12), bg="white", padx=10, pady=10, highlightthickness=0, highlightbackground="white")
        label.pack(padx=10, pady=10)
        def close_window():
            edit_help.destroy()
    def guide_menu_edit(self):
        self.edit_help()

    # Function which configures the Password Help tab
    def password_help(self):
        password_help = tk.Toplevel(self.master)
        password_help.title("Password Help")
        password_help.geometry("800x200")
        password_help.resizable(False, False)
        password_help.configure(bg="white")
        
        frame = tk.Frame(password_help, bg="white", bd=0)
        frame.pack(fill="both", expand=True)

        text = """
        • Set Password - Sets Master Password. No requirements, but please make it secure.\n\n
        • Remove Password - Removes Master Password.\n\n"""

        label = tk.Label(frame, text=text, justify="left", font=("Helvetica", 12), bg="white", padx=10, pady=10, highlightthickness=0, highlightbackground="white")
        label.pack(padx=10, pady=10)
        def close_window():
            password_help.destroy()
    def guide_menu_password(self):
        self.password_help()

    # Function which configures the Manage Data Help tab
    def data_help(self):
        data_help = tk.Toplevel(self.master)
        data_help.title("Manage Data Help")
        data_help.geometry("1000x200")
        data_help.resizable(False, False)
        data_help.configure(bg="white")
        
        frame = tk.Frame(data_help, bg="white", bd=0)
        frame.pack(fill="both", expand=True)

        text = """
        • Export Data - Export your vault data via QR code, .json (encrypted/unencrypted), or txt.\n\n
        • Import Data - Import your data via QR code or .json.\n\n
        • Recycle Bin - View all accounts deleted from your vault over the month. You can restore or permanently delete them."""

        label = tk.Label(frame, text=text, justify="left", font=("Helvetica", 12), bg="white", padx=10, pady=10, highlightthickness=0, highlightbackground="white")
        label.pack(padx=10, pady=10)
        def close_window():
            data_help.destroy()
    def guide_menu_data(self):
        self.data_help()

    # Function which configures the Manage Preferences Help tab
    def pref_help(self):
        pref_help = tk.Toplevel(self.master)
        pref_help.title("Manage Preferences Help")
        pref_help.geometry("1000x200")
        pref_help.resizable(False, False)
        pref_help.configure(bg="white")
        
        frame = tk.Frame(pref_help, bg="white", bd=0)
        frame.pack(fill="both", expand=True)

        text = """
        • Automatic Backups - Set your data to automatically backup every session. Choose the file path and how you want the data exported. 
        You will have access to the 5 most recent backups.\n\n
        • More options coming soon. Stay tuned!"""

        label = tk.Label(frame, text=text, justify="left", font=("Helvetica", 12), bg="white", padx=10, pady=10, highlightthickness=0, highlightbackground="white")
        label.pack(padx=10, pady=10)
        def close_window():
            pref_help.destroy()
    def guide_menu_pref(self):
        self.pref_help()

    # Function which configures the Common Errors tab
    def common_errors(self):
        common_errors = tk.Toplevel(self.master)
        common_errors.title("Common Errors")
        common_errors.geometry("800x500")
        common_errors.resizable(False, False)
        common_errors.configure(bg="white")

        frame = tk.Frame(common_errors, bg="white", bd=0)
        frame.pack(fill="both", expand=True)

        text = """
        • Name Required - You haven't entered a name.\n\n
        • Name cannot contain 'char' - You've inputted an invalid character, includes: "\\/:*?\"<>|"\n\n
        • Character limit is 30 - Your name has reached the limit of 30 characters\n\n
        • Name already exists - Name is already in use. \n\n
        • Override account - An account with the same name already exist, choosing to override will replace your old 
        account. Otherwise, the program will automatically rename your account with a (#) at the end.\n\n
        • Invalid Key - Your secert key is invalid, verify its correct.\n\n
        • Invalid Format - File/input format incorrect.\n\n
        """

        label = tk.Label(frame, text=text, justify="left", font=("Helvetica", 12), bg="white", padx=10, pady=10, highlightthickness=0, highlightbackground="white")
        label.pack(padx=10, pady=10)
        def close_window():
            common_errors.destroy()
    def guide_menu_errors(self):
        self.common_errors()
