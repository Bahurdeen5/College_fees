import bcrypt
from backend.db import create_connection

# Get DB connection
conn, cur = create_connection()

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def login(username, password):
    cur.execute("SELECT password, role FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    if user and verify_password(password, user[0]):
        return user[1]  # return role
    return None

def check_auth(session_state, required_role):
    if not session_state.get("auth") or session_state.auth.get("role") != required_role:
        return False
    return True
