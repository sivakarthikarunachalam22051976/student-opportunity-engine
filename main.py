import sys
import os

# Insert the backend subfolder natively into Python's runtime search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

# Import your actual live FastAPI routing map application instance 
from backend.main import app
