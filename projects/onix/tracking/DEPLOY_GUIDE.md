# Guía de Despliegue — Tracking ONIX en Render + Supabase (staging)

El backend está versionado en `projects/onix/tracking` dentro de `LIAMHADES/.DEV`.
La web pública de GitHub Pages sigue siendo estática; Render ejecuta este backend y
Supabase conserva la base PostgreSQL del staging. No uses SQLite como persistencia de
Render: su disco es efímero.

## PASO 1 — Crear los servicios gratuitos (5 min)

1. Crea un proyecto en https://supabase.com y copia su connection string de PostgreSQL.
2. Crea un servicio Web en https://render.com conectado al repositorio.
3. Configura `Root Directory` como `projects/onix/tracking`.
4. Usa el `render.yaml` de la raíz del repositorio como configuración del Blueprint.
5. Ejecuta `migrations/001_initial.sql` y después `migrations/002_scalable_analytics.sql`
   en el SQL Editor de Supabase.

**Render y Supabase tienen límites gratuitos.** Este despliegue es staging y no debe
usarse todavía para datos reales de clientes sin revisar retención, privacidad y
condiciones actuales de ambos servicios.

---

## PASO 2 — Configurar Render (5 min)

1. Conecta el repositorio `LIAMHADES/.DEV` en Render.
2. Selecciona `Web Service` y `Root Directory = projects/onix/tracking`.
3. Build command: `pip install -r requirements.txt`.
4. Start command: `gunicorn --bind 0.0.0.0:$PORT flask_app:application`.
5. Health check: `/admin`.

---

## PASO 3 — Configurar las variables (5 min)

En Render configura estas variables, sin subirlas al repositorio:

- `ONIX_ENV=staging`
- `ONIX_DATABASE_URL`: connection string de Supabase.
- `ONIX_ADMIN_PASSWORD_HASH`: hash Werkzeug generado con `generate_password_hash`.
- `ONIX_DEVICE_SALT`: secreto aleatorio estable.
- `ONIX_SECRET_KEY`: secreto aleatorio estable para la sesión.
- `ONIX_TRUST_PROXY=1`
- `ONIX_COOKIE_SECURE=1`
- `ONIX_SPLASH_SECONDS=2`
- `ONIX_RATE_LIMIT_STORAGE_URI=memory://`

Para generar el hash sin guardar la contraseña en el repositorio:

```bash
python -c "import getpass; from werkzeug.security import generate_password_hash; print(generate_password_hash(getpass.getpass()))"
```

---

## PASO 4 — Inicializar la base de datos (2 min)

1. En Supabase abre **SQL Editor**.
2. Ejecuta el contenido de `migrations/001_initial.sql` y después `migrations/002_scalable_analytics.sql`.
3. Para crear los dos negocios demo, ejecuta localmente con `ONIX_DATABASE_URL` apuntando a Supabase:
   ```bash
   python seed_demo.py
   ```

## Secretos de producción

Antes de abrir la web públicamente, configura estas variables en el entorno de la aplicación:

- `ONIX_ADMIN_PASSWORD_HASH`: hash Werkzeug de una contraseña nueva; no uses `onix2026`.
- `ONIX_DEVICE_SALT`: valor aleatorio largo, privado y estable. Si cambia, las recurrencias históricas dejarán de coincidir.
- `ONIX_SECRET_KEY`: valor aleatorio largo para firmar la sesión del panel admin.
- `ONIX_COOKIE_SECURE=1`: activa cookies de sesión solo por HTTPS.

La plantilla `.env.example` contiene los nombres, pero los valores reales nunca deben subirse al repositorio.

---

## PASO 5 — Probar que funciona (5 min)

1. Espera a que Render termine el deploy y copia `https://TU_SERVICIO.onrender.com`.
2. Abre `https://TU_SERVICIO.onrender.com/admin`.
3. Inicia sesión con la contraseña usada para generar el hash Werkzeug.
4. Abre `https://TU_SERVICIO.onrender.com/t/test-element`.
    - Verás el splash ONIX animado
    - Después de 2s por defecto, redirigirá al destino de Element.
