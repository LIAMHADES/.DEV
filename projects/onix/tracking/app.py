"""
Sistema de Tracking ONIX — Página puente NFC
=============================================
/t/{slug}  → splash ONIX + contador visitas (server-side, sin cookies) → redirige al destino
/d/{slug}  → Dashboard del cliente
/c/{slug}  → Captación con doble consentimiento (campañas + insights de sector)
/pedir/{slug}  → Lista de espera / avísame
/menu/{slug}  → Menú condicionado (email a cambio de contenido)
/admin     → Panel admin
"""

from flask import Flask, request, redirect, render_template_string, jsonify, session, send_file
import sqlite3, os, json, hashlib, re
from datetime import datetime, timedelta
from uuid import uuid4
from html import escape
from urllib.parse import urlparse

app = Flask(__name__)
DB = os.path.join(os.path.dirname(__file__), "tracking.db")
MASTER_LOGO = os.path.join(os.path.dirname(__file__), "assets", "onix-logo.png")
DEVICE_SALT_SECRET = os.environ.get("ONIX_DEVICE_SALT", "onix_dev_salt_2026_CAMBIAR_EN_PROD")
app.secret_key = os.environ.get("ONIX_SECRET_KEY", "onix_dev_secret_CAMBIAR_EN_PROD")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("ONIX_COOKIE_SECURE", "0") == "1",
)

# Contraseña de /admin: se lee como HASH desde variable de entorno, nunca en texto plano.
# Si falta la variable, el login queda bloqueado de forma segura.
ADMIN_PASSWORD_HASH = os.environ.get(
    "ONIX_ADMIN_PASSWORD_HASH",
    ""
)

try:
    SPLASH_SECONDS = max(1, min(5, int(os.environ.get("ONIX_SPLASH_SECONDS", "1"))))
except ValueError:
    SPLASH_SECONDS = 2


def check_admin_password(password: str) -> bool:
    return hashlib.sha256((password or "").encode()).hexdigest() == ADMIN_PASSWORD_HASH


def is_valid_destination(url: str) -> bool:
    """Allow only absolute HTTP(S) destinations for client redirects."""
    try:
        parsed = urlparse((url or "").strip())
    except ValueError:
        return False
    return parsed.scheme.lower() in {"http", "https"} and bool(parsed.netloc)


def is_valid_phone(phone: str) -> bool:
    compact = re.sub(r"[\s().-]", "", (phone or "").strip())
    return bool(re.fullmatch(r"\+?\d{9,15}", compact))


def is_valid_email(email: str) -> bool:
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", (email or "").strip()))


def safe_script_json(value: str) -> str:
    """Serialize a string for an inline script without allowing </script> breakout."""
    return (json.dumps(value, ensure_ascii=True)
            .replace("<", "\\u003c")
            .replace(">", "\\u003e")
            .replace("&", "\\u0026"))


