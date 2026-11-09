---
name: category-content
description: Sản xuất nội dung trang category hàng loạt cho wholesalehats.com (hat wholesaler Mỹ, người đọc B2B buyer) theo quy trình team content Digiworks — 5 template T1–T5 (Brand cha, Brand con, Product type cha construction/pattern, Product type cha use-case, Product type con), fact bank wholesalehats.com, internal link lấy từ FILE (2). Script tự giải mô hình link từ CSV, tự QA (sentence case, dash, fact bank, link mỗi URL một lần, số từ) và xuất .docx; Claude chỉ research brand và viết prose. Dùng khi người dùng nói "Follow quy trình tạo nội dung cho category page", "Phân tích loạt trang", "Tạo nội dung cho N trang", đưa URL trang category wholesalehats.com kèm Brand cha/Brand con, hoặc file internal linking / Onpage_PDPs.
license: MIT
compatibility: Cần Python 3.8+ (py -3 trên Windows, python3 trên macOS/Linux) và python-docx (pip install --break-system-packages python-docx). WebFetch để đọc website brand và trang category. FILE (2) internal linking export ra .csv.
allowed-tools: Read, Write, Edit, Glob, Grep, WebFetch, WebSearch, Bash(py -3 ${CLAUDE_SKILL_DIR}/scripts/links.py:*), Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/links.py:*), Bash(py -3 ${CLAUDE_SKILL_DIR}/scripts/check.py:*), Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/check.py:*), Bash(py -3 ${CLAUDE_SKILL_DIR}/scripts/build_doc.py:*), Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/build_doc.py:*)
metadata:
  site: wholesalehats.com
  templates: T1 Brand cha, T2 Brand con, T3 Product type cha (construction/pattern), T4 Product type cha (use-case), T5 Product type con
---

# Nội dung category wholesalehats.com

**Phân vai.** Mọi luật cố định (template, fact bank, mô hình link, QA máy) do tài liệu nền và script lo:
**lấy từ thẻ/script, không suy luận lại**. Claude chỉ làm phần phán đoán: research brand từ website brand,
viết prose theo outline, rà các luật judgement. Nguồn dữ liệu, giọng văn, link, chống trùng: xem
`common/rules.md`. **FILE (1) (bộ quy trình) luôn thắng khi mâu thuẫn.**

`$SK = ${CLAUDE_SKILL_DIR}`; `$F2` = FILE (2) internal linking dạng .csv (hỏi nếu chưa có); `$OUT = ./output/wholesalehats`.

## 0. Đầu phiên (một lần)
Đọc `common/rules.md`, `common/templates.md`, `common/product-guideline.md`, `common/qa.md`,
`common/analysis-template.md`. Đã đọc ở lượt trước trong cùng phiên thì bỏ qua, sang bước 1.
Có `$F2` chưa? Nếu người dùng đưa link Google Sheet internal linking, lưu tab
"Copy of Danh sách chi tiết" (có cột URL + Anchor home page + STT) ra `$OUT/file2.csv`. Tab
"Danh sách chi tiết" thiếu URL và anchor, không dùng. FILE (3) Onpage_PDPs (tab PDPs) lưu ra
`$OUT/pdps.csv`, chỉ dùng để đối chiếu SKU.

**Đọc Google Sheet:** công cụ Sheets có thể báo "not found" với file được chia sẻ từ tài khoản công ty,
trong khi Drive vẫn đọc được. Khi đó dùng Drive `download_file_content` với
`exportMimeType` = xlsx, giải base64 rồi đọc bằng openpyxl và ghi tab cần dùng ra CSV.
`read_file_content` chỉ trả mẫu vài dòng đầu, không đủ để giải link.

**Danh sách trang cần viết:** lọc sheet theo dõi (tab Categories) theo PIC và các dòng chưa có Draft URL.
Cột "Content type" ở đó cho biết loại trang.

## 1. Mỗi trang — link card (deterministic, tiết kiệm token)
```bash
py -3 $SK/scripts/links.py --file2 "$F2" --page "<Tên danh mục>"   # hoặc --url <URL>
```
In LINK CARD: template (T1–T5), anchor homepage, và mọi link bắt buộc kèm URL + H2. URL **chỉ** từ CSV;
thiếu URL → flag `[INPUT]`, không bịa. Trang không có trong CSV → ghi mục F, bỏ qua.

## 2. Research (nguồn theo `rules.md` mục 7.1)
- Số SKU + danh sách style: mở trang category trên wholesalehats.com (WebFetch; trang có phân trang
  thì mở thêm `?p=2`).
