from __future__ import annotations

import argparse
import threading
import webbrowser

import uvicorn


HOST = "127.0.0.1"
PORT = 8000
URL = f"http://{HOST}:{PORT}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local Product Importer browser UI.")
    parser.add_argument("--no-browser", action="store_true", help="Do not open the browser automatically")
    args = parser.parse_args()

    if not args.no_browser:
        threading.Timer(1.0, lambda: webbrowser.open(URL)).start()

    uvicorn.run("web_app:app", host=HOST, port=PORT, reload=False)


if __name__ == "__main__":
    main()
