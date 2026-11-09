# Mẫu bản phân tích (Phần 5, Bước 2) và đầu ra mỗi draft

Trả về khối dưới đây cho **mỗi trang**, theo thứ tự danh sách, rồi **dừng chờ**. Chỉ viết bài khi người
dùng gửi "Tạo nội dung" (hoặc đã nói rõ "viết luôn" / "tự chạy"). Yêu cầu sửa một trang thì chỉ cập nhật
bản phân tích của trang đó.

```
=== TRANG [số]/[tổng]: [Tên danh mục] ===
URL: [...]
A. RESEARCH
A1. Spec
| Đặc điểm | Giá trị | URL nguồn |
(Số SKU: lấy từ trang category trên wholesalehats.com, không đối chiếu nguồn khác, không hỏi lại)
A2. Màu sắc (chỉ từ các trang brand đã mở để tra spec; swatch ảnh không đọc được tên thì ghi nhóm màu + kiểu phối, không flag)
- Màu cốt lõi (vài ví dụ): [...]
- Kiểu phối: [...]
- Họa tiết: [...]
A3. Size (T1 chỉ cần hệ fit; T2 cần hệ fit + size + số đo; không có dạng chữ → [INPUT: cần ảnh size chart])
| Hệ fit / size / số đo | URL nguồn |
A4. Bảng fact brand (chỉ Brand cha, Brand con)
| Fact | Trích dẫn ngắn | URL nguồn |
(hoặc: "Dùng lại bảng fact brand ở trang [số]" / "Dùng brands/<brand>.md")
B. TEMPLATE
- Template: T[số] – [tên]
- Nhánh / dạng trang: [...] (Brand con: Model hay Dải sản phẩm do người giao task quyết; tự suy thì ghi rõ ở F)
- STT: [số] → Format section entity: văn xuôi / bullet
C. ĐẶC ĐIỂM DÙNG Ở H2-1
| Đặc điểm | Nguồn (A1 / A4 / Product guideline) |
D. SECTION
| H2 | Dùng / Bỏ | Lý do (nếu bỏ) |
E. LINK (copy từ link card của links.py)
| URL | Anchor dự kiến | Đặt ở H2 |
F. LƯU Ý
- [Mâu thuẫn giữa các nguồn, thông tin thiếu, điểm cần người viết quyết định. Không có thì ghi "Không có"]
```

Cuối bản phân tích của cả loạt: gom mọi `[INPUT]` thành **một** danh sách để người viết bổ sung một lần.

## Đầu ra của mỗi draft (Phần 5, Bước 2 VIẾT)

- Dòng đầu (trong báo cáo, không đưa vào doc): `TRANG [số]/[tổng]: [Tên danh mục]`.
- Bài viết tiếng Anh Mỹ; `# H1` giữ nguyên H1 gốc; heading `##`; link `[anchor](URL)`.
- Cuối mỗi draft (trong báo cáo, không đưa vào doc): template đã dùng; format section entity; danh sách
  link đã đặt kèm vị trí; số từ.
- Kèm báo cáo QA theo Phần 4 cho từng trang: Có/Không từng mục, lý do nếu "Không".
