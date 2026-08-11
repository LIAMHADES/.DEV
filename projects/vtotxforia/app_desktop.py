"""
VtoTXforIA Desktop v4 — CustomTkinter + faster-whisper
Diseño replicando la web original: splash, orb animado, rec dot, historial.
"""

import json
import os
import sys
import time
import threading
import traceback
import warnings
from datetime import datetime

warnings.filterwarnings("ignore", message=".*FP16.*")

import numpy as np
import sounddevice as sd
import customtkinter as ctk
from faster_whisper import WhisperModel

# ─── config ────────────────────────────────
MODEL_SIZE = os.environ.get("WHISPER_MODEL", "small")
SAMPLE_RATE = 16000
CHUNK_SEC = 4
HISTORY_FILE = os.path.join(os.path.dirname(__file__), "history.json")

C = {
    "bg": "#000000",
    "surface": "#040408",
    "surface2": "#010104",
    "border": "#0F1A2E",
    "text": "#D0DCE8",
    "muted": "#587090",
    "bright": "#A0D8F1",
    "mid": "#4A90D9",
    "shadow": "#002244",
    "glow": "#7FC1ED",
    "dim": "#00102B",
    "danger": "#ff4444",
    "dot_active": "#38BDF8",
}

# ─── model ─────────────────────────────────
_model = None
_lock = threading.Lock()


def get_model():
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                _model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8", num_workers=2)
    return _model


# ─── history ───────────────────────────────
def load_history():
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_history(entries):
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ─── recorder ──────────────────────────────
class Recorder:
    def __init__(self, on_text, on_error):
        self.on_text = on_text
        self.on_error = on_error
        self.buf = []
        self.running = False
        self.stream = None
        self.thr = None
        self.acc = ""
        self.chk = 0

    def _cb(self, indata, frames, t, status):
        if self.running and len(indata) > 0:
            self.buf.extend(indata.flatten().copy())

    def _loop(self):
        try:
            model = get_model()
        except Exception as e:
            self.on_error(f"Error modelo: {e}")
            return
        chunk = int(CHUNK_SEC * SAMPLE_RATE)
        while self.running:
            time.sleep(0.3)
            total = len(self.buf)
            unprocessed = total - self.chk
            if unprocessed < chunk:
                continue
            audio = np.array(self.buf[self.chk : total], dtype=np.float32)
            self.chk = total
            try:
                segs, _ = model.transcribe(audio, beam_size=1, vad_filter=False)
                txt = " ".join(s.text.strip() for s in segs if s.text).strip()
                if txt:
                    self.acc = (self.acc + " " + txt).strip()
                    self.on_text(self.acc)
            except Exception as e:
                self.on_error(f"Error chunk: {e}")

    def start(self):
        self.buf = []
        self.chk = 0
        self.acc = ""
        self.running = True
        try:
            self.stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32", callback=self._cb)
            self.stream.start()
        except Exception as e:
            self.running = False
            self.on_error(f"Audio: {e}")
            return
        self.thr = threading.Thread(target=self._loop, daemon=True)
        self.thr.start()

    def stop(self):
        self.running = False
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
        if self.thr and self.thr.is_alive():
            self.thr.join(timeout=2)
        return self.acc


