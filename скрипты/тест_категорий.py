import json

in_path = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\маркеры_миссии.json"
with open(in_path, "r", encoding="utf-8") as f:
    markers = json.load(f)

def categorize(m):
    t = m.get('type', '').lower()
    name = m.get('name', '').lower()
    text = m.get('text', '').lower()

    # 1. DP
    if 'dp' in t or name.startswith('dp') or 'dp' in text:
        return 'dp'

    # 2. Нелегальные точки
    if ('illegal' in t or 'illegal' in name or 'cocaine' in t or 'heroine' in t or 
        'canabis' in t or 'weed' in t or 'gera' in t or 'narko' in t or 'drug' in t or 
        'uran' in t or 'perebivka' in t or 'moneylaundering' in t or 'slaver' in t):
        return 'illegal'

    # 3. Базы и особняки
    if t.startswith('amazing_group_') or 'rebelcamp' in t or 'rentbase' in t or 'база' in text or 'особняк' in text or 'мафия' in text:
        return 'bases'

    # 4. Недвижимость
    if 'garage' in t or 'garage' in name or 'гараж' in text or 'недвиж' in text:
        return 'realestate'

    # 5. Территории
    if t in ['ellipse', 'rectangle'] or 'zone' in name or 'зона' in text or 'территори' in text:
        return 'territories'

    # 6. Ресурсы
    if any(k in t for k in [
        'oil', 'salt', 'sand', 'water', 'beans', 'minerals', 'jasperquartz', 
        'gornorudka', 'fish', 'meteorite', 'wastes', 'huntarea'
    ]) and not any(k in t for k in ['factory', 'sell', 'store']):
        return 'resources'

    # 7. Маршруты добычи (Переработка и сбыт)
    if any(k in t for k in [
        'factory', 'sell', 'license', 'delivery', 'storage', 'depot'
    ]):
        return 'routes'

    # 8. Магазины
    if any(k in t for k in [
        'car', 'truck', 'richcar', 'conceptcar', 'motorcycle', 'gunstore', 
        'clothes', 'grocery', 'univermag', 'marketplace', 'pharmacy', 
        'garden_shop', 'beautysaloon', 'piercing', 'mask', 'drivingschool'
    ]):
        return 'shops'

    # 9. Инфраструктура
    if any(k in t for k in [
        'atm', 'loc_fountain', 'bank', 'hospital', 'policestation', 'jail', 
        'gasstation', 'parkingfine', 'pochtomat', 'government', 'harbor', 
        'boat', 'airplane', 'helicopter', 'bridge', 'checkpoing'
    ]) or 'atm' in name or 'банкомат' in text or 'родник' in text:
        return 'infra'

    # 10. Прочее
    return 'other'

counts = {}
for m in markers:
    cat = categorize(m)
    m['category'] = cat
    counts[cat] = counts.get(cat, 0) + 1

print("Marker category distribution:")
for cat, cnt in sorted(counts.items()):
    print(f"  {cat}: {cnt}")
