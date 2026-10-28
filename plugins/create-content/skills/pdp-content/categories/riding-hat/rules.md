# Bổ sung cho First Prompt — Riding Hat

Chỉ gồm điều **không** nằm sẵn trong `first-prompt.md` / `template.md` / `checklist.md`, hoặc
là cách skill thay cho thao tác thủ công trong `writer-guide.md`.

## Ánh xạ quy trình

| Writer guide (thủ công) | Với skill |
| --- | --- |
| Bước 1–3: dán First prompt, File (1), File (2) vào thread | Không cần; skill đọc `first-prompt.md`, `template.md` một lần mỗi phiên |
| Bước 5 "Đối chiếu dữ liệu sản phẩm số N" | `product.py --category riding-hat --stt N` → thẻ, rồi BÁO CÁO ĐỐI CHIẾU theo `analysis-template.md` |
| Bước 6 phản hồi báo cáo, lệnh "Viết bài" | Như cũ: chỉ viết khi người dùng nói "Viết bài" / "Tạo nội dung" |
| Bước 7–8 kiểm draft, link | `check_draft.py --category riding-hat` + rà `checklist.md` |
| Bước 9–10 HTML, lưu doc 2 tab | `to_html.py --category riding-hat --submit` |

## THÔNG TIN TỪ BRAND

First prompt cấm web search: THÔNG TIN TỪ BRAND do người dùng dán (copy từ trang sản phẩm trên
website chính thức của brand). Chỉ tự mở trang brand khi người dùng yêu cầu rõ, và chỉ website
chính thức, không shop khác. Không có trang brand → xử lý theo "Trường hợp không có trang sản
phẩm của brand" trong First prompt (không tiêu chuẩn, quality mark, trọng lượng, Competition
suitability).

## File (2) của bài test khác File (2) mô tả trong First prompt

- Không có cột **No.**: script đánh số theo thứ tự dòng (dòng 2 = No. 1).
- Không có cột **DE ranges**: link range (Children's, Sparkly, Custom design) chỉ gắn khi người
  dùng xác nhận; riêng Children's sizes dựa vào cột `Children's size range` ("yes ..." = Y).
- Cột **Duplicate Risk** có thể bị Excel đổi thành ngày (vd "1, 2" → 02/01/2016): thẻ báo CHECK,
  hỏi lại số No. thật.
- Cột màu có thể dính ký tự tab ở đầu: script đã bỏ.

## Bài học từ review

- Size và màu: luật chung §2–3 (`common/universal-rules.md`). Dùng đúng "câu Size gợi ý" và danh
  sách màu trên thẻ.
- `discount-equestrian.co.uk` trong đoạn About link về trang chủ (luật chung §4).
- Charles Owen: File (2) có thể ghi "Made In United Kingdom"; vẫn **không** viết made in UK nếu
  người dùng chưa xác nhận ngày sản xuất.
- Phụ kiện (Hat Silks & Covers, Liners & Parts, Helmet Accessories): không nhắc tiêu chuẩn an toàn,
  không nói "safer"/"more protection" (đoạn brand trích sứ mệnh "for a safer world" thì được).
