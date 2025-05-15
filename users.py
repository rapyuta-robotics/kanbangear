import bcrypt

# Hash the password
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Verify password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# Update USERS dictionary to store usernames, hashed passwords, and roles
USERS = {
    "rr": {"password": hash_password("dina"), "role": "super_admin"},
    "user1": {"password": hash_password("airborne1"), "role": "user"},
    "user2": {"password": hash_password("airborne2"), "role": "user"},
    "admin1": {"password": hash_password("rr_airborne"), "role": "super_admin"},
    "user3": {"password": hash_password("airborne3"), "role": "user"},
    "fe": {"password": hash_password("airborne"), "role": "user"}
}