def valid_slug(slug: str) -> bool:
    return bool(re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", (slug or "").strip()))


def compute_device_hash(ip: str, user_agent: str, slug: str) -> str:
    """Huella de dispositivo, calculada 100% server-side (sin localStorage/cookies).
    Estable por dispositivo+negocio (no rota en el tiempo, no cruza entre negocios) para
    permitir tracking real de recurrencia a largo plazo (nuevo/regular/ocasional).
    Base legal: interés legítimo (art. 6.1.f RGPD), no excepción de cookies — ver doc 45 §6
    y doc 46/47 (aviso + oposición en política de privacidad, sin checkbox de consentimiento
    porque no hay PII directa, solo un hash). No se guarda IP ni User-Agent en claro."""
    raw = f"{ip}|{user_agent}|{slug}|{DEVICE_SALT_SECRET}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def get_client_ip() -> str:
    fwd = request.headers.get("X-Forwarded-For", "")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.remote_addr or "0.0.0.0"


def init_db():
    with sqlite3.connect(DB) as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                slug TEXT PRIMARY KEY, nombre TEXT NOT NULL, sector TEXT,
                url_destino TEXT NOT NULL, activo INTEGER DEFAULT 1,
                creado TEXT DEFAULT (datetime('now','localtime')),
                tipo_campana TEXT DEFAULT 'sorteo',
                premio TEXT DEFAULT ''
            )""")
        c.execute("""
            CREATE TABLE IF NOT EXISTS toques (
                id INTEGER PRIMARY KEY AUTOINCREMENT, slug TEXT NOT NULL,
                fecha TEXT DEFAULT (datetime('now','localtime')), dispositivo TEXT,
                device_id TEXT,
                device_hash TEXT,
                FOREIGN KEY (slug) REFERENCES clientes(slug)
            )""")
        c.execute("""
            CREATE TABLE IF NOT EXISTS leads_clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                negocio_slug TEXT NOT NULL, telefono TEXT, email TEXT,
                nombre TEXT, fecha_captacion TEXT DEFAULT (datetime('now','localtime')),
                fuente TEXT, motivo TEXT,
                acepta_campanas INTEGER DEFAULT 0,
                texto_consentimiento TEXT,
                acepta_insights_sector INTEGER DEFAULT 0,
                texto_consentimiento_insights TEXT,
                device_hash TEXT,
                FOREIGN KEY (negocio_slug) REFERENCES clientes(slug)
            )""")
        c.execute("CREATE INDEX IF NOT EXISTS idx_toques_slug ON toques(slug)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_leads_slug ON leads_clientes(negocio_slug)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_toques_hash ON toques(device_hash)")
        c.commit()

        # Migración no destructiva para BDs ya existentes (columnas añadidas julio 2026)
        cols_toques = {r[1] for r in c.execute("PRAGMA table_info(toques)")}
        if "device_hash" not in cols_toques:
            c.execute("ALTER TABLE toques ADD COLUMN device_hash TEXT")

        cols_leads = {r[1] for r in c.execute("PRAGMA table_info(leads_clientes)")}
        for col, ddl in [
            ("acepta_campanas", "ALTER TABLE leads_clientes ADD COLUMN acepta_campanas INTEGER DEFAULT 0"),
            ("texto_consentimiento", "ALTER TABLE leads_clientes ADD COLUMN texto_consentimiento TEXT"),
            ("acepta_insights_sector", "ALTER TABLE leads_clientes ADD COLUMN acepta_insights_sector INTEGER DEFAULT 0"),
            ("texto_consentimiento_insights", "ALTER TABLE leads_clientes ADD COLUMN texto_consentimiento_insights TEXT"),
            ("device_hash", "ALTER TABLE leads_clientes ADD COLUMN device_hash TEXT"),
        ]:
            if col not in cols_leads:
                c.execute(ddl)

        cols_clientes = {r[1] for r in c.execute("PRAGMA table_info(clientes)")}
        for col, ddl in [
            ("tipo_campana", "ALTER TABLE clientes ADD COLUMN tipo_campana TEXT DEFAULT 'sorteo'"),
            ("premio", "ALTER TABLE clientes ADD COLUMN premio TEXT DEFAULT ''"),
        ]:
            if col not in cols_clientes:
                c.execute(ddl)
        c.commit()

# ============================================================
# SPLASH ONIX - 100% pasivo, sin cookies ni localStorage.
# La huella de dispositivo se calcula server-side (ver doc 45 seccion 6).
# ============================================================
SPLASH_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ONIX - Tu negocio, a un toque</title>
<link rel="preconnect" href="https://www.google.com">
<link rel="preconnect" href="https://search.google.com">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#080705;display:flex;align-items:center;justify-content:center;
     height:100vh;overflow:hidden;font-family:system-ui}
  .logo{width:min(58vw,280px);animation:arrive 1s cubic-bezier(.16,1,.3,1) both}
 @keyframes arrive{0%{opacity:0;transform:scale(.6) rotate(-8deg)}55%{opacity:1;transform:scale(1.04) rotate(0)}100%{opacity:1;transform:scale(1)}}
 @media(prefers-reduced-motion:reduce){.logo{animation:none}}
</style>
<script>
 setTimeout(function(){ window.location.href = {url_destino_json}; }, {splash_seconds}000);
</script>
</head>
<body>
<img class="logo" src="/onix-logo.png" alt="ONIX">
</body>
</html>"""

@app.route("/t/<slug>")
def track_and_redirect(slug):
    dispositivo = request.headers.get("User-Agent", "desconocido")[:200]
    ip = get_client_ip()
    device_hash = compute_device_hash(ip, dispositivo, slug)

    with sqlite3.connect(DB) as c:
        cliente = c.execute(
            "SELECT nombre, url_destino, activo FROM clientes WHERE slug=?", (slug,)
        ).fetchone()
        if not cliente or not cliente[1] or not cliente[2]:
            return "Stand no encontrado", 404
        if not is_valid_destination(cliente[1]):
            return "Destino no configurado correctamente", 500

        # Hash estable por dispositivo+negocio (sin ventana temporal): cuenta todo el
        # historico, permite distinguir clientes nuevos/regulares/ocasionales a largo plazo.
        visitas_previas = c.execute(
            "SELECT COUNT(*) FROM toques WHERE slug=? AND device_hash=?",
            (slug, device_hash)
        ).fetchone()[0]

        c.execute(
            "INSERT INTO toques (slug, dispositivo, device_hash) VALUES (?,?,?)",
            (slug, dispositivo, device_hash)
        )
        c.commit()

    count = visitas_previas + 1
    print(
        f"[ONIX NFC] {datetime.now().isoformat(timespec='seconds')} "
        f"slug={slug} negocio={cliente[0]!r} toque={count} "
        f"device={device_hash[:8]}",
        flush=True,
    )

    html = (SPLASH_HTML
            .replace("{url_destino_json}", safe_script_json(cliente[1]))
            .replace("{splash_seconds}", str(SPLASH_SECONDS)))
    return html

