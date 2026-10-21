# Create Content — PDP hàng loạt

Skill cho [Claude Code](https://claude.com/claude-code) giúp **sản xuất nội dung trang sản phẩm
(PDP) hàng loạt** cho discount-equestrian.co.uk theo đúng quy trình của team content (PDP
Template, File (1), File (2), First Prompt). Ngành hàng đầu tiên: **Riding Body Protector**
(body protector, back protector, air vest, phụ kiện).

Skill chuyển phần việc lặp lại sang script, để Claude chỉ làm phần cần phán đoán:

| Việc | Quy trình thủ công | Với skill |
| --- | --- | --- |
| Dán First Prompt + File (1) + File (2) vào thread | Mỗi lần mở thread mới | Skill tự nạp; mỗi sản phẩm chỉ đọc đúng 1 outline |
| Outline, tên H2, nhãn bullet, phiên bản About, {Role}, link | AI suy ra, writer soát | `product.py` tính theo luật |
| Đoạn discount-equestrian.co.uk | AI chép Appendix 2, hay lệch chữ | Dựng sẵn nguyên văn, `check_draft.py` so từng chữ |
| Sản phẩm gần giống, trùng focus, đẩy phiên bản About | Writer tự dò | `product.py` báo BLOCK/CHECK |
| Chống trùng với 9 sản phẩm liền trước | Phải ở cùng một thread | `--history` đọc draft đã lưu |
| Soát lỗi thường gặp + internal link | Writer đọc tay | `check_draft.py` tự bắt |
| Bản HTML | AI sinh lại | `to_html.py` chuyển bằng code |

```
Bạn:    Phân tích sản phẩm số 2
Claude: Thẻ: Air vest · Outline C · About A2 · {Role} "an authorised Racesafe stockist and"
        BLOCK: Product Type = 'Body Protectors' nhưng Sub type = 'Air Jackets and Air Vests' …
Bạn:    Đúng là air vest.
Claude: (lấy THÔNG TIN TỪ BRAND từ racesafe.co.uk + trang DE) → phân tích 7 mục … Cần bạn quyết: …
Bạn:    Tạo nội dung
Claude: (draft.md → check_draft.py: 0 ERROR) …
Bạn:    Tạo bản HTML
```

## Cài đặt

### Cách 1 — Plugin (khuyến nghị)

```
/plugin marketplace add phuctranj12/Create-Content-Skill-
/plugin install create-content@hawee-content
```

Gọi bằng `/create-content:pdp-content`, hoặc cứ nói việc cần làm ("phân tích sản phẩm số 5",
"làm hàng loạt STT 5–20").

### Cách 2 — Chép thẳng vào thư mục skill

```powershell
git clone https://github.com/phuctranj12/Create-Content-Skill-.git
Copy-Item -Recurse Create-Content-Skill-\skills\pdp-content $HOME\.claude\skills\   # Windows
```

```bash
cp -r Create-Content-Skill-/skills/pdp-content ~/.claude/skills/                     # macOS / Linux
```

Gọi bằng `/pdp-content`. Yêu cầu Python 3.8+ (`py -3` trên Windows), **không cần cài thư viện**.

## Dùng thế nào

1. Nói cho Claude đường dẫn File (2).
2. Một sản phẩm: `Phân tích sản phẩm số N` (kèm `THÔNG TIN TỪ BRAND: …` nếu muốn tự dán; không có
   thì Claude tự lấy từ website hãng và trang DE) → duyệt conflict → `Tạo nội dung` →
   `Tạo bản HTML`.
3. Hàng loạt: `Làm STT 5–20`. Mọi vấn đề của File (2) và mọi conflict được gom thành **một** danh
   sách để quyết một lần; draft được viết tuần tự theo STT.

Kết quả mỗi sản phẩm: `output/<ngành>/<STT>-<tên>/` gồm `card.md`, `brand-info.txt`,
`analysis.md`, `draft.md`, `draft.html` (thư mục `output/` bị gitignore).

```bash
cd skills/pdp-content/scripts
py -3 product.py --file2 "File (2).xlsx" --list                    # tổng quan, sản phẩm bị BLOCK
py -3 product.py --file2 "File (2).xlsx" --stt 4                   # thẻ một sản phẩm
py -3 product.py --file2 "File (2).xlsx" --stt 2 --type air        # khi đã xác nhận loại
py -3 check_draft.py --draft d.md --file2 "File (2).xlsx" --stt 4 --brand-info b.txt --history <output>
py -3 to_html.py d.md
```

## Cấu trúc

```
Create-Content-Skill-/
├── .claude-plugin/{plugin,marketplace}.json
├── skills/pdp-content/
│   ├── SKILL.md                         # quy trình 6 bước + hàng loạt + kỷ luật token
│   ├── categories/riding-body-protector/
│   │   ├── category.json                # cột File (2), loại→outline, H2, bullet, URL, {Role}, luật kiểm
│   │   ├── first-prompt.md              # First Prompt          ┐
│   │   ├── file1-general.md             # File (1) phần chung   │ sinh bởi import_template.py
│   │   ├── outline-A.md … outline-D.md  # File (1) từng outline │ từ PDP Template .docx
│   │   ├── about-versions.json          # Appendix 2 nguyên văn │
│   │   ├── writer-guide.md, file2-columns.md                    ┘
│   │   ├── rules.md                     # conflict phải hỏi, lưu ý File (2)
│   │   ├── analysis-template.md         # khuôn phân tích Lượt 1
│   │   └── draft-format.md              # định dạng draft.md
│   └── scripts/
│       ├── pdplib.py                    # đọc .xlsx (thư viện chuẩn) + engine luật
│       ├── product.py                   # thẻ sản phẩm
│       ├── check_draft.py               # kiểm draft
│       ├── to_html.py                   # xuất HTML
│       └── import_template.py           # PDP Template .docx → tệp tham chiếu
├── source/PDP Template - RIDING BODY PROTECTOR.docx
└── tests/                               # self-check, chỉ dùng thư viện chuẩn
```

## Cập nhật template / thêm ngành hàng

Khi team sửa PDP Template: tải lại .docx **đủ các tab** (Tệp → Tải xuống → .docx), đặt vào
`source/`, rồi:

```bash
py -3 skills/pdp-content/scripts/import_template.py "source/PDP Template - RIDING BODY PROTECTOR.docx" \
   --out skills/pdp-content/categories/riding-body-protector
py -3 tests/run_tests.py
```

Nếu tên H2, nhãn bullet, URL, danh sách brand/{Role} đổi thì sửa `category.json` cho khớp (test
báo khi tệp sinh tự động lệch với .docx). Ngành hàng mới (horse rug, riding hat…): chép thư mục
category, sửa `category.json` và `rules.md`, chạy import với `--out` thư mục mới. Không phải sửa
code.

## Kiểm thử

```bash
py -3 tests/run_tests.py
```

## Lưu ý

- `source/` và `categories/` chứa quy trình nội bộ của dự án content (prompt, đoạn About, URL).
  Nếu repo để public, cân nhắc chuyển sang private.
- Skill hỗ trợ writer, không thay bước duyệt: conflict về chuẩn an toàn luôn dừng chờ người phụ
  trách, và draft vẫn cần người đọc lại trước khi đăng.

## Giấy phép

[MIT](LICENSE)
