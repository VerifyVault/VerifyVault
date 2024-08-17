import sqlite3

# Function to create database file
def create_database_if_not_exists():
    conn = sqlite3.connect('keys.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS encryption_keys
                 (name TEXT PRIMARY KEY, key TEXT)''')

    conn.commit()
    conn.close()

# Function to add key to database
def insert_key(name, key):
    create_database_if_not_exists()
    conn = sqlite3.connect('keys.db')
    c = conn.cursor()

    try:
        c.execute('INSERT INTO encryption_keys (name, key) VALUES (?, ?)', (name, key))
        conn.commit()
        print(f"Key '{name}' successfully inserted into the database.")
    except sqlite3.IntegrityError:
        print(f"Key '{name}' already exists in the database. Use update_key() to update it.")

    conn.close()

# Function to access key in database
def retrieve_key(name):
    create_database_if_not_exists()
    conn = sqlite3.connect('keys.db')
    c = conn.cursor()

    c.execute('SELECT key FROM encryption_keys WHERE name=?', (name,))
    key = c.fetchone()

    conn.close()

    if key:
        return key[0]
    else:
        print(f"Key '{name}' not found in the database.")
        return None

# Function to update key in database
def update_key(name, new_key):
    create_database_if_not_exists()
    conn = sqlite3.connect('keys.db')
    c = conn.cursor()

    try:
        c.execute('UPDATE encryption_keys SET key=? WHERE name=?', (new_key, name))
        conn.commit()
        print(f"Key '{name}' updated successfully.")
    except sqlite3.Error as e:
        print(f"Error updating key '{name}': {e}")

    conn.close()

# Function to delete key in database
def delete_key(name):
    create_database_if_not_exists()
    conn = sqlite3.connect('keys.db')
    c = conn.cursor()

    try:
        c.execute('DELETE FROM encryption_keys WHERE name=?', (name,))
        conn.commit()
        print(f"Key '{name}' deleted successfully.")
    except sqlite3.Error as e:
        print(f"Error deleting key '{name}': {e}")

    conn.close()

