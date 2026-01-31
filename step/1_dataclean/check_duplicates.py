import json
import os

files = {
    'luatdedieu.json': 'data/input/luatdedieu.json',
    'luatkhituongthuyvan.json': 'data/input/luatkhituongthuyvan.json',
    'luatphongchongthientai.json': 'data/input/luatphongchongthientai.json',
    'luatthuyloi.json': 'data/input/luatthuyloi.json'
}

print('=' * 80)
print('PHÂN TÍCH ID TRÙNG LẶP')
print('=' * 80)

# Load all data
all_data = {}
for name, path in files.items():
    with open(path, 'r', encoding='utf-8') as f:
        all_data[name] = json.load(f)

# Find duplicates
from collections import defaultdict
id_to_files = defaultdict(list)

for fname, data in all_data.items():
    for record in data:
        id_to_files[record['id']].append(fname)

# Filter duplicates
duplicates = {id: files for id, files in id_to_files.items() if len(files) > 1}

print(f'\nTổng số IDs trùng lặp: {len(duplicates)}')
print(f'\nCác ID bị trùng và file chứa chúng:\n')

for id, file_list in sorted(duplicates.items()):
    print(f'{id}:')
    for fname in file_list:
        # Find the record
        for record in all_data[fname]:
            if record['id'] == id:
                print(f'  - {fname}')
                print(f'    doc_name: {record["metadata"]["doc_name"]}')
                print(f'    content preview: {record["content_for_embedding"][:100]}...')
                break

print('\n' + '=' * 80)
print('NGUYÊN NHÂN')
print('=' * 80)
print('''
Có vẻ như có 2 file đang sử dụng cùng doc_id "VBHN_05_2020":
- luatkhituongthuyvan.json (Luật Khí tượng thủy văn)
- luatthuyloi.json (Luật Thủy lợi)

Điều này dẫn đến việc IDs bị trùng lặp vì IDs được tạo dựa trên:
doc_id + chapter_no + article_no

Giải pháp:
1. Cần phân biệt doc_id giữa 2 luật này
2. Hoặc thêm prefix/suffix để phân biệt
3. Hoặc sử dụng tên luật viết tắt vào ID
''')
