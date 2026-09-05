"""Dual Apify scrape - refill cities with lowest data counts"""
import json, urllib.request, time, os, threading

ACTOR = "scrapesage~google-maps-scraper"
API = "https://api.apify.com/v2"
KEYWORDS = [
    "veterinario", "parque para perros", "tienda de mascotas",
    "hotel pet friendly", "peluqueria canina", "adiestrador canino",
    "playa para perros", "guarderia canina", "protectora de animales",
    "residencia canina", "paseador de perros"
]


def required_token(name):
    value = os.environ.get(name, "")
    if not value:
        raise RuntimeError(f"Set {name} before running the Apify scraper")
    return value

# Token 1 ($5) -> cities < 100
T1 = {
    "token": required_token("APIFY_API_TOKEN_SMALL"),
    "cities": ["Pamplona", "Santiago de Compostela", "Santander",
               "San Sebastian", "Salamanca", "Cadiz"],
    "name": "T1-SMALL"
}

# Token 2 ($5) -> cities 100-150
T2 = {
    "token": required_token("APIFY_API_TOKEN_MEDIUM"),
    "cities": ["Toledo", "Leon", "Vigo", "Granada",
               "A Coruna", "Cordoba", "Valladolid"],
    "name": "T2-MEDIUM"
}

def run_scrape(cfg):
    token = cfg["token"]
    name = cfg["name"]
    cities = cfg["cities"]
    queries = [f"{kw} {c}" for c in cities for kw in KEYWORDS]
    print(f"[{name}] {len(cities)} cities x {len(KEYWORDS)} kw = {len(queries)} queries")

    payload = {
        "searchQueries": queries, "maxResults": 1500,
        "maxPlacesPerSearch": 50, "language": "es", "countryCode": "es",
        "skipClosedPlaces": True, "enrichContacts": False,
        "scrapePlaceDetails": False, "sortBy": "rating",
    }
    url = f"{API}/acts/{ACTOR}/runs?token={token}"
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                  headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode())
    rid = result["data"]["id"]
    print(f"[{name}] STARTED Run={rid} | Cost ~$6")

    # Wait
    url2 = f"{API}/acts/{ACTOR}/runs/{rid}?token={token}"
    start = time.time()
    while time.time() - start < 900:
        time.sleep(15)
        with urllib.request.urlopen(url2, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        st = data["data"]["status"]
        cost = data["data"].get("usageTotalUsd", 0)
        print(f"[{name}] {st} | ${cost:.4f} | {int(time.time()-start)}s", flush=True)
        if st == "SUCCEEDED":
            # Download
            durl = f"{API}/acts/{ACTOR}/runs/{rid}/dataset/items?token={token}&format=json&clean=true"
            items = []; off = 0
            while True:
                p = f"{durl}&offset={off}&limit=1000"
                with urllib.request.urlopen(p, timeout=120) as resp:
                    batch = json.loads(resp.read().decode())
                if not batch: break
                items.extend(batch); off += 1000
                print(f"[{name}] DL {len(items)} items...", flush=True)
            path = os.path.join(OUT, f"{name}_results.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(items, f, ensure_ascii=False)
            print(f"[{name}] SAVED {len(items)} items | ${cost:.4f}", flush=True)
            return {"name": name, "count": len(items), "cost": cost, "run": rid}
        elif st in ("FAILED", "ABORTED", "TIMED-OUT"):
            print(f"[{name}] {st}", flush=True)
            return None
    return None

OUT = r"C:\Users\solde\OneDrive\Desktop\ARES\GPS\landing"

# Run in parallel using threads
results = []
def runner(cfg):
    r = run_scrape(cfg)
    results.append(r)

t1 = threading.Thread(target=runner, args=(T1,))
t2 = threading.Thread(target=runner, args=(T2,))
t1.start(); t2.start()
t1.join(); t2.join()

print("\n=== RESUMEN ===")
for r in results:
    if r:
        print(f"  {r['name']}: {r['count']} items | ${r['cost']:.4f} | Run={r['run']}")
    else:
        print(f"  {'UNKNOWN'}: FAILED")
