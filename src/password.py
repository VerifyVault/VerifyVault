import os, bcrypt

class PasswordManager:
    def __init__(self):
        # Sets the initial password configurations
        self.password_hash = None
        self.password_file = ".secure"
        self.salt = bcrypt.gensalt()

    # Hashes the password
    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode(), self.salt)

        with open(self.password_file, "wb") as f:
            f.write(self.password_hash)
        os.chmod(self.password_file, 0o700)

    # Verifies if the password is correct
    def verify_password(self, password):
        with open(self.password_file, "rb") as f:
            saved_password_hash = f.read()
        return bcrypt.checkpw(password.encode(), saved_password_hash)

    # Loads password from file
    def load_password(self):
        with open(self.password_file, "rb") as f:
            self.password_hash = f.read()

    # Adds password to file
    def add_password(self, password):
        with open(self.password_file, "wb") as f:
            f.write(password)

    # Retrieves password from file
    def get_password(self):
        return self.password_hash

