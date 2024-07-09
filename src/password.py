import os, bcrypt

class PasswordManager:
    def __init__(self):
        # Sets the initial password configurations
        self.password_hash = None
        self.password_file = ".secure"
        self.salt = bcrypt.gensalt()

    # Function that hashes the password
    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode(), self.salt)

        with open(self.password_file, "wb") as f:
            f.write(self.password_hash)
        os.chmod(self.password_file, 0o700)

    # Function that verifies if the password is correct
    def verify_password(self, password):
        with open(self.password_file, "rb") as f:
            saved_password_hash = f.read()
        return bcrypt.checkpw(password.encode(), saved_password_hash)

    # Function that loads the password from the file
    def load_password(self):
        with open(self.password_file, "rb") as f:
            self.password_hash = f.read()

    # Function that adds the password to the file
    def add_password(self, password):
        with open(self.password_file, "wb") as f:
            f.write(password)

    # Function that retrieves the password from the file
    def get_password(self):
        return self.password_hash

