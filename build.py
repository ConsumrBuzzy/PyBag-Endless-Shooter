import os
import subprocess

def build_web():
    # Create the build command with full configuration but build-only
    cmd = [
        "pygbag",
        "--title", "Endless Shooter",
        "--build",
        "--template", "default",
        "--app_name", "endless_shooter",
        "--ume_block", "0",
        "--html",
        "main.py"
    ]
    
    # Run the build command
    subprocess.run(cmd)

if __name__ == "__main__":
    build_web() 