# Định dạng draft.md

Sáu khối, mỗi khối mở bằng heading cấp 1 viết đúng như dưới (để `check_draft.py` và
`to_html.py` đọc được). H2 của trang viết bằng `##` trong `# LONG DESCRIPTION`, đúng tên và thứ
tự trong thẻ; H2 About là H2 cuối. Link dạng `[chữ neo](URL)`. Bảng dạng pipe.

```markdown
# DRAFT INFO
Outline: C · About: A2 · {Role}: an authorised Racesafe stockist and

# H1
<Product Name chính xác>

# META DESCRIPTION
<~150–160 ký tự>

# SHORT DESCRIPTION
<Intro 1–2 câu, có Differentiator, link type/category theo thẻ>

- Type: Air vest
- <Nhãn đúng File (1)>: <cụm 4–12 từ>

# LONG DESCRIPTION
## Safety Standards & Protection Level
<đoạn văn>

## Sizing & Fit
<đoạn văn>

| Size | Chest (cm) |
| --- | --- |
| S | 86-91 |

<câu chốt: free in-store fitting + advice line 01429 864112, không link>

## Riding Use Cases
<…> Always check the current rules of your governing body before competing.

## About Racesafe & discount-equestrian.co.uk
<đoạn brand: [Racesafe](brand-url) …, câu cuối gắn brand với sản phẩm>

<đoạn discount-equestrian.co.uk: chép nguyên văn từ thẻ>

# SELF-CHECK
- check_draft.py: 0 ERROR · WARN đã xét: …
- <các điểm tự kiểm máy không làm được: overlap ý, đúng focus, other features…>
```

`DRAFT INFO` và `SELF-CHECK` không vào bản HTML.
