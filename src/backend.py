from cryptography.fernet import Fernet, InvalidToken
import keys, threading, shutil, qrcode, pyotp, time, json, sys, os, ctypes, binascii

print("[2FA App]")

FILE_ATTRIBUTE_HIDDEN = 0x02

# Generates or loads the encryption key for securing sensitive data.
def load_key():
    data_key = keys.retrieve_key('data_key')
    if data_key:
        return data_key.encode()
    else:
        key = Fernet.generate_key()
        keys.insert_key('data_key', key.decode())
        return key

# Generates or loads a separate encryption key for grouping accounts.
def load_groups_key():
    group_key = keys.retrieve_key('group_key')
    if group_key:
        return group_key.encode()
    else:
        key = Fernet.generate_key()
        keys.insert_key('group_key', key.decode())
        return key

# Generates and loads a key for storing preferences..
def load_pref_key():
    pref_key = Fernet.generate_key()
    if not keys.retrieve_key('pref_key'):
        keys.insert_key('pref_key', pref_key.decode())
    return pref_key

# Generates or loads the recycling key used for temporarily deleted accounts.
def load_rec_key():
    recycle_key = keys.retrieve_key('recycle_key')
    if recycle_key:
        return recycle_key.encode()
    else:
        key = Fernet.generate_key()
        keys.insert_key('recycle_key', key.decode())
        return key

# Generates or loads the hint key for providing account hints.
def load_hint_key():
    hint_key = keys.retrieve_key('hint_key')
    if hint_key:
        return hint_key.encode()
    else:
        key = Fernet.generate_key()
        keys.insert_key('hint_key', key.decode())
        return key

# Encrypts a given message using the provided key.
def encrypt_message(message, key):
    f = Fernet(key)
    return f.encrypt(message.encode())

# Decrypts an encrypted message using the provided key.
def decrypt_message(encrypted_message, key):
    f = Fernet(key)
    return f.decrypt(encrypted_message).decode()

# Validates a TOTP key by checking if the current TOTP code is valid.
def is_valid_totp_key(key):
    try:
        totp = pyotp.TOTP(key)
        if totp.verify(totp.now()):
            return True
        else:
            print("Invalid TOTP code.")
            return Falseadd
    except (ValueError, binascii.Error) as e:
        if "Non-base32 digit found" in str(e):
            print("Invalid TOTP Key Format.")
        else:
            print(f"Error generating TOTP: {e}")
        return False

# Validates the account name by ensuring it doesn't contain invalid characters.
def validate_name(name):
    invalid_chars = "\\/:*?\"<>|"
    if any(char in invalid_chars for char in name):
        return False
    return True

# Marks a file as hidden on the filesystem based on the operating system.
def mark_file_hidden(file_path):
    if os.name == 'nt':
        ctypes.windll.kernel32.SetFileAttributesW(file_path, FILE_ATTRIBUTE_HIDDEN)
    elif os.name == 'posix':
        if os.uname().sysname == 'Linux' or os.uname().sysname == 'Darwin':
            make_file_hidden_unix(file_path)

# Helper function for Unix-based systems to hide a file by renaming it.
def make_file_hidden_unix(file_path):
    directory, filename = os.path.split(file_path)
    hidden_file_path = os.path.join(directory, '.' + filename)
    if not os.path.exists(hidden_file_path):
        os.rename(file_path, hidden_file_path)
        print(f"File renamed to {hidden_file_path} to hide it")
    else:
        print(f"Hidden file already exists: {hidden_file_path}")

# Unhides a hidden file on the filesystem.
def unhide_file(file_path):
    if os.name == 'nt':
        ctypes.windll.kernel32.SetFileAttributesW(file_path, ctypes.windll.kernel32.GetFileAttributesW(file_path) & ~0x02)
    elif os.name == 'posix':
        if os.uname().sysname == 'Linux' or os.uname().sysname == 'Darwin':
            self.make_file_visible_unix(file_path)

# Helper function for Unix-based systems to unhide a file by renaming it back.
def make_file_visible_unix(file_path):
    directory, filename = os.path.split(file_path)
    hidden_file_path = os.path.join(directory, '.' + filename)
    if os.path.exists(hidden_file_path):
        os.rename(hidden_file_path, file_path)
        print(f"File renamed to {file_path} to make it visible")
    else:
        print(f"No hidden file to unhide: {hidden_file_path}")
        
