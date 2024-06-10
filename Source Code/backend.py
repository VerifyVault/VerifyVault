import threading, shutil, qrcode, pyotp, time, json, sys, os, hashlib
from cryptography.fernet import Fernet, InvalidToken

print("[2FA App]")

# Generates/loads encryption key
def generate_key():
    return Fernet.generate_key()
def load_key():
    try:
        with open(get_key_filename(), "rb") as key_file:
            return key_file.read()
    except FileNotFoundError:
        key = generate_key()
        save_key(key)
        return key

#Gets/sets encryption key file
def get_key_filename():
    key_identifier = "encryption_key"
    return generate_hash(key_identifier) + ".vv"

#Saves encryption key
def save_key(key):
    with open(get_key_filename(), "wb") as key_file:
        key_file.write(key)
    os.chmod(get_key_filename(), 0o700)

#Generates name for key file
def generate_hash(data):
    hasher = hashlib.sha256()
    hasher.update(data.encode())
    return hasher.hexdigest()

#Encrypt and decrypt functions
def encrypt_message(message, key):
    f = Fernet(key)
    return f.encrypt(message.encode())
def decrypt_message(encrypted_message, key):
    f = Fernet(key)
    return f.decrypt(encrypted_message).decode()

#Loads accounts
def load_accounts(key):
    if os.path.exists("data.json.vv"):
        with open("data.json.vv", "rb") as file:
            try:
                encrypted_data = file.read()
                decrypted_data = decrypt_message(encrypted_data, key)
                accounts = json.loads(decrypted_data)
            except (json.JSONDecodeError, InvalidToken):
                print("Error: Unable to decode or decrypt JSON file. Resetting accounts.")
                accounts = {}
    else:
        accounts = {}
    return accounts

#Saves accounts
def save_accounts(accounts, key):
    with open("data.json.vv", "wb") as file:
        encrypted_data = encrypt_message(json.dumps(accounts), key)
        file.write(encrypted_data)
    os.chmod("data.json.vv", 0o700)

#Exports accounts through .json
def export_json():
    src_file = "data.json"
    dest_dir = input("Enter the destination directory: ")
    dest_file = os.path.join(dest_dir, "data.json")
    shutil.copy(src_file, dest_file)
    print(f"JSON file exported to {dest_file}")

#Exports accounts through QR Code(s)
def export_totps(accounts):
    for name, info in accounts.items():
        secret = info['secret']
        totp = pyotp.TOTP(secret)
        img = qrcode.make(totp.provisioning_uri(name))
        img_path = f"{name}.png"
        img.save(img_path)
        print(f"QR code for {name} saved as {img_path}")

key = load_key()
accounts = load_accounts(key)

last_display_time = 0
timer_running = False

#Clears screen
def clear_screen():
    if os.name == 'posix':
        _ = os.system('clear')
    else:
        _ = os.system('cls')

#Displays accounts
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

#Main Menu
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
                
                save_accounts(accounts, key)  # Ensure to pass the key here
                
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
                    save_accounts(accounts, key)  # Ensure to pass the key here
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

#Calls main function
if __name__ == "__main__":
    main()
