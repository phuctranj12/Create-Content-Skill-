---
name: pdp-content
description: Sản xuất nội dung trang sản phẩm (PDP) hàng loạt cho discount-equestrian.co.uk theo quy trình của team content (Template/File (1), File (2) .xlsx, First prompt, checklist), cho mọi ngành hàng có "category pack" trong skill. Hiện có Riding Body Protector (body/back protector, air vest, phụ kiện) và Riding Hat (Riding Hat, Hat Silks & Covers, Liners & Parts, Helmet Accessories). Script đọc File (2), tính sẵn template, H2, nhãn bullet, đoạn discount-equestrian.co.uk nguyên văn, link, màu và câu size theo size DE bán; Claude đối chiếu THÔNG TIN TỪ BRAND, báo conflict, viết bài; script tự kiểm draft (H2, bullet, màu, size, link, đoạn About, chuẩn an toàn, trùng lặp) và xuất bản nộp Text + HTML. Dùng khi người dùng nói "Đối chiếu dữ liệu sản phẩm số …", "Phân tích sản phẩm số …", "Viết bài", "Tạo nội dung", "Tạo bản HTML", "viết PDP STT/No. …", "làm hàng loạt 5-20", hoặc đưa File (2) / THÔNG TIN TỪ BRAND / ảnh comment review của một bài PDP.
license: MIT
compatibility: Cần Python 3.8+ (py -3 trên Windows, python3 trên macOS/Linux), chỉ dùng thư viện chuẩn. WebFetch/WebSearch chỉ dùng khi First prompt của category cho phép; không thì người dùng dán THÔNG TIN TỪ BRAND.
allowed-tools: Read, Write, Edit, Glob, Grep, WebFetch, WebSearch, Bash(py -3 ${CLAUDE_SKILL_DIR}/scripts/product.py:*), Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/product.py:*), Bash(py -3 ${CLAUDE_SKILL_DIR}/scripts/check_draft.py:*), Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/check_draft.py:*), Bash(py -3 ${CLAUDE_SKILL_DIR}/scripts/to_html.py:*), Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/to_html.py:*), Bash(py -3 ${CLAUDE_SKILL_DIR}/scripts/import_template.py:*), Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/import_template.py:*)
metadata:
  categories: riding-body-protector, riding-hat
  site: discount-equestrian.co.uk
---

# Nội dung PDP hàng loạt

**Phân vai.** Claude là writer, làm đúng First prompt của ngành hàng. Mọi thứ có luật cố định
(template, tên H2, nhãn bullet, đoạn discount-equestrian.co.uk, link, màu/size DE bán, các lỗi kiểm
được bằng máy) do script làm: **lấy từ thẻ, không suy luận lại, không đọc thẳng File (2)**. Claude
chỉ làm phần cần phán đoán: đọc THÔNG TIN TỪ BRAND, xử lý conflict, viết, rà checklist.

**Bốn điều cốt lõi (mọi ngành)** — chi tiết ở `common/universal-rules.md`:

1. **Chỉ viết điều brand nói.** Thiếu thì bỏ ý / bỏ H2; chỉ suy ra *lợi ích*, không suy ra *thông tin*.
2. **Màu, size, size trẻ em, range: theo File (2)**, không theo brand. Màu liệt kê đủ, không
   "Choose from"; size chỉ size DE bán, không dải ngụ ý size không bán (dùng "câu Size gợi ý").
3. **Chuẩn an toàn / thi đấu không tự quyết**: lệch, thiếu năm, thiếu quality mark → dừng, hỏi.
4. **Sau mỗi draft: `check_draft.py` 0 ERROR rồi rà checklist từng dòng.**

## Chọn ngành hàng (category pack)

`${CLAUDE_SKILL_DIR}` là thư mục skill; Windows dùng `py -3`, macOS/Linux dùng `python3`.
`$CAT` = `${CLAUDE_SKILL_DIR}/categories/<slug>`; mọi lệnh nhận `--category <slug>`.

| slug | Ngành | Engine | Tệp nền đọc một lần mỗi phiên |
| --- | --- | --- | --- |
| `riding-body-protector` (mặc định) | Body/back protector, air vest, phụ kiện | riêng (`pdplib`) | `first-prompt.md`, `file1-general.md`, `rules.md` |
| `riding-hat` | Riding Hat, Hat Silks & Covers, Liners & Parts, Helmet Accessories | `generic` | `first-prompt.md`, `template.md`, `rules.md`, `checklist.md` |

Không chắc ngành nào → nhìn tiêu đề cột File (2) / tên sản phẩm, hỏi nếu vẫn mơ hồ.
`$F2` = đường dẫn File (2) (hỏi nếu chưa có). `$OUT` = `./output/<slug>`.
Luôn đọc `common/universal-rules.md` cùng các tệp nền.

## Quy trình một sản phẩm

### 1. Thẻ

```bash
py -3 ${CLAUDE_SKILL_DIR}/scripts/product.py --category <slug> --file2 "$F2" --stt N --workdir "$OUT"
```

Ghi `$OUT/NNN-<slug>/card.md`. **BLOCK** → dừng, báo đúng câu đó, chờ quyết định (loại sản phẩm
không rõ → người dùng xác nhận, chạy lại với `--type <khoá trong category.json>`). **CHECK** → đưa
vào mục Conflict / "Cần xử lý trước khi viết". File (2) không có cột No./STT thì dòng 2 = số 1.

### 2. THÔNG TIN TỪ BRAND

Theo First prompt của category: người dùng dán sau "THÔNG TIN TỪ BRAND:", hoặc `brand-info.txt` đã
có trong thư mục sản phẩm; chỉ tự lấy từ **website chính thức của hãng** khi category cho phép
(riding-body-protector) hoặc người dùng yêu cầu. Lưu `brand-info.txt` (mỗi nguồn mở bằng
`### <URL>`). Không viết từ trí nhớ.

