---
name: pdp-content
description: Sản xuất nội dung trang sản phẩm (PDP) hàng loạt cho discount-equestrian.co.uk theo quy trình chuẩn của team content (PDP Template, File (1), File (2), First Prompt), bắt đầu với ngành hàng Riding Body Protector (body protector, back protector, air vest / air jacket, phụ kiện). Script đọc File (2) .xlsx và tính sẵn outline A-D, tên H2, nhãn bullet, phiên bản đoạn About và đoạn discount-equestrian.co.uk nguyên văn, {Role}, bộ internal link, sản phẩm gần giống, trùng Writing focus; Claude thu thập THÔNG TIN TỪ BRAND, trả phân tích để duyệt conflict, viết H1 / Meta Description / Short / Long description; script tự kiểm draft (gạch dài, H2, bullet, hướng dẫn đo, feature bịa, chuẩn thi đấu, link, đoạn About, trùng 8 từ với sản phẩm gần giống) và xuất HTML. Dùng khi người dùng nói "Phân tích sản phẩm số …", "Tạo nội dung", "Tạo bản HTML", "viết PDP / content sản phẩm STT …", "làm hàng loạt STT 5-20", hoặc đưa File (2) / THÔNG TIN TỪ BRAND.
license: MIT
compatibility: Cần Python 3.8+ (py -3 trên Windows, python3 trên macOS/Linux), chỉ dùng thư viện chuẩn. Cần WebFetch/WebSearch nếu muốn tự lấy thông tin hãng; không có thì người dùng dán THÔNG TIN TỪ BRAND.
allowed-tools: Read, Write, Edit, Glob, Grep, WebFetch, WebSearch, Bash(py -3 ${CLAUDE_SKILL_DIR}/scripts/product.py:*), Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/product.py:*), Bash(py -3 ${CLAUDE_SKILL_DIR}/scripts/check_draft.py:*), Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/check_draft.py:*), Bash(py -3 ${CLAUDE_SKILL_DIR}/scripts/to_html.py:*), Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/to_html.py:*), Bash(py -3 ${CLAUDE_SKILL_DIR}/scripts/import_template.py:*), Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/import_template.py:*)
metadata:
  categories: riding-body-protector
  site: discount-equestrian.co.uk
---

# Nội dung PDP hàng loạt

**Phân vai.** Claude là writer, làm đúng First Prompt của ngành hàng. Mọi thứ có luật cố định
(outline, tên H2, nhãn bullet, phiên bản About, đoạn discount-equestrian.co.uk, {Role}, link, sản
phẩm gần giống, các lỗi kiểm được bằng máy) do script làm: **lấy từ thẻ, không suy luận lại, không
đọc thẳng File (2)**. Claude chỉ làm phần cần phán đoán: đọc THÔNG TIN TỪ BRAND, xử lý conflict,
viết.

**Ba điều cốt lõi**

1. **Chỉ viết điều hãng nói.** Feature, số liệu, chứng nhận phải có trong THÔNG TIN TỪ BRAND. Thiếu
   thì bỏ ý hoặc bỏ H2; chỉ được suy ra *lợi ích*, không suy ra *thông tin*.
2. **Chuẩn an toàn không tự quyết.** Năm/level lệch hoặc thiếu năm → dừng, hỏi. Chỉ BETA 2018
   Level 3 mới được khẳng định dùng thi đấu; air vest chỉ nói "mặc kèm body protector BETA Level 3".
3. **Đúng thứ tự STT, luôn lưu draft.** Luật phiên bản About, xoay câu mở đoạn brand và chống trùng
   dựa trên các STT trước; `check_draft.py --history` đọc draft đã lưu thay cho "cùng một thread".

## Thiết lập (một lần mỗi phiên)

`${CLAUDE_SKILL_DIR}` là thư mục skill; Windows dùng `py -3`, macOS/Linux dùng `python3`.
`$CAT` = `${CLAUDE_SKILL_DIR}/categories/<slug>` (mặc định `riding-body-protector`; lệnh nào cũng
nhận `--category <slug>`). `$F2` = đường dẫn File (2), hỏi nếu chưa có. `$OUT` = `./output/<slug>`.

Đọc một lần: `$CAT/first-prompt.md` (luật đầu ra, tự kiểm), `$CAT/file1-general.md` (luật chung,
Section ownership, Other features, Meta Description, Brand/Supplier/rotation rule, link) và
`$CAT/rules.md` (conflict phải hỏi, lưu ý File (2)). Bước 1–2 của First Prompt không có đầu ra.

## Quy trình một sản phẩm

### 1. Thẻ

```bash
py -3 ${CLAUDE_SKILL_DIR}/scripts/product.py --file2 "$F2" --stt N --workdir "$OUT"
```

Ghi `$OUT/NNN-<slug>/card.md`. **BLOCK** → dừng, báo đúng câu đó, chờ quyết định (Product Type
không rõ → người dùng sửa File (2) hoặc xác nhận, rồi chạy lại với `--type <loại>`; phụ kiện không
rõ phục vụ loại nào → `--serves`). **CHECK** → đưa vào mục Conflict. Đã dùng `--type`/`--serves`
thì dùng lại ở mọi lệnh sau của sản phẩm đó.

### 2. THÔNG TIN TỪ BRAND

