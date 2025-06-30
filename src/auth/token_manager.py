import json
import time
import os
from cryptography.fernet import Fernet

# This is a placeholder for a more secure key management strategy.
# In a real application, this key should be stored securely (e.g., environment variable, secrets manager)
# and not hardcoded or committed to version control.
# For local development, you might generate one and store it in a .env file.
ENCRYPTION_KEY_ENV_VAR = "TOKEN_ENCRYPTION_KEY"
ENCRYPTION_KEY = os.getenv(ENCRYPTION_KEY_ENV_VAR)

if not ENCRYPTION_KEY:
    print(f"Warning: {ENCRYPTION_KEY_ENV_VAR} not found. Generating a temporary key. THIS IS NOT SECURE FOR PRODUCTION.")
    ENCRYPTION_KEY = Fernet.generate_key().decode() #.decode() to store as string if needed, Fernet uses bytes

try:
    fernet = Fernet(ENCRYPTION_KEY.encode()) # Ensure key is bytes
except ValueError as e:
    raise ValueError(f"Invalid {ENCRYPTION_KEY_ENV_VAR}. It must be a URL-safe base64-encoded 32-byte key. Error: {e}")


TOKEN_FILE = "bungie_tokens.json.encrypted"

def save_tokens(token_info):
    """Saves the token information (access token, refresh token, expiry) securely."""
    # Add 'received_at' timestamp to calculate expiry accurately
    token_info['received_at'] = time.time()
    
    encrypted_data = fernet.encrypt(json.dumps(token_info).encode())
    
    with open(TOKEN_FILE, "wb") as f:
        f.write(encrypted_data)
    print("Tokens saved securely.")

def load_tokens():
    """Loads token information from the secure file."""
    if not os.path.exists(TOKEN_FILE):
        return None
    
    with open(TOKEN_FILE, "rb") as f:
        encrypted_data = f.read()
        
    decrypted_data = fernet.decrypt(encrypted_data)
    token_info = json.loads(decrypted_data.decode())
    
    # Check if access token has expired
    if is_access_token_expired(token_info):
        print("Access token has expired.")
        # Depending on the app type (public/confidential), you might try to refresh it here
        # or prompt the user to re-authenticate.
        # For now, we'll just indicate it's expired. The main auth flow should handle refresh.
    return token_info

def get_access_token():
    """Retrieves the current access token.
    Returns None if no token is available or if it's expired and cannot be refreshed.
    """
    tokens = load_tokens()
    if tokens and not is_access_token_expired(tokens):
        return tokens.get("access_token")
    
    # Placeholder for refresh logic if applicable
    # if tokens and tokens.get("refresh_token"):
    #     print("Attempting to refresh token...")
    #     # new_tokens = bungie_auth.refresh_access_token(tokens["refresh_token"]) # Requires bungie_auth import
    #     # if new_tokens:
    #     #     save_tokens(new_tokens)
    #     #     return new_tokens.get("access_token")
    #     # else:
    #     #     print("Failed to refresh token.")
    #     #     return None # Or trigger re-authentication
    
    return None 

def is_access_token_expired(token_info):
    """Checks if the access token has expired."""
    if not token_info or 'received_at' not in token_info or 'expires_in' not in token_info:
        return True # Cannot determine, assume expired
    
    # expires_in is in seconds
    expiry_time = token_info['received_at'] + token_info['expires_in']
    # Add a small buffer (e.g., 60 seconds) to consider it expired a bit earlier
    return time.time() > (expiry_time - 60)

def get_membership_id():
    """Retrieves the Bungie.net membership ID of the authenticated user."""
    tokens = load_tokens()
    if tokens:
        return tokens.get("membership_id")
    return None

def clear_tokens():
    """Clears any stored tokens, effectively logging the user out."""
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
        print("Stored tokens have been cleared.")

if __name__ == "__main__":
    # Example usage:
    # Note: This requires bungie_auth.py to be in the same directory or accessible via PYTHONPATH
    # and ENCRYPTION_KEY to be set for proper operation.
    
    # For testing, ensure ENCRYPTION_KEY is set in your environment or a .env file
    if not ENCRYPTION_KEY or ENCRYPTION_KEY == Fernet.generate_key().decode(): # Check if it's the temp one
        print("Please set a TOKEN_ENCRYPTION_KEY environment variable for proper testing.")
        print("Example: export TOKEN_ENCRYPTION_KEY=$(python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\")")

    # Simulate saving tokens (replace with actual token_info from Bungie)
    # sample_token_info = {
    #     "access_token": "dummy_access_token_example",
    #     "token_type": "Bearer",
    #     "expires_in": 3600, # 1 hour
    #     "refresh_token": "dummy_refresh_token_example", # Only for confidential clients
    #     "refresh_expires_in": 7776000, # 90 days
    #     "membership_id": "123456789"
    # }
    # save_tokens(sample_token_info)

    # Load tokens
    loaded_tokens = load_tokens()
    if loaded_tokens:
        print("\nLoaded Tokens:")
        print(f"  Access Token: {loaded_tokens.get('access_token')}")
        print(f"  Membership ID: {loaded_tokens.get('membership_id')}")
        print(f"  Expires in (seconds from now, approx): { (loaded_tokens.get('received_at', 0) + loaded_tokens.get('expires_in', 0)) - time.time() }")
        
        if is_access_token_expired(loaded_tokens):
            print("  Status: Access token is EXPIRED.")
        else:
            print("  Status: Access token is VALID.")
            
        retrieved_access_token = get_access_token()
        print(f"\nRetrieved via get_access_token(): {retrieved_access_token}")

        retrieved_membership_id = get_membership_id()
        print(f"Retrieved Membership ID: {retrieved_membership_id}")

    else:
        print("No tokens found or failed to load.")

    # Clear tokens (for testing cleanup)
    # clear_tokens()
    # if not load_tokens():
    #     print("Tokens successfully cleared.")
