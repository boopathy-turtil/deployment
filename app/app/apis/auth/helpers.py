import random
import string

def generate_temp_password(length=12):
    """
    Generates a temporary password that meets AWS Cognito password policy requirements.

    Parameters:
    length (int): The length of the password. Default is 12.

    Returns:
    str: A randomly generated password.
    """
    if length < 8:  # Minimum length is typically 8 characters in AWS Cognito
        raise ValueError("Password length must be at least 8 characters.")

    # Define character sets
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    digits = string.digits
    symbols = "!@#$%^&*()-_+="

    # Ensure the password contains at least one of each required character type
    password = [
        random.choice(lower),
        random.choice(upper),
        random.choice(digits),
        random.choice(symbols),
    ]

    # Fill the rest of the password length with a mix of all character sets
    remaining_length = length - 4
    all_characters = lower + upper + digits + symbols
    password += random.choices(all_characters, k=remaining_length)

    # Shuffle the list to ensure the password is not in any predictable order
    random.shuffle(password)

    return "".join(password)