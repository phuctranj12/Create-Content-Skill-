# Hạn chế của skill và cách chuẩn bị dữ liệu

Tài liệu cho writer dùng skill `pdp-content`. Mục tiêu: chuẩn bị File (2) đủ để skill viết đúng ngay
lần đầu, và biết phần nào skill **không** tự lo được.

## 1. Skill chặn được gì, không chặn được gì

| Nhóm lỗi | Skill xử lý | Ví dụ |
| --- | --- | --- |
| **Kiểm được bằng máy** | `check_draft.py` báo ERROR, phải sửa đến 0 ERROR | Màu sai/thiếu so với File (2); "Choose from"; dải size ngụ ý size DE không bán; thiếu "in a round fit"; link trang chủ sai (kể cả `http://discount-equestrian.co.uk`); đoạn giới thiệu DE lệch chữ; sai variant; H2 sai thứ tự; Care khi Shared care guide = Y; gạch dài; độ dài meta |
| **Kiểm một phần** | WARN | Con số (kể cả viết bằng chữ: "three to five years") không có trong File (2) / brand-info / phụ lục |
| **Cần đọc hiểu** | Không chặn được, người duyệt phải đọc | Câu không có trong nguồn (không chứa số); lặp ý giữa các H2; nguồn sai ngay từ đầu |
| **File (2) tự mâu thuẫn** | `--preflight` báo HỎI trước khi viết | Compatible product URL có mẫu không nằm trong Compatible hats; Duplicate Risk bị Excel đổi thành ngày |
| **Phát sinh khi dán bài vào Google Doc** | Ngoài tầm skill, trừ khi gửi lại link để kiểm | Gõ tay khiến Docs tự tạo link `http://…`; sửa tay làm mất chữ |

Mỗi lỗi reviewer bắt được mà máy kiểm được thì thêm vào checker và `common/universal-rules.md`, để
không lặp lại.

## 2. Hạn chế

| Hạn chế | Hệ quả | Cách xử lý |
| --- | --- | --- |
| Web DE chặn máy truy cập (403). Trang brand thì máy chỉ nhận bản tóm tắt, không nguyên văn, có khi sai màu/size; một số trang còn chặn, chỉ hiện bằng JavaScript, hoặc để size chart dạng ảnh/PDF | Skill không tự lấy được nội dung từ link | Dán nội dung trang vào cột cuối **`Nội dung trang web (dán)`** (xem mục 3). Link chỉ để ghi nguồn |
| Một ô Excel chứa tối đa 32.767 ký tự | Dán cả trang bằng Ctrl+A (lẫn menu, footer) dễ bị cắt phần cuối | Chỉ bôi đen phần nội dung; preflight cảnh báo khi ô gần đầy |
| Skill chỉ đọc chữ trong ô Excel | Link ẩn sau chữ, comment trong ô, màu tô, ảnh đều bị bỏ qua | Ghi URL dạng chữ đầy đủ; không đánh dấu ý bằng màu tô |
| Skill chỉ viết điều có trong nguồn | Ô trống thì mục đó bị bỏ, kể cả H2 tuỳ chọn | Điền đủ cột tính năng của đúng template, mỗi ý kèm URL nguồn |
| Không sửa hay tạo tab trong Google Doc (chỉ đọc doc và comment) | Writer tự dán bài | Dán từ `ban-text.html` (tab Text) và `ban-html.txt` (tab HTML). Bật connector Google Docs thì Claude sửa thẳng vào doc được |
| Chống trùng chỉ so với bài đã lưu trong `output/` | Bài viết ở phiên/máy khác không được so | Dùng chung một thư mục `output/<ngành>/` cho cả đợt, không xoá |
| Gặp File (2) mâu thuẫn hoặc chuẩn an toàn lệch, skill dừng lại hỏi | Chủ ý, không phải lỗi | Khi làm hàng loạt, mọi câu hỏi được gom thành một danh sách, trả lời một lần |
| Một phiên có giới hạn dung lượng | Làm quá nhiều sản phẩm một phiên thì chất lượng giảm | Chia đợt khoảng 10–15 sản phẩm mỗi phiên |

## 3. File (2) cần có gì

Tên cột phải khớp `columns` trong `categories/<ngành>/category.json`. Ví dụ dưới đây theo Riding Hat.

**Bắt buộc mọi dòng**

- **No.**
- **Product name**
- **Brand name**
- **Product type**: đúng một tên template của ngành (Riding Hat: `Riding Hat`, `Hat Silks & Covers`,
  `Liners & Parts`, `Helmet Accessories`). Tên khác thì skill dừng lại hỏi.
- **Brand info**: từng fact kèm URL nguồn.

**Thông tin bán hàng của DE (quyết định màu và size trong bài, ưu tiên hơn brand)**

- **Colours sold**: đúng tên màu như trên trang DE, cách nhau bằng `;` (vd `Black; Black - Charcoal; Navy`).
- **Sizes sold**: dạng `52CM; 53CM; 54CM; 59CM ROUND`, size round ghi rõ `ROUND`. Có bảng quy đổi UK
  (`52 = 6 ⅜`) thì ghi kèm, bài sẽ có size UK.
- **Children's sizes**: `Y` hoặc `N`.
- **DE ranges**.
- **Shared care guide**: `Y` hoặc `N`.

**Cột tính năng của template**

- Điền các cột của đúng template (vd Liners & Parts: Function, Fitting, Material, Properties, Usage
  restrictions, Compatible hats). Dán chữ thật từ trang brand vào ô.
- **Compatible hats** và **Compatible product URL** phải khớp nhau: mẫu nào có URL thì phải có trong
  danh sách, và ngược lại.

**Nên có**: Duplicate Risk, Writing focus.

**Cột cuối `Nội dung trang web (dán)`** (cho mọi sản phẩm): dán trang sản phẩm của brand, trang DE,
hướng dẫn chọn size và hướng dẫn bảo quản/lifespan của brand. Mỗi trang mở bằng một dòng URL. Skill
tự ghi ô này thành `brand-info.txt`. Bài mẫu đã duyệt (YR8) có các câu fit guidance và "three to five
years" chỉ lấy được từ các trang này: không dán thì skill phải bỏ những ý đó.

**Không dùng** dấu gạch dài (—, –) trong ô.

## 4. Quy trình làm hàng loạt

1. Gửi đường dẫn File (2), nói **"Làm No. 1–15"**.
2. Skill chạy `product.py --preflight`: in phần nhắc (`common/nhac-nguoi-dung.md`) và bảng từng dòng
   THIẾU / HỎI / LƯU Ý. Bổ sung File (2) và trả lời các HỎI một lần.
3. Skill viết tuần tự từng bài, mỗi bài `check_draft.py` 0 ERROR rồi rà checklist.
4. Mở `ban-text.html` → Ctrl+A → copy → dán vào Google Doc. **Không gõ lại bằng tay.**
5. Gửi **"kiểm tra doc <link> sản phẩm số N"**: Claude đọc doc và chạy checker trên đúng bản trong doc.
6. Có comment review → gửi link doc, Claude áp comment và đề xuất luật mới nếu áp dụng chung.
