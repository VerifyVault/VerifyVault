import threading, shutil, qrcode, pyotp, time, json, sys, os

print("[2FA App]")

def load_accounts():
    if os.path.exists("data.json"):
        with open("data.json", "r") as file:
            try:
                accounts = json.load(file)
            except json.JSONDecodeError:
                print("Error: Unable to decode JSON file. Resetting accounts.")
                accounts = {}
                
        filtered_accounts = {}
        for name, info in accounts.items():
            if not name.startswith("C:/"):
                filtered_accounts[name] = info
        
        return filtered_accounts
    else:
        return {}

def save_accounts(accounts):
    filtered_accounts = {name: info for name, info in accounts.items() if not name.startswith("C:/")}
    with open("data.json", "w") as file:
        json.dump(filtered_accounts, file)

def export_json():
    src_file = "data.json"
    dest_dir = input("Enter the destination directory: ")
    dest_file = os.path.join(dest_dir, "data.json")
    shutil.copy(src_file, dest_file)
    print(f"JSON file exported to {dest_file}")

def export_totps(accounts):
    for name, info in accounts.items():
        secret = info['secret']
        totp = pyotp.TOTP(secret)
        img = qrcode.make(totp.provisioning_uri(name))
        img_path = f"{name}.png"
        img.save(img_path)
        print(f"QR code for {name} saved as {img_path}")

accounts = load_accounts()

last_display_time = 0
timer_running = False

def clear_screen():
    if os.name == 'posix':
        _ = os.system('clear')
    else:
        _ = os.system('cls')

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
                
                save_accounts(accounts)
                
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
                    save_accounts(accounts)
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

if __name__ == "__main__":
    main()
