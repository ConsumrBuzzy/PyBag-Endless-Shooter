import os
import subprocess

def build_web():
    # Create the build command
    cmd = [
        "pygbag",
        "--title", "Endless Shooter",
        "--build",
        "main.py"
    ]
    
    # Run the build command
    subprocess.run(cmd)

if __name__ == "__main__":
    build_web() 