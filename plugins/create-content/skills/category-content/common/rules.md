# Luật chung (Phần 1) — đọc một lần mỗi phiên

## Nguồn dữ liệu (7.1) — KHÔNG dùng nguồn ngoài bảng
| Loại thông tin | Nguồn |
| --- | --- |
| Spec, fit, chất liệu, màu, size, fact brand | **Website brand** (vd richardsonsports.com). KHÔNG lấy từ text đang có trên wholesalehats.com |
| Số SKU | Số hiển thị trên trang category tại wholesalehats.com |
| URL danh mục, anchor homepage, quan hệ cha–con, link bắt buộc | **FILE (2) internal linking** (script `links.py` tự giải) |
| SKU có thật trên site (để nêu ở FAQ) | FILE (3) Onpage_PDPs, đối chiếu cột SKU |
| Định nghĩa loại mũ, performance, customization | `product-guideline.md` |
| Đặc điểm nêu trong "Shop by.../Other... to explore" | Nội dung hiện có trên chính trang category đó (mở nhanh trang để lấy) |

- Không bịa. Thiếu nguồn → ghi `[INPUT: cần nguồn]` / `[INPUT: cần ảnh size chart]`, báo người giao task.
- Suy luận (7.3): chỉ suy ra **lợi ích** từ đặc điểm vật lý có thật, dùng hedge (typically, generally, tends to); KHÔNG suy ra thông số/đặc điểm mới.
- SKU (7.4): KHÔNG nêu tên model/SKU ở section chính (What defines, Color, Size, Best, Customization). FAQ được nêu tối đa khi SKU xác nhận có trên wholesalehats.com (FILE 3).

## Fact bank wholesalehats.com (5.1) — nguồn DUY NHẤT, không đổi số liệu
1. Trusted source for wholesale hats in the USA since 1979, nearly five decades of experience, loyal customer base of 10,000+.
2. 600+ styles across all major headwear categories.
3. Sourced directly from New Era, Flexfit, Imperial and 30+ other leading brands; 100% authentic, brand-verified merchandise.
4. Supplies both blank (bulk) and custom embroidered hats.
5. Orders from 24 units to tens of thousands; ready-to-ship inventory, reliable fulfillment.

Dùng (5.2): fact bank xuất hiện đầy đủ ở **đúng 1 section entity** mỗi trang. Thu hẹp: Fact 2 chỉ nói category nằm trong 600+ styles; Fact 3 chỉ nêu brand liên quan trang. **Format theo STT (FILE 2): STT lẻ → văn xuôi; STT chẵn → bullet** (câu dẫn: "Trusted source for wholesale hats in the USA since 1979"). Luôn viết `wholesalehats.com` (thường), dùng "we".

## Giọng văn (6)
- American English; sentence case (chỉ hoa đầu câu + tên riêng brand/technology như Flexfit, PRO-FORMANCE®, Realtree®).
- Không em/en dash (— –); dùng phẩy/chấm/ngoặc.
- Không superlative tuyệt đối ("the best", "#1"); không opening chung chung ("Looking for..."); không giá/MOQ khác fact bank/thời gian giao.
- Chủ động, cụ thể; chủ–vị số nhiều khi tên category số nhiều. Đa dạng cách mở câu giữa các trang.
- Độ dài tham chiếu ~700–1200 từ (gồm FAQ), không bắt buộc.
- H2 là mẫu ý, **phải paraphrase**, thể hiện tính wholesale; **giữ nguyên H1 gốc**, không link trong heading.

## Internal link (8)
- FILE (2) là nguồn DUY NHẤT; ô trống = không có link, không tự thay. Không tự tạo URL.
- Anchor homepage = cột "Anchor home page"; anchor category khác = tên danh mục hoặc biến thể chứa từ khóa; không anchor chung chung.
- Mỗi URL 1 lần; không link PDP, không link chính trang; link trong câu/dòng list có nghĩa; ≤2 link/đoạn; ≤1 link/câu.
- `links.py` xuất "link card" đủ bộ (homepage, product type, brand cha khác, và cha/anh em/con suy từ cây). URL thiếu trong CSV → flag, không bịa.

## Chống trùng lặp (9)
- Trang con không định nghĩa lại cái trang cha đã định nghĩa; trang cha không đi sâu chi tiết của con.
- Mỗi ý chỉ triển khai ở 1 section; section khác chỉ nhắc tên.
- Test hoán đổi: thay tên category vào câu; nếu câu vẫn đúng nguyên vẹn thì viết lại.
