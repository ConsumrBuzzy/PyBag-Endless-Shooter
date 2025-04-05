import os
import subprocess

def build_web():
    # Create the build command with CDN configuration
    cmd = [
        "pygbag",
        "--title", "Endless Shooter",
        "--build",
        "--template", "default",
        "--app_name", "endless_shooter",
        "--ume_block", "0",
        "--cdn", "https://pygame-web.github.io/archives/",
        "main.py"
    ]
    
    # Run the build command
    subprocess.run(cmd)

if __name__ == "__main__":
    build_web() 