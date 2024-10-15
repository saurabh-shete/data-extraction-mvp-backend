# src/utils/helpers/encryption_helper.py
import bcrypt

# Password Encryption
def encrypt(password):
    salt = bcrypt.gensalt(rounds=10)
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


# Password Comparison
def compare(password, encoded_password):
    return bcrypt.checkpw(password.encode('utf-8'), encoded_password.encode('utf-8'))
