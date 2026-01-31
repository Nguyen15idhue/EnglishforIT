import json
import os

print('=' * 80)
print('FIXING DUPLICATE IDs')
print('=' * 80)

# File paths
files = {
    'luatdedieu.json': 'data/input/luatdedieu.json',
    'luatkhituongthuyvan.json': 'data/input/luatkhituongthuyvan.json',
    'luatphongchongthientai.json': 'data/input/luatphongchongthientai.json',
    'luatthuyloi.json': 'data/input/luatthuyloi.json'
}

# Load luatkhituongthuyvan.json - file cần sửa
print('\n1. Đang sửa file luatkhituongthuyvan.json...')
with open(files['luatkhituongthuyvan.json'], 'r', encoding='utf-8') as f:
    data_kthtv = json.load(f)

print(f'   Số records: {len(data_kthtv)}')

# Fix doc_id và doc_name
old_doc_id = "VBHN_05_2020"
new_doc_id = "VBHN_06_2020"
old_doc_name = "Luật Thủy lợi"
new_doc_name = "Luật Khí tượng thủy văn"

fixed_count = 0
doc_name_fixed = 0

for record in data_kthtv:
    # Fix ID
    if record['id'].startswith(old_doc_id):
        old_id = record['id']
        record['id'] = record['id'].replace(old_doc_id, new_doc_id, 1)
        fixed_count += 1
    
    # Fix doc_id in metadata
    if record['metadata']['doc_id'] == old_doc_id:
        record['metadata']['doc_id'] = new_doc_id
    
    # Fix doc_name in metadata
    if record['metadata']['doc_name'] == old_doc_name:
        record['metadata']['doc_name'] = new_doc_name
        doc_name_fixed += 1

print(f'   ✓ Đã sửa {fixed_count} IDs')
print(f'   ✓ Đã sửa {doc_name_fixed} doc_names')

# Backup original file
backup_path = files['luatkhituongthuyvan.json'] + '.backup'
print(f'\n2. Đang tạo backup: {backup_path}')
with open(files['luatkhituongthuyvan.json'], 'r', encoding='utf-8') as f:
    original_content = f.read()
with open(backup_path, 'w', encoding='utf-8') as f:
    f.write(original_content)
print('   ✓ Backup hoàn tất')

# Save fixed file
print(f'\n3. Đang lưu file đã sửa...')
with open(files['luatkhituongthuyvan.json'], 'w', encoding='utf-8') as f:
    json.dump(data_kthtv, f, ensure_ascii=False, indent=2)
print('   ✓ Đã lưu file')

# Verify - check for duplicates across all files
print(f'\n4. Kiểm tra lại toàn bộ dữ liệu...')
all_ids = []
for fname, fpath in files.items():
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    file_ids = [r['id'] for r in data]
    all_ids.extend(file_ids)
    print(f'   {fname}: {len(file_ids)} records')

unique_ids = set(all_ids)
print(f'\n   Tổng IDs: {len(all_ids)}')
print(f'   IDs duy nhất: {len(unique_ids)}')

if len(all_ids) == len(unique_ids):
    print('   ✓ KHÔNG CÒN ID TRÙNG LẶP!')
else:
    print(f'   ⚠️ VẪN CÒN {len(all_ids) - len(unique_ids)} ID TRÙNG LẶP')
    from collections import Counter
    id_counts = Counter(all_ids)
    duplicates = [id for id, count in id_counts.items() if count > 1]
    print(f'   IDs trùng: {duplicates[:10]}')

print('\n' + '=' * 80)
print('HOÀN TẤT!')
print('=' * 80)
