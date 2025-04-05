import os
import subprocess

def build_web():
    # Create the build command with additional web-specific options
    cmd = [
        "pygbag",
        "--title", "Endless Shooter",
        "--build",
        "--template", "default",
        "--cdn", "http://localhost:8000/",
        "--app_name", "endless_shooter",
        "--ume_block", "0",
        "--cache", "no-cache",
        "main.py"
    ]
    
    # Run the build command
    subprocess.run(cmd)

if __name__ == "__main__":
    build_web() 