### 3. Đối chiếu (chưa viết)

Đối chiếu thẻ với `brand-info.txt` theo thứ tự ưu tiên nguồn, ghi `analysis.md` theo
`$CAT/analysis-template.md`, trả người dùng rồi **dừng**. Phản hồi chưa có "Viết bài" / "Tạo nội
dung" → chỉ cập nhật báo cáo.

### 4. Viết

Viết `draft.md` theo `$CAT/draft-format.md` (body protector: đọc thêm đúng một `outline-<X>.md`):

- H2, nhãn bullet: đúng tên, đúng thứ tự trên thẻ; bỏ mục optional thiếu dữ liệu.
- Màu: đúng danh sách trên thẻ. Size: đúng "câu Size gợi ý" trên thẻ.
- Đoạn discount-equestrian.co.uk: **chép nguyên văn từ thẻ** (đã có link trang chủ).
- Link: đúng bảng link trên thẻ (BẮT BUỘC / được phép / KHÔNG gắn), mỗi URL một lần.

### 5. Tự kiểm

```bash
py -3 ${CLAUDE_SKILL_DIR}/scripts/check_draft.py --category <slug> --draft "$OUT/NNN-<slug>/draft.md" \
  --file2 "$F2" --stt N --brand-info "$OUT/NNN-<slug>/brand-info.txt" --history "$OUT"
```

Sửa đến **0 ERROR**; xét từng WARN. Rồi **rà checklist** (`$CAT/checklist.md` nếu có, hoặc mục "Tự
kiểm tra" / "CHECKLIST QA" của First prompt) từng dòng cho phần máy không làm được (lặp ý giữa H2,
lặp Short/Long, Writing focus, nguồn của từng câu). Ghi vào `# SELF-CHECK`, trả draft.

### 6. HTML và tệp nộp (sau "Tạo bản HTML")

```bash
py -3 ${CLAUDE_SKILL_DIR}/scripts/to_html.py --category <slug> "$OUT/NNN-<slug>/draft.md" --submit
```

Ghi `draft.html` (bản xem) và hai tệp nộp: `ban-text.html` (mở trình duyệt → Ctrl+A → dán vào tab
**Text** của Google Doc) và `ban-html.txt` (tab **HTML**; với riding-hat có sẵn hai dòng Meta
title / Meta Description rồi 3 khối code). Không tự viết HTML. Nộp theo bước cuối của
`$CAT/writer-guide.md` (1 Google Doc / sản phẩm, 2 tab, dán link vào sheet theo dõi).

## Sửa bài theo comment review

Người dùng đưa ảnh / link Google Doc có comment: đọc doc (Drive `read_file_content` với
`includeComments: true`), dựng lại `draft.md` từ nội dung doc, áp từng comment, chạy bước 5–6.
"Kiểm tra doc <link> sản phẩm số N" (không có comment): đọc doc, dựng `draft.md`, chạy bước 5 và báo
lỗi, nhất là lỗi do dán tay (link `http://` tự tạo, mất chữ).
Comment nêu một luật mới áp dụng được cho mọi sản phẩm → đề xuất thêm vào
`common/universal-rules.md` hoặc `$CAT/rules.md` (và vào checker nếu kiểm được bằng máy).

## Hàng loạt ("làm 5–20")

1. `product.py --category <slug> --file2 "$F2" --list` rồi `--stt 5-20 --brief`: gom **mọi
   BLOCK/CHECK** thành một danh sách, hỏi người dùng **một lần**.
2. Bước 2–3 cho tất cả, trả **một bảng**: No. · template · variant/About · conflict cần quyết.
3. Bước 4–6 **tuần tự** (draft trước phải lưu thì `--history` mới chống trùng được). Không dán lại
   draft vào chat; báo bảng: No. · đường dẫn · ERROR/WARN · ghi chú.
4. "Tự chạy luôn" → bỏ chờ với sản phẩm **không** có conflict, nhưng vẫn dừng ở mọi BLOCK và mọi
   conflict về chuẩn an toàn.

## Kỷ luật tiết kiệm token

- Không mở `.xlsx`; dùng `product.py`. `writer-guide.md` chỉ đọc khi cần bước nộp bài.
- Tệp nền đọc một lần mỗi phiên; không đọc lại draft cũ để chống trùng (`--history` làm việc đó).
- THÔNG TIN TỪ BRAND lưu tệp, lần sau đọc tệp, không fetch lại.

## Thêm ngành hàng mới

Ngành mới dùng engine `generic`, không cần sửa code: chép `categories/riding-hat/` thành
`categories/<slug>/`, rồi sửa:

- `category.json`: `columns` (mỗi khoá nhận danh sách tên cột thay thế), `types` (từ nhận diện,
  type word, product type số nhiều, cột, H2 `[tên, always]`, nhãn bullet, giới hạn câu, frame),
  `detect_order`, `variant_rules`, `brand_urls`, `links` (anchor, vị trí, khối, điều kiện
  `always` / `optional` / `children` / `shape:…` / `range:…`), từ/cụm bị cấm.
- `variants.json`: các đoạn discount-equestrian.co.uk nguyên văn (`[Brand]`, `[product type]`).
- `first-prompt.md`, `template.md`, `checklist.md`, `writer-guide.md`: tài liệu gốc của team.
- `rules.md`, `analysis-template.md`, `draft-format.md`.

Chạy `py -3 tests/run_tests.py` (test tự kiểm cấu hình mọi category). Body protector cập nhật
template bằng `import_template.py "<PDP Template>.docx" --out $CAT`.
