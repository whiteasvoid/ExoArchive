import tkinter as tk
from tkinter import messagebox
import webbrowser
import os
from dotenv import load_dotenv

# Assuming bungie_auth and token_manager are in the same directory or accessible
try:
    from . import bungie_auth 
    from . import token_manager
except ImportError: # Fallback for running script directly
    import bungie_auth
    import token_manager


load_dotenv()

# --- Configuration ---
# Attempt to load CLIENT_ID to check if .env is properly loaded and configured.
# The actual usage of CLIENT_ID is within bungie_auth.py.
CLIENT_ID = os.getenv("BUNGIE_CLIENT_ID")
if not CLIENT_ID:
    # This is a fallback/warning. Real error handling for missing CLIENT_ID is in bungie_auth.py
    print("Warning: BUNGIE_CLIENT_ID not found. Ensure .env is configured or environment variables are set.")
    # In a real app, you might disable the auth button or show a config error.

# --- UI Functions ---

def display_auth_status(status_label):
    """Updates the status label based on current token availability."""
    access_token = token_manager.get_access_token()
    membership_id = token_manager.get_membership_id()
    if access_token and membership_id:
        status_label.config(text=f"Authenticated: Yes\nMembership ID: {membership_id}", fg="green")
        return True
    else:
        status_label.config(text="Authenticated: No", fg="red")
        return False

def start_authentication_flow(status_label, root_window):
    """Initiates the Bungie OAuth authentication flow."""
    try:
        auth_url = bungie_auth.get_authorization_url()
        webbrowser.open(auth_url)
        # After opening the browser, we need to get the authorization code.
        # This typically requires a local web server to capture the redirect.
        # For a desktop app, this is more complex. One common approach:
        # 1. Ask the user to copy the full redirect URL or just the 'code' param.
        # 2. Provide an input field for them to paste it.
        prompt_for_auth_code(status_label, root_window)
    except Exception as e:
        messagebox.showerror("Authentication Error", f"Could not start authentication: {e}")
        display_auth_status(status_label)

def prompt_for_auth_code(status_label, root_window):
    """Creates a dialog to ask the user for the authorization code."""
    dialog = tk.Toplevel(root_window)
    dialog.title("Enter Authorization Code")
    dialog.geometry("400x150")
    dialog.transient(root_window) # Make it appear on top of the main window
    dialog.grab_set() # Modal behavior

    tk.Label(dialog, text="Please authorize the application in your browser.\nThen, paste the full redirect URL or just the 'code' parameter below:").pack(pady=10)
    
    code_entry = tk.Entry(dialog, width=50)
    code_entry.pack(pady=5)
    code_entry.focus_set()

    def submit_code():
        input_value = code_entry.get().strip()
        auth_code = ""

        if "?code=" in input_value: # User pasted full URL
            try:
                auth_code = input_value.split("?code=")[1].split("&")[0]
            except IndexError:
                messagebox.showerror("Error", "Could not parse the code from the URL. Please paste the full URL or just the code.", parent=dialog)
                return
        else: # User pasted just the code
            auth_code = input_value
        if not auth_code:
            messagebox.showerror("Error", "Authorization code cannot be empty.", parent=dialog)
            return
        dialog.destroy()

        try:
            print(f"Attempting to exchange auth code: {auth_code[:20]}...") # Log part of code
            token_info = bungie_auth.request_token(auth_code)
            token_manager.save_tokens(token_info)
            messagebox.showinfo("Authentication Successful", "Successfully authenticated with Bungie.net!")
        except Exception as e:
            print(f"Token request failed: {e}")
            messagebox.showerror("Authentication Failed", f"Failed to get token: {e}")
        finally:
            display_auth_status(status_label) # Update status regardless of outcome

    submit_button = tk.Button(dialog, text="Submit", command=submit_code)
    submit_button.pack(pady=10)
    
    dialog.bind('<Return>', lambda event: submit_code())


def logout(status_label):
    """Clears stored tokens and updates the UI."""
    confirmed = messagebox.askyesno("Logout", "Are you sure you want to log out? This will clear your saved Bungie.net tokens.")
    if confirmed:
        token_manager.clear_tokens()
        display_auth_status(status_label)
        messagebox.showinfo("Logout", "You have been logged out.")

def create_auth_frame(parent_frame):
    """Creates and returns the authentication UI frame."""
    auth_frame = tk.LabelFrame(parent_frame, text="Bungie.net Authentication", padx=10, pady=10)
    
    status_label = tk.Label(auth_frame, text="Authenticated: Unknown", justify=tk.LEFT)
    status_label.pack(pady=(0,10), anchor="w")

    auth_button = tk.Button(auth_frame, text="Login with Bungie.net", command=lambda: start_authentication_flow(status_label, parent_frame.winfo_toplevel()))
    auth_button.pack(fill=tk.X, pady=5)
    
    logout_button = tk.Button(auth_frame, text="Logout", command=lambda: logout(status_label))
    logout_button.pack(fill=tk.X, pady=5)

    # Initial status update
    display_auth_status(status_label)
    
    return auth_frame


# --- Main Application (Example Usage) ---
if __name__ == "__main__":
    root = tk.Tk()
    root.title("DIM-like App - Auth Test")
    root.geometry("400x200")

    # This is where the auth UI will be placed
    main_auth_frame = create_auth_frame(root)
    main_auth_frame.pack(padx=10, pady=10, fill="both", expand=True)

    # Check if .env is loaded and CLIENT_ID is available
    if not CLIENT_ID:
        messagebox.showwarning("Configuration Error", 
                               "BUNGIE_CLIENT_ID is not set. Please create a .env file "
                               "with your Bungie API credentials (BUNGIE_CLIENT_ID, BUNGIE_API_KEY, "
                               "and BUNGIE_CLIENT_SECRET if applicable). "
                               "Authentication will likely fail.")
    
    # Check for ENCRYPTION_KEY for token_manager
    if not token_manager.ENCRYPTION_KEY or token_manager.ENCRYPTION_KEY == Fernet.generate_key().decode():
         messagebox.showwarning("Security Warning", 
                               f"{token_manager.ENCRYPTION_KEY_ENV_VAR} is not set or is using a temporary key. "
                               "For secure token storage, please set this environment variable. "
                               "See token_manager.py for details. Your tokens will NOT be stored securely.")


    root.mainloop()