@app.route("/t/<slug>/device", methods=["POST"])
def track_device_deprecated(slug):
    """Ruta obsoleta: la huella de dispositivo ahora se calcula 100% server-side
    (sin localStorage) en /t/<slug>. Se mantiene solo para no romper clientes cacheados."""
    return jsonify({"ok": False, "deprecated": True}), 410

# ============================================================
# DASHBOARD DEL CLIENTE
# ============================================================
DASH_HTML = """<!DOCTYPE html><html lang="es"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ONIX — {{ nombre }}</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#080705;color:#F0EBE3;font-family:'Segoe UI',system-ui,sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center}
.card{background:#1a1612;border:1px solid #2a2520;border-radius:16px;padding:40px;max-width:420px;width:90%;text-align:center}
h1{font-size:28px;margin-bottom:4px}
.badge{display:inline-block;background:#E8A04422;color:#E8A044;padding:4px 14px;border-radius:20px;font-size:13px;margin-bottom:24px}
.bignum{font-size:72px;font-weight:800;color:#E8A044;line-height:1}
.label{color:#6B5D4F;font-size:14px;margin-bottom:32px}
.row{display:flex;justify-content:space-between;padding:12px 0;border-top:1px solid #2a2520;font-size:14px}
.row span:last-child{color:#E8A044;font-weight:600}
.footer{margin-top:24px;font-size:12px;color:#3a3028}
.cta{display:inline-block;margin-top:20px;padding:12px 24px;border-radius:8px;background:#E8A044;color:#080705;text-decoration:none;font-size:13px;font-weight:700}
</style></head><body>
<div class="card">
    <h1>{{ nombre }}</h1>
    <div class="badge">{{ sector }}</div>
    <div class="bignum">{{ total }}</div>
    <div class="label">toques totales</div>
    <div class="row"><span>Hoy</span><span>{{ hoy }}</span></div>
    <div class="row"><span>Esta semana</span><span>{{ semana }}</span></div>
    <div class="row"><span>Este mes</span><span>{{ mes }}</span></div>
    <div class="row"><span>Último toque</span><span>{{ ultimo }}</span></div>
    <div class="row"><span>Leads captados</span><span>{{ leads }}</span></div>
    <div class="row"><span>Recurrentes (estimado)</span><span>{{ recurrentes }}</span></div>
    <div class="row"><span>Aceptan campañas</span><span>{{ acepta_camp }}</span></div>
    <div class="row"><span>Aceptan insights sector</span><span>{{ acepta_insights }}</span></div>
    <div class="footer">ONIX · Tu negocio, a un toque</div>
</div>
</body></html>"""

@app.route("/d/<slug>")
def dashboard(slug):
    with sqlite3.connect(DB) as c:
        cl = c.execute("SELECT nombre, sector FROM clientes WHERE slug=?", (slug,)).fetchone()
        if not cl: return "Dashboard no encontrado", 404
        nombre, sector = cl
        hoy = datetime.now().strftime("%Y-%m-%d")
        inicio_semana = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d")
        inicio_mes = datetime.now().strftime("%Y-%m") + "-01"
        total = c.execute("SELECT COUNT(*) FROM toques WHERE slug=?", (slug,)).fetchone()[0]
        hoy_n = c.execute("SELECT COUNT(*) FROM toques WHERE slug=? AND fecha LIKE ?",
                          (slug, f"{hoy}%")).fetchone()[0]
        semana_n = c.execute("SELECT COUNT(*) FROM toques WHERE slug=? AND fecha >= ?",
                             (slug, inicio_semana)).fetchone()[0]
        mes_n = c.execute("SELECT COUNT(*) FROM toques WHERE slug=? AND fecha >= ?",
                          (slug, inicio_mes)).fetchone()[0]
        ultimo = c.execute("SELECT fecha FROM toques WHERE slug=? ORDER BY fecha DESC LIMIT 1",
                           (slug,)).fetchone()
        ultimo_str = ultimo[0][:16] if ultimo else "—"
        leads = c.execute("SELECT COUNT(*) FROM leads_clientes WHERE negocio_slug=?",
                          (slug,)).fetchone()[0]
        recurrentes = c.execute("""
            SELECT COUNT(DISTINCT device_hash) FROM toques
            WHERE slug=? AND device_hash IS NOT NULL
            AND device_hash IN (
                SELECT device_hash FROM toques WHERE slug=? GROUP BY device_hash HAVING COUNT(*) > 1
            )""", (slug, slug)).fetchone()[0]
        acepta_camp = c.execute(
            "SELECT COUNT(*) FROM leads_clientes WHERE negocio_slug=? AND acepta_campanas=1",
            (slug,)).fetchone()[0]
        acepta_insights = c.execute(
            "SELECT COUNT(*) FROM leads_clientes WHERE negocio_slug=? AND acepta_insights_sector=1",
            (slug,)).fetchone()[0]
    return render_template_string(
        DASH_HTML, nombre=nombre, sector=sector, total=total,
        hoy=hoy_n, semana=semana_n, mes=mes_n, ultimo=ultimo_str, leads=leads,
        recurrentes=recurrentes, acepta_camp=acepta_camp, acepta_insights=acepta_insights)

