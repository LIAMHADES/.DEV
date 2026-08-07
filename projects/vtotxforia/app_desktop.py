"""
VtoTXforIA Desktop v3 — CustomTkinter + faster-whisper
App nativa, sin navegador, backend whisper integrado.
"""

import os
import sys
import time
import threading
import warnings
import numpy as np
import sounddevice as sd

warnings.filterwarnings("ignore", message=".*FP16 is not supported.*")

import customtkinter as ctk
from faster_whisper import WhisperModel

# ─── config ──────────────────────────────────────
MODEL_SIZE = os.environ.get("WHISPER_MODEL", "small")
SAMPLE_RATE = 16000
CHUNK_SEC = 4
THEME = {
    "bg": "#0b0b0e",
    "surface": "#141419",
    "border": "#1e1e26",
    "green": "#22c55e",
    "green_hover": "#16a34a",
    "red": "#ef4444",
    "text": "#e8e8e8",
    "dim": "#6b6b7b",
    "accent": "#30303a",
}

# ─── model ───────────────────────────────────────
_model = None
_model_lock = threading.Lock()


def get_model():
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                _model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8", num_workers=2)
    return _model


# ─── audio recorder ──────────────────────────────
class Recorder:
    def __init__(self, on_text):
        self.on_text = on_text
        self.buffer = []
        self.stream = None
        self.running = False
        self.thread = None
        self.accumulated = ""
        self.checkpoint = 0

    def _callback(self, indata, frames, t, status):
        if self.running:
            self.buffer.extend(indata.flatten().copy())

    def _loop(self):
        model = get_model()
        chunk = int(CHUNK_SEC * SAMPLE_RATE)
        while self.running:
            time.sleep(0.3)
            total = len(self.buffer)
            unprocessed = total - self.checkpoint
            if unprocessed < chunk:
                continue
            audio = np.array(self.buffer[self.checkpoint:total], dtype=np.float32)
            self.checkpoint = total
            try:
                segs, _ = model.transcribe(audio, beam_size=1, vad_filter=False)
                txt = " ".join(s.text.strip() for s in segs if s.text).strip()
                if txt:
                    self.accumulated = (self.accumulated + " " + txt).strip()
                    self.on_text(self.accumulated)
            except Exception:
                pass

    def start(self):
        self.buffer = []
        self.checkpoint = 0
        self.accumulated = ""
        self.running = True
        self.stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32", callback=self._callback)
        self.stream.start()
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        return self.accumulated


