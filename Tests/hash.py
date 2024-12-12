import bcrypt

# List of passwords
passwords = [
    "adminPW-1212",
    "Sunset!1743",
    "Sunflower#537",
    "Mountain%485",
    "Eagle!842"
]

# Function to hash passwords
def hash_passwords(password_list):
    hashed_passwords = {}
    for idx, password in enumerate(password_list):
        # Generate a salt and hash the password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        hashed_passwords[f"Emp ID {101 + idx}"] = hashed.decode('utf-8')
    return hashed_passwords

# Hash the passwords and print them
hashed_passwords = hash_passwords(passwords)
for emp_id, hashed in hashed_passwords.items():
    print(f"{emp_id}: {hashed}")
