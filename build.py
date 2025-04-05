from pybag import build

build(
    "main.py",
    "Endless Shooter",
    "A mobile-friendly endless top-down shooter game",
    "1.0.0",
    author="Your Name",
    icon="icon.png",  # Optional: Add an icon file
    requirements=["pygame", "pybag"],
    include_files=[],  # Add any additional files your game needs
) 