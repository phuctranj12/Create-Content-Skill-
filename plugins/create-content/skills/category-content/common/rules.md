# Luật chung (Phần 1) — đọc một lần mỗi phiên

## Nguồn dữ liệu (7.1) — KHÔNG dùng nguồn ngoài bảng
| Loại thông tin | Nguồn |
| --- | --- |
| Spec, fit, chất liệu, màu, size, fact brand | **Website brand** (vd richardsonsports.com). KHÔNG lấy từ text đang có trên wholesalehats.com |
| Số SKU | Số hiển thị trên trang category tại wholesalehats.com |
| URL danh mục, anchor homepage, quan hệ cha–con, link bắt buộc | **FILE (2) internal linking** (script `links.py` tự giải) |
| SKU có thật trên site (để nêu ở FAQ) | FILE (3) Onpage_PDPs (tab PDPs), đối chiếu cột SKU. KHÔNG lấy spec/màu/size từ các cột Product specifications, Color, Size range của file này, KHÔNG dùng để xác định sản phẩm thuộc category nào |
| Định nghĩa loại mũ, performance, customization | `product-guideline.md` |
| Đặc điểm nêu trong "Shop by.../Other... to explore" | Nội dung hiện có trên chính trang category đó (mở nhanh trang để lấy) |

- Không bịa. Thiếu nguồn → ghi `[INPUT: cần nguồn]` / `[INPUT: cần ảnh size chart]`, báo người giao task.
- Suy luận (7.3): chỉ suy ra **lợi ích** từ đặc điểm vật lý có thật, dùng hedge (typically, generally, tends to); KHÔNG suy ra thông số/đặc điểm mới.
- SKU (7.4): hạn chế nêu tên model/SKU ở section chính (What defines/What is, Color, Size, Best customization): viết khái quát cho cả dải; chỉ nêu 1 sản phẩm cụ thể khi nó có điểm khác mà phần còn lại không có, và **tối đa 3 SKU** (Bước 5 QA: >3 thì xóa). FAQ được nêu SKU làm ví dụ/so sánh, nhưng SKU phải có trong FILE (3) hoặc trên site.
- Product guideline: các cụm "thường đi cùng…" chỉ là xu hướng, không dùng làm đặc điểm của trang nếu nguồn của trang không xác nhận. Tên danh mục + spec của trang thắng định nghĩa chung khi mâu thuẫn (vd Fitted Trucker Hats là trucker có fit dạng fitted). Realtree®/Mossy Oak® dùng định nghĩa Camo, kèm tên thương hiệu họa tiết.
- Size (điểm quan trọng số 3): Size options/Size chart **chia theo loại size trước** (OSFA/OSFM, S/M, L/XL, Youth, XXL, R-Flex…), rồi mới nói dòng nào dùng loại đó. Không chia theo tên model trước.
- Hai nguồn mâu thuẫn (vd trang wholesalehats.com và website brand) → theo website brand, ghi vào mục F, báo người giao task.

## Fact bank wholesalehats.com (5.1) — nguồn DUY NHẤT, không đổi số liệu
1. Trusted source for wholesale hats in the USA since 1979, nearly five decades of experience, loyal customer base of 10,000+.
2. 600+ styles across all major headwear categories.
3. Sourced directly from New Era, Flexfit, Imperial and 30+ other leading brands; 100% authentic, brand-verified merchandise.
4. Supplies both blank (bulk) and custom embroidered hats.
5. Orders from 24 units to tens of thousands; ready-to-ship inventory, reliable fulfillment.

Dùng (5.2): fact bank xuất hiện đầy đủ ở **đúng 1 section entity** mỗi trang. Thu hẹp: Fact 2 chỉ nói category nằm trong 600+ styles (không liệt kê category khác); Fact 3 chỉ nêu brand **thực sự liên quan** trang, không mặc định liệt kê New Era, Flexfit, Imperial; Fact 1, 4, 5 giữ nguyên ý nhưng **câu chữ khác nhau giữa các trang** (riêng câu "trusted source … since 1979 … 10,000+" giữ sát nguyên văn vì Bước 5 QA soát câu này). **Format theo STT (FILE 2): STT lẻ → văn xuôi; STT chẵn → bullet** (câu dẫn: "Trusted source for wholesale hats in the USA since 1979"). Luôn viết `wholesalehats.com` (thường), dùng "we".