# ============================================================
# CAPTACION CON DOBLE CONSENTIMIENTO - /c/<slug> (ver doc 45)
# ============================================================
CONSENT_TEXT_CAMPANAS = (
    "Acepto que {nombre} me contacte por WhatsApp/email con ofertas y novedades. "
    "Puedo darme de baja cuando quiera respondiendo BAJA."
)
CONSENT_TEXT_INSIGHTS = (
    "Acepto que ONIX use mis datos, de forma agregada y anonimizada junto a los de otros "
    "negocios del sector, para elaborar estudios estadisticos del sector {sector}. "
    "ONIX nunca compartira mi telefono, email o nombre con terceros. Puedo retirar este "
    "consentimiento en cualquier momento sin que afecte a mi relacion con {nombre}."
)
CONSENT_VERSION = "v1-2026-07"

CAPTACION_COPY = {
    "sorteo": {
        "titulo": "Participa en nuestro SORTEO MENSUAL!",
        "subtitulo": "Deja tu numero y llevate {premio}",
        "cta": "PARTICIPAR",
    },
    "oferta": {
        "titulo": "Un {premio} solo por dejarnos tu numero",
        "subtitulo": "Sin sorteos, sin esperas: te lo enviamos hoy mismo por WhatsApp.",
        "cta": "QUIERO MI REGALO",
    },
    "registro_recompensa": {
        "titulo": "Unete al club de {nombre}",
        "subtitulo": "Registrate y consigue {premio}.",
        "cta": "UNIRME",
    },
}

CAPTACION_HTML = """<!DOCTYPE html><html lang="es"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ nombre }} - Captacion</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#080705;color:#F0EBE3;font-family:'Segoe UI',system-ui,sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}
.card{background:#1a1612;border:1px solid #2a2520;border-radius:16px;padding:36px;max-width:440px;width:100%}
h1{font-size:22px;margin-bottom:6px}
p.sub{color:#9A8672;font-size:14px;margin:6px 0 20px;line-height:1.5}
input{padding:12px 14px;border:1px solid #2a2520;border-radius:8px;background:#0f0d0a;color:#F0EBE3;font-size:14px;width:100%;margin-bottom:10px}
.consent{display:flex;gap:10px;align-items:flex-start;margin:14px 0;font-size:12.5px;color:#9A8672;line-height:1.5}
.consent input{width:auto;margin:2px 0 0 0}
.context{font-size:12px;color:#6B5D4F;margin-bottom:10px;font-style:italic}
button{padding:13px;border-radius:8px;background:#E8A044;color:#080705;border:none;font-size:14px;font-weight:700;cursor:pointer;width:100%;margin-top:6px}
.error{color:#E04444;font-size:13px;display:none;margin-bottom:8px}
.succ{display:none;text-align:center;padding:20px 0;color:#8BC34A;font-size:16px}
.footer{margin-top:18px;font-size:11px;color:#3a3028;text-align:center}
</style></head><body>
<div class="card" id="app">
    <div id="form-view">
        <h1>{{ titulo }}</h1>
        <p class="sub">{{ subtitulo }}</p>
        {% if contexto %}<p class="context">{{ contexto }}</p>{% endif %}
        <input id="telefono" type="tel" placeholder="Tu telefono" autocomplete="tel" required>
        <input id="nombre_cliente" type="text" placeholder="Tu nombre (opcional)" autocomplete="name">
        <div class="error" id="err">Introduce un telefono valido</div>
        <label class="consent">
            <input type="checkbox" id="chk_campanas">
            <span>{{ texto_campanas }}</span>
        </label>
        <label class="consent">
            <input type="checkbox" id="chk_insights">
            <span>{{ texto_insights }}</span>
        </label>
        <button onclick="enviar()">{{ cta }}</button>
    </div>
    <div class="succ" id="succ">Gracias! Hemos recibido tus datos.</div>
    <div class="footer">ONIX - Tu negocio, a un toque</div>
</div>
<script>
function enviar(){
    var tel = document.getElementById('telefono').value.trim();
    if(tel.length < 9){ document.getElementById('err').style.display='block'; return; }
    document.getElementById('err').style.display='none';
    fetch({capture_endpoint}, {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({
            telefono: tel,
            nombre: document.getElementById('nombre_cliente').value.trim(),
            acepta_campanas: document.getElementById('chk_campanas').checked,
            acepta_insights_sector: document.getElementById('chk_insights').checked
        })
    }).then(function(response){
        if(!response.ok) throw new Error('captura fallida');
        document.getElementById('form-view').style.display='none';
        document.getElementById('succ').style.display='block';
    }).catch(function(){ document.getElementById('err').textContent='No se pudo enviar. Intentalo de nuevo'; document.getElementById('err').style.display='block'; });
}
</script>
</body></html>"""

