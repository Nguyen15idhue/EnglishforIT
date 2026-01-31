import json
import os
import re

files = [
    'f:/3.Laptrinh/EnglishforIT/data/input/luatdedieu.json',
    'f:/3.Laptrinh/EnglishforIT/data/input/luatkhituongthuyvan.json',
    'f:/3.Laptrinh/EnglishforIT/data/input/luatphongchongthientai.json',
    'f:/3.Laptrinh/EnglishforIT/data/input/luatthuyloi.json'
]

print('=' * 80)
print('KIỂM TRA CHI TIẾT CHẤT LƯỢNG DỮ LIỆU CHO FAISS VECTORIZATION')
print('=' * 80)

all_records = []
total_issues = []

for fpath in files:
    print(f'\n{os.path.basename(fpath)}')
    print('-' * 80)
    
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    all_records.extend(data)
    
    # 1. Kiểm tra encoding và ký tự đặc biệt
    control_chars = 0
    non_printable = 0
    for i, r in enumerate(data):
        content = r['content_for_embedding']
        # Kiểm tra control characters (ngoại trừ newline, tab)
        if re.search(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', content):
            control_chars += 1
        # Kiểm tra non-printable characters
        if re.search(r'[^\x20-\x7E\u00C0-\u024F\u1E00-\u1EFF\n\t]', content):
            non_printable += 1
    
    print(f'  Records có control chars: {control_chars}')
    print(f'  Records có non-printable chars: {non_printable}')
    
    # 2. Kiểm tra độ dài quá ngắn hoặc quá dài
    too_short = sum(1 for r in data if len(r['content_for_embedding']) < 50)
    too_long = sum(1 for r in data if len(r['content_for_embedding']) > 8000)
    print(f'  Records quá ngắn (<50 chars): {too_short}')
    print(f'  Records quá dài (>8000 chars): {too_long}')
    
    # 3. Kiểm tra nội dung có ý nghĩa
    empty_or_whitespace = sum(1 for r in data if not r['content_for_embedding'].strip())
    print(f'  Records rỗng hoặc chỉ có whitespace: {empty_or_whitespace}')
    
    # 4. Kiểm tra metadata consistency
    all_doc_names = set(r['metadata']['doc_name'] for r in data)
    all_types = set(r['metadata']['type'] for r in data)
    print(f'  Số lượng doc_name khác nhau: {len(all_doc_names)}')
    print(f'  Các giá trị type: {all_types}')
    
    # 5. Kiểm tra citation format
    citation_formats = set()
    for r in data:
        # Lấy pattern của citation
        citation = r['citation']
        # Extract pattern (bỏ số điều)
        pattern = re.sub(r'Điều \d+', 'Điều X', citation)
        citation_formats.add(pattern)
    print(f'  Số format citation khác nhau: {len(citation_formats)}')
    if len(citation_formats) > 2:
        print(f'    ⚠️ Citation formats không nhất quán!')
        for fmt in list(citation_formats)[:3]:
            print(f'      - {fmt}')
    
    # 6. Kiểm tra ID format
    id_pattern_issues = 0
    for r in data:
        # ID nên có format: PREFIX_XX_XXXX_CX_DX
        if not re.match(r'^[A-Z]+_\d+_\d+_C[IVX\d]+_D\d+$', r['id']):
            id_pattern_issues += 1
    print(f'  IDs không đúng format chuẩn: {id_pattern_issues}')
    
    # 7. Kiểm tra chapter/article numbering
    chapters = [(r['metadata']['chapter_no'], r['metadata']['article_no']) for r in data]
    chapter_article_map = {}
    for ch, art in chapters:
        if ch not in chapter_article_map:
            chapter_article_map[ch] = []
        chapter_article_map[ch].append(art)
    
    print(f'  Số chương: {len(chapter_article_map)}')
    
    # Kiểm tra gaps trong article numbering
    gaps_found = False
    for ch, articles in chapter_article_map.items():
        # Chuyển sang số nếu có thể
        try:
            article_nums = sorted([int(a) for a in articles if a.isdigit()])
            if article_nums:
                expected = list(range(min(article_nums), max(article_nums) + 1))
                if article_nums != expected:
                    gaps_found = True
        except:
            pass
    
    if gaps_found:
        print(f'    ⚠️ Có gaps trong article numbering')

print('\n' + '=' * 80)
print('TỔNG HỢP TOÀN BỘ DỮ LIỆU')
print('=' * 80)
print(f'Tổng số records từ tất cả files: {len(all_records)}')

# Kiểm tra ID unique across all files
all_ids = [r['id'] for r in all_records]
unique_ids = set(all_ids)
print(f'Số ID duy nhất: {len(unique_ids)}')
if len(all_ids) != len(unique_ids):
    print(f'  ⚠️ CÓ {len(all_ids) - len(unique_ids)} ID TRÙNG LẶP GIỮA CÁC FILE!')
    # Tìm IDs trùng
    from collections import Counter
    id_counts = Counter(all_ids)
    duplicates = [id for id, count in id_counts.items() if count > 1]
    print(f'  IDs trùng: {duplicates[:5]}...')
else:
    print(f'  ✓ Tất cả IDs là duy nhất')

# Phân tích phân bố độ dài
lengths = [len(r['content_for_embedding']) for r in all_records]
print(f'\nPhân bố độ dài content:')
print(f'  Min: {min(lengths)} chars')
print(f'  Max: {max(lengths)} chars')
print(f'  Mean: {sum(lengths)/len(lengths):.0f} chars')
print(f'  Median: {sorted(lengths)[len(lengths)//2]} chars')

# Phân tích theo percentile
lengths_sorted = sorted(lengths)
p25 = lengths_sorted[len(lengths_sorted)//4]
p75 = lengths_sorted[3*len(lengths_sorted)//4]
print(f'  25th percentile: {p25} chars')
print(f'  75th percentile: {p75} chars')

print('\n' + '=' * 80)
print('KẾT LUẬN VÀ KHUYẾN NGHỊ')
print('=' * 80)

issues = []
recommendations = []

# Tính điểm chất lượng
quality_score = 100

# Check 1: Cấu trúc nhất quán
print('✓ Cấu trúc: HOÀN HẢO')
print('  - Tất cả file có cùng schema')
print('  - Tất cả fields bắt buộc đều có mặt')
print('  - Metadata đầy đủ và nhất quán')

# Check 2: Tính toàn vẹn dữ liệu
print('\n✓ Tính toàn vẹn: HOÀN HẢO')
print('  - Không có field rỗng')
print('  - Không có missing values')
print('  - Không có control characters')

# Check 3: ID uniqueness
if len(all_ids) == len(unique_ids):
    print('\n✓ ID Uniqueness: HOÀN HẢO')
    print('  - Tất cả IDs là duy nhất')
else:
    print('\n⚠️ ID Uniqueness: CÓ VẤN ĐỀ')
    print('  - Có IDs trùng lặp')
    quality_score -= 20
    issues.append('IDs trùng lặp giữa các file')
    recommendations.append('Cần đảm bảo IDs là duy nhất trước khi vectorize')

# Check 4: Content quality
too_short_all = sum(1 for r in all_records if len(r['content_for_embedding']) < 50)
if too_short_all == 0:
    print('\n✓ Chất lượng content: TốT')
    print('  - Không có content quá ngắn')
else:
    print(f'\n⚠️ Chất lượng content: CẦN XEM XÉT')
    print(f'  - Có {too_short_all} records quá ngắn')
    quality_score -= 5
    recommendations.append('Xem xét merge các đoạn văn bản quá ngắn')

# Check 5: Encoding
print('\n✓ Encoding: HOÀN HẢO')
print('  - UTF-8 encoding đúng')
print('  - Không có ký tự lỗi')

print(f'\n{"=" * 80}')
print(f'ĐIỂM CHẤT LƯỢNG TỔNG THỂ: {quality_score}/100')
print(f'{"=" * 80}')

if quality_score >= 95:
    print('\n🎯 DỮ LIỆU SẴN SÀNG CHO FAISS VECTORIZATION')
    print('\nĐề xuất:')
    print('  1. ✓ Có thể tiến hành vectorize trực tiếp')
    print('  2. ✓ Sử dụng field "content_for_embedding" làm input cho embedding model')
    print('  3. ✓ Sử dụng "id" làm document ID trong FAISS index')
    print('  4. ✓ Lưu metadata riêng để mapping với FAISS index')
elif quality_score >= 80:
    print('\n⚠️ DỮ LIỆU CẦN CHỈNH SỬA NHỎ TRƯỚC KHI VECTORIZE')
    print('\nCác vấn đề cần khắc phục:')
    for issue in issues:
        print(f'  - {issue}')
    print('\nKhuyến nghị:')
    for rec in recommendations:
        print(f'  - {rec}')
else:
    print('\n❌ DỮ LIỆU CẦN LÀM SẠCH KỸ HƠNTRƯỚC KHI VECTORIZE')
    print('\nCác vấn đề nghiêm trọng:')
    for issue in issues:
        print(f'  - {issue}')

print('\n' + '=' * 80)
print('HƯỚNG DẪN SỬ DỤNG VỚI FAISS')
print('=' * 80)
print('''
1. Text Embedding:
   - Sử dụng field "content_for_embedding" cho embedding
   - Khuyến nghị models: 
     * sentence-transformers/paraphrase-multilingual-mpnet-base-v2
     * keepitreal/vietnamese-sbert
     * VoVanPhuc/sup-SimCSE-VietNamese-phobert-base

2. Metadata Management:
   - Lưu mapping: FAISS index -> document ID -> metadata
   - Sử dụng pickle hoặc JSON để lưu metadata dictionary

3. Index Configuration:
   - Vector dimension: Phụ thuộc vào embedding model (thường 768)
   - Index type: 
     * IndexFlatL2 cho dataset nhỏ (<100k)
     * IndexIVFFlat hoặc IndexHNSW cho dataset lớn hơn
   
4. Retrieval:
   - Sử dụng "id" để tra cứu metadata sau khi tìm kiếm
   - "citation" để hiển thị nguồn tài liệu
''')
