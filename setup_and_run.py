import os
import subprocess
import sys
import venv

VENV_DIR = "venv"

def create_venv():
    if not os.path.exists(VENV_DIR):
        print("Creating virtual environment...")
        venv.create(VENV_DIR, with_pip=True)
    else:
        print("Virtual environment already exists.")

def get_python_executable():
    if os.name == "nt":
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    else:
        return os.path.join(VENV_DIR, "bin", "python")

def install_packages(python_exe):
    print("Installing required packages...")
    subprocess.check_call([
        python_exe, "-m", "pip", "install",
        "--upgrade", "pip"
    ])
    subprocess.check_call([
        python_exe, "-m", "pip", "install",
        "yfinance", "pandas", "numpy"
    ])

def run_stock_engine(python_exe):
    print("Running stock engine...\n")
    subprocess.check_call([python_exe, "stock_engine.py"])

if __name__ == "__main__":
    create_venv()
    python_exe = get_python_executable()
    install_packages(python_exe)
    run_stock_engine(python_exe)
