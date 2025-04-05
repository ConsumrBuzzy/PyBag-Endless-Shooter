import os
import subprocess

def build_web():
    # Create the build command to generate JS files
    cmd = [
        "pygbag",
        "--port", "0",  # Use port 0 to just build without serving
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