# Trước khi chạy: skill cần gì từ bạn

Skill **chỉ viết điều có trong File (2)**, không tự lấy đủ dữ liệu từ link:

- **Trang discount-equestrian.co.uk chặn máy truy cập** (lỗi 403). Màu, size, range phải nằm sẵn trong
  File (2).
- **Trang brand**: máy thường chỉ đọc được bản tóm tắt, không có nguyên văn. Có trang còn chặn, chỉ
  hiện nội dung bằng JavaScript, hoặc để size chart dạng ảnh/PDF. Tóm tắt có thể sai lệch, nên không
  dùng làm nguồn viết.
- **Ô Excel**: chỉ đọc chữ. Link ẩn sau chữ, comment, màu tô, ảnh đều bị bỏ qua. Ghi URL dạng chữ đầy đủ.

## Cách bổ sung: cột `Nội dung trang web (dán)`

1. Thêm **một cột cuối cùng** vào File (2), tiêu đề đúng là `Nội dung trang web (dán)`.
2. Với **mọi** sản phẩm (kể cả khi các cột tính năng đã có dữ liệu): mở trang bằng trình duyệt,
   copy rồi dán vào ô của dòng đó. Nên dán các trang sau:
   - trang sản phẩm trên web brand: mô tả, tính năng, thông số;
   - trang sản phẩm trên DE;
   - hướng dẫn chọn size / fitting guide của brand;
   - hướng dẫn bảo quản / care & lifespan của brand.

   Bài mẫu đã duyệt có những câu như "round up if between two sizes", "lasts three to five years"
   chỉ lấy được từ các trang này. Thiếu trang nào thì skill phải bỏ ý đó.
3. **Một ô Excel chứa tối đa 32.767 ký tự**; dán dài hơn sẽ bị cắt mất phần cuối. Copy cả trang
   bằng Ctrl+A thường lẫn menu, footer, sản phẩm liên quan: chỉ bôi đen phần nội dung. Hướng dẫn
   chọn size và bảo quản dùng chung cho cả brand thì chỉ cần dán đoạn liên quan.
4. Mỗi trang dán nên bắt đầu bằng một dòng URL (để biết câu nào lấy từ trang nào), ví dụ:

   ```
   https://www.charlesowen.com/products/yr8
   Fully trimmed in microfibre suede, four discreet ventilation holes ...
   ```

   Nhiều trang thì dán nối tiếp, mỗi trang mở bằng dòng URL của nó.
5. Không cần sửa câu chữ. Skill tự lọc ý, nhưng chỉ dùng những gì có trong ô; con số nào trong bài
   không có trong File (2) hoặc ô này đều bị checker báo.

## Ô nào phải đúng định dạng

| Cột | Định dạng | Vì sao |
| --- | --- | --- |
| Colours sold | Tên màu đúng như trang DE, cách nhau bằng `;` | Bài liệt kê đúng các màu này |
| Sizes sold | `52CM; 53CM; 59CM ROUND` (size round ghi rõ `ROUND`), có quy đổi UK thì ghi kèm `52 = 6 ⅜` | Câu Size chỉ nêu size DE bán |
| Children's sizes, Shared care guide | `Y` hoặc `N` | Chọn đoạn giới thiệu DE và link |
| Product type | Đúng một tên template của ngành | Sai tên thì skill dừng lại hỏi |
| Compatible hats / Compatible product URL | Mẫu nào có URL thì phải có trong danh sách, và ngược lại | Lệch thì bài nói sai số mẫu tương thích |

Không dùng dấu gạch dài (— –) trong ô.

## Sau khi skill viết xong

Mở `ban-text.html`, bấm Ctrl+A, copy rồi dán vào Google Doc. **Không gõ lại bằng tay**: Google Docs
tự đổi link thành `http://…`, và sửa tay dễ làm mất chữ. Dán xong, gửi
**"kiểm tra doc <link> sản phẩm số N"** để skill kiểm tra lại trên đúng bản trong doc.
