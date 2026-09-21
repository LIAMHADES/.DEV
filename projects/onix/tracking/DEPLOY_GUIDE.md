# Guía de Despliegue — Tracking ONIX en PythonAnywhere (GRATIS)

El backend está versionado en `projects/onix/tracking` dentro de `LIAMHADES/.DEV`.
La web pública de GitHub Pages sigue siendo estática; PythonAnywhere ejecuta este
backend y conserva la base SQLite del piloto.

## PASO 1 — Crear cuenta en PythonAnywhere (3 min)

1. Ve a https://www.pythonanywhere.com
2. Click "Start running Python online" → "Create a Beginner account"
3. Username: elige uno (ej: `onix-tracking`)
4. Email: tu email
5. **Confirmar email** (importante, sin confirmar no funciona)

**Coste: 0€. El plan Beginner es gratis sin caducidad.**

---

## PASO 2 — Clonar el repositorio (5 min)

1. En PythonAnywhere, abre una consola **Bash**.
2. Ejecuta:
   ```bash
   git clone https://github.com/LIAMHADES/.DEV.git
   cd .DEV/projects/onix/tracking
   ```
3. Verifica que existen `app.py`, `flask_app.py`, `requirements.txt` y `static/onix-round.png`.

---

## PASO 3 — Configurar la Web App (5 min)

1. Ve a la pestaña **"Web"**
2. Click **"Add a new web app"**
3. Click "Next" (deja domain por defecto: `TU_USUARIO.pythonanywhere.com`)
4. Selecciona **"Flask"** y la última versión de Python (3.10 o superior)
5. En "Path to Flask app", pon: `/home/TU_USUARIO/.DEV/projects/onix/tracking/flask_app.py`
6. Click "Next" y luego "Next" para terminar

> Sustituye `TU_USUARIO` por el usuario real de PythonAnywhere en todos los pasos.

---

## PASO 4 — Inicializar la base de datos (2 min)

1. Ve a la pestaña **"Consoles"**
2. Abre una consola **"Bash"**
3. Ejecuta:
   ```bash
   cd /home/TU_USUARIO/mysite
   python3 -c "from app import init_db; init_db(); print('BD creada correctamente')"
   ```
4. Deberías ver "BD creada correctamente"

## Secretos de producción

Antes de abrir la web públicamente, configura estas variables en el entorno de la aplicación:

- `ONIX_ADMIN_PASSWORD_HASH`: SHA-256 de una contraseña nueva; no uses `onix2026`.
- `ONIX_DEVICE_SALT`: valor aleatorio largo, privado y estable. Si cambia, las recurrencias históricas dejarán de coincidir.
- `ONIX_SECRET_KEY`: valor aleatorio largo para firmar la sesión del panel admin.
- `ONIX_COOKIE_SECURE=1`: activa cookies de sesión solo por HTTPS.

La plantilla `.env.example` contiene los nombres, pero los valores reales nunca deben subirse al repositorio.

---

## PASO 5 — Probar que funciona (5 min)

1. Ve a la pestaña **"Web"**
2. Click el botón grande verde **"Reload"**
3. Abre en el navegador: `https://TU_USUARIO.pythonanywhere.com/admin`
4. Verás la página de login. Usa la contraseña cuyo SHA-256 configuraste en `ONIX_ADMIN_PASSWORD_HASH`.
5. Entra al admin y añade un cliente de prueba:
   - slug: `test`
   - nombre: `Test Negocio`
   - sector: `test`
   - url_destino: `https://onixgirona.com` (o cualquier URL `http://`/`https://` válida)
6. Abre `https://TU_USUARIO.pythonanywhere.com/t/test`
   - Verás el splash ONIX animado
    - Después de 2s por defecto, redirigirá a la URL configurada
7. Abre `https://TU_USUARIO.pythonanywhere.com/d/test`
   - Verás el dashboard con 1 toque registrado

---

## PASO 6 — Programar chip NFC

Usa la app **NFC Tools** (gratis en Android/iOS):

1. Abre NFC Tools
2. Ve a "Escribir" → "Añadir un registro" → "URL"
3. Pega la URL estable: `https://TU_USUARIO.pythonanywhere.com/t/test`
4. Acerca un chip NFC al móvil → "Escribir"
5. Acerca el chip al móvil otra vez → deberías ver el splash ONIX

La URL del chip es la de ONIX, no la URL final del negocio. Si el negocio cambia de web,
se actualiza `url_destino` desde el panel y no hace falta reprogramar el chip.

## Cómo funciona el flujo

1. El móvil lee el chip y abre `/t/<slug>`.
2. ONIX verifica que el cliente existe, está activo y tiene un destino `http`/`https` válido.
3. ONIX registra el toque en SQLite y calcula una huella server-side para estimar recurrencia sin cookies ni `localStorage`.
4. Se muestra el splash ONIX durante 2 segundos por defecto.
5. El navegador redirige a `url_destino`, que puede cambiarse desde el panel admin.
6. Las rutas `/c/<slug>`, `/pedir/<slug>` y `/menu/<slug>` son flujos opcionales de captación; validan el cliente y los datos antes de guardar un lead.

## Estado antes de producción

- Las rutas principales y capturas tienen pruebas automatizadas en `tests/test_tracking_app.py`.
- El panel admin usa sesión firmada; la contraseña no se reenvía en cada alta.
- Sigue pendiente añadir protección CSRF y rate limiting al panel si se expone directamente a Internet.
- La política de privacidad y la base legal del hash de dispositivo deben revisarse con asesoría legal antes de captar datos reales.

---

## URLs de tu tracking

| Ruta | Función |
|---|---|
| `https://TU_USUARIO.pythonanywhere.com/admin` | Panel de administración |
| `https://TU_USUARIO.pythonanywhere.com/t/test` | NFC apunta aquí → splash → redirige |
| `https://TU_USUARIO.pythonanywhere.com/d/test` | Dashboard del cliente |
| `https://TU_USUARIO.pythonanywhere.com/pedir/test` | Lista de espera / pedir cita |
| `https://TU_USUARIO.pythonanywhere.com/menu/test` | Menú condicionado (email a cambio de contenido) |

---

## SOLUCIÓN DE PROBLEMAS

### "Something went wrong" al recargar
→ Ve a la pestaña "Web" → Scroll abajo → "Log files" → Mira el error log
→ Lo más común: typo en el path del WSGI o Python path mal configurado

### "No module named flask"
→ Abre una consola Bash y ejecuta:
```bash
pip3 install --user flask
```
→ Luego vuelve a la pestaña "Web" y haz "Reload"

### Error 500 en /admin
→ La BD no se inicializó. Ve a la consola Bash y ejecuta:
```bash
    cd /home/TU_USUARIO/.DEV/projects/onix/tracking
python3 -c "from app import init_db; init_db()"
```

## Conexión con la URL del chip

El chip no guarda la web final del negocio. Guarda una URL estable de ONIX:

```text
https://TU_USUARIO.pythonanywhere.com/t/test
```

`test` es el `slug` del negocio en la tabla `clientes`. Cuando el móvil lee el chip:

1. El navegador entra en `/t/test`.
2. Flask busca `clientes.slug = "test"`.
3. Flask registra el toque en `toques`.
4. Muestra el logo circular ONIX durante `ONIX_SPLASH_SECONDS` segundos.
5. Redirige al valor actual de `url_destino`.

Si el negocio cambia de web, se modifica `url_destino` desde `/admin`; el chip no se
reprograma porque su URL estable sigue siendo la misma.