# ─── UI ──────────────────────────────────────────
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("VtoTXforIA")
        self.geometry("900x640")
        self.minsize(640, 480)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        self.configure(fg_color=THEME["bg"])

        self.recorder = None
        self.recording = False
        self._anim_job = None
        self._pulse = 0

        self._build_ui()

    def _build_ui(self):
        # ── header ──
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=28, pady=(24, 0))

        ctk.CTkLabel(
            header, text="V2TX4IA",
            font=ctk.CTkFont(family="Space Grotesk", size=20, weight="bold"),
            text_color=THEME["green"],
        ).pack(side="left")

        self.status_label = ctk.CTkLabel(
            header, text="Listo",
            font=ctk.CTkFont(family="Space Grotesk", size=11),
            text_color=THEME["dim"],
        )
        self.status_label.pack(side="right", padx=(0, 4))

        ctk.CTkLabel(
            header, text="⚡",
            font=ctk.CTkFont(size=16),
            text_color=THEME["green"],
        ).pack(side="right", padx=(0, 2))

        # ── model info ──
        model_row = ctk.CTkFrame(self, fg_color="transparent")
        model_row.pack(fill="x", padx=28, pady=(4, 12))

        ctk.CTkLabel(
            model_row, text=f"Whisper {MODEL_SIZE} · int8 · CPU · streaming {CHUNK_SEC}s",
            font=ctk.CTkFont(family="Space Grotesk", size=10),
            text_color=THEME["dim"],
        ).pack(side="left")

        # ── text area ──
        self.text_box = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Inter", size=14),
            fg_color=THEME["surface"],
            border_color=THEME["border"],
            border_width=1,
            corner_radius=10,
            text_color=THEME["text"],
            wrap="word",
        )
        self.text_box.pack(fill="both", expand=True, padx=28, pady=(0, 16))

        # ── bottom bar ──
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=28, pady=(0, 24))

        self.record_btn = ctk.CTkButton(
            bar,
            text="● GRABAR",
            font=ctk.CTkFont(family="Space Grotesk", size=14, weight="bold"),
            fg_color=THEME["green"],
            hover_color=THEME["green_hover"],
            corner_radius=28,
            width=180,
            height=44,
            command=self._toggle_record,
        )
        self.record_btn.pack(side="left")

        self.char_label = ctk.CTkLabel(
            bar,
            text="0 caracteres",
            font=ctk.CTkFont(family="Space Grotesk", size=11),
            text_color=THEME["dim"],
        )
        self.char_label.pack(side="left", padx=(20, 0))

        ctk.CTkButton(
            bar,
            text="Copiar",
            font=ctk.CTkFont(family="Space Grotesk", size=12),
            fg_color=THEME["accent"],
            hover_color="#404050",
            corner_radius=8,
            width=80,
            height=36,
            command=self._copy,
        ).pack(side="right", padx=(6, 0))

        ctk.CTkButton(
            bar,
            text="Limpiar",
            font=ctk.CTkFont(family="Space Grotesk", size=12),
            fg_color=THEME["accent"],
            hover_color="#404050",
            corner_radius=8,
            width=80,
            height=36,
            command=self._clear,
        ).pack(side="right", padx=(0, 6))

        # ── status bar ──
        self.footer = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(family="Space Grotesk", size=9),
            text_color=THEME["dim"],
        )
        self.footer.pack(side="bottom", padx=28, pady=(0, 12))

    # ── actions ─────────────────────────────────
    def _toggle_record(self):
        if self.recording:
            self._stop()
        else:
            self._start()

    def _start(self):
        self.recording = True
        self.record_btn.configure(text="■ PARAR", fg_color=THEME["red"], hover_color="#dc2626")
        self.status_label.configure(text="Grabando", text_color=THEME["red"])
        self.footer.configure(text="Habla ahora…")
        self._pulse_anim()
        self.recorder = Recorder(on_text=self._on_stream_text)
        threading.Thread(target=self.recorder.start, daemon=True).start()

    def _stop(self):
        self.recording = False
        self.record_btn.configure(text="● GRABAR", fg_color=THEME["green"], hover_color=THEME["green_hover"])
        self.status_label.configure(text="Procesando…", text_color=THEME["dim"])
        self.footer.configure(text="Transcribiendo último fragmento…")
        if self._anim_job:
            self.after_cancel(self._anim_job)
            self._anim_job = None
        self.record_btn.configure(fg_color=THEME["accent"], text="⏳", state="disabled")

        def _finish():
            final = self.recorder.stop() if self.recorder else ""
            self.recorder = None
            self.after(0, lambda: self._on_final(final))

        threading.Thread(target=_finish, daemon=True).start()

    def _on_final(self, final_text):
        self.record_btn.configure(text="● GRABAR", fg_color=THEME["green"], hover_color=THEME["green_hover"], state="normal")
        self.status_label.configure(text="Listo", text_color=THEME["green"])
        self.footer.configure(text="")
        if final_text:
            current = self.text_box.get("1.0", "end-1c").strip()
            self.text_box.delete("1.0", "end")
            self.text_box.insert("1.0", (current + "\n" + final_text).strip())
            self._update_char_count()

    def _on_stream_text(self, text):
        self.after(0, lambda: self._set_text(text))

    def _set_text(self, text):
        self.text_box.delete("1.0", "end")
        self.text_box.insert("1.0", text)
        self._update_char_count()

    def _update_char_count(self):
        n = len(self.text_box.get("1.0", "end-1c"))
        self.char_label.configure(text=f"{n} caracteres")

    def _copy(self):
        self.clipboard_clear()
        self.clipboard_append(self.text_box.get("1.0", "end-1c"))
        self.footer.configure(text="Copiado al portapapeles ✓", text_color=THEME["green"])
        self.after(2000, lambda: self.footer.configure(text="", text_color=THEME["dim"]))

    def _clear(self):
        self.text_box.delete("1.0", "end")
        self._update_char_count()

    def _pulse_anim(self):
        if not self.recording:
            return
        self._pulse += 0.08
        a = 0.6 + 0.4 * abs(np.sin(self._pulse * 2))
        r, g, b = int(239 * a), int(68 * a), int(68 * a)
        self.record_btn.configure(fg_color=f"#{r:02x}{g:02x}{b:02x}")
        self._anim_job = self.after(50, self._pulse_anim)


# ─── entry point ────────────────────────────────
def main():
    # Preload model in background
    threading.Thread(target=get_model, daemon=True).start()
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
