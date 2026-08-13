# VtoTXforIA

Dictado por voz + transcripción local con Whisper.

## Dos componentes

### 1. Web demo (este directorio)
`index.html` — demo standalone en el navegador (Whisper WASM).
Abrir directamente en el navegador.

### 2. App de escritorio (REAL — la que usa el usuario)
**UBICACIÓN:** `C:\Users\solde\OneDrive\Desktop\EJECUTER_EXT\VtoTXforIA\`
**Acceso directo:** `V2TX4IA.lnk` en el escritorio.

Es la app **Tkinter** (`VtoTXforIA.py` + `vtotx_ui.py` + `vtotx_splash.py` + `vtotx_overlay.py` + `vtotx_history*.py`).

- Modelo: `faster-whisper small` (CPU, int8) — configurable en la UI
- Hotkey global: **F8** (graba/pausa desde cualquier app)
- Overlay flotante de grabación + toast de transcripción
- Splash screen dot-matrix animado
- Historial de sesiones + panel flotante
- Text injection (PostMessage) + clipboard
- System tray
- Paleta: cyan/azul (como la web)

> **NOTA PARA AGENTES:** No reemplazar esta app. Si el usuario pide cambios visuales,
> modificar SOLO colores/tipografías/animaciones en los `vtotx_*.py`. La funcionalidad
> (F8, overlay, tray, historial, PostMessage) NO se toca.
