import os
import subprocess

def build_web():
    # Create the build command with minimal options
    cmd = [
        "pygbag",
        "--build",
        "--no_opt",
        "--no_archive",
        "main.py"
    ]
    
    # Run the build command
    subprocess.run(cmd)

if __name__ == "__main__":
    build_web() 