@app.route("/c/<slug>", methods=["GET", "POST"])
def captacion(slug):
    with sqlite3.connect(DB) as c:
        cl = c.execute(
            "SELECT nombre, sector, tipo_campana, premio, activo FROM clientes WHERE slug=?", (slug,)
        ).fetchone()
        if not cl or not cl[4]:
            return "No encontrado", 404
        nombre, sector, tipo_campana, premio, _ = cl
        sector = sector or "tu sector"
        premio = premio or "un regalo"
        tipo_campana = tipo_campana if tipo_campana in CAPTACION_COPY else "sorteo"

        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            tel = data.get("telefono", "").strip()
            if not is_valid_phone(tel):
                return jsonify({"error": "telefono invalido"}), 400

            acepta_campanas = 1 if data.get("acepta_campanas") else 0
            acepta_insights = 1 if data.get("acepta_insights_sector") else 0

            texto_campanas = CONSENT_TEXT_CAMPANAS.format(nombre=nombre) if acepta_campanas else None
            texto_insights = CONSENT_TEXT_INSIGHTS.format(nombre=nombre, sector=sector) if acepta_insights else None

            ip = get_client_ip()
            ua = request.headers.get("User-Agent", "desconocido")[:200]
            device_hash = compute_device_hash(ip, ua, slug)

            c.execute("""
                INSERT INTO leads_clientes
                (negocio_slug, telefono, nombre, fuente, motivo,
                 acepta_campanas, texto_consentimiento,
                 acepta_insights_sector, texto_consentimiento_insights, device_hash)
                VALUES (?,?,?,?,?,?,?,?,?,?)
            """, (
                slug, tel, data.get("nombre", ""), "captacion", tipo_campana,
                acepta_campanas,
                (texto_campanas + " (" + CONSENT_VERSION + ", " + datetime.now().isoformat() + ")") if texto_campanas else None,
                acepta_insights,
                (texto_insights + " (" + CONSENT_VERSION + ", " + datetime.now().isoformat() + ")") if texto_insights else None,
                device_hash,
            ))
            c.commit()
            return jsonify({"ok": True})

    copy = CAPTACION_COPY[tipo_campana]
    contexto = (
        "Cuantos mas datos compartamos de forma anonima con el sector, mejor entendemos que valoras."
        if tipo_campana == "registro_recompensa" else ""
    )
    html = (CAPTACION_HTML
            .replace("{{ nombre }}", escape(nombre))
            .replace("{{ slug }}", escape(slug))
            .replace("{capture_endpoint}", safe_script_json("/c/" + slug))
            .replace("{{ titulo }}", escape(copy["titulo"].format(nombre=nombre, premio=premio)))
            .replace("{{ subtitulo }}", escape(copy["subtitulo"].format(nombre=nombre, premio=premio)))
            .replace("{{ cta }}", escape(copy["cta"]))
            .replace('{% if contexto %}<p class="context">{{ contexto }}</p>{% endif %}', ('<p class="context">' + contexto + '</p>') if contexto else "")
            .replace("{{ texto_campanas }}", escape(CONSENT_TEXT_CAMPANAS.format(nombre=nombre)))
            .replace("{{ texto_insights }}", escape(CONSENT_TEXT_INSIGHTS.format(nombre=nombre, sector=sector))))
    return html

