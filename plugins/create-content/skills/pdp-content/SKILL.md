---
name: pdp-content
description: Sản xuất nội dung trang sản phẩm (PDP) hàng loạt cho discount-equestrian.co.uk theo quy trình của team content (Template/File (1), File (2) .xlsx, First prompt, checklist), cho mọi ngành hàng: đưa file Word (template) và file Excel là skill tự đọc luật từ Word, người dùng xác nhận một lần rồi chạy, kể cả ngành mới như Horse Rugs. Có sẵn pack Riding Body Protector và Riding Hat. Script đọc File (2), tính sẵn H2, bullet, đoạn nguyên văn, link, màu, size; Claude đối chiếu THÔNG TIN TỪ BRAND, báo conflict, viết bài; script tự kiểm draft và xuất bản nộp Text + HTML. Dùng khi người dùng nói "Đối chiếu dữ liệu sản phẩm số …", "Phân tích sản phẩm số …", "Viết bài", "Tạo nội dung", "Tạo bản HTML", "viết PDP STT/No. …", "làm hàng loạt 5-20", hoặc đưa file Word template, File (2) / THÔNG TIN TỪ BRAND / ảnh comment review của một bài PDP.
license: MIT
compatibility: Cần Python 3.8+ (py -3 trên Windows, python3 trên macOS/Linux), chỉ dùng thư viện chuẩn. WebFetch/WebSearch chỉ dùng khi First prompt của category cho phép; không thì người dùng dán THÔNG TIN TỪ BRAND.
allowed-tools: Read, Write, Edit, Glob, Grep, WebFetch, WebSearch, Bash(py -3 ${CLAUDE_SKILL_DIR}/scripts/product.py:*), Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/product.py:*), Bash(py -3 ${CLAUDE_SKILL_DIR}/scripts/check_draft.py:*), Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/check_draft.py:*), Bash(py -3 ${CLAUDE_SKILL_DIR}/scripts/to_html.py:*), Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/to_html.py:*), Bash(py -3 ${CLAUDE_SKILL_DIR}/scripts/import_template.py:*), Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/import_template.py:*), Bash(py -3 ${CLAUDE_SKILL_DIR}/scripts/template_engine.py:*), Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/template_engine.py:*)
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

## Chế độ theo file Word (mặc định khi có file Word và Excel)

Người dùng đưa **file Word (template) và file Excel** của một ngành chưa có pack, hoặc yêu cầu chạy theo
file Word: luật lấy từ file Word, không cần pack. Chỉ dùng hai file đó và phần dán trong Excel.
`$TE` = `${CLAUDE_SKILL_DIR}/scripts/template_engine.py`; `$OUT` = `./output/<tên-ngành>`.

1. `py -3 $TE init --template "<Word>" --file2 "<Excel>" --workdir "$OUT"`, rồi làm theo dòng TRẠNG THÁI:
   - **MỚI**: đọc toàn bộ `$OUT/template.txt`, `$OUT/file2-columns.txt` và `common/rules-schema.md`,
     viết `$OUT/rules.json`.
   - **KHÔNG ĐỔI**: dùng lại luật, sang bước 3.
   - **FILE WORD ĐÃ ĐỔI**: đọc `template.diff`, cập nhật `rules.json`, báo người dùng luật nào đổi.
2. `py -3 $TE validate --workdir "$OUT"`, sửa đến hết ERROR, xử lý từng WARN. **Đưa bảng luật và các
   `questions` cho người dùng, dừng chờ.** Họ đồng ý mới chạy `confirm`. Không tự confirm: mọi lệnh sau
   từ chối chạy nếu chưa confirm, và khi Word hoặc `rules.json` đổi.
3. `py -3 $TE preflight --workdir "$OUT" [--pic "<tên>"] [--no 94-97]`. **Đưa nguyên phần nhắc và bảng
   cho người dùng, gom mọi THIẾU/HỎI hỏi một lần.** Thiếu cột hoặc ô `Nội dung trang web (dán)` là THIẾU:
   nhắc bổ sung, không viết dòng đó, không tự lấy web để lấp. Excel mới thì chạy lại `init` với đường dẫn mới.
   Lưu câu trả lời vào `$OUT/answers.json` để không hỏi lại: `{"116": {"type": "Cooler Rugs", "ok": true}}`
   (giá trị thay cho ô Excel của riêng đợt này; `ok` = đã chốt các HỎI của dòng đó). Sai ở Excel gốc thì báo
   người dùng sửa, theo đúng quy trình trong Word.
4. Với từng sản phẩm, **theo đúng thứ tự file**, làm đúng quy trình trong file Word:
   `py -3 $TE card --workdir "$OUT" --no N` tạo `card.md` và `brand-info.txt`. Lấy H2, bullet, link, đoạn
   nguyên văn và variant từ thẻ, không tính lại. Các bước phân tích, chờ duyệt, lệnh viết, phân bổ dữ
   liệu theo First prompt trong Word; `template.txt` là nguồn luật khi thẻ không nói tới.
