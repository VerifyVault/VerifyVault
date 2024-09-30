from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import sqlite3, os, ctypes

# Variable initialization
FILE_ATTRIBUTE_HIDDEN = 0x02
DATABASE_FILE = 'keys.db'
ENCRYPTION_KEY_FILE = 'encryption_key.bin'
SALT = b'salt_32_bytes_salt_'

# Function to mark file as hidden on Windows
def mark_file_hidden(file_path):
    if os.name == 'nt':
        ctypes.windll.kernel32.SetFileAttributesW(file_path, FILE_ATTRIBUTE_HIDDEN)
    elif os.name == 'posix':
        make_file_hidden_unix(file_path)

#Function to mark file as hidden on Linux/Mac
def make_file_hidden_unix(file_path):
    directory, filename = os.path.split(file_path)
    hidden_file_path = os.path.join(directory, '.' + filename)
    if not os.path.exists(hidden_file_path):
        os.rename(file_path, hidden_file_path)

#Function to unmark file as hidden on Windows
def unhide_file(file_path):
    if os.name == 'nt':
        ctypes.windll.kernel32.SetFileAttributesW(file_path, ctypes.windll.kernel32.GetFileAttributesW(file_path) & ~0x02)
    elif os.name == 'posix':
        self.make_file_visible_unix(file_path)

#Function to unmark file as hidden on Linux/Mac
def make_file_visible_unix(file_path):
    directory, filename = os.path.split(file_path)
    hidden_file_path = os.path.join(directory, '.' + filename)
    if os.path.exists(hidden_file_path):
        os.rename(hidden_file_path, file_path)

# Function to retrieve key
def get_key():
    unhide_file(ENCRYPTION_KEY_FILE)
    if os.path.exists(ENCRYPTION_KEY_FILE):
        with open(ENCRYPTION_KEY_FILE, 'rb') as key_file:
            key = key_file.read()
    else:
        key = get_random_bytes(32)
        with open(ENCRYPTION_KEY_FILE, 'wb') as key_file:
            key_file.write(key)
    mark_file_hidden(ENCRYPTION_KEY_FILE)
    return key

# Function to encrypt data
def encrypt_data(data, key):
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return cipher.nonce + tag + ciphertext

# Function to decrypt data
def decrypt_data(data, key):
    nonce, tag, ciphertext = data[:16], data[16:32], data[32:]
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)

# Function to encrypt database
def encrypt_database():
    key = get_key()
    with open(DATABASE_FILE, 'rb') as db_file:
        data = db_file.read()
    encrypted_data = encrypt_data(data, key)
    with open(DATABASE_FILE, 'wb') as db_file:
        db_file.write(encrypted_data)

# Function to decrypt database
def decrypt_database():
    key = get_key()
    with open(DATABASE_FILE, 'rb') as db_file:
        encrypted_data = db_file.read()
    decrypted_data = decrypt_data(encrypted_data, key)
    with open(DATABASE_FILE, 'wb') as db_file:
        db_file.write(decrypted_data)

# Function to create database file
def create_database_if_not_exists():    
    if not os.path.exists(DATABASE_FILE):
        for file in ['data.json', 'encryption_key.bin', 'groups.json', 'deleted.json']:
            if os.path.exists(file):
                os.remove(file)

        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS encryption_keys
                     (name TEXT PRIMARY KEY, key TEXT)''')
        conn.commit()
        conn.close()
        encrypt_database()
        mark_file_hidden(DATABASE_FILE)
create_database_if_not_exists()

# Function to add key to database ile
def insert_key(name, key):
    unhide_file(DATABASE_FILE)
    decrypt_database()
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()

    try:
        c.execute('INSERT INTO encryption_keys (name, key) VALUES (?, ?)', (name, key))
        conn.commit()
    except sqlite3.IntegrityError:
        update_key(name, key)

    conn.close()
    encrypt_database()
    mark_file_hidden(DATABASE_FILE)

# Function to retrieve key from database
def retrieve_key(name):
    unhide_file(DATABASE_FILE)
    decrypt_database()

    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute('SELECT key FROM encryption_keys WHERE name=?', (name,))
    key = c.fetchone()
    conn.close()

    encrypt_database()
    mark_file_hidden(DATABASE_FILE)

    if key:
        return key[0]
    else:
        return None

# Function to update key
def update_key(name, new_key):
    decrypt_database()
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    try:
        c.execute('UPDATE encryption_keys SET key=? WHERE name=?', (new_key, name))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error updating key '{name}': {e}")
    conn.close()
    encrypt_database()
    mark_file_hidden(DATABASE_FILE)

# Function to delete key
def delete_key(name):
    unhide_file(DATABASE_FILE)
    decrypt_database()
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()

    try:
        c.execute('DELETE FROM encryption_keys WHERE name=?', (name,))
        conn.commit()
        print(f"Key '{name}' deleted successfully.")
    except sqlite3.Error as e:
        print(f"Error deleting key '{name}': {e}")

    conn.close()
    encrypt_database()
    mark_file_hidden(DATABASE_FILE)
