import os
import subprocess
from pathlib import Path

def build_web():
    # Get the absolute path to main.py
    main_script = Path("main.py").resolve()
    
    # Create the build command with correct path handling
    cmd = [
        "pygbag",
        "--title", "Endless Shooter",
        "--build",
        "--template", "default",
        "--app_name", "endless_shooter",
        "--ume_block", "0",
        "--html",
        "--no_archive",
        str(main_script)
    ]
    
    # Run the build command
    subprocess.run(cmd)

if __name__ == "__main__":
    build_web() 