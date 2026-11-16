import re

raw = open('../данные/uploaded_mission.cpp', 'rb').read()
tm = re.findall(rb'text="([^"]+)";', raw)
print('Found texts count:', len(tm))
print('First 10 as utf-8:')
for t in tm[:10]:
    try:
        print(' ', t.decode('utf-8'))
    except Exception as e:
        print('  ERR utf-8:', e)

print('First 10 as cp1251:')
for t in tm[:10]:
    try:
        print(' ', t.decode('cp1251'))
    except Exception as e:
        print('  ERR cp1251:', e)