Nguồn theo thứ tự: (a) người dùng dán sau "THÔNG TIN TỪ BRAND:"; (b) `brand-info.txt` đã có trong
thư mục sản phẩm; (c) tự lấy: trang sản phẩm trên **website chính thức của hãng** (+ size chart,
chứng nhận, hướng dẫn sử dụng/bảo quản/bảo hành của đúng sản phẩm) và Product URL trên DE.
Lưu `brand-info.txt`: chỉ phần chữ về sản phẩm, mỗi nguồn mở bằng `### <URL>`. Không mở được trang
hãng → nói rõ, xin người dùng dán; không viết từ trí nhớ.

### 3. Phân tích (Lượt 1 — chưa viết)

Đối chiếu thẻ với `brand-info.txt` theo nguyên tắc conflict của First Prompt, ghi `analysis.md`
theo `$CAT/analysis-template.md`, trả cho người dùng rồi **dừng**. Phản hồi về conflict mà chưa có
"Tạo nội dung" → chỉ cập nhật phân tích.

### 4. Viết (Lượt 2 — sau "Tạo nội dung")

Đọc `$CAT/outline-<X>.md` của đúng outline trong thẻ (chỉ outline đó). Viết `draft.md` theo
`$CAT/draft-format.md`:

- H2 và nhãn bullet: đúng tên, đúng thứ tự trong thẻ; bỏ cái thiếu dữ liệu.
- Intro và điểm nhấn Long description theo Writing focus; Differentiator trong Meta Description và
  câu intro; link đặt đúng như thẻ ghi.
- Đoạn brand: **chỉ** từ cột Brand background, mở bằng sự kiện thẻ ghi ("Đoạn brand mở bằng"),
  câu cuối gắn brand với sản phẩm.
- Đoạn discount-equestrian.co.uk: **chép nguyên văn từ thẻ** (được rút gọn tên sản phẩm).

### 5. Tự kiểm

```bash
py -3 ${CLAUDE_SKILL_DIR}/scripts/check_draft.py --draft "$OUT/NNN-<slug>/draft.md" \
  --file2 "$F2" --stt N --brand-info "$OUT/NNN-<slug>/brand-info.txt" --history "$OUT"
```

Sửa đến **0 ERROR**; xét từng WARN. Rồi tự soát phần máy không làm được trong mục "Tự kiểm tra"
của First Prompt (ý trùng giữa các đoạn, chuẩn/size/màu khớp giữa Meta-Short-Long, đúng focus,
other features đúng luật, Section ownership). Ghi kết quả vào `# SELF-CHECK`, trả draft cho người
dùng.

### 6. HTML và tệp nộp (sau "Tạo bản HTML")

```bash
py -3 ${CLAUDE_SKILL_DIR}/scripts/to_html.py "$OUT/NNN-<slug>/draft.md" --submit
```

Ghi `draft.html` (bản xem, có chú thích) và hai tệp nộp: `ban-text.html` (mở bằng trình duyệt →
Ctrl+A → dán vào tab **Text** của Google Doc; gồm H1, dòng "Meta Description:", nội dung; không có
DRAFT INFO/SELF-CHECK) và `ban-html.txt` (code sạch cho tab **HTML**). Không tự viết HTML.

**Nộp (Bước 10 của writer guide):** mỗi sản phẩm 1 Google Doc, 2 tab Text/HTML, đặt trong
Folder Riding Body Protector, dán link doc vào cột I của sheet DE | CONTENT | ONPAGE | RIDING BODY
PROTECTORS (link trong `writer-guide.md`). Claude không tạo được Google Doc: hướng dẫn người dùng
dán hai tệp trên, và nhắc click thử từng link.

## Hàng loạt ("làm STT 5–20")

1. `product.py --file2 "$F2" --list` rồi `--stt 5-20 --brief`: gom **mọi BLOCK/CHECK** thành một
   danh sách, hỏi người dùng **một lần**.
2. Bước 1–2 cho từng sản phẩm.
3. Bước 3 cho tất cả, trả **một bảng**: STT · outline · About · conflict cần quyết ("ok" nếu không
   có). Chờ quyết một lần.
4. Bước 4–6 **tuần tự theo STT** (draft trước phải lưu xong thì `--history` mới chống trùng được).
   Không dán lại draft vào chat; báo bảng: STT · đường dẫn · ERROR/WARN · ghi chú.
5. Người dùng nói "tự chạy luôn" thì bỏ chờ ở bước 3 với sản phẩm **không** có conflict, nhưng vẫn
   dừng ở mọi BLOCK và mọi conflict về chuẩn an toàn.

## Kỷ luật tiết kiệm token

- Không mở `.xlsx`; dùng `product.py`. Không đọc `writer-guide.md` (dành cho người).
- Mỗi sản phẩm chỉ đọc một `outline-<X>.md`; ba tệp nền đọc một lần mỗi phiên.
- Không đọc lại draft cũ để chống trùng; `check_draft.py --history` làm việc đó.
- THÔNG TIN TỪ BRAND lưu tệp, lần sau đọc tệp, không fetch lại.

## Cập nhật template / thêm ngành hàng

Tải PDP Template (đủ các tab) về dạng .docx rồi:

```bash
py -3 ${CLAUDE_SKILL_DIR}/scripts/import_template.py "<PDP Template>.docx" --out $CAT
```

Script tách File (1) thành `file1-general.md` + `outline-*.md`, Appendix 2 thành
`about-versions.json`, First Prompt thành `first-prompt.md`. Nếu tên H2, nhãn bullet, URL, brand,
{Role} trong File (1) đổi thì sửa `category.json` cho khớp. Ngành hàng mới: chép thư mục category,
sửa `category.json` + `rules.md`, chạy lệnh trên với `--out` thư mục mới.
