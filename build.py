import os
import subprocess

def build_web():
    # Create the build command to generate JS files
    cmd = [
        "pygbag",
        "--build",
        "--app_name", "endless_shooter",
        "--package", "endless_shooter",
        "main.py"
    ]
    
    print("Building game...")
    print("Command:", " ".join(cmd))
    
    # Run the build command
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Print output for debugging
    print("\nOutput:")
    print(result.stdout)
    print("\nErrors:")
    print(result.stderr)

if __name__ == "__main__":
    build_web() 