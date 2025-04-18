import sys
import os
from dotenv import load_dotenv

def internalPath(relative_path):  
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def externalPath(relative_path):   
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.join(base_path, relative_path)

def loadEnvFile():
    dotenv_path = internalPath(".env")
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)