# main.py
import os
import sys
import webbrowser
from app import app

if __name__ == '__main__':
    # Determine if running as script or frozen exe
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))

    # Change to the application directory
    os.chdir(application_path)
    
    # Open browser automatically
    webbrowser.open('http://127.0.0.1:5000/')
    
    # Run the app
    app.run(port=5000)