- Spec/fit/chất liệu/màu/size + fact brand: **website brand** (WebFetch trang About → dòng sản phẩm →
  model → size chart). Trang tìm kiếm của brand (vd `richardsonsports.com/?s=<model>`) cho nhanh fit,
  closure, size, structure của nhiều model. Không cần mở mọi model của một dải: mở đủ để biết đặc điểm
  chung và các ngoại lệ (quy trình nhắc không check quá nhiều sản phẩm).
- **Bảng fact brand** (fact · trích dẫn · URL): xem `brands/<brand>.md` trước (đã có `richardson.md`,
  `nike.md`), có rồi thì **dùng lại**, chỉ research phần thiếu. Brand mới thì lập bảng, lưu
  `$OUT/brand-<brand>.md`, cuối đợt đề xuất thêm vào `brands/`.
- Bài đã submit cùng brand (folder "WH _ Category content") đọc được để giữ nhất quán dữ liệu (vd số
  đo từ ảnh size chart) và để **tránh trùng câu chữ**, không chép cách diễn đạt.
- Câu phân biệt ở "Shop by.../Other... to explore": mở nhanh chính trang category được nhắc tới.
- Thiếu/không đọc được (size chart dạng ảnh…) → `[INPUT: cần ảnh size chart]` / `[INPUT: cần nguồn]`, không suy đoán.

## 2b. Bản phân tích — dừng chờ duyệt
Trả bản phân tích theo `common/analysis-template.md` cho từng trang (mục A–F), gom mọi `[INPUT]` hỏi
**một lần**, rồi **dừng**. Chỉ sang bước 3 khi người dùng gửi "Tạo nội dung", hoặc đã nói rõ "viết luôn" /
"làm xong lưu file". Khi viết luôn: ghi bản phân tích + bảng fact + báo cáo QA vào một tệp kèm draft
(vd `00 - Ban phan tich va QA.docx`), và đưa các điểm mục F vào báo cáo cuối.

## 3. Viết `$OUT/<slug>/draft.md`
Theo đúng template trong `common/templates.md` (chọn template = dòng TEMPLATE của link card). Định dạng:
`# H1` (giữ H1 gốc của trang), `## H2`, đoạn văn, `- bullet`, link `[anchor](url)` đúng link card.
Fact bank đặt ở section entity, format theo STT (lẻ văn xuôi / chẵn bullet). Sentence case, American
English, không em/en dash. H2 paraphrase, thể hiện wholesale.

## 4. Tự kiểm
```bash
py -3 $SK/scripts/check.py --file2 "$F2" --page "<Tên>" "$OUT/<slug>/draft.md"
```
Sửa đến **0 ERROR**, xét từng WARN, rồi rà tay phần judgement trong `common/qa.md` (chống trùng, nguồn
dữ liệu, SKU, fact bank thu hẹp) và 5 điểm rủi ro cao của Bước 5. Viết báo cáo QA theo Phần 4
(Có/Không từng mục, lý do nếu Không) cho từng trang.

## 5. Xuất tệp nộp
```bash
py -3 $SK/scripts/build_doc.py "$OUT/<slug>/draft.md" --out "$OUT/<slug>/<Tên danh mục>.docx"
```
Nộp theo Bước 6 quy trình: đặt doc vào folder "WH _ Category content", điền "Draft URL" + "Ready to
review" + ngày vào sheet theo dõi. **Chỉ làm bước nộp khi người dùng yêu cầu** ("chưa cần up drive" =
chỉ giao tệp .docx).

## Hàng loạt (5–10 trang/đợt)
Bước 1 (link card) + research cho cả đợt, gom mọi `[INPUT]` hỏi **một lần**. Bước 3–5 tuần tự, đối chiếu
các trang đã viết để tránh trùng câu (chống trùng, `rules.md` mục 9). Báo **một bảng**: trang · template ·
ERROR/WARN · đường dẫn docx · `[INPUT]` còn lại. Không dán draft vào chat.

## Sửa theo review
"Trang [số]: sửa [lỗi]" → chỉ sửa đúng phần đó, chạy lại bước 4–5. Comment nêu luật áp dụng cho mọi trang
→ đề xuất thêm vào `common/rules.md` (và `check.py` nếu kiểm được bằng máy).

## Kỷ luật token
Tài liệu nền đọc **một lần/phiên**. Bảng fact brand lưu tệp, dùng lại, không fetch lại. Mô hình link do
`links.py`, QA máy do `check.py` — không tự dò tay. Không mở file .xlsx; export CSV.
