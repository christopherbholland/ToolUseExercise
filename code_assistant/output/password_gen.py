n
import string
import secrets

def generate_secure_password(length=12):
    """
    Generates a secure password.
    
    This function generates a secure password of a specified length. The generated password includes
    a mix of uppercase and lowercase letters, digits, and special characters, ensuring a strong
    level of security.
    
    Parameters:
    - length (int): The desired length of the password. Defaults to 12 characters.
    
    Returns:
    - str: A securely generated password.
    """
    
    # Define the characters to use in the password
    alphabet = string.ascii_letters + string.digits + string.punctuation
    
    # Ensure the password length is at least 4 to include each character type
    if length < 4:
        raise ValueError("Password length should be at least 4 characters.")
    
    # Securely generate a random password
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    
    # Ensure the password includes at least one of each required character type
    while (not any(c.islower() for c in password) or
           not any(c.isupper() for c in password) or
           not any(c.isdigit() for c in password) or
           not any(c in string.punctuation for c in password)):
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
    
    return password

# Example usage
if __name__ == "__main__":
    print("Secure password:", generate_secure_password(12))