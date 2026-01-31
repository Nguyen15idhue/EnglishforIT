import json
import os

files = [
    'f:/3.Laptrinh/EnglishforIT/data/input/luatdedieu.json',
    'f:/3.Laptrinh/EnglishforIT/data/input/luatkhituongthuyvan.json',
    'f:/3.Laptrinh/EnglishforIT/data/input/luatphongchongthientai.json',
    'f:/3.Laptrinh/EnglishforIT/data/input/luatthuyloi.json'
]

print('=' * 60)
print('PHÂN TÍCH CHI TIẾT CẤU TRÚC VÀ CHẤT LƯỢNG DỮ LIỆU')
print('=' * 60)

all_structures = []
all_issues = []

for fpath in files:
    print(f'\n{"=" * 60}')
    print(f'{os.path.basename(fpath)}')
    print('=' * 60)
    
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f'Tổng số records: {len(data)}')
    
    # Kiểm tra cấu trúc
    if data:
        keys = set(data[0].keys())
        print(f'Các field chính: {sorted(keys)}')
        
        metadata_keys = set(data[0]['metadata'].keys())
        print(f'Các field metadata: {sorted(metadata_keys)}')
        all_structures.append({'file': os.path.basename(fpath), 'keys': keys, 'metadata_keys': metadata_keys})
    
    # Kiểm tra giá trị type
    types = set(r['metadata']['type'] for r in data)
    print(f'Giá trị type: {types}')
    
    # Kiểm tra ID patterns
    id_prefixes = set(r['id'].split('_')[0] for r in data)
    print(f'ID prefixes: {id_prefixes}')
    
    # Kiểm tra doc_id values
    doc_ids = set(r['metadata']['doc_id'] for r in data)
    print(f'doc_id values: {doc_ids}')
    
    # Kiểm tra newline, tab trong content
    newlines = sum(1 for r in data if '\n' in r['content_for_embedding'])
    tabs = sum(1 for r in data if '\t' in r['content_for_embedding'])
    print(f'Records có newline: {newlines}')
    print(f'Records có tab: {tabs}')
    
    # Kiểm tra khoảng trắng thừa
    leading_spaces = sum(1 for r in data if r['content_for_embedding'].startswith(' '))
    trailing_spaces = sum(1 for r in data if r['content_for_embedding'].endswith(' '))
    double_spaces = sum(1 for r in data if '  ' in r['content_for_embedding'])
    print(f'Records có khoảng trắng đầu: {leading_spaces}')
    print(f'Records có khoảng trắng cuối: {trailing_spaces}')
    print(f'Records có khoảng trắng kép: {double_spaces}')
    
    # Độ dài content
    lengths = [len(r['content_for_embedding']) for r in data]
    print(f'Độ dài content - Min: {min(lengths)}, Max: {max(lengths)}, Avg: {sum(lengths)/len(lengths):.0f}')
    
    # Kiểm tra ID trùng
    ids = [r['id'] for r in data]
    unique_ids = set(ids)
    if len(ids) != len(unique_ids):
        print(f'⚠️ CẢNH BÁO: Có ID trùng lặp!')
        all_issues.append(f'{os.path.basename(fpath)}: ID trùng lặp')
    
    # Kiểm tra field rỗng
    for i, r in enumerate(data):
        if not r.get('id'):
            all_issues.append(f'{os.path.basename(fpath)}: Record {i} thiếu id')
        if not r.get('content_for_embedding'):
            all_issues.append(f'{os.path.basename(fpath)}: Record {i} thiếu content')
        if not r.get('citation'):
            all_issues.append(f'{os.path.basename(fpath)}: Record {i} thiếu citation')
        if not r.get('metadata'):
            all_issues.append(f'{os.path.basename(fpath)}: Record {i} thiếu metadata')

print(f'\n{"=" * 60}')
print('SO SÁNH CẤU TRÚC GIỮA CÁC FILE')
print('=' * 60)

# So sánh cấu trúc
if len(all_structures) > 0:
    ref_keys = all_structures[0]['keys']
    ref_metadata_keys = all_structures[0]['metadata_keys']
    
    structure_consistent = True
    for s in all_structures:
        if s['keys'] != ref_keys:
            print(f"⚠️ {s['file']}: Cấu trúc field chính khác biệt")
            print(f"   Thiếu: {ref_keys - s['keys']}")
            print(f"   Thừa: {s['keys'] - ref_keys}")
            structure_consistent = False
            all_issues.append(f"{s['file']}: Cấu trúc field chính không nhất quán")
        
        if s['metadata_keys'] != ref_metadata_keys:
            print(f"⚠️ {s['file']}: Cấu trúc metadata khác biệt")
            print(f"   Thiếu: {ref_metadata_keys - s['metadata_keys']}")
            print(f"   Thừa: {s['metadata_keys'] - ref_metadata_keys}")
            structure_consistent = False
            all_issues.append(f"{s['file']}: Cấu trúc metadata không nhất quán")
    
    if structure_consistent:
        print('✓ Tất cả các file có cấu trúc giống nhau')
        print(f'  Fields chính: {sorted(ref_keys)}')
        print(f'  Fields metadata: {sorted(ref_metadata_keys)}')

print(f'\n{"=" * 60}')
print('ĐÁNH GIÁ ĐỘ SẠCH DỮ LIỆU CHO FAISS')
print('=' * 60)

if len(all_issues) == 0:
    print('✓ KHÔNG CÓ VẤN ĐỀ NGHIÊM TRỌNG')
    print('\nĐánh giá:')
    print('1. Cấu trúc: ✓ Nhất quán giữa các file')
    print('2. Tính toàn vẹn: ✓ Không có field rỗng hoặc thiếu')
    print('3. ID duy nhất: ✓ Không có trùng lặp')
    print('4. Sẵn sàng cho vectorization: ✓ CÓ THỂ')
    print('\nLưu ý nhỏ:')
    print('- Có thể cần normalize khoảng trắng (leading/trailing/double spaces)')
    print('- Nên xem xét xử lý newline nếu muốn content trên 1 dòng')
else:
    print('⚠️ PHÁT HIỆN CÁC VẤN ĐỀ:')
    for issue in all_issues:
        print(f'  - {issue}')
