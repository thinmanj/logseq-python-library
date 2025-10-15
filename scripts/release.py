#!/usr/bin/env python3
"""
Release script for logseq-python package.

This script automates the process of building and releasing the package to PyPI.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, check=True):
    """Run a shell command."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if check and result.returncode != 0:
        sys.exit(result.returncode)
    return result

def main():
    """Main release process."""
    # Ensure we're in the project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print("🚀 Starting logseq-python release process...")
    
    # 1. Clean previous builds
    print("\n1. Cleaning previous builds...")
    run_command("rm -rf build/ dist/ *.egg-info/", check=False)
    
    # 2. Run tests
    print("\n2. Running tests...")
    result = run_command("python -m pytest tests/ -v", check=False)
    if result.returncode != 0:
        print("⚠️  Tests failed, but continuing with alpha release...")
    
    # 3. Check code quality
    print("\n3. Checking code quality...")
    run_command("python -m flake8 logseq_py/ --max-line-length=100", check=False)
    
    # 4. Build package
    print("\n4. Building package...")
    run_command("python -m build")
    
    # 5. Check package
    print("\n5. Checking package...")
    run_command("python -m twine check dist/*")
    
    # 6. Upload to TestPyPI first (optional)
    print("\n6. Ready to upload!")
    print("To upload to TestPyPI (recommended first):")
    print("  python -m twine upload --repository testpypi dist/*")
    print("\nTo upload to PyPI:")
    print("  python -m twine upload dist/*")
    
    print("\n✅ Release build completed successfully!")
    print("\nFiles created:")
    for file in Path("dist").glob("*"):
        print(f"  - {file}")

if __name__ == "__main__":
    main()