# ─── splash screen ─────────────────────────
class SplashScreen(ctk.CTkToplevel):
    def __init__(self, master, on_done):
        super().__init__(master)
        self.on_done = on_done
        self.overrideredirect(True)
        w, h = 500, 340
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{sw//2 - w//2}+{sh//2 - h//2}")
        self.configure(fg_color=C["bg"])
        self.attributes("-topmost", True)

        # Logo canvas — dibujamos "V2TX4IA" como texto estilizado
        self.canvas = ctk.CTkCanvas(self, width=w, height=220, bg=C["bg"], highlightthickness=0)
        self.canvas.pack(pady=(30, 0))
        self._draw_logo()

        # Subtitle
        self.sub = ctk.CTkLabel(
            self, text="V O I C E  .  T O  .  T E X T  .  F O R  .  I A",
            font=ctk.CTkFont(family="Courier New", size=11), text_color=C["muted"],
        )
        self.sub.pack(pady=(12, 8))

        # Hint
        self.hint = ctk.CTkLabel(
            self, text="[ CLICK · O CUALQUIER TECLA · PARA CONTINUAR ]",
            font=ctk.CTkFont(family="Courier New", size=9), text_color=C["muted"],
        )
        self.hint.pack(pady=(0, 10))

        self.bind("<Button-1>", self._dismiss)
        self.bind("<Key>", self._dismiss)
        self.focus_set()

        # Glow animation
        self._glow_x = -100
        self._animate_glow()

    def _draw_logo(self):
        c = self.canvas
        letters = ["V", "2", "T", "X", "4", "I", "A"]
        # Bitmap 5x7 para cada letra (simplificado del dot-matrix)
        font_5x7 = {
            "V": [0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b01010, 0b00100],
            "2": [0b01110, 0b10001, 0b00001, 0b00010, 0b00100, 0b01000, 0b11111],
            "T": [0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100],
            "X": [0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b01010, 0b10001],
            "4": [0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010],
            "I": [0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110],
            "A": [0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001],
        }
        dot_r = 4
        spacing = 12
        letter_gap = 24
        start_x = 50
        start_y = 30

        for li, ch in enumerate(letters):
            pat = font_5x7[ch]
            off_x = li * (5 * spacing + letter_gap)
            for row in range(7):
                for col in range(5):
                    if pat[row] & (1 << (4 - col)):
                        x = start_x + off_x + col * spacing
                        y = start_y + row * spacing
                        if row <= 1:
                            color = C["bright"]
                        elif row <= 4:
                            color = C["mid"]
                        else:
                            color = C["shadow"]
                        c.create_oval(x - dot_r, y - dot_r, x + dot_r, y + dot_r, fill=color, outline="", tags="dot")

        self._dots = c.find_withtag("dot")

    def _animate_glow(self):
        self._glow_x += 8
        if self._glow_x > 550:
            self._glow_x = -100
        c = self.canvas
        c.delete("glow")
        gx = self._glow_x
        for i in range(10):
            x = gx + i * 50
            a = 1.0 - abs(x - 250) / 250
            a = max(0, min(1, a))
            c.create_line(x, 0, x, 220, fill=f"#{int(255*a):02x}{int(215*a):02x}{int(240*a):02x}", width=2, tags="glow", stipple="gray50" if i % 2 else "")
        self.after(40, self._animate_glow)

    def _dismiss(self, event=None):
        self.destroy()
        self.on_done()


# ─── main app ──────────────────────────────
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("VtoTXforIA")
        self.geometry("860x680")
        self.minsize(600, 500)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=C["bg"])

        self.recorder = None
        self.recording = False
        self._blink_id = None
        self._anim_id = None
        self._pulse = 0

        # Preload model
        threading.Thread(target=get_model, daemon=True).start()

        # Splash → then build
        SplashScreen(self, on_done=self._build_ui)

    def _build_ui(self):
        self.deiconify()

        # ── header ──
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=28, pady=(20, 4))

        ctk.CTkLabel(
            hdr, text="V2TX4IA",
            font=ctk.CTkFont(family="Courier New", size=20, weight="bold"),
            text_color=C["bright"],
        ).pack(side="left")

        self.rec_dot = ctk.CTkLabel(hdr, text="●", font=ctk.CTkFont(size=14), text_color=C["bg"])
        self.rec_dot.pack(side="left", padx=(8, 0))

        # Badge row
        ctk.CTkFrame(self, fg_color="transparent").pack(fill="x", padx=28)
        self.badge = ctk.CTkLabel(
            hdr,
            text=f"WHISPER {MODEL_SIZE.upper()} · LOCAL · SIN BACKEND",
            font=ctk.CTkFont(family="Courier New", size=9),
            text_color=C["muted"],
        )
        self.badge.pack(side="right")

        # ── orb canvas ──
        self.orb_canvas = ctk.CTkCanvas(self, width=200, height=160, bg=C["bg"], highlightthickness=0)
        self.orb_canvas.pack(pady=(10, 0))
        self._draw_orb_idle()
        self.orb_canvas.bind("<Button-1>", lambda e: self._toggle_record())

        # ── status line ──
        self.status_label = ctk.CTkLabel(
            self, text="Listo — pulsa el orb para grabar",
            font=ctk.CTkFont(family="Courier New", size=10),
            text_color=C["muted"],
        )
        self.status_label.pack(pady=(2, 12))

        # ── text area ──
        self.text_box = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Courier New", size=13),
            fg_color=C["surface"],
            border_color=C["border"],
            border_width=1,
            corner_radius=10,
            text_color=C["text"],
            wrap="word",
        )
        self.text_box.pack(fill="both", expand=True, padx=28, pady=(0, 4))

        # ── toolbar ──
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=28, pady=(0, 4))

        self.char_label = ctk.CTkLabel(bar, text="0 caracteres", font=ctk.CTkFont(family="Courier New", size=10), text_color=C["muted"])
        self.char_label.pack(side="left")

        ctk.CTkButton(bar, text="COPIAR", font=ctk.CTkFont(family="Courier New", size=11, weight="bold"), fg_color=C["mid"], hover_color=C["shadow"], corner_radius=6, width=100, height=30, command=self._copy).pack(side="right", padx=(6, 0))
        ctk.CTkButton(bar, text="LIMPIAR", font=ctk.CTkFont(family="Courier New", size=11), fg_color=C["surface2"], hover_color=C["border"], border_color=C["border"], border_width=1, corner_radius=6, width=90, height=30, command=self._clear).pack(side="right")

        # ── history ──
        self._build_history()

        # ── footer status ──
        self.footer = ctk.CTkLabel(self, text="", font=ctk.CTkFont(family="Courier New", size=9), text_color=C["muted"])
        self.footer.pack(side="bottom", padx=28, pady=(0, 8))

    def _build_history(self):
        self.hist_frame = ctk.CTkFrame(self, fg_color=C["surface"], border_color=C["border"], border_width=1, corner_radius=10)
        self.hist_frame.pack(fill="x", padx=28, pady=(0, 12))

        hdr = ctk.CTkFrame(self.hist_frame, fg_color="transparent")
        hdr.pack(fill="x", padx=14, pady=(10, 2))

        ctk.CTkLabel(hdr, text="HISTORIAL", font=ctk.CTkFont(family="Courier New", size=11, weight="bold"), text_color=C["muted"]).pack(side="left")
        ctk.CTkButton(hdr, text="BORRAR TODO", font=ctk.CTkFont(family="Courier New", size=9), fg_color="transparent", hover_color=C["border"], text_color=C["muted"], width=100, height=22, command=self._clear_history).pack(side="right")

        self.hist_list = ctk.CTkScrollableFrame(self.hist_frame, fg_color="transparent", height=120)
        self.hist_list.pack(fill="x", padx=6, pady=(0, 8))
        self._render_history()

    # ── orb drawing ──────────────────────────
    def _draw_orb_idle(self):
        c = self.orb_canvas
        c.delete("all")
        cx, cy = 100, 90
        r = 34
        # Outer glow
        for i in range(8):
            a = 0.03 - i * 0.003
            rr = r + i * 6
            color = f"#{int(160*a*255):02x}{int(216*a*255):02x}{int(241*a*255):02x}"
            c.create_oval(cx - rr, cy - rr, cx + rr, cy + rr, fill=color, outline="", tags="orb_bg")
        # Main circle
        c.create_oval(cx - r, cy - r, cx + r, cy + r, fill=C["mid"], outline="", tags="orb")
        c.create_oval(cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4, fill="", outline=C["bright"], width=1, tags="orb")
        # Mic icon
        c.create_oval(cx - 10, cy - 14, cx + 10, cy + 6, fill="", outline=C["bg"], width=2, tags="orb_icon")
        c.create_line(cx - 5, cy + 6, cx - 5, cy + 18, fill=C["bg"], width=2, tags="orb_icon")
        c.create_line(cx + 5, cy + 6, cx + 5, cy + 18, fill=C["bg"], width=2, tags="orb_icon")
        c.create_line(cx - 18, cy + 18, cx + 18, cy + 18, fill=C["bg"], width=3, tags="orb_icon")

    def _draw_orb_recording(self):
        c = self.orb_canvas
        c.delete("all")
        cx, cy = 100, 90
        a = 0.6 + 0.4 * abs(np.sin(self._pulse * 2))
        rr = 34 + int(a * 8)
        # Glow pulse
        c.create_oval(cx - rr - 10, cy - rr - 10, cx + rr + 10, cy + rr + 10, fill=C["danger"], outline="", stipple="gray50")
        c.create_oval(cx - rr, cy - rr, cx + rr, cy + rr, fill=C["danger"], outline="")
        # Stop icon
        c.create_rectangle(cx - 10, cy - 10, cx + 10, cy + 10, fill=C["bg"], outline="", tags="orb_icon")

    # ── record actions ───────────────────────
    def _toggle_record(self):
        if self.recording:
            self._stop()
        else:
            self._start()

    def _start(self):
        self.recording = True
        self._draw_orb_recording()
        self._blink_dot()
        self._pulse_anim()
        self.status_label.configure(text="GRABANDO — pulsa el orb para parar", text_color=C["danger"])
        self.footer.configure(text="Habla ahora…")

        def _on_err(msg):
            self.after(0, lambda: self._on_error(msg))

        self.recorder = Recorder(on_text=lambda t: self.after(0, lambda: self._set_text(t)), on_error=_on_err)
        threading.Thread(target=self.recorder.start, daemon=True).start()

    def _stop(self):
        self.recording = False
        self.status_label.configure(text="Procesando…", text_color=C["muted"])
        self.footer.configure(text="Transcribiendo último fragmento…")
        self._stop_blink()
        self._stop_anim()
        self._draw_orb_idle()

        def _finish():
            try:
                final = self.recorder.stop() if self.recorder else ""
            except Exception as e:
                self.after(0, lambda: self._on_error(f"Stop error: {e}"))
                return
            self.recorder = None
            self.after(0, lambda: self._on_final(final))

        threading.Thread(target=_finish, daemon=True).start()

    def _on_final(self, text):
        self.status_label.configure(text="Listo", text_color=C["bright"])
        self.footer.configure(text="")
        if text and text.strip():
            current = self.text_box.get("1.0", "end-1c").strip()
            if current:
                self.text_box.delete("1.0", "end")
                self.text_box.insert("1.0", current + "\n\n" + text.strip())
            else:
                self.text_box.insert("1.0", text.strip())
            self._update_char_count()
            self._add_to_history(text.strip())

    def _on_error(self, msg):
        self.status_label.configure(text=f"ERROR: {msg[:60]}", text_color=C["danger"])
        self.footer.configure(text="Revisa que el micrófono esté conectado")
        self.recording = False
        self._stop_blink()
        self._stop_anim()
        self._draw_orb_idle()
        self.recorder = None

    def _set_text(self, text):
        self.text_box.delete("1.0", "end")
        self.text_box.insert("1.0", text)
        self._update_char_count()

    def _update_char_count(self):
        self.char_label.configure(text=f"{len(self.text_box.get('1.0','end-1c'))} caracteres")

    # ── animations ───────────────────────────
    def _blink_dot(self):
        if not self.recording:
            return
        visible = self.rec_dot.cget("text_color") == C["bg"]
        self.rec_dot.configure(text_color=C["bright"] if visible else C["bg"])
        self._blink_id = self.after(550, self._blink_dot)

    def _stop_blink(self):
        if self._blink_id:
            self.after_cancel(self._blink_id)
            self._blink_id = None
        self.rec_dot.configure(text_color=C["bg"])

    def _pulse_anim(self):
        if not self.recording:
            return
        self._pulse += 0.1
        self._draw_orb_recording()
        self._anim_id = self.after(50, self._pulse_anim)

    def _stop_anim(self):
        if self._anim_id:
            self.after_cancel(self._anim_id)
            self._anim_id = None

    # ── history ──────────────────────────────
    def _add_to_history(self, text):
        entries = load_history()
        entries.insert(0, {"text": text, "ts": datetime.now().isoformat()})
        entries = entries[:50]
        save_history(entries)
        self._render_history()

    def _clear_history(self):
        save_history([])
        self._render_history()

    def _render_history(self):
        for w in self.hist_list.winfo_children():
            w.destroy()
        entries = load_history()
        if not entries:
            ctk.CTkLabel(self.hist_list, text="No hay transcripciones aún", font=ctk.CTkFont(family="Courier New", size=10), text_color=C["muted"]).pack(pady=12)
            return
        for i, e in enumerate(entries[:20]):
            row = ctk.CTkFrame(self.hist_list, fg_color=C["surface2"], corner_radius=6)
            row.pack(fill="x", pady=2)
            ts = datetime.fromisoformat(e["ts"]).strftime("%H:%M") if "ts" in e else ""
            txt = e["text"][:120] + ("…" if len(e["text"]) > 120 else "")
            ctk.CTkLabel(row, text=f"{ts}  {txt}", font=ctk.CTkFont(family="Courier New", size=10), text_color=C["text"], anchor="w", justify="left").pack(side="left", padx=8, pady=4, fill="x", expand=True)
            idx = i
            ctk.CTkButton(row, text="COPIAR", font=ctk.CTkFont(family="Courier New", size=8), fg_color="transparent", hover_color=C["border"], text_color=C["mid"], width=55, height=20, command=lambda j=idx: self._copy_hist(j)).pack(side="right", padx=(0, 2), pady=2)
            ctk.CTkButton(row, text="✕", font=ctk.CTkFont(size=10), fg_color="transparent", hover_color=C["danger"], text_color=C["muted"], width=25, height=20, command=lambda j=idx: self._del_hist(j)).pack(side="right", pady=2)

    def _copy_hist(self, idx):
        entries = load_history()
        if 0 <= idx < len(entries):
            self.clipboard_clear()
            self.clipboard_append(entries[idx]["text"])
            self.footer.configure(text="Copiado ✓", text_color=C["bright"])
            self.after(2000, lambda: self.footer.configure(text=""))

    def _del_hist(self, idx):
        entries = load_history()
        if 0 <= idx < len(entries):
            entries.pop(idx)
            save_history(entries)
            self._render_history()

    # ── toolbar actions ──────────────────────
    def _copy(self):
        self.clipboard_clear()
        self.clipboard_append(self.text_box.get("1.0", "end-1c"))
        self.footer.configure(text="Copiado ✓", text_color=C["bright"])
        self.after(2000, lambda: self.footer.configure(text=""))

    def _clear(self):
        self.text_box.delete("1.0", "end")
        self._update_char_count()


# ─── entry ──────────────────────────────────
def main():
    app = App()
    app.withdraw()  # hidden until splash ends
    app.mainloop()


if __name__ == "__main__":
    main()
