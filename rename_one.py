import subprocess
import os

def main():
    result = subprocess.run(["git", "log", "-1", "--format=%B"], capture_output=True, text=True)
    msg = result.stdout.strip()
    if msg == "v1":
        print("Renaming 'v1' commit...")
        subprocess.run(["git", "commit", "--amend", "-m", "feat: Add NeuroBuilder and Collector specialists", "--no-edit"], check=True)

if __name__ == "__main__":
    main()
