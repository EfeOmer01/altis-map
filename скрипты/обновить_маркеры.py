import json

markers_path = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\маркеры_миссии.json"

with open(markers_path, 'r', encoding='utf-8') as f:
    markers = json.load(f)

updated_atm = 0
updated_286 = 0
updated_dp = 0

for m in markers:
    m_name = m.get('name', '').lower()
    m_id = m.get('id', '').lower()
    m_type = m.get('type', '')
    
    # 1. ATM markers
    if 'atm_marker' in m_name or 'atm_marker' in m_id or m_name == 'atm':
        m['text'] = "Банкомат"
        m['type'] = "atm"
        m['icon'] = "/иконки/atm.png"
        updated_atm += 1
        
    # 2. Marker 286 (Spring / Fountain)
    if '286' in m_name or '286' in m_id or m_type == 'loc_Fountain':
        m['text'] = "Родник"
        m['type'] = "loc_Fountain"
        m['icon'] = "/иконки/loc_Fountain.png"
        updated_286 += 1
        
    # 3. DP markers
    if 'dp' in m_type.lower() or 'amazing_marker_dp' in m.get('icon', '').lower():
        m['icon'] = "/иконки/amazing_marker_DP.png"
        if not m.get('text') or m.get('text') == m.get('name'):
            m['text'] = "Курьер DP"
        updated_dp += 1

with open(markers_path, 'w', encoding='utf-8') as f:
    json.dump(markers, f, ensure_ascii=False, indent=2)

print(f"Updated {updated_atm} ATMs, {updated_286} Spring/Fountain markers, {updated_dp} DP markers.")
