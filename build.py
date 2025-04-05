import os
import subprocess

def build_web():
    # Create the build command with correct paths and settings
    cmd = [
        "pygbag",
        "--title", "Endless Shooter",
        "--build",
        "--template", os.path.abspath("templates/default.html"),
        "--app_name", "endless_shooter",
        "--ume_block", "0",
        "--package", "web.pygame.endless_shooter",
        os.path.abspath("main.py")
    ]
    
    # Run the build command
    subprocess.run(cmd)

if __name__ == "__main__":
    build_web() 