5. Viết `<thư mục sản phẩm>/draft.md` theo định dạng ở `common/rules-schema.md`.
   `py -3 $TE check --workdir "$OUT" --no N`: sửa đến 0 ERROR, xét từng WARN, rồi rà `$OUT/checklist.txt`
   và `judgement` từng dòng.
6. `py -3 $TE html --workdir "$OUT" --no N` (từ chối nếu draft còn ERROR) ghi `ban-text.html`,
   `ban-html.txt`, `ban-ghi-chu.txt`. Nộp theo bước cuối trong Word.

**Ưu tiên nguồn (quyết định của người dùng, thắng luật ưu tiên brand trong Word):** Excel lệch web thì theo
Excel, gồm type, tên màu, size và thông số; thông tin chỉ có trong Excel vẫn được viết. Vẫn ghi điểm lệch vào
phần Conflict nhưng không dừng hỏi. Ngoại lệ: lệch về chuẩn an toàn, chứng nhận thì dừng hỏi.

Hàng loạt: bước 3 một lần cho cả đợt; bước 4–6 tuần tự, vì bộ đếm variant và chống trùng dựa trên các
draft đã lưu. "Tự chạy luôn" chỉ bỏ chờ với sản phẩm không có conflict; vẫn dừng ở mọi THIẾU, HỎI,
conflict. Báo kết quả bằng một bảng, không dán lại draft vào chat. Bốn điều cốt lõi ở trên vẫn áp dụng; nếu
khác file Word thì theo file Word.

## Chọn ngành hàng (category pack)

Ngành đã có pack dưới đây vẫn chạy theo quy trình pack, trừ khi người dùng đưa file Word mới hoặc yêu
cầu chạy theo file Word.

`${CLAUDE_SKILL_DIR}` là thư mục skill; Windows dùng `py -3`, macOS/Linux dùng `python3`.
`$CAT` = `${CLAUDE_SKILL_DIR}/categories/<slug>`; mọi lệnh nhận `--category <slug>`.

| slug | Ngành | Engine | Tệp nền đọc một lần mỗi phiên |
| --- | --- | --- | --- |
| `riding-body-protector` (mặc định) | Body/back protector, air vest, phụ kiện | riêng (`pdplib`) | `first-prompt.md`, `file1-general.md`, `rules.md` |
| `riding-hat` | Riding Hat, Hat Silks & Covers, Liners & Parts, Helmet Accessories | `generic` | `first-prompt.md`, `template.md`, `rules.md`, `checklist.md` |

Không chắc ngành nào → nhìn tiêu đề cột File (2) / tên sản phẩm, hỏi nếu vẫn mơ hồ.
`$F2` = đường dẫn File (2) (hỏi nếu chưa có). `$OUT` = `./output/<slug>`.
Luôn đọc `common/universal-rules.md` cùng các tệp nền.

## 0. Kiểm tra đầu vào (lần đầu nhận File (2), và trước mọi đợt hàng loạt)

```bash
py -3 ${CLAUDE_SKILL_DIR}/scripts/product.py --category <slug> --file2 "$F2" --preflight
```

In ra `common/nhac-nguoi-dung.md` (hạn chế của skill, cách thêm cột cuối **`Nội dung trang web
(dán)`** để dán nội dung trang web mà máy không truy cập được) và bảng từng dòng: THIẾU / HỎI / LƯU Ý.
**Đưa nguyên phần nhắc và bảng cho người dùng**, dừng chờ họ bổ sung File (2) và trả lời các HỎI
một lần. Chỉ viết những dòng không còn THIẾU. Không tự lấy web để lấp chỗ thiếu: WebFetch trả bản
tóm tắt, không phải nguyên văn, và trang DE trả 403.

## Quy trình một sản phẩm

### 1. Thẻ

```bash
py -3 ${CLAUDE_SKILL_DIR}/scripts/product.py --category <slug> --file2 "$F2" --stt N --workdir "$OUT"
```

Ghi `$OUT/NNN-<slug>/card.md`. **BLOCK** → dừng, báo đúng câu đó, chờ quyết định (loại sản phẩm
không rõ → người dùng xác nhận, chạy lại với `--type <khoá trong category.json>`). **CHECK** → đưa
vào mục Conflict / "Cần xử lý trước khi viết". File (2) không có cột No./STT thì dòng 2 = số 1.

### 2. THÔNG TIN TỪ BRAND

Ưu tiên cột `Nội dung trang web (dán)`: `product.py --workdir` tự ghi ô đó thành `brand-info.txt`.
Không có thì người dùng dán sau "THÔNG TIN TỪ BRAND:"; chỉ tự lấy từ **website chính thức của
hãng** khi category cho phép (riding-body-protector) hoặc người dùng yêu cầu. Lưu `brand-info.txt`
(mỗi nguồn mở bằng `### <URL>`). Không viết từ trí nhớ. Luôn truyền `--brand-info` cho checker:
số nào trong bài không có trong File (2) / brand-info / phụ lục đều bị WARN.

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

1. Bước 0 (`--preflight`), rồi `--stt 5-20 --brief`: gom **mọi THIẾU/HỎI/BLOCK/CHECK** thành
   một danh sách, hỏi người dùng **một lần**.
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
