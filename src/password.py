import os
import bcrypt
from keys import insert_key, retrieve_key

class PasswordManager:
    def __init__(self):
        # Sets the initial password configurations
        self.password_hash = None
        self.salt = bcrypt.gensalt()

    # Function that hashes the password and saves the hash in keys.db
    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode(), self.salt)
        insert_key('pw_hash', self.password_hash)

    # Function that verifies if the password is correct
    def verify_password(self, password):
        saved_password_hash = retrieve_key()
        if saved_password_hash:
            return bcrypt.checkpw(password.encode(), saved_password_hash)
        return False

    # Function that loads the password hash from keys.db
    def load_password_hash(self):
        self.password_hash = get_password_hash()

    # Function that retrieves the password hash
    def get_password_hash(self):
        return self.password_hash
