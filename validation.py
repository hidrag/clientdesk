from database import create_connection


def validate_full_name(full_name):
     full_name = full_name.strip()
     if full_name == "":
         return False, "Full name cannot be empty"
     if not full_name.isalpha():
         return False, "Full name should only contain alphabets"
     if len(full_name) < 3:
         return False, "Full name should have at least 3 characters"
     if len(full_name) > 60:
         return False, "Full name should not exceed 60 characters"
     return True, full_name

def validate_email(email):
    email = email.strip().lower()
    if not email:
        return False, "Email cannot be empty"
    if "@" not in email:
        return False, "Email should contain '@'"
    if email.count("@") > 1:
        return False, "Email should contain only one '@'"
    if email.endswith("@"):
        return False, "Email should not end with '@'"
    if "." not in email.split("@")[-1]:
        return False, "Enter a valid email"
    if len(email.split("@")[0]) < 1:
        return False, "Email should have a non-empty local part"
    if len(email.split("@")[1].split(".")[0]) < 1:
        return False, "Email should have a non-empty domain part"
    if len(email.split("@")[1].split(".")[-1]) < 1:
        return False, "Email should have a non-empty top-level domain"
    if len(email.split("@")[1].split(".")[-1]) > 6:
        return False, "Email should have a top-level domain with at most 6 characters"
    if len(email.split("@")[1].split(".")[-1]) == 1:
        return False, "Email should have a top-level domain with at least 2 characters"
    if len(email) > 254:
        return False, "Email should not exceed 254 characters"
    return True, email

def validate_address(address):
    address = address.strip()
    if not address:
        return False, "Address cannot be empty"
    if len(address) > 500:
        return False, "Address should not exceed 500 characters"
    return True, address

def validate_phone_number(phone_number):
    phone_number = phone_number.strip()
    if not phone_number:
        return False, "Phone number cannot be empty"
    if len(phone_number) != 10:
        return False, "Phone number should be 10 digits long"
    if not phone_number.isdigit():
        return False, "Phone number should only contain digits"
    return True, phone_number

def validate_password(password):
    password = password.strip()
    if not password:
        return False, "Password cannot be empty"
    if len(password) < 8:
        return False, "Password should be at least 8 characters long"
    if len(password) > 50:
        return False, "Password should not exceed 50 characters"
    if not any(char.isupper() for char in password):
        return False, "Password should contain at least one uppercase letter"
    if not any(char.islower() for char in password):
        return False, "Password should contain at least one lowercase letter"
    if not any(char.isdigit() for char in password):
        return False, "Password should contain at least one digit"
    return True, password

def validate_user_id(user_id):
    user_id = user_id.strip()
    if not user_id:
        return False, "User ID cannot be empty"
    if len(user_id) > 50:
        return False, "User ID should not exceed 50 characters"
    if " " in user_id:
        return False, "User ID should not contain spaces"
    if not user_id.isalnum():
        return False, "User ID should only contain alphanumeric characters"
    return True, user_id

def validate_confirm_password(password, confirm_password):
    if password != confirm_password:
        return False, "Passwords do not match"
    return True, confirm_password



print(validate_full_name("  Rajdeep Bhadra  "))
print(validate_phone_number("9876543210"))
print(validate_phone_number("987654321"))
print(validate_email("TEST@GMAIL.COM"))
print(validate_password("Rajdeep123"))