import os
import sys
import subprocess

def main():
    # Ensure pygbag is installed
    try:
        import pygbag
    except ImportError:
        print("Installing pygbag...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygbag"])

    # Get the directory containing main.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Build command with proper flags
    cmd = [
        sys.executable, "-m", "pygbag",
        "--app_name", "EndlessShooter",
        "--title", "Endless Top-Down Shooter",
        "--ume_block", "0",  # Don't block on user media
        "--can_close", "1",  # Allow window to close
        "--template", "default.tmpl",
        "--archive",  # Create downloadable archive
        current_dir
    ]
    
    print("Building WASM version...")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
