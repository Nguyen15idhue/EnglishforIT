#!/usr/bin/env python
"""
Quick start script for Vietnamese Legal Assistant Demo
Runs the Streamlit app
"""

import subprocess
import sys
import os

def main():
    # Ensure we're in the right directory
    os.chdir(r"L:\Download\EnglishforIT")
    
    print("=" * 50)
    print("Vietnamese Legal Assistant - Stage 5 Demo")
    print("=" * 50)
    print()
    print("Starting Streamlit app...")
    print("Opening browser at: http://localhost:8501")
    print()
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            "step/5_demo/app.py"
        ])
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        print("Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
