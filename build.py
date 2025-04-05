import os
import subprocess

def build_web():
    # Create the build command with web-specific options
    cmd = [
        "pygbag",
        "--title", "Endless Shooter",
        "--build",
        "--template", "default",
        "--app_name", "endless_shooter",
        "--ume_block", "0",
        "main.py"
    ]
    
    # Run the build command
    subprocess.run(cmd)

if __name__ == "__main__":
    build_web() 