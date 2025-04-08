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
    
    # Build command for pygame-script mode
    cmd = [
        sys.executable, "-m", "pygbag",
        "--html",  # Build as HTML with embedded assets
        "--title", "Endless Top-Down Shooter",
        "--cdn", "https://pygame-web.github.io/archives/0.6/",  # Use older version
        "--package", "endless_shooter",  # Unique package name
        "--bind", "localhost",  # Local testing only
        "--port", "8000",  # Explicit port
        current_dir
    ]
    
    print("Building WASM version...")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
