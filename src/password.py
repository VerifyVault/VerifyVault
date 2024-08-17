import bcrypt
from keys import insert_key, retrieve_key

class PasswordManager:
    def __init__(self):
        # Sets the initial password configurations
        self.password_hash = None
        self.name = None
        self.salt = bcrypt.gensalt()

    # Function to hash/save the password
    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode(), self.salt)
        insert_key('pw_hash', self.password_hash)

    # Function to verify the password
    def verify_password(self, password):
        saved_password_hash = retrieve_key('pw_hash')
        if saved_password_hash:
            return bcrypt.checkpw(password.encode(), saved_password_hash)
        return False

    # Function to set password hash
    def load_password_hash(self):
        self.password_hash = get_password_hash()

    # Function to retrieve password hash
    def get_password_hash(self):
        return self.password_hash
