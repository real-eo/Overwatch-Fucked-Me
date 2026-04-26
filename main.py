from src.constants import DEBUG
from ui import ui


if __name__ == "__main__":
    # Notify running mode
    if DEBUG:
        print("[DEBUG MODE] Running in debug mode. Assets will be loaded from the project directory.")
    
    # Start the UI
    ui()