# ============================================================
# PEDIR — Lista de espera / avísame (Estrategia #3)
# ============================================================
PEDIR_HTML = """<!DOCTYPE html><html lang="es"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ONIX — {{ nombre }}</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#080705;color:#F0EBE3;font-family:'Segoe UI',system-ui,sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}
.card{background:#1a1612;border:1px solid #2a2520;border-radius:16px;padding:36px;max-width:420px;width:100%}
h1{font-size:24px;margin-bottom:4px}
p{color:#9A8672;font-size:14px;margin:8px 0 20px;line-height:1.6}
.opt{background:#0f0d0a;border:1px solid #2a2520;border-radius:10px;padding:14px 16px;margin-bottom:8px;cursor:pointer;color:#F0EBE3;font-size:14px;transition:.2s}
.opt:hover{border-color:#E8A04444}
.opt.sel{border-color:#E8A044;background:#E8A04411}
form{display:none;margin-top:16px}
input{padding:12px 14px;border:1px solid #2a2520;border-radius:8px;background:#0f0d0a;color:#F0EBE3;font-size:14px;width:100%;margin-bottom:10px}
button{padding:12px;border-radius:8px;background:#E8A044;color:#080705;border:none;font-size:14px;font-weight:700;cursor:pointer;width:100%}
.succ{display:none;color:#8BC34A;font-size:16px;text-align:center;padding:24px}
.error{color:#E04444;font-size:13px;display:none}
</style></head><body>
<div class="card" id="app">
    <h1>{{ nombre }}</h1>
    <p>¿Qué necesitas? Cuéntanos y te llamamos.</p>
    <div id="options"></div>
    <form id="form">
        <input id="motivo" type="hidden">
        <input id="telefono" type="tel" placeholder="Tu teléfono" required>
        <input id="nombre_cliente" type="text" placeholder="Tu nombre (opcional)">
        <div class="error" id="err">Por favor, introduce un teléfono válido</div>
        <button type="submit">Enviar →</button>
    </form>
    <div class="succ" id="succ">✓ Recibido. Te llamamos pronto.</div>
</div>
<script>
var opciones = [
    "Reservar cita para la próxima vez",
    "Que me avisen cuando haya cita libre",
    "Pedir presupuesto",
    "Consultar disponibilidad / precio",
    "Hacer un encargo especial",
    "Otra cosa"
];
var opts = document.getElementById('options');
opciones.forEach(function(t){
    var d = document.createElement('div');
    d.className = 'opt';
    d.textContent = t;
    d.onclick = function(){
        document.querySelectorAll('.opt').forEach(function(o){o.classList.remove('sel');});
        d.classList.add('sel');
        document.getElementById('motivo').value = t;
        document.getElementById('form').style.display = 'block';
    };
    opts.appendChild(d);
});
document.getElementById('form').onsubmit = function(e){
    e.preventDefault();
    var tel = document.getElementById('telefono').value.trim();
    if(tel.length < 9){ document.getElementById('err').style.display='block'; return; }
    document.getElementById('err').style.display='none';
    fetch({capture_endpoint}, {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({
            telefono: tel,
            nombre: document.getElementById('nombre_cliente').value.trim(),
            motivo: document.getElementById('motivo').value
        })
    }).then(function(response){
        if(!response.ok) throw new Error('captura fallida');
        document.getElementById('form').style.display='none';
        document.getElementById('options').style.display='none';
        document.querySelector('p').style.display='none';
        document.getElementById('succ').style.display='block';
    }).catch(function(){ document.getElementById('err').textContent='No se pudo enviar. Intentalo de nuevo'; document.getElementById('err').style.display='block'; });
};
</script>
</div></body></html>"""

@app.route("/pedir/<slug>", methods=["GET", "POST"])
def pedir(slug):
    with sqlite3.connect(DB) as c:
        cl = c.execute("SELECT nombre, activo FROM clientes WHERE slug=?", (slug,)).fetchone()
        if not cl or not cl[1]: return "No encontrado", 404
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            tel = data.get("telefono", "").strip()
            if is_valid_phone(tel):
                device_hash = compute_device_hash(get_client_ip(), request.headers.get("User-Agent", "desconocido")[:200], slug)
                c.execute("INSERT INTO leads_clientes (negocio_slug, telefono, nombre, fuente, motivo, device_hash) VALUES (?,?,?,?,?,?)",
                          (slug, tel, data.get("nombre", ""), "pedir", data.get("motivo", ""), device_hash))
                c.commit()
                return jsonify({"ok": True})
            return jsonify({"error": "teléfono inválido"}), 400
    html = (PEDIR_HTML
            .replace("{{ nombre }}", escape(cl[0]))
            .replace("{capture_endpoint}", safe_script_json("/pedir/" + slug)))
    return html


