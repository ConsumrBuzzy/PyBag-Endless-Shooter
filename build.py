import subprocess
import sys
import os

def build_wasm():
    try:
        print("\n=== Building WebAssembly with PyBag ===")
        
        # Run pygbag directly as a module with our desired settings
        cmd = [
            sys.executable,
            "-m", "pygbag",
            "--build",
            "--app_name", "endless_shooter",
            "--title", "Endless Shooter",
            "--icon", "favicon.png",
            "--html", "template_mobile.html",
            "--package", "com.endlessshooter.game",
            "--ume_block=1",
            "--can_close",
            "main.py"
        ]
        
        print(f"Running command: {' '.join(cmd)}")
        
        # Execute the build process
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Print the output
        if result.stdout:
            print("\nOutput:")
            print(result.stdout)
            
        if result.stderr:
            print("\nErrors/Warnings:")
            print(result.stderr)
            
        if result.returncode == 0:
            print("\n=== Build Complete ===")
            print("Your game should be available in the 'build/web' directory")
        else:
            print(f"\nBuild failed with exit code: {result.returncode}")
            sys.exit(result.returncode)
            
    except Exception as e:
        print(f"\nError during build: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    build_wasm()