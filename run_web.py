import webbrowser
import threading
from web.app import app # Import your Flask app

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == "__main__":
    threading.Timer(1.0, open_browser).start()
    app.run(debug=True, use_reloader=False) # use_reloader=False to prevent browser from opening twice