@app.route("/onix-logo.png")
def onix_logo():
    """Serve only the user-provided master logo; never a generated substitute."""
    return send_file(MASTER_LOGO, mimetype="image/png", conditional=True)

# ============================================================
# MENÚ CONDICIONADO — email a cambio de contenido (Estrategia #5)
# ============================================================
MENU_HTML = """<!DOCTYPE html><html lang="es"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ nombre }} — Contenido</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#080705;color:#F0EBE3;font-family:'Segoe UI',system-ui,sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}
.card{background:#1a1612;border:1px solid #2a2520;border-radius:16px;padding:36px;max-width:420px;width:100%;text-align:center}
.logo{font-size:48px;font-weight:800;color:#E8A044;letter-spacing:6px;margin-bottom:4px}
p{color:#9A8672;font-size:14px;margin:10px 0 24px;line-height:1.6}
input{padding:12px 14px;border:1px solid #2a2520;border-radius:8px;background:#0f0d0a;color:#F0EBE3;font-size:14px;width:100%;margin-bottom:10px}
button{padding:12px;border-radius:8px;background:#E8A044;color:#080705;border:none;font-size:14px;font-weight:700;cursor:pointer;width:100%}
.succ{display:none}
.succ a{color:#E8A044}
</style></head><body>
<div class="card" id="app">
    <div class="logo">ONIX</div>
    <p>Déjanos tu email y accede a <strong>{{ contenido }}</strong></p>
    <div id="form-view">
        <input id="email" type="email" placeholder="Tu email">
        <input id="telefono_menu" type="tel" placeholder="Tu teléfono (opcional)">
        <button onclick="enviar()">Acceder →</button>
    </div>
    <div class="succ" id="succ">
        <p style="font-size:18px;color:#E8A044;margin-bottom:16px">✓ Gracias</p>
        <a href="{{ url_destino }}" target="_blank">Acceder al contenido →</a>
    </div>
</div>
<script>
function enviar(){
    var email = document.getElementById('email').value.trim();
    if(!email.includes('@')) return;
    fetch({capture_endpoint}, {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({email: email, telefono: document.getElementById('telefono_menu').value.trim()})
    }).then(function(response){
        if(!response.ok) throw new Error('captura fallida');
        document.getElementById('form-view').style.display='none';
        document.getElementById('succ').style.display='block';
    }).catch(function(){ alert('No se pudo enviar. Intentalo de nuevo'); });
}
</script>
</div></body></html>"""

@app.route("/menu/<slug>")
def menu_condicionado(slug):
    with sqlite3.connect(DB) as c:
        cl = c.execute("SELECT nombre, url_destino, activo FROM clientes WHERE slug=?", (slug,)).fetchone()
        if not cl or not cl[2] or not is_valid_destination(cl[1]): return "No encontrado", 404
    html = MENU_HTML.replace("{{ nombre }}", escape(cl[0]))
    html = html.replace("{{ url_destino }}", escape(cl[1], quote=True))
    html = html.replace("{capture_endpoint}", safe_script_json("/menu/" + slug + "/captura"))
    # Contenido por defecto
    html = html.replace("{{ contenido }}", "la carta / el contenido de " + escape(cl[0]))
    return html

@app.route("/menu/<slug>/captura", methods=["POST"])
def menu_captura(slug):
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip()
    telefono = data.get("telefono", "").strip()
    with sqlite3.connect(DB) as c:
        cl = c.execute("SELECT activo FROM clientes WHERE slug=?", (slug,)).fetchone()
        if not cl or not cl[0]:
            return jsonify({"error": "cliente no encontrado"}), 404
        if not is_valid_email(email) or (telefono and not is_valid_phone(telefono)):
            return jsonify({"error": "datos invalidos"}), 400
        c.execute("INSERT INTO leads_clientes (negocio_slug, email, telefono, fuente) VALUES (?,?,?,?)",
                  (slug, email, telefono, "menu"))
        c.commit()
    return jsonify({"ok": True})

# ============================================================
# ADMIN
# ============================================================

