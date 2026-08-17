import json

with open(r'C:\Users\solde\OneDrive\Desktop\ARES\leads_pet_friendly\ares_pet_friendly_merged.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

cat_map = {
    'veterinario': 'veterinario', 'clinica veterinaria': 'veterinario',
    'parque para perros': 'parque', 'parque': 'parque',
    'tienda de productos para mascotas': 'tienda', 'tienda de mascotas': 'tienda',
    'hotel': 'alojamiento', 'hotel pet friendly': 'alojamiento',
    'peluquero de mascotas': 'peluqueria', 'peluqueria canina': 'peluqueria',
    'adiestrador canino': 'adiestrador',
    'guarderia canina': 'guarderia', 'residencia canina': 'guarderia',
    'protectora de animales': 'protectora',
    'playa para perros': 'playa_perros', 'playa': 'playa_perros',
}

city_centers = {
    'madrid': (40.4168, -3.7038, 12), 'barcelona': (41.3874, 2.1686, 12),
    'valencia': (39.4699, -0.3763, 12), 'malaga': (36.7213, -4.4214, 12),
    'bilbao': (43.2630, -2.9350, 12), 'girona': (41.9794, 2.8214, 13),
    'zaragoza': (41.6488, -0.8891, 12), 'sevilla': (37.3891, -5.9845, 12),
    'murcia': (37.9922, -1.1307, 12), 'palma_de_mallorca': (39.5696, 2.6502, 12),
    'alicante': (38.3452, -0.4810, 12), 'las_palmas': (28.1235, -15.4363, 12),
    'cordoba': (37.8882, -4.7794, 12), 'valladolid': (41.6523, -4.7245, 12),
    'vigo': (42.2328, -8.7226, 12), 'oviedo': (43.3619, -5.8494, 12),
    'santiago_de_compostela': (42.8782, -8.5448, 12),
    'santander': (43.4623, -3.8100, 12), 'pamplona': (42.8125, -1.6458, 12),
    'salamanca': (40.9701, -5.6635, 12), 'leon': (42.5987, -5.5671, 12),
    'granada': (37.1773, -3.5986, 12), 'toledo': (39.8628, -4.0273, 12),
    'la_coruna': (43.3709, -8.3959, 12), 'cadiz': (36.5270, -6.2886, 12),
    'san_sebastian': (43.3183, -1.9812, 12),
}

type_labels = {
    'veterinario': 'Veterinario', 'parque': 'Parque para perros',
    'tienda': 'Tienda de mascotas', 'alojamiento': 'Hotel / Alojamiento',
    'peluqueria': 'Peluqueria canina', 'adiestrador': 'Adiestrador canino',
    'guarderia': 'Guarderia canina', 'protectora': 'Protectora de animales',
    'playa_perros': 'Playa para perros', 'otros': 'Otros'
}

def norm_city(c):
    c = (c or '').lower().strip()
    # Strip postal codes like '08006 Barcelona' -> 'Barcelona'
    if c and c[0].isdigit():
        parts = c.split(' ', 1)
        if len(parts) > 1:
            c = parts[1]
    # Unify variants
    c = c.replace('bizkaia', 'bilbao').replace('biscay', 'bilbao').replace('vizcaya', 'bilbao')
    c = c.replace('illes balears', 'palma_de_mallorca').replace('balearic islands', 'palma_de_mallorca')
    c = c.replace('alacant', 'alicante').replace('asturias', 'oviedo')
    c = c.replace('cantabria', 'santander').replace('navarra', 'pamplona')
    c = c.replace('gipuzkoa', 'san_sebastian').replace('pontevedra', 'vigo')
    c = c.replace('la coruna', 'la_coruna').replace('llo coruna', 'la_coruna')
    c = c.replace(' ', '_')  # make JS-safe keys
    return c.strip()

# Only keep cities we explicitly scraped
TARGET_CITIES = {
    'madrid', 'barcelona', 'valencia', 'malaga', 'bilbao', 'girona',
    'zaragoza', 'sevilla', 'murcia', 'palma_de_mallorca', 'alicante',
    'las_palmas', 'cordoba', 'valladolid', 'vigo', 'oviedo',
    'santiago_de_compostela', 'santander', 'pamplona', 'salamanca',
    'leon', 'granada', 'toledo', 'la_coruna', 'cadiz', 'san_sebastian'
}

cities = {}
types_present = set()

for item in data:
    city = norm_city(item.get('city', ''))
    if city not in TARGET_CITIES:
        continue
    
    cat = (item.get('categoryName', '') or '').lower()
    tipo = 'otros'
    for k, v in cat_map.items():
        if k in cat:
            tipo = v
            break
    
    loc = item.get('location') or {}
    lat = item.get('latitude') or loc.get('lat')
    lng = item.get('longitude') or loc.get('lng')
    if not lat or not lng:
        continue
    
    # Fix encoding
    title = (item.get('title', '') or '')[:50]
    street = (item.get('street', '') or '')[:80]
    title = title.encode('latin-1', errors='replace').decode('utf-8', errors='replace')
    street = street.encode('latin-1', errors='replace').decode('utf-8', errors='replace')
    title = title.replace('"', '\\"').replace('\\', '')
    street = street.replace('"', '\\"').replace('\\', '')
    
    entry = {
        'tipo': tipo,
        'nombre': title,
        'direccion': street,
        'lat': lat,
        'lng': lng
    }
    
    if city not in cities:
        cities[city] = []
    cities[city].append(entry)
    types_present.add(tipo)

total = sum(len(v) for v in cities.values())
print(f'Cities: {len(cities)} | Total: {total} places')
for c, items in sorted(cities.items()):
    print(f'  {c}: {len(items)}')

# Generate JS
lines = []
lines.append('/* ============================================')
lines.append('   ARES GPS — Datos REALES pet-friendly (Apify extractor)')
lines.append(f'   Fuente: Google Maps Scraper x 3 runs | Total: {total} lugares')
lines.append('   Generado: 2026-07-24')
lines.append('   ============================================ */')
lines.append('')
lines.append('window.ARES_PET_FRIENDLY_MOCK = {')

for city, items in sorted(cities.items()):
    lines.append(f'  "{city}": [')
    for i, item in enumerate(items):
        comma = ',' if i < len(items) - 1 else ''
        lines.append(f'    {{ nombre: "{item["nombre"]}", tipo: "{item["tipo"]}", direccion: "{item["direccion"]}", lat: {item["lat"]}, lng: {item["lng"]} }}{comma}')
    lines.append('  ],')
lines.append('};')

lines.append('')
lines.append('window.ARES_PET_FRIENDLY_TYPE_LABEL = {')
for t in sorted(types_present):
    lines.append(f'  {t}: "{type_labels.get(t, t)}",')
lines.append('};')

lines.append('')
lines.append('window.ARES_PET_FRIENDLY_CITY_CENTER = {')
for city_key, items in sorted(cities.items()):
    if city_key in city_centers:
        lat, lng, zoom = city_centers[city_key]
    else:
        lats = [i['lat'] for i in items]
        lngs = [i['lng'] for i in items]
        lat = sum(lats) / len(lats)
        lng = sum(lngs) / len(lngs)
        zoom = 12
    lines.append(f'  "{city_key}": {{ lat: {lat:.4f}, lng: {lng:.4f}, zoom: {zoom} }},')
lines.append('};')

out_path = r'C:\Users\solde\OneDrive\Desktop\ARES\GPS\landing\contenido\assets\js\pet-friendly-mock.js'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print(f'\nSaved: {out_path}')
print(f'File: {len(lines)} lines')
