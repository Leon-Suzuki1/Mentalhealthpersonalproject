import json
import bcrypt

USERS_FILE = "users.json"

def load_users():
    """Loads users from the USERS_FILE."""
    try:
        with open(USERS_FILE, "r") as f:
            users = json.load(f)
            return users
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f"Warning: Could not decode JSON from {USERS_FILE}. Starting with an empty list of users.")
        return []

def save_users(users):
    """Saves the list of users to USERS_FILE."""
    try:
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=4)
    except IOError as e:
        print(f"Error: Could not save user data to {USERS_FILE}. {e}")

def hash_password(password):
    """Hashes a password using bcrypt."""
    encoded_password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password_bytes = bcrypt.hashpw(encoded_password, salt)
    return hashed_password_bytes.decode('utf-8') # Store as string

def check_password(hashed_password_str, password):
    """Checks a password against a stored hashed password string."""
    encoded_password = password.encode('utf-8')
    encoded_hashed_password_str = hashed_password_str.encode('utf-8')
    return bcrypt.checkpw(encoded_password, encoded_hashed_password_str)

def sign_up():
    """Handles new user registration."""
    email = input("Enter your email: ")
    password = input("Enter your password: ")

    users = load_users()

    for user in users:
        if user["email"] == email:
            print("Error: Email already exists.")
            return None

    hashed_password = hash_password(password)
    new_user = {"email": email, "password": hashed_password}
    users.append(new_user)
    save_users(users)
    # print("Signup successful!") # Moved after onboarding for better flow

    # --- Onboarding ---
    _prompt_onboarding_questions(email)
    # --- End Onboarding ---

    # Reload users to get the updated user with onboarding info
    users = load_users()
    for user_obj in users:
        if user_obj["email"] == email:
            print("Signup and onboarding complete!")
            return user_obj

    # Fallback, though user should always be found here
    print("Signup successful, but could not retrieve updated user details after onboarding.")
    return new_user

def _prompt_onboarding_questions(user_email):
    """Prompts the user for onboarding information and saves it."""
    print("\n--- Onboarding Questions ---")
    age = input("How old are you? ")
    gender = input("Gender (male/female/rather not say): ")
    coping_mechanisms = input("What makes you feel better or calm down when you're stressed or upset? ")

    users = load_users()
    user_found = False
    for user in users:
        if user["email"] == user_email:
            user["age"] = age
            user["gender"] = gender
            user["coping_mechanisms"] = coping_mechanisms
            user_found = True
            break

    if user_found:
        save_users(users)
        print("Onboarding information saved.")
    else:
        # This case should ideally not happen if called from sign_up correctly
        print(f"Error: Could not find user {user_email} to save onboarding info.")


def log_in():
    """Handles existing user login."""
    email = input("Enter your email: ")
    password = input("Enter your password: ")

    users = load_users()

    for user in users:
        if user["email"] == email:
            if "password" not in user: # Handle older user entries that might not have password
                 print("Error: User account is incomplete (missing password). Please sign up again or contact support.")
                 return None
            if check_password(user["password"], password):
                print("Login successful!")
                return user
            else:
                print("Incorrect password.")
                return None

    print("User not found.")
    return None

if __name__ == '__main__':
    # Simple test cases (optional, for direct execution of auth.py)
    print("Testing auth.py...")
    # Test sign_up
    # Note: Running this multiple times with the same email will show the "Email already exists" error.
    # To re-run sign_up tests, delete users.json before execution.

    # print("\n--- Attempting Sign Up ---")
    # test_user = sign_up()
    # if test_user:
    #    print(f"Signed up user: {test_user['email']}, Age: {test_user.get('age')}")
    # else:
    #    print("Sign up failed or user already exists.")

    # print("\n--- Attempting Log In ---")
    # logged_in_user = log_in()
    # if logged_in_user:
    #     print(f"Logged in user: {logged_in_user['email']}, Onboarding info: Age {logged_in_user.get('age')}")
    # else:
    #     print("Log in failed.")

    # To manually test:
    # 1. Delete users.json if it exists.
    # 2. Run `python auth.py`, sign up. You will be asked onboarding questions.
    # 3. Check users.json to see stored data including onboarding.
    # 4. Run `python auth.py` again, log in with the created user.
    pass
