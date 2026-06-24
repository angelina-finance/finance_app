import hashlib
import secrets
from datetime import datetime

def generate_salt(length=16):
    return secrets.token_bytes(length)

def hash_password(password, salt=None):
    if salt is None:
        salt = generate_salt()
    salt_hex = salt.hex() if isinstance(salt, bytes) else salt
    salt_bytes = bytes.fromhex(salt_hex) if isinstance(salt, str) else salt
    pwd_bytes = password.encode('utf-8')
    salted = pwd_bytes + salt_bytes
    pwd_hash = hashlib.sha256(salted).hexdigest()
    return salt_hex, pwd_hash

def verify_password(password, salt_hex, stored_hash):
    _, computed_hash = hash_password(password, salt_hex)
    return computed_hash == stored_hash

def validate_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_email(email):
    return '@' in email if email else True

def validate_amount(amount_str):
    try:
        val = float(amount_str)
        return val > 0
    except ValueError:
        return False