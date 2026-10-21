<!-- Sinh tự động bởi import_template.py từ PDP Template - RIDING BODY PROTECTOR.docx. Không sửa tay. -->

# Hướng dẫn thực hiện tạo content PDP Riding Body Protector cho writers

## Phần 1: Thiết lập thread (chỉ làm 1 lần)

**Bước 1:** Copy và paste toàn bộ nội dung **First Prompt – Riding Body Protector** vào Claude.

**Bước 2:** Download **File (1) – Riding Body Protector**, đặt tên file là "File (1)", rồi upload lên thread đã dán prompt ở bước 1.

**Bước 3:** Download [file data sản phẩm](https://docs.google.com/spreadsheets/d/1mUjPLdSiVnqOIZHV6I3SQa-VLwQV8YmPHLheKYnLPU4/edit?gid=0#gid=0), đặt tên file là "File (2)", rồi upload lên cùng thread. Trước khi upload, kiểm tra File (2) đã điền đủ các cột bắt buộc:

| Cột | Lưu ý khi điền |
| --- | --- |
| STT | Đánh số liên tục; các sản phẩm gần giống (cùng model) nên đặt liền nhau |
| Product Name, Product URL | Đúng như trên DE |
| **Differentiator** | Điểm khác biệt so với sản phẩm gần giống (ví dụ "Adults / Black"). Không có sản phẩm gần giống thì điền "/" |
| **Writing focus** | Body protector, Back protector, Air vest: chọn 1 trong 5 focus (Protection & certification / Fit & sizing / Freedom of movement / Comfort & breathability / Competition use). Accessory: chọn 1 trong 3 focus (Compatibility / Function / Ease of use). **Các sản phẩm cùng model phải chọn focus khác nhau** |
| Brand name, DE Brand URL | Theo Appendix 1 của File (1) |
| **Product Type**, Product type URL | Body protector / Back protector / Air vest / **Accessory**, kèm URL category tương ứng (Body protector và Accessory dùng URL category mẹ) |
| Rider, Colours, Size | Colours và Size ghi đúng như trên DE, kể cả size hết hàng |
| Size guide | Chỉ cần số liệu size chart của hãng |
| Body Protector Finder (Y/N) | Chỉ áp dụng cho Body protector |
| Certification & level | Ghi đúng như nhãn, **có năm** (2009 hay 2018). Phụ kiện chỉ điền khi hãng có công bố |
| **Brand background** | Đã xác minh từ website chính thức của hãng. **Ô trống thì AI sẽ dừng lại** |
| **Type-specific (Accessory): Compatibility** | Sản phẩm, model và size dùng được, **chỉ khi hãng xác nhận** |
| **Type-specific (Accessory): Specification** | Dung tích, kiểu lắp, kích thước, chất liệu, số lượng trong gói |
| Các cột thông tin sản phẩm và type-specific khác | Theo hướng dẫn trong header của File (2). Không áp dụng thì điền "/" |
| How to measure | Không bắt buộc, chỉ để tham khảo khi kiểm tra size chart. AI không dùng cột này để viết |

**Lưu ý:**

- Bước 1, 2, 3 chỉ làm 1 lần nếu dùng đúng 1 thread để sản xuất nội dung từ đầu đến cuối.
- **Làm sản phẩm theo đúng thứ tự STT trong cùng một thread.** Rule chống trùng wording và rule không lặp đoạn brand chỉ hoạt động khi AI nhìn thấy nội dung của 9 sản phẩm liền trước.
- Nếu phải mở thread mới: làm lại bước 1–3, rồi dán nội dung (bản text) của **9 sản phẩm liền trước** vào thread mới kèm câu: "Đây là nội dung 9 sản phẩm liền trước, dùng để đối chiếu chống trùng wording và đoạn brand. Không trả lời gì."

## Phần 2: Sản xuất nội dung cho từng sản phẩm

**Bước 4: Thu thập thông tin sản phẩm**

4.1. Tìm tên sản phẩm trên Google, vào đúng **trang sản phẩm trên website chính thức của hãng**, copy toàn bộ text mô tả sản phẩm. Nếu hãng có các trang liên quan đến đúng sản phẩm đó, copy thêm:

- Size chart (chỉ cần số liệu, **không cần copy hướng dẫn cách đo**)
- Thông tin chứng nhận (tên chuẩn, level, **năm**)
- Hướng dẫn sử dụng, bảo quản, bảo hành (đặc biệt với air vest)
- **Với phụ kiện:** danh sách sản phẩm và size tương thích, thông số (dung tích, kiểu lắp, kích thước), số lượng trong gói, hướng dẫn lắp

4.2. Mở đúng trang sản phẩm trên **discount-equestrian.co.uk** (Product URL trong File (2)), copy toàn bộ text mô tả sản phẩm.

*Ví dụ: với Racesafe Motion3 Adults Body Protector, copy từ trang sản phẩm Motion3 trên racesafe.co và trang https://www.discount-equestrian.co.uk/racesafe-motion-3-adults-body-protector.html*

**Bước 5: Gửi lệnh phân tích**

Nhập prompt theo đúng cú pháp:

Phân tích sản phẩm số [STT của sản phẩm trong File (2)] THÔNG TIN TỪ BRAND: [Paste toàn bộ nội dung copy ở bước 4, không cần ghi chú gì]

AI sẽ **chỉ trả về phần phân tích**, chưa viết nội dung.

**Bước 6: Kiểm tra phân tích và phản hồi AI**

Đọc kỹ 7 mục AI trả về và kiểm tra:

| Mục | Writer cần kiểm tra / quyết định |
| --- | --- |
| **1. Outline** | Đúng với loại sản phẩm: A Body protector / B Back protector / C Air vest / D Accessory |
| **2. Conflict** | Quyết định theo quy tắc bên dưới. Với phụ kiện, kiểm tra kỹ thông tin tương thích và thông số |
| **3. Heading bị loại** | Các heading bị loại đúng là do hãng không có thông tin |
| **4. Phiên bản About và {Role}** | **Bộ phiên bản:** Body protector và phụ kiện cho body protector (cover, shoulder protector, leg straps) → B · Back protector và phụ kiện cho back protector → K · Air vest và phụ kiện cho air vest (bình CO₂, lanyard, saddle strap, outer jacket) → A. **Phiên bản trong bộ:** B và A theo STT ÷ 3 (dư 1 → 1, dư 2 → 2, dư 0 → 3); K theo STT lẻ → K1, chẵn → K2. **{Role}:** Racesafe, Charles Owen, Champion, Airowear, Point Two → authorised stockist · Helite, Seaver, Freejump → official retailer · brand khác → không gắn danh xưng |
| **5. Brand background / URL brand** | Nếu AI báo trống: bổ sung vào File (2) hoặc gửi trực tiếp cho AI. Nếu brand chưa có URL: cung cấp URL trang brand trên site |
| **6. Sản phẩm gần giống** | AI xác định đúng sản phẩm gần giống. Nếu AI báo **Writing focus bị trùng**, chọn focus khác cho sản phẩm hiện tại và gửi lại cho AI |
| **7. Other features** | Feature được chọn có trong thông tin của hãng, không thuộc heading khác, không phải câu quảng cáo chung chung. Với phụ kiện, other feature chỉ nằm ở bullet, không có H2 riêng |

**Quy tắc xử lý conflict:**

- Thông tin bị lệch giữa File (2) và thông tin từ brand: **chọn thông tin từ brand.**
- Thông tin chỉ có trong File (2) mà brand không có: **bỏ.**
- Ngoại lệ, **luôn lấy từ File (2):** Product Type, Colours, Size, Body Protector Finder, Brand background, các URL, Differentiator, Writing focus.
- **Đặc biệt với chuẩn an toàn:** nếu năm chứng nhận (2009 hay 2018) hoặc level bị lệch, hoặc hãng không ghi rõ năm, **không tự quyết định**. Báo lại người phụ trách để xác minh với hãng hoặc nhà cung cấp trước khi viết.
- **Đặc biệt với phụ kiện:** nếu thông tin tương thích chỉ có ở File (2) hoặc trang DE mà hãng không xác nhận, **bỏ thông tin đó**. Không suy ra tương thích từ việc cùng brand.

Phản hồi AI cách xử lý từng conflict. Khi đã ổn, gửi lệnh:

Tạo nội dung

**Lưu ý:** nếu chỉ phản hồi về conflict mà chưa gửi "Tạo nội dung", AI chỉ cập nhật lại phần phân tích.

**Bước 7: Đọc và kiểm tra draft**

AI sẽ tạo draft và tự kiểm tra. Writer vẫn cần đọc lại, tập trung vào các lỗi AI hay mắc:

| Lỗi thường gặp | Cách kiểm tra |
| --- | --- |
| Dấu gạch dài (—) | Tìm ký tự "—" trong draft |
| Tên H2 sai | H2 phải đúng như File (1), **không chứa tên sản phẩm** (ví dụ "Sizing & Fit", không phải "Motion3 Sizing & Fit") |
| Bullet sai dạng | Bullet trong Short phải là "Nhãn: nội dung", nội dung sau dấu ":" ngắn gọn, khoảng 4–12 từ |
| Overlap giữa các H2 | Mỗi thông tin chỉ nằm ở một H2 (ví dụ khoá kéo chỉ ở Ease of Use, segment chỉ ở Freedom of Movement). Không có câu như "as mentioned above" |
| Còn hướng dẫn cách đo | Không được có đoạn hướng dẫn đo chest, over shoulder, back length. Size chart chỉ có số liệu |
| Bịa feature | Các từ như "lightweight", "multi-density", "breathable" phải có trong thông tin của hãng |
| Sai thông tin an toàn | Chỉ BETA 2018 Level 3 mới được nói dùng thi đấu. Back protector phải ghi rõ chỉ bảo vệ lưng, không dùng cho XC. H2 Riding Use Cases kết thúc bằng câu "Always check the current rules of your governing body before competing." |
| **Phụ kiện: tương thích không có nguồn** | Mọi sản phẩm, model, size được ghi là tương thích phải có trong thông tin của hãng |
| **Phụ kiện: sai cấu trúc** | Không có H2 Other Highlights; đúng bộ phiên bản About theo loại sản phẩm mà phụ kiện phục vụ |
| Đoạn About rời rạc | Đoạn brand kết thúc bằng câu gắn với sản phẩm; đoạn discount-equestrian.co.uk mở đầu bằng "The [Product] is supplied by discount-equestrian.co.uk…" |
| Sai danh xưng | "authorised stockist" hoặc "official retailer" chỉ dùng đúng theo bảng {Role}; các phần khác của đoạn About giữ nguyên như Appendix 2 |
| Lặp đoạn brand | So với sản phẩm cùng hãng trong 9 sản phẩm liền trước: không có câu giống hệt |
| Trùng wording với sản phẩm gần giống | Differentiator có trong Meta Description và câu intro; nội dung đi đúng Writing focus; không có câu giống hệt với bản gần giống |
| Other Highlights sai | Với Outline A, B, C: H2 Other Highlights chỉ xuất hiện khi có từ 2 feature hợp lệ trở lên |

**Bước 8: Kiểm tra internal link**

Link **chỉ nằm ở Short description và phần About**, mỗi URL **chỉ một lần**. Số link theo từng loại:

| Loại sản phẩm | Link cần có |
| --- | --- |
| Body protector | Category mẹ (ở chữ "body protector" trong intro) + brand |
| Back protector | Category type + category mẹ + brand |
| Air vest | Category type + category mẹ + brand |
| **Accessory** | Category mẹ (trong intro) + brand |

| Link | URL |
| --- | --- |
| Category mẹ | https://www.discount-equestrian.co.uk/rider/riding-wear/body-protectors.html |
| Category type: Back protector | https://www.discount-equestrian.co.uk/rider/riding-wear/body-protectors/back-protectors.html |
| Category type: Air vest | https://www.discount-equestrian.co.uk/rider/riding-wear/body-protectors/air-jackets-and-air-vests.html |
| Brand | Theo cột DE Brand URL trong File (2) hoặc Appendix 1 của File (1); đặt ở tên brand lần nhắc đầu tiên trong phần About |

Ngoài ra, đoạn About discount-equestrian.co.uk đã có sẵn link về trang chủ.

Click thử từng link để chắc chắn trang mở được. Nếu sai, yêu cầu AI sửa lại.

**Bước 9:** Sau khi draft không còn sai sót, nhập prompt:

Tạo bản HTML

**Bước 10:** Copy bản text và bản HTML ra file doc, đặt ở 2 tab riêng biệt.

Cuối cùng, tạo docs tại [Folder Riding Body Protector](https://drive.google.com/drive/folders/1ePdtFeSB0EmEr9_vs-fSQDKyYhSKUMqG?usp=sharing) và gắn link tại [DE | CONTENT | ONPAGE | RIDING BODY PROTECTORS](https://docs.google.com/spreadsheets/d/1mUjPLdSiVnqOIZHV6I3SQa-VLwQV8YmPHLheKYnLPU4/edit?gid=0#gid=0&range=I:I)