# Loads accounts from a JSON file, decrypting the content.
def load_accounts(key):
    unhide_file("data.json")
    key = load_key()
    if os.path.exists("data.json"):
        with open("data.json", "rb") as file:
            try:
                encrypted_data = file.read()
                decrypted_data = decrypt_message(encrypted_data, key)
                accounts = json.loads(decrypted_data)
            except (json.JSONDecodeError, InvalidToken):
                print("Error: Unable to decode or decrypt JSON file. Resetting accounts.")
                accounts = {}
    else:
        accounts = {}
        keys.delete_key("data_key")
    mark_file_hidden("data.json")
    return accounts

# Saves accounts to a JSON file, encrypting the content.
def save_accounts(accounts, key):
    unhide_file("data.json")
    key = load_key()
    with open("data.json", "wb") as file:
        encrypted_data = encrypt_message(json.dumps(accounts), key)
        file.write(encrypted_data)
    mark_file_hidden("data.json")

# Exports accounts as a JSON file to a specified destination directory.
def export_json():
    src_file = "data.json"
    dest_dir = input("Enter the destination directory: ")
    dest_file = os.path.join(dest_dir, "data.json")
    shutil.copy(src_file, dest_file)
    print(f"JSON file exported to {dest_file}")

# Exports accounts by generating QR codes for each TOTP.
def export_totps(accounts):
    for name, info in accounts.items():
        secret = info['secret']
        totp = pyotp.TOTP(secret)
        img = qrcode.make(totp.provisioning_uri(name))
        img_path = f"{name}.png"
        img.save(img_path)
        print(f"QR code for {name} saved as {img_path}")\

# Sets up the key and loads existing accounts.
key = load_key()
accounts = load_accounts(key)
last_display_time = 0
timer_running = False

# Clears the terminal screen.
def clear_screen():
    if os.name == 'posix':
        _ = os.system('clear')
    else:
        _ = os.system('cls')

# Displays TOTP codes and refresh countdown for saved accounts.
def countdown_timer():
    global timer_running
    while timer_running:
        clear_screen()
        current_time = time.time()

        print("[Saved Accounts] - Press Enter to stop displaying accounts")
        for name, info in accounts.items():
            secret = info['secret']
            totp = pyotp.TOTP(secret)
            remaining_time = 30 - (current_time - (current_time // 30) * 30)
            remaining_time = max(0, int(remaining_time))
            countdown = time.strftime("%M:%S", time.gmtime(remaining_time))
            print(f"Name: {name} | TOTP: {totp.now()} | Time until refresh: {countdown}")            
        time.sleep(1)


# Main menu for user interaction with the application.
def main():
    global timer_running
    while True:
        add_acc = input("\n1) Add Account\n2) Display Accounts\n3) Delete Account\n4) Settings\n5) Exit\nI choose: ")

        if add_acc == '1':
            clear_screen()
            while True:
                name = input("Name: ")
                if not name:
                    break
                key = input("Key: ")
                accounts[name] = {'key': key, 'secret': pyotp.TOTP(key).secret}
                
                save_accounts(accounts, key)
                
                exit = input("Exit (Yes/No)? ")
                if exit.lower() == "yes":
                    clear_screen()
                    break

        elif add_acc == '2':
            timer_running = True
            threading.Thread(target=countdown_timer, daemon=True).start()
            print()
            input()
            timer_running = False

        elif add_acc == '3':
            while True:
                clear_screen()
                print("[Delete Account]")
                account_to_delete = input("Enter the name of the account to delete (press Enter to go back): ")
                if not account_to_delete:
                    break
                if account_to_delete in accounts:
                    del accounts[account_to_delete]
                    print("Account deleted successfully!")
                    save_accounts(accounts, key)
                else:
                    print("Account not found!")

        elif add_acc == '4':
            clear_screen()
            print("\n[Settings]")
            while True:
                option = input("Choose an option:\n1) Export JSON file\n2) Export TOTP(s)\n3) Exit\nI choose: ")
                if option == '1':
                    export_json()
                elif option == '2':
                    export_totps(accounts)
                elif option == '3':
                    break
                else:
                    print("Invalid option!")

        elif add_acc == '5':
            print("\nExiting...")
            break

        else:
            print("Invalid Input!")

# Calls main function to start the application.
if __name__ == "__main__":
    main()
