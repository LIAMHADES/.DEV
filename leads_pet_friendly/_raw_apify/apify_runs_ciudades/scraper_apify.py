"""
ARES GPS — Apify re-scraper (26 ciudades Espana)
Fix encoding + add missing cities
"""
import json, urllib.request, time, os, re

APIFY_API = "https://api.apify.com/v2"
ACTOR = "scrapesage~google-maps-scraper"
TOKEN = os.environ.get("APIFY_API_TOKEN", "")

if not TOKEN:
    raise RuntimeError("Set APIFY_API_TOKEN before running the Apify scraper")

KEYWORDS = [
    "veterinario", "clinica veterinaria 24h", "parque para perros",
    "tienda de mascotas", "hotel pet friendly", "peluqueria canina",
    "adiestrador canino", "protectora de animales", "playa para perros",
    "guarderia canina", "residencia canina", "paseador de perros"
]

# All 26 cities + their mock keys
CITIES = [
    ("Madrid", "madrid"), ("Barcelona", "barcelona"), ("Valencia", "valencia"),
    ("Sevilla", "sevilla"), ("Zaragoza", "zaragoza"), ("Malaga", "malaga"),
    ("Murcia", "murcia"), ("Palma de Mallorca", "palma_de_mallorca"),
    ("Las Palmas de Gran Canaria", "las_palmas"), ("Bilbao", "bilbao"),
    ("Alicante", "alicante"), ("Cordoba", "cordoba"),
    ("Valladolid", "valladolid"), ("Vigo", "vigo"), ("Girona", "girona"),
    ("Oviedo", "oviedo"), ("Granada", "granada"),
    ("San Sebastian", "san_sebastian"), ("Santander", "santander"),
    ("Pamplona", "pamplona"), ("Salamanca", "salamanca"),
    ("A Coruna", "la_coruna"), ("Leon", "leon"),
    ("Santiago de Compostela", "santiago_de_compostela"),
    ("Cadiz", "cadiz"), ("Toledo", "toledo")
]

OUTPUT_DIR = r"C:\Users\solde\OneDrive\Desktop\ARES\GPS\landing\contenido\assets\js"
MAX_RESULTS = 4000
MAX_PER_SEARCH = 80

def start_run(queries):
    payload = {
        "searchQueries": queries,
        "maxResults": MAX_RESULTS,
        "maxPlacesPerSearch": MAX_PER_SEARCH,
        "language": "es",
        "countryCode": "es",
        "skipClosedPlaces": True,
        "enrichContacts": False,
        "scrapePlaceDetails": False,
        "sortBy": "rating",
    }
    url = f"{APIFY_API}/acts/{ACTOR}/runs?token={TOKEN}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode())
    rid = result["data"]["id"]
    did = result["data"].get("defaultDatasetId", "")
    print(f"STARTED Run={rid} Dataset={did} | {len(queries)} queries")
    return rid, did

def wait_run(run_id, max_wait=900):
    url = f"{APIFY_API}/acts/{ACTOR}/runs/{run_id}?token={TOKEN}"
    start = time.time()
    while time.time() - start < max_wait:
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read().decode())
            st = data["data"]["status"]
            if st == "SUCCEEDED":
                cost = data["data"].get("usageTotalUsd", 0)
                print(f"DONE | Cost: ${cost:.4f} | {int(time.time()-start)}s")
                return True, cost
            elif st in ("FAILED", "ABORTED", "TIMED-OUT"):
                print(f"STATUS={st}")
                return False, 0
            time.sleep(15)
        except Exception as e:
            print(f"Poll err: {e}")
            time.sleep(20)
    print("TIMEOUT")
    return False, 0

def download_results(run_id):
    url = f"{APIFY_API}/acts/{ACTOR}/runs/{run_id}/dataset/items?token={TOKEN}&format=json&clean=true"
    items = []
    offset = 0
    while True:
        p = f"{url}&offset={offset}&limit=1000"
        with urllib.request.urlopen(p, timeout=60) as resp:
            data = json.loads(resp.read().decode())
        if not data:
            break
        items.extend(data)
        offset += 1000
        print(f"  Downloaded {len(items)} items...")
    return items

def classify_type(category_name):
    cn = (category_name or "").lower()
    if any(k in cn for k in ("veterinaria","veterinario","vet")):
        return "veterinario"
    if any(k in cn for k in ("parque","perros area","dog park","pipican","esparcimiento")):
        return "parque"
    if any(k in cn for k in ("tienda","pet store","mascotas")):
        return "tienda"
    if any(k in cn for k in ("peluquer","groom","spa pe","esttica canin")):
        return "peluqueria"
    if any(k in cn for k in ("adiest","educac","entren","train","dog school")):
        return "adiestrador"
    if any(k in cn for k in ("hotel","hostal","apartahotel","alojamiento","albergue","pension","hostel")):
        return "alojamiento"
    if any(k in cn for k in ("protectora","animalist","refugio","adopcion","acogida","albergue municipal")):
        return "protectora"
    if any(k in cn for k in ("playa","beach","cala")):
        return "playa_perros"
    if any(k in cn for k in ("guarderia","daycare","residencia","kennel","boarding")):
        return "otros"
    return "otros"

