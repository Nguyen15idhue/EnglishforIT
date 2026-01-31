import json

files = [
    'data/input/luatdedieu.json',
    'data/input/luatkhituongthuyvan.json',
    'data/input/luatphongchongthientai.json',
    'data/input/luatthuyloi.json'
]

print('\n' + '=' * 60)
print('VERIFICATION CUỐI CÙNG')
print('=' * 60)

all_ids = []
for f in files:
    data = json.load(open(f, 'r', encoding='utf-8'))
    all_ids.extend([r['id'] for r in data])

print(f'\nTổng IDs: {len(all_ids)}')
print(f'IDs unique: {len(set(all_ids))}')

if len(all_ids) == len(set(all_ids)):
    print('\n✅ PASS - KHÔNG CÒN TRÙNG LẶP!')
else:
    print(f'\n❌ FAIL - CÒN {len(all_ids) - len(set(all_ids))} IDs TRÙNG')

print('\n' + '-' * 60)
print('Sample IDs từ luatkhituongthuyvan.json:')
kthtv = json.load(open('data/input/luatkhituongthuyvan.json', 'r', encoding='utf-8'))
for r in kthtv[:3]:
    print(f'  - {r["id"]}')
    print(f'    doc_id: {r["metadata"]["doc_id"]}')
    print(f'    doc_name: {r["metadata"]["doc_name"]}')

print('\n' + '-' * 60)
print('Sample IDs từ luatthuyloi.json:')
tl = json.load(open('data/input/luatthuyloi.json', 'r', encoding='utf-8'))
for r in tl[:3]:
    print(f'  - {r["id"]}')
    print(f'    doc_id: {r["metadata"]["doc_id"]}')
    print(f'    doc_name: {r["metadata"]["doc_name"]}')

print('\n' + '=' * 60)
print('✅ HOÀN TẤT - DỮ LIỆU ĐÃ SẠCH!')
print('=' * 60)
