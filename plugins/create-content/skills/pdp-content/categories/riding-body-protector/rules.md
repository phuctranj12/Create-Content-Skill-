# Bổ sung cho First Prompt — Riding Body Protector

Chỉ gồm những điều **không** có trong `first-prompt.md` / `file1-general.md` mà writer guide
(Bước 6) và thực tế File (2) đòi hỏi. Phần còn lại đã nằm trong hai tệp đó hoặc do script làm.

## Conflict cần người phụ trách quyết (không tự chọn)

| Tình huống | Xử lý |
| --- | --- |
| Năm chứng nhận (2009/2018) hoặc level lệch giữa File (2) và hãng, hoặc hãng không ghi năm | Ghi vào Conflict là **CHỜ NGƯỜI PHỤ TRÁCH**, không viết cho tới khi được xác minh với hãng/nhà cung cấp |
| Phụ kiện: tương thích chỉ có ở File (2) hoặc trang DE, hãng không xác nhận | **Bỏ**. Không suy ra tương thích từ việc cùng brand |
| Product Type trống, hoặc là "Body protector" trong khi Sub type là loại cụ thể hơn (thẻ báo BLOCK) | Hỏi người dùng; họ sửa File (2) hoặc xác nhận để chạy với `--type` |

## Về File (2)

- File (2) có thể **không có cột STT**: script đánh STT theo thứ tự dòng (dòng 2 = STT 1). Nói
  rõ điều này khi người dùng gọi theo STT.
- **Size guide** có thể bị dính chữ khi copy bảng (mất dấu phân cách). Dựng lại bảng từ size
  chart trong THÔNG TIN TỪ BRAND; số liệu phải khớp File (2), lệch thì ghi Conflict.
- Hướng dẫn điền từng cột: `file2-columns.md` (chỉ đọc khi nghi một cột điền sai chỗ).

## THÔNG TIN TỪ BRAND

= nội dung trang sản phẩm trên **website chính thức của hãng** (kèm trang size chart, chứng nhận,
hướng dẫn sử dụng/bảo quản/bảo hành của đúng sản phẩm) **và** trang sản phẩm trên
discount-equestrian.co.uk (Product URL). Không lấy trang đại lý khác. Đoạn brand trong About
**không** dùng nguồn này mà chỉ dùng cột Brand background.

Kinh nghiệm thực tế:

- **Trang DE chặn truy cập tự động (HTTP 403).** Đừng thử lại; xin người dùng mở trang, Ctrl+A,
  Ctrl+C và dán. Breadcrumb của trang DE (vd. *Body Protectors › Air Jackets and Air Vests*) là
  bằng chứng tốt để chốt loại sản phẩm.
- **Size chart của hãng thường là ảnh hoặc chạy bằng JavaScript**, máy không đọc được. Dùng cột Size
  guide của File (2) (người thu thập đã gõ lại từ ảnh), đánh dấu ✱ và xin ảnh chụp để đối chiếu.
- **Trang DE mâu thuẫn trang nhà sản xuất** (vùng bảo vệ, cách vệ sinh…): theo **nhà sản xuất**,
  ghi vào Conflict. Không dùng câu quảng cáo của trang DE ngụ ý dùng thi đấu, tên vận động viên, hay
  so sánh "fastest/among the best" không có nguồn hãng.
- Trang DE hay có ký tự "—": không chép kèm.
