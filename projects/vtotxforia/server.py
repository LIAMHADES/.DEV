#!/usr/bin/env python3
"""VtoTXforIA — Backend Flask con faster-whisper (small, int8)
   API: POST /api/transcribe  →  { "text": "...", "model": "small" }
   Health: GET /api/health"""

import atexit
import logging
import os
import subprocess
import tempfile
import threading

import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS
from scipy.io import wavfile

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO, format="[server] %(message)s")
log = logging.getLogger("server")

MODEL_SIZE = os.environ.get("WHISPER_MODEL", "small")
PORT = int(os.environ.get("WHISPER_PORT", 5100))

_fw_model = None
_model_lock = threading.Lock()


def get_model():
    global _fw_model
    if _fw_model is None:
        with _model_lock:
            if _fw_model is None:
                from faster_whisper import WhisperModel

                log.info("Loading faster-whisper %s (int8, cpu) …", MODEL_SIZE)
                _fw_model = WhisperModel(
                    MODEL_SIZE, device="cpu", compute_type="int8", num_workers=2
                )
                log.info("faster-whisper loaded OK")
    return _fw_model


def webm_to_audio(webm_bytes: bytes) -> np.ndarray:
    """Convert WebM bytes → numpy float32 (mono 16kHz)."""
    fd_webm, webm_path = tempfile.mkstemp(suffix=".webm")
    fd_wav, wav_path = tempfile.mkstemp(suffix=".wav")
    try:
        os.write(fd_webm, webm_bytes)
        os.close(fd_webm)
        os.close(fd_wav)

        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", webm_path,
                "-ar", "16000",
                "-ac", "1",
                "-f", "wav",
                wav_path,
            ],
            check=True,
            capture_output=True,
        )
        sr, data = wavfile.read(wav_path)
        return data.astype(np.float32) / 32768.0
    finally:
        for p in (webm_path, wav_path):
            try:
                os.unlink(p)
            except OSError:
                pass


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": MODEL_SIZE, "loaded": _fw_model is not None})


@app.route("/api/transcribe", methods=["POST"])
def transcribe():
    try:
        audio_bytes = request.get_data()
        if not audio_bytes or len(audio_bytes) < 1000:
            return jsonify({"error": "audio empty or too short"}), 400

        audio = webm_to_audio(audio_bytes)
        if len(audio) < 16000:
            return jsonify({"error": "audio shorter than 1s"}), 400

        model = get_model()
        segments, _info = model.transcribe(
            audio, beam_size=1, language=None, task="transcribe", vad_filter=False
        )
        text = " ".join(s.text.strip() for s in segments if s.text).strip()

        return jsonify({"text": text, "model": MODEL_SIZE})
    except Exception as exc:
        log.exception("transcribe error")
        return jsonify({"error": str(exc)}), 500


def _preload():
    try:
        get_model()
    except Exception:
        log.warning("Preload failed — model will load on first request")


_atomic = threading.Thread(target=_preload, daemon=True)
_atomic.start()


def main():
    log.info("VtoTXforIA server on http://localhost:%d (model: %s)", PORT, MODEL_SIZE)
    app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True)


if __name__ == "__main__":
    main()
