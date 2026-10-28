# Định dạng draft.md — Riding Hat (engine generic)

Mỗi khối mở bằng heading cấp 1 viết đúng như dưới. H2 viết `##`, nhóm nhỏ `###`, ý dài là đoạn mở
bằng nhãn in đậm `**Nhãn:**`; Safety standards & certification và Specifications là bullet.
Link dạng `[chữ neo](URL)`.

```markdown
# DRAFT INFO
Template: Riding Hat · DE variant: F (quy tắc số 2) · No. 2

# H1
Charles Owen YR8 Riding Hat

# META TITLE
Charles Owen YR8 Riding Hat | Discount Equestrian

# META DESCRIPTION
<140–155 ký tự>

# SHORT DESCRIPTION
<Câu mở đầu theo frame của template, link "riding hat">

- **Type:** <spec>, <benefit>
- **Protection:** <spec>, <benefit>

<Navigation bridge>

# LONG DESCRIPTION
## Safety standards & construction
### Safety standards & certification
- **PAS 015: 2011:** <giải thích theo B1>

## Sizing & fit
**Size:** <câu Size gợi ý trên thẻ>, all of them [children's sizes](...).

## Design details
**Colour:** Black, Black - Charcoal and Navy.

## Care & maintenance
**Post-impact replacement & lifespan:** <1 câu>

## About the brand
<brand paragraph 40–60 từ, [Brand](brand-url) ở lần nhắc đầu>

<đoạn discount-equestrian.co.uk: chép nguyên văn từ thẻ, đã có link trang chủ>

# SELF-CHECK
- check_draft.py: 0 ERROR · WARN đã xét: …
- Checklist (checklist.md): đã rà từng mục; điểm cần người duyệt: …
```

`DRAFT INFO` và `SELF-CHECK` không vào HTML. `to_html.py --submit` ghi `ban-text.html` (tab Text:
H1, Meta title, Meta Description, nội dung) và `ban-html.txt` (tab HTML: hai dòng meta dạng text,
rồi 3 khối code H1 / Short / Long).
