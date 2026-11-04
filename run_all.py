"""
run_all.py — starts the Study Specs website AND the Streamlit app together.

Put this file in the SAME folder as:
    app.py            (the Streamlit wizard)
    recommend.py      (scoring logic)
    editing.html      (the website front page)
    study_specs_laptops_upgraded.csv

Run it:
    python run_all.py

Then open  http://localhost:5500  (it opens automatically).
The "Launch the wizard" and "Find My Laptop" buttons on the website take you
to the Streamlit app on http://localhost:8501.

Stop everything with Ctrl+C.

Options:
    python run_all.py --site-port 5500 --app-port 8501 --no-browser
"""

import argparse
import signal
import subprocess
import sys
import time
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

BASE_DIR = Path(__file__).resolve().parent
SITE_FILE = BASE_DIR / "editing.html"
APP_FILE = BASE_DIR / "app.py"

# The line in editing.html that holds the app address. The launcher swaps it
# for the real port, so the website always points at the running app.
APP_URL_LINE = 'const APP_URL = "http://localhost:8501";'


class SiteHandler(BaseHTTPRequestHandler):
    """Serves ONLY the website page (never app.py, the CSV, or other files)."""

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/", "/index.html", "/editing.html"):
            html = SITE_FILE.read_text(encoding="utf-8")
            html = html.replace(
                APP_URL_LINE,
                f'const APP_URL = "http://localhost:{self.server.app_port}";',
            )
            body = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404, "Not found")

    def log_message(self, *args):
        pass  # keep the terminal quiet


def wait_for_app(app_port, timeout=40):
    """Waits until Streamlit answers, so the browser never opens too early."""
    url = f"http://localhost:{app_port}/_stcore/health"
    end = time.time() + timeout
    while time.time() < end:
        try:
            with urllib.request.urlopen(url, timeout=1) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(0.5)
    return False


def main():
    parser = argparse.ArgumentParser(description="Run the Study Specs website + app together.")
    parser.add_argument("--site-port", type=int, default=5500, help="port for the website (default 5500)")
    parser.add_argument("--app-port", type=int, default=8501, help="port for the Streamlit app (default 8501)")
    parser.add_argument("--no-browser", action="store_true", help="don't open the browser automatically")
    args = parser.parse_args()

    for f in (SITE_FILE, APP_FILE):
        if not f.exists():
            sys.exit(f"Missing file: {f.name} (it must be in the same folder as run_all.py)")

    # 1) Website server
    try:
        site = ThreadingHTTPServer(("127.0.0.1", args.site_port), SiteHandler)
    except OSError:
        sys.exit(f"Port {args.site_port} is already in use. Try: python run_all.py --site-port 5600")
    site.app_port = args.app_port
    Thread(target=site.serve_forever, daemon=True).start()

    # 2) Streamlit app
    app = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run", str(APP_FILE),
            "--server.port", str(args.app_port),
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false",
        ],
        cwd=BASE_DIR,
    )

    # Closing the terminal / killing the script also shuts the app down cleanly.
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))

    site_url = f"http://localhost:{args.site_port}"
    print(f"\nStarting Study Specs...\n  Website : {site_url}\n  App     : http://localhost:{args.app_port}\n")

    try:
        if wait_for_app(args.app_port):
            print("Both are running. Press Ctrl+C to stop.")
            if not args.no_browser:
                webbrowser.open(site_url)
        else:
            print("The app did not start in time. Check the messages above "
                  "(is streamlit installed? try: pip install streamlit pandas).")
        app.wait()
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        site.shutdown()
        if app.poll() is None:
            app.terminate()
            try:
                app.wait(timeout=5)
            except subprocess.TimeoutExpired:
                app.kill()


if __name__ == "__main__":
    main()
