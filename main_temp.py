import tkinter as tk
# from components.ui_manager import start_ui # Keep if UIManager is separate
from src.auth import create_auth_frame # Import auth UI components
from dotenv import load_dotenv
import os

load_dotenv() # Ensure environment variables are loaded for auth modules

# Função principal que executa o programa
def main():
    root = tk.Tk()
    root.title("Destiny Item Manager Clone")
    root.geometry("800x600") # Adjusted default size

    # Main application frame that will hold auth and content areas
    app_frame = tk.Frame(root)
    app_frame.pack(fill="both", expand=True, padx=5, pady=5)

    # Authentication Frame (e.g., at the top)
    # This frame is created by our auth_ui module
    auth_ui_frame = create_auth_frame(app_frame) 
    auth_ui_frame.pack(side=tk.TOP, fill=tk.X, pady=(0,10)) # pady adds some space below auth frame

    # Placeholder for the main UI content (DIM clone features)
    # This is where your existing ui_manager.start_ui() might be integrated,
    # or where new components for inventory display will go.
    dim_content_frame = tk.LabelFrame(app_frame, text="Inventory Management Area")
    dim_content_frame.pack(fill="both", expand=True)
    
    tk.Label(dim_content_frame, text="Authenticate above to enable features.\nInventory and item management UI will appear here.").pack(padx=20, pady=20, expand=True)

    # --- Initial Auth Check & Warnings (Optional but good for UX) ---
    # The create_auth_frame already calls display_auth_status.
    # You might add further logic here based on auth status if needed,
    # for example, to conditionally enable/disable the dim_content_frame.

    # Check if .env is loaded and CLIENT_ID is available (visual feedback for user)
    if not os.getenv("BUNGIE_CLIENT_ID"):
        # This is a simplified way to show a warning. In a more complex app,
        # you might have a dedicated status bar or notification area.
        warning_label = tk.Label(root, text="Warning: BUNGIE_CLIENT_ID not set. Authentication will fail. Check .env file.", fg="red")
        warning_label.pack(side=tk.BOTTOM, fill=tk.X)
    
    if not os.getenv("TOKEN_ENCRYPTION_KEY"):
        warning_label_key = tk.Label(root, text="Warning: TOKEN_ENCRYPTION_KEY not set. Tokens will not be stored securely.", fg="orange")
        warning_label_key.pack(side=tk.BOTTOM, fill=tk.X)


    root.mainloop()

# Verifica se este arquivo está a ser executado diretamente
if __name__ == "__main__":
    main()