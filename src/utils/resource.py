import os
import sys

from dotenv import load_dotenv


def internal_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(
            sys._MEIPASS, relative_path  # pylint: disable=protected-access
        )
    return os.path.join(os.path.abspath("."), relative_path)


def external_path(relative_path):
    if getattr(sys, "frozen", False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.join(base_path, relative_path)


def load_env_file():
    if hasattr(sys, "_MEIPASS"):
        # Running in a PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running in a normal Python environment
        # Get the path of the current file (resource.py) and go up two levels
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    dotenv_path = os.path.join(base_path, ".env")

    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