def build_city_data(items, city_name):
    """Filter items for a specific city and return mock entries"""
    cn_lower = city_name.lower()
    entries = []
    seen = set()
    for item in items:
        addr = (item.get("street") or "").strip()
        city_item = (item.get("city") or "").strip()
        title = (item.get("title") or "").strip()
        loc = item.get("location", {})
        lat = loc.get("lat", 0) if loc else 0
        lng = loc.get("lng", 0) if loc else 0
        cat = item.get("categoryName") or ""

        # Match city: item's city field OR search query
        if city_item.lower() != cn_lower and cn_lower not in city_item.lower():
            continue

        if not title or not lat:
            continue

        key = f"{title}|{lat:.4f}|{lng:.4f}"
        if key in seen:
            continue
        seen.add(key)

        tipo = classify_type(cat)

        entry = f'    {{ nombre: "{title}", tipo: "{tipo}", direccion: "{addr}", lat: {lat}, lng: {lng} }},\n'
        entries.append(entry)

    return entries

def build_mock_file(all_entries):
    """Build the full mock JS file"""
    lines = []
    lines.append("/* ============================================")
    lines.append("   ARES GPS — Datos REALES pet-friendly (Apify extractor)")
    lines.append(f"   Fuente: Google Maps Scraper | Total: ~{sum(len(v) for v in all_entries.values())} lugares")
    lines.append(f"   Generado: 2026-07-31")
    lines.append("   ============================================ */")
    lines.append("")
    lines.append("window.ARES_PET_FRIENDLY_MOCK = {")

    first = True
    for city_key in [c[1] for c in CITIES]:
        entries = all_entries.get(city_key, [])
        if not entries:
            entries = ['    // No data yet\n']
        comma = "" if first else ""
        if first:
            comma = ""
        lines.append(f'  "{city_key}": [')
        for e in entries:
            lines.append(e.rstrip())
        lines.append("  ],")
        first = False

    lines.append("};")
    lines.append("")
    lines.append("window.ARES_PET_FRIENDLY_TYPE_LABEL = {")
    lines.append('  adiestrador: "Adiestrador canino",')
    lines.append('  alojamiento: "Hotel / Alojamiento",')
    lines.append('  otros: "Otros",')
    lines.append('  parque: "Parque para perros",')
    lines.append('  peluqueria: "Peluqueria canina",')
    lines.append('  playa_perros: "Playa para perros",')
    lines.append('  protectora: "Protectora de animales",')
    lines.append('  tienda: "Tienda de mascotas",')
    lines.append('  veterinario: "Veterinario",')
    lines.append("};")
    lines.append("")
    lines.append("window.ARES_PET_FRIENDLY_CITY_CENTER = {")
    centers = {
        "madrid": (40.4168, -3.7038), "barcelona": (41.3874, 2.1686),
        "valencia": (39.4699, -0.3763), "sevilla": (37.3891, -5.9845),
        "zaragoza": (41.6488, -0.8891), "malaga": (36.7213, -4.4214),
        "murcia": (37.9922, -1.1307), "palma_de_mallorca": (39.5696, 2.6502),
        "las_palmas": (28.1235, -15.4363), "bilbao": (43.2630, -2.9350),
        "alicante": (38.3452, -0.4810), "cordoba": (37.8882, -4.7794),
        "valladolid": (41.6523, -4.7245), "vigo": (42.2328, -8.7226),
        "girona": (41.9794, 2.8214), "oviedo": (43.3619, -5.8494),
        "granada": (37.1773, -3.5986), "san_sebastian": (43.3183, -1.9812),
        "santander": (43.4623, -3.8100), "pamplona": (42.8125, -1.6458),
        "salamanca": (40.9701, -5.6635), "la_coruna": (43.3623, -8.4115),
        "leon": (42.5987, -5.5671), "santiago_de_compostela": (42.8782, -8.5448),
        "cadiz": (36.5270, -6.2886), "toledo": (39.8628, -4.0273)
    }
    for c, (lat, lng) in centers.items():
        lines.append(f'  "{c}": {{ lat: {lat}, lng: {lng}, zoom: 12 }},')
    lines.append("};")
    lines.append("")

    return "\n".join(lines)

# ===== MAIN =====
queries = [f"{kw} {city}" for city in [c[0] for c in CITIES] for kw in KEYWORDS]
print(f"Total queries: {len(queries)} ({len(KEYWORDS)} kw x {len(CITIES)} cities)")
print(f"Estimated cost: ~${MAX_RESULTS * 0.004:.2f}")

rid, did = start_run(queries)
if rid:
    ok, cost = wait_run(rid)
    if ok:
        items = download_results(rid)
        print(f"\nTotal items: {len(items)}")

        # Group by city
        all_entries = {}
        for city_name, city_key in CITIES:
            entries = build_city_data(items, city_name)
            all_entries[city_key] = entries
            print(f"  {city_key}: {len(entries)} lugares")

        # Build and save mock file
        mock = build_mock_file(all_entries)
        path = os.path.join(OUTPUT_DIR, "pet-friendly-mock.js")
        with open(path, "w", encoding="utf-8") as f:
            f.write(mock)
        print(f"\nSaved: {path}")
