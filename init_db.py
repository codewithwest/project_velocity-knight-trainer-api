import os
import secrets
import string
import bcrypt
from config import Connection

def generate_strong_password(length=12):
    """Generates a strong random password."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = ''.join(secrets.choice(alphabet) for i in range(length))
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in string.punctuation for c in password)):
            break
    return password

def drop_users_collection():
    """Drops the users collection from the database."""
    db = Connection.get_db()
    db.drop_collection('users')
    print("Users collection dropped.")

def initialize_database():
    """Initializes the database with a default admin user if one doesn't exist."""
    db = Connection.get_db()
    users_collection = db.get_collection('users')

    # Check if an admin user already exists
    if users_collection.find_one({"is_admin": True}):
        print("Admin user already exists.")
        return

    # Create a new admin user
    admin_email = "admin@vkt.com"
    admin_password = generate_strong_password()
    hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())

    users_collection.insert_one({
        "email": admin_email,
        "password": hashed_password, # Store the hashed password
        "name": "Admin",
        "is_admin": True
    })

    print("="*50)
    print("Default Admin User Created")
    print(f"Email: {admin_email}")
    print(f"Password: {admin_password}")
    print("Please save this password securely. You will not be able to retrieve it again.")
    print("="*50)

if __name__ == "__main__":
    # drop_users_collection() # Commented out to prevent accidental data loss
    initialize_database()