## Giọng văn (6)
- American English; sentence case (chỉ hoa đầu câu + tên riêng brand/technology như Flexfit, PRO-FORMANCE®, Realtree®).
- Không em/en dash (— –); dùng phẩy/chấm/ngoặc.
- Không superlative tuyệt đối ("the best", "#1"); không opening chung chung ("Looking for..."); không giá/MOQ khác fact bank/thời gian giao.
- Chủ động, cụ thể; chủ–vị số nhiều khi tên category số nhiều ("Flexfit fitted hats offer"). Đa dạng cách mở câu giữa các trang, không chép cách diễn đạt từ bài đã triển khai.
- Hạn chế cấu trúc so sánh phủ định ("rather than", "instead of", "without") khi mô tả trực tiếp được. Thuật ngữ kỹ thuật giải thích ngắn ở lần đầu xuất hiện.
- Dùng "we" cho wholesalehats.com, ngôi thứ ba cho brand. Không nhồi từ "wholesale"; tính wholesale thể hiện qua bối cảnh đặt số lượng lớn, tổ chức mua, reorder.
- Tách đoạn khi đoạn quá dài.
- Độ dài tham chiếu ~700–1200 từ (gồm FAQ), không bắt buộc.
- H2 là mẫu ý, **phải paraphrase**, thể hiện tính wholesale; **giữ nguyên H1 gốc**, không link trong heading.

## Internal link (8)
- FILE (2) là nguồn DUY NHẤT; ô trống = không có link, không tự thay. Không tự tạo URL.
- Anchor homepage = cột "Anchor home page"; anchor category khác = tên danh mục hoặc biến thể chứa từ khóa; không anchor chung chung.
- Mỗi URL 1 lần; không link PDP, không link chính trang; link trong câu/dòng list có nghĩa; ≤2 link/đoạn; ≤1 link/câu.
- `links.py` xuất "link card" đủ bộ (homepage, product type, brand cha khác, và cha/anh em/con suy từ cây). URL thiếu trong CSV → flag, không bịa.

## Chức năng từng section (6.6) — mỗi section một việc
Intro: phạm vi + thông tin tổng quan cho người mua sỉ. What defines: cấu tạo, chất liệu, công nghệ. Color: màu, họa tiết, kiểu phối thực tế có trong category (không chỉ nói "nhiều màu"). Size: nhóm size + số đo chính xác, phân biệt size phổ biến với size chỉ có ở vài sản phẩm. Best for: nhu cầu + đặc điểm làm căn cứ. Customization: phương pháp theo chất liệu/bề mặt/cấu tạo, không khẳng định cho toàn category nếu chưa xác nhận. Supplier: năng lực wholesalehats.com. Other styles to explore: mỗi trang 1 câu phân biệt **kèm lý do/lợi ích ngắn**, không chỉ nêu thuật ngữ trần.

## Quy trình research brand (Phần 3.1)
- Lấy: định danh (công ty mẹ/quan hệ brand khác, năm thành lập, trụ sở), định vị (brand tự mô tả), sản phẩm chủ lực/công nghệ có tên riêng, color chart, size chart. Không lấy giá, khuyến mãi, chính sách bán hàng.
- Thứ tự tìm: About/Our Story/History → trang dòng sản phẩm/công nghệ → trang sản phẩm của model (T2) → color/size chart hoặc catalog PDF → footer/Contact. Trang con: search tên style trên website brand.
- Được dùng: fact cụ thể (năm, địa điểm, tên công ty, công nghệ, dòng sản phẩm); lời brand tự mô tả viết gián tiếp ("according to [Brand]…"). Phải bỏ: claim tuyệt đối ("the world's best", "leading … in the world"), giải thưởng/số liệu khách hàng không nêu cụ thể, thông tin suy từ hình ảnh hoặc tên sản phẩm mà website không viết thành chữ.
- Bảng fact brand (Fact · trích dẫn ngắn · URL) lập **một lần mỗi brand**, lưu kèm draft, dùng lại cho mọi trang cùng brand. Bảng đã có sẵn: `brands/` trong skill.

## Chống trùng lặp (9)
- Trang con không định nghĩa lại cái trang cha đã định nghĩa; trang cha không đi sâu chi tiết của con.
- Mỗi ý chỉ triển khai ở 1 section; section khác chỉ nhắc tên.
- Test hoán đổi: thay tên category vào câu; nếu câu vẫn đúng nguyên vẹn thì viết lại.

## Mâu thuẫn đã biết trong FILE (1) — làm theo cách dưới và ghi mục F, không tự quyết thêm
- Câu dẫn section entity dạng bullet: mục 5.2 ghi "Trusted source for **wholesale** hats…", Bước 5 QA ghi "trusted source for **bulk** hats…". Dùng "wholesale hats" theo fact bank 5.1 (trừ khi anchor homepage chứa chữ "bulk").
- T3 H2-5 "Top styles" yêu cầu chỉ liệt kê tên + link, không mô tả; luật 8.3 cấm liệt kê link trần. Theo template, báo mục F.
- Mục 6.1 ghi "không đề cập tên model/SKU", mục 7.4 và Bước 5 cho phép tối đa 3 (khi có điểm khác biệt). Theo 7.4.
- Phần 4 dẫn chiếu lệch số mục (H2 paraphrase là 6.3, độ dài là 6.5); Bước 3 ghi "Bước E" (thực tế là Bước 4); Bước 5 ghi "H1 (Tiêu đề - Tên sản phẩm - SKU)" là cách gọi của PDP, với category chỉ giữ nguyên H1 gốc.
- Ô "Link Homepage" trống ở dòng Product type cha nhưng 8.1 vẫn bắt buộc link Homepage → vẫn link.