5. Repite con `https://TU_SERVICIO.onrender.com/t/test-cafe`.
6. Tras leer cada URL, abre `/d/test-element` y `/d/test-cafe` desde la sesión admin.

---

## PASO 6 — Programar chip NFC

Usa la app **NFC Tools** (gratis en Android/iOS):

1. Abre NFC Tools
2. Ve a "Escribir" → "Añadir un registro" → "URL"
3. Pega la URL estable: `https://TU_SERVICIO.onrender.com/t/test-element`
4. Acerca un chip NFC al móvil → "Escribir"
5. Acerca el chip al móvil otra vez → deberías ver el splash ONIX

La URL del chip es la de ONIX, no la URL final del negocio. Si el negocio cambia de web,
se actualiza `url_destino` desde el panel y no hace falta reprogramar el chip.

## Cómo funciona el flujo

1. El móvil lee el chip y abre `/t/<slug>`.
2. ONIX verifica que el cliente existe, está activo y tiene un destino `http`/`https` válido.
3. ONIX registra el toque en Supabase/PostgreSQL y calcula una huella server-side para estimar recurrencia sin cookies ni `localStorage`.
4. Se muestra el splash ONIX durante 2 segundos por defecto.
5. El navegador redirige a `url_destino`, que puede cambiarse desde el panel admin.
6. Las rutas `/c/<slug>`, `/pedir/<slug>` y `/menu/<slug>` son flujos opcionales de captación; validan el cliente y los datos antes de guardar un lead.

## Estado antes de producción

- Las rutas principales y capturas tienen pruebas automatizadas en `tests/test_tracking_app.py`.
- El panel admin usa sesión firmada; la contraseña no se reenvía en cada alta.
- El staging ya incluye CSRF, cabeceras de seguridad, HTTPS forzado, hash de contraseña y rate limiting.
- La política de privacidad y la base legal del hash de dispositivo deben revisarse con asesoría legal antes de captar datos reales.

---

## URLs de tu tracking

| Ruta | Función |
|---|---|
| `https://TU_SERVICIO.onrender.com/admin` | Panel de administración |
| `https://TU_SERVICIO.onrender.com/t/test-element` | NFC apunta aquí → splash → Google Maps |
| `https://TU_SERVICIO.onrender.com/d/test-element` | Dashboard del cliente |
| `https://TU_SERVICIO.onrender.com/pedir/test-element` | Lista de espera / pedir cita |
| `https://TU_SERVICIO.onrender.com/menu/test-element` | Menú condicionado (email a cambio de contenido) |

---

## SOLUCIÓN DE PROBLEMAS

### "Something went wrong" al desplegar
→ Revisa los logs del servicio en Render.
→ Lo más común: `Root Directory`, `Start Command` o variables de entorno incorrectas.

### "No module named flask"
→ Comprueba que el build instaló `requirements.txt` completo:
```bash
pip install -r requirements.txt
```

### Error 500 en /admin
→ Comprueba que `ONIX_DATABASE_URL`, `ONIX_SECRET_KEY`, `ONIX_DEVICE_SALT` y
`ONIX_ADMIN_PASSWORD_HASH` existen y que `001_initial.sql` se ejecutó en Supabase.

## Conexión con la URL del chip

El chip no guarda la web final del negocio. Guarda una URL estable de ONIX:

```text
https://TU_SERVICIO.onrender.com/t/test-element
```

`test-element` es el `slug` de Element Barbería en la tabla `clientes`. Cuando el móvil lee el chip:

1. El navegador entra en `/t/test-element`.
2. Flask busca `clientes.slug = "test-element"`.
3. Flask registra el toque en `toques`.
4. Muestra el logo circular ONIX durante `ONIX_SPLASH_SECONDS` segundos.
5. Redirige al valor actual de `url_destino`.

Si el negocio cambia de web, se modifica `url_destino` desde `/admin`; el chip no se
reprograma porque su URL estable sigue siendo la misma.