ADMIN_HTML = """<!DOCTYPE html><html><head><meta charset="utf-8"><title>ONIX Admin</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#080705;color:#F0EBE3;font-family:system-ui;padding:20px}
h1{color:#E8A044;margin-bottom:20px}
table{width:100%;border-collapse:collapse;margin-bottom:24px}
th,td{padding:10px 14px;text-align:left;border-bottom:1px solid #2a2520;font-size:14px}
th{color:#6B5D4F;font-size:12px;text-transform:uppercase}
form{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:24px}
input,button{padding:10px 14px;border:1px solid #2a2520;border-radius:8px;background:#1a1612;color:#F0EBE3;font-size:14px}
button{background:#E8A044;color:#080705;font-weight:600;cursor:pointer;border:none}
button:hover{opacity:.9}
</style></head><body>
<h1>ONIX — Admin</h1>
<form method="POST" action="/admin/add">
    <input name="slug" placeholder="slug" required>
    <input name="nombre" placeholder="Nombre negocio" required>
    <input name="sector" placeholder="Sector">
    <input name="url_destino" placeholder="URL destino" required>
    <select name="tipo_campana">
        <option value="sorteo">Sorteo</option>
        <option value="oferta">Oferta directa</option>
        <option value="registro_recompensa">Registro con recompensa</option>
    </select>
    <input name="premio" placeholder="Premio/recompensa">
    <button type="submit">Añadir cliente</button>
</form>
<table>
<tr><th>Slug</th><th>Nombre</th><th>Toques</th><th>Leads</th><th>Dashboard</th></tr>
{% for c in clientes %}
<tr>
    <td>{{ c.slug }}</td><td>{{ c.nombre }}</td><td>{{ c.toques }}</td><td>{{ c.leads }}</td>
    <td><a href="/d/{{ c.slug }}" style="color:#E8A044">Ver</a></td>
</tr>
{% endfor %}
</table>
<p style="color:#6B5D4F;font-size:12px">
    <a href="/pedir/{{ demo_slug }}" style="color:#E8A044">Demo lista de espera</a> ·
    <a href="/menu/{{ demo_slug }}" style="color:#E8A044">Demo menú condicionado</a> ·
    <a href="/c/{{ demo_slug }}" style="color:#E8A044">Demo captación (doble consentimiento)</a>
</p>
</body></html>"""

@app.route("/admin")
def admin_panel():
    if not session.get("admin_authenticated"):
        return render_template_string("""
<!DOCTYPE html><html><head><meta charset="utf-8"><title>Login</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#080705;display:flex;align-items:center;justify-content:center;height:100vh;font-family:system-ui}
form{display:flex;flex-direction:column;gap:12px}
input,button{padding:12px 18px;border-radius:8px;border:1px solid #2a2520;background:#1a1612;color:#F0EBE3;font-size:16px}
button{background:#E8A044;color:#080705;cursor:pointer;border:none}
</style></head><body>
<form method="POST" action="/admin/login">
    <input name="password" placeholder="Contraseña" type="password" autofocus>
    <button type="submit">Entrar</button>
</form>
</body></html>""")
    return render_admin()


def render_admin():
    with sqlite3.connect(DB) as c:
        clientes = c.execute("""
            SELECT cl.slug, cl.nombre,
                   (SELECT COUNT(*) FROM toques t WHERE t.slug=cl.slug) as toques,
                   (SELECT COUNT(*) FROM leads_clientes l WHERE l.negocio_slug=cl.slug) as leads
            FROM clientes cl ORDER BY toques DESC
        """).fetchall()
    html = ADMIN_HTML.replace("{{ demo_slug }}", clientes[0][0] if clientes else "")
    return render_template_string(
        html,
        clientes=[{"slug": r[0], "nombre": r[1], "toques": r[2], "leads": r[3]} for r in clientes])

@app.route("/admin/login", methods=["POST"])
def admin_login():
    if check_admin_password(request.form.get("password")):
        session.clear()
        session["admin_authenticated"] = True
        return redirect("/admin")
    return "Contraseña incorrecta", 403

@app.route("/admin/add", methods=["POST"])
def admin_add():
    if not session.get("admin_authenticated"):
        return "No autorizado", 403
    slug = request.form.get("slug", "").strip()
    url_destino = request.form.get("url_destino", "").strip()
    if not valid_slug(slug):
        return "Slug invalido: usa letras minusculas, numeros y guiones", 400
    if not is_valid_destination(url_destino):
        return "URL destino invalida: usa http:// o https://", 400
    with sqlite3.connect(DB) as c:
        c.execute("""
            INSERT OR REPLACE INTO clientes (slug, nombre, sector, url_destino, tipo_campana, premio)
            VALUES (?,?,?,?,?,?)
        """, (
            slug, request.form["nombre"].strip(),
            request.form.get("sector", "").strip(), url_destino,
            request.form.get("tipo_campana", "sorteo"),
            request.form.get("premio", "").strip(),
        ))
        c.commit()
    return redirect("/admin")


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect("/admin")

@app.route("/")
def home():
    return redirect("/admin")

# Inicializar BD al arrancar (desarrollo + WSGI)
init_db()

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8500, debug=True)
