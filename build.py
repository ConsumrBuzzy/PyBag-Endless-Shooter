import os
import subprocess

def build_web():
    # Create the build command with local template
    cmd = [
        "pygbag",
        "--title", "Endless Shooter",
        "--build",
        "--template", "templates/default.html",
        "--app_name", "endless_shooter",
        "--ume_block", "0",
        "main.py"
    ]
    
    # Run the build command
    subprocess.run(cmd)

if __name__ == "__main__":
    build_web() 