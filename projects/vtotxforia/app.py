"""VtoTXforIA Desktop — PyWebView + Flask backend

   Lanza el servidor whisper en segundo plano y abre la UI web
   en una ventana nativa (Edge WebView2 en Windows).

   Uso:  python app.py
         python app.py --tray        (arranca minimizado al tray)
"""

import argparse
import logging
import os
import sys
import threading
import time
import webbrowser

import webview
import server as whisper_server

log = logging.getLogger("app")
PORT = int(os.environ.get("WHISPER_PORT", 5100))
URL = f"http://127.0.0.1:{PORT}"

TRAY_ENABLED = False  # Se activa si pystray está instalado


def start_server():
    """Flask en thread daemon."""
    t = threading.Thread(
        target=whisper_server.app.run,
        kwargs={"host": "0.0.0.0", "port": PORT, "debug": False, "threaded": True},
        daemon=True,
    )
    t.start()
    # Esperar hasta que el servidor responda (máx 60s esperando el modelo)
    for _ in range(300):
        try:
            import urllib.request
            urllib.request.urlopen(URL + "/api/health", timeout=0.5)
            log.info("server ready on %s", URL)
            return
        except Exception:
            time.sleep(0.2)
    log.warning("server did not start in time")


def main():
    parser = argparse.ArgumentParser(description="VtoTXforIA Desktop")
    parser.add_argument("--tray", action="store_true", help="start in system tray")
    parser.add_argument("--browser", action="store_true", help="use browser instead of native window")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="[app] %(message)s")
    log.info("starting VtoTXforIA server…")
    start_server()

    if args.browser:
        webbrowser.open(URL)
        log.info("opened in browser. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            log.info("bye")
        return

    log.info("opening native window (%s)", URL)
    window = webview.create_window(
        "VtoTXforIA",
        URL,
        width=1100,
        height=800,
        min_size=(640, 480),
        resizable=True,
        fullscreen=False,
        confirm_close=False,
        background_color="#0b0b0e",
    )
    webview.start(debug=False)


if __name__ == "__main__":
    main()
