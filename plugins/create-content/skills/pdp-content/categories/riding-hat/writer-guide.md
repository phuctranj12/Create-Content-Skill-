<!-- Tách tự động từ "BSS Digiworks_Tài liệu tham khảo cho bài test.docx". -->

# Hướng dẫn tạo content PDP category Riding Hat cho writer

## PHẦN 1: SETUP THREAD (làm 1 lần cho mỗi thread)

Bước 1: Mở một thread mới trên Claude. Copy toàn bộ First prompt và paste vào thread.
Bước 2: Download template, đặt tên file là "File (1)" rồi upload lên thread.
Bước 3: Download bảng dữ liệu sản phẩm, đặt tên file là "File (2)" rồi upload lên thread.
Sau bước 3, AI sẽ trả lời xác nhận. Bạn kiểm tra AI đã:
Xác nhận nhận đủ 2 file.
Xác nhận thấy Template chung, 4 template riêng và Phụ lục A, B, C trong File (1).
Nêu đúng tổng số sản phẩm trong File (2).
Xác nhận File (2) có đủ các trường chung và các nhóm trường theo template.
Nếu AI báo File (2) thiếu trường, hoặc Phụ lục A hay Phụ lục B đã quá 12 tháng chưa kiểm tra, dừng lại và báo content lead trước khi viết.
Lưu ý:
Bước 1, 2, 3 chỉ làm 1 lần cho mỗi thread.
Mỗi thread chỉ nên làm khoảng 10 đến 15 sản phẩm. Thread càng dài, AI càng dễ quên quy tắc. Khi đến giới hạn, mở thread mới và làm lại Bước 1 đến 3.
Ưu tiên làm các sản phẩm cùng nhóm Duplicate Risk trong cùng một thread, vì AI chỉ tránh trùng được với những bài nó nhìn thấy trong thread. Với nhóm lớn phải tách qua nhiều thread (ví dụ nhóm uvex exxeed có 15 sản phẩm), bạn tự so với các bài đã viết ở thread trước tại Bước 7.4.

## PHẦN 2: TẠO NỘI DUNG CHO TỪNG SẢN PHẨM

Mỗi sản phẩm đi qua 3 câu lệnh theo đúng thứ tự: "Đối chiếu dữ liệu", sau đó "Viết bài", cuối cùng "Tạo bản HTML". Không gộp hay bỏ qua câu lệnh nào.

### Bước 4: Thu thập thông tin sản phẩm từ brand

Mở link ở trường Brand product URL trong File (2). Nếu trường này trống, copy tên sản phẩm, tìm trên Google, vào đúng trang sản phẩm trên website chính thức của brand.
Copy toàn bộ text: mô tả, thông số kỹ thuật, tiêu chuẩn an toàn, trọng lượng, size chart, hướng dẫn chăm sóc, compatibility (nếu có).
Nếu không tìm được trang sản phẩm trên website chính thức của brand, ở Bước 5 ghi: "Không có trang sản phẩm trên website brand." Không lấy thông tin từ website của shop khác.
Dữ liệu trong File (2) là THÔNG TIN TỪ DE, do content lead collect nên có thể sai. AI sẽ tự lấy theo số No. và đối chiếu với thông tin brand bạn cung cấp, bạn không cần copy.
Ví dụ: với sản phẩm uvex exxeed Glow (No. 98), bạn chỉ cần copy text từ trang sản phẩm trên uvex-sports.com.

### Bước 5: Nhập prompt đối chiếu dữ liệu

Copy mẫu dưới đây, thay phần trong ngoặc vuông, rồi gửi cho AI:
Đối chiếu dữ liệu sản phẩm số [No. của sản phẩm trong File 2].
LƯU Ý: Ở bước này bạn CHƯA viết bất kỳ nội dung nào (không viết H1, Meta title, Meta Description, Short description, Long description hay đoạn mẫu). Chỉ thực hiện GIAI ĐOẠN 1 và trả về BÁO CÁO ĐỐI CHIẾU theo First prompt, sau đó dừng lại chờ tôi phản hồi.
THÔNG TIN TỪ BRAND: [Paste text ở bước 4, hoặc ghi "Không có trang sản phẩm trên website brand."]
NHẮC LẠI: Chỉ trả về BÁO CÁO ĐỐI CHIẾU. Chưa viết bài. Chỉ viết bài khi tôi gửi câu lệnh "Viết bài".
Chỉ thay số No. và paste khối THÔNG TIN TỪ BRAND, giữ nguyên các dòng còn lại.
Lưu ý: Nếu AI vẫn viết bài (rất hiếm khi xảy ra), không dùng bản nháp đó. Nhắn tiếp: "Bỏ bản nháp vừa rồi. Trả về BÁO CÁO ĐỐI CHIẾU." rồi tiếp tục Bước 6 như bình thường.

### Bước 6: Phản hồi BÁO CÁO ĐỐI CHIẾU

Đây là bước quan trọng nhất của quy trình, cần đọc kỹ từng mục. Báo cáo gồm dòng Template ở đầu và 4 mục.
Dòng đầu báo cáo: Template
AI lấy template theo trường Product type trong File (2) và kiểm tra chéo với thông tin brand. Bạn kiểm tra template có đúng không:
Riding Hat: mũ, helmet, jockey skull.
Hat Silks & Covers: hat silk, hat cover, skull cap cover.
Liners & Parts: liner, padding, headband, panel, peak set, fitting kit.
Helmet Accessories: phụ kiện gắn trên mũ hoặc dùng cùng mũ (intercom, micro, đèn, sticker...).
Nếu AI báo "không khớp", hoặc bạn thấy template sai, trả lời "Dùng template [tên]" và ghi lại để báo content lead sửa trường Product type.
Mục 1: Bảng dữ liệu sẽ dùng
Rà nhanh bảng, đặc biệt các dòng sau:
Type (dòng đầu tiên): với Riding Hat, phải là một trong ba dáng peaked, wide peak, jockey skull; "adjustable" chỉ có khi brand xác nhận hệ thống chỉnh fit. Với các template khác, phải đúng loại sản phẩm.
Tiêu chuẩn an toàn (Riding Hat): ghi theo cách brand ghi, kèm dòng B1 tương ứng. Quality mark chỉ có khi brand nêu.
Trọng lượng: chỉ được lấy từ brand.
Size và màu: khớp với trường Colours sold và Sizes sold trong File (2).
Cột Nguồn: thông tin sản phẩm phải có nguồn là brand. Chỉ các trường ngoại lệ (màu, size, size trẻ em, Brand info...) được có nguồn là File (2).
Cột H2: mỗi thông tin chỉ được gán vào một H2. Thông tin dễ bị gán nhầm: shell và construction phải ở Design details (không ở Safety); cách chỉnh harness ở Sizing & fit; liner tháo rời/giặt được ở Comfort features; replacement parts ở Accessories & compatibility.
Mục 2: Conflict
Conflict là những điểm mà THÔNG TIN TỪ BRAND và dữ liệu trong File (2) ghi khác nhau. Nguyên tắc:
Thông tin về sản phẩm (thông số kỹ thuật, tiêu chuẩn an toàn, chất liệu, tính năng, compatibility, cách chăm sóc...): luôn dùng brand.
Thông tin về tình trạng đang bán trên DE (màu, size, size trẻ em): dùng File (2), vì brand không có các thông tin này. Brand chỉ dùng để kiểm tra tên màu và quy đổi size sang cm.
Ví dụ: brand ghi mũ có 5 màu (Black, Navy, Grey, Brown, Pink), nhưng trường Colours sold trong File (2) chỉ có Black và Navy. Trong trường hợp này, bài chỉ viết Black và Navy.
Loại thông tin bị lệch
Chọn nguồn nào
Thông số kỹ thuật (tiêu chuẩn, chất liệu, ventilation, lining, fit system, compatibility...)
THÔNG TIN TỪ BRAND
Trọng lượng
Chỉ THÔNG TIN TỪ BRAND. Brand không ghi thì bỏ.
Màu sắc, size đang bán, size trẻ em
File (2)
Mỗi conflict cũng là một lỗi dữ liệu trong File (2). Ghi lại để báo content lead sửa (Bước 11).
Mục 3: Sẽ bỏ
Gồm thông tin chỉ có trong File (2) mà brand không có, và các mục optional trong template không có dữ liệu. Các thông tin này mặc định bị bỏ.
Nếu bạn thấy một thông tin bị bỏ nhưng tìm được trên một trang chính thức khác của brand (ví dụ trang công nghệ, trang FAQ của brand), paste thêm text từ trang đó vào phản hồi. Thông tin đó sẽ được tính là có từ brand.
Mục 4: Cần xử lý trước khi viết
AI báo
Bạn xử lý
Product type trống hoặc không khớp với thông tin brand
Trả lời AI: "Dùng template [tên]". Ghi lại để báo content lead sửa File (2). Nếu sản phẩm không thuộc template nào, dừng và báo content lead.
Không có trang sản phẩm của brand
Trả lời AI: "Xác nhận không có trang brand, xử lý theo quy tắc". AI sẽ dùng dữ liệu File (2), trừ tiêu chuẩn an toàn, quality mark và trọng lượng.
Không xác định được dáng mũ (Riding Hat)
Xem ảnh sản phẩm trên trang brand hoặc DE, rồi trả lời AI dáng mũ đúng (peaked, wide peak hoặc jockey skull).
Tiêu chuẩn an toàn không khớp Phụ lục B1
Trả lời AI: "Bỏ tiêu chuẩn này". Ghi lại để báo content lead.
Tiêu chuẩn không có quality mark, hoặc chỉ khớp AS/NZS 3838
Trả lời AI: "Không viết Competition suitability".
Brand không xác nhận compatibility (phụ kiện)
Tìm thêm trên trang chính thức của brand và paste vào. Nếu không có, trả lời AI: "Bỏ phần compatibility".
Brand info thiếu hoặc quá ít
Báo content lead bổ sung trường Brand info trong File (2). Nếu cần làm tiếp, trả lời AI: "Dùng lại fact, diễn đạt khác".
Writing focus không được nguồn xác nhận
Trả lời AI: "Bỏ Writing focus này, chọn điểm khác biệt khác có trong bảng dữ liệu". Ghi lại để báo content lead.
Link cần dùng nhưng chưa có trong Phụ lục A
Trả lời AI: "Không gắn link này". Ghi lại để báo content lead.
Shared care guide = Y nhưng chưa có URL care guide
Không cần trả lời. Ghi lại để báo content lead (đề xuất chủ đề blog).
Sản phẩm Charles Owen chưa xác định được ngày sản xuất
Trả lời AI: "Không xác định được, không viết made in UK hay handmade in Britain".
Cuối báo cáo, kiểm tra:
DE variant: đúng quy tắc chọn variant.
E: Charles Owen, EQx hoặc evoke, và số No. lẻ.
F: Children's sizes = Y.
C: Riding Hat dáng jockey skull.
A, B, D: các trường hợp còn lại, theo số No. chia 3 dư 1, dư 2, chia hết.
Tổ chức thi đấu (Riding Hat): chỉ British Eventing, The Pony Club, British Riding Clubs, BHS, British Showjumping.
Danh sách internal link: xem Bước 8.
Duplicate Risk: AI đã nhận diện đúng các sản phẩm liên quan đã viết trong thread và Writing focus.
Brand paragraph: các fact và cách mở đầu khác với brand paragraph cùng brand đã viết trong thread.
Mẫu phản hồi:
Template: Đồng ý. Mục 1: Đồng ý. Mục 2: Đồng ý. Mục 3: Đồng ý. Mục 4: Bỏ tiêu chuẩn [tên]. Không gắn link [tên]. Viết bài.
Lưu ý: Câu lệnh "Viết bài" là tín hiệu duy nhất để AI bắt đầu viết. Nếu bạn cần trao đổi thêm với AI (paste thêm nguồn, hỏi lại một conflict), chưa ghi "Viết bài" cho đến khi mọi mục đã được chốt.

### Bước 7: Kiểm tra draft

Sau khi nhận câu lệnh "Viết bài", AI sẽ viết draft gồm 5 khối (H1, Meta title, Meta Description, Short description, Long description) kèm CHECKLIST QA.
7.1. Kiểm tra CHECKLIST QA: tất cả các dòng phải là "Đạt". Nếu còn dòng "Không đạt", yêu cầu AI sửa.
7.2. Kiểm tra draft đúng format template (File 1)
Mở File (1), đến đúng template riêng AI đang dùng để so:
H1 và Meta title: đúng format ở Template chung C1, C2, đúng type word của template riêng.
Short description: không có heading; đủ 3 phần theo đúng thứ tự (câu mở đầu, Key features, navigation bridge).
Câu mở đầu: đúng frame của template riêng. Với Riding Hat, câu mở đầu chỉ dùng chữ "riding hat", không có dáng mũ.
Key features: bullet đầu tiên là Type; các bullet tiếp theo đúng nhãn và đúng thứ tự trong template riêng; mỗi bullet theo format "Label: spec, benefit".
Long description: H2 đúng tên và đúng thứ tự trong template riêng; có đủ các mục (always included); các mục (optional) không có dữ liệu đã được bỏ.
Bên trong section: nhóm nhỏ là H3; Safety standards & certification và Specifications viết dạng bullet; các ý còn lại là đoạn ngắn mở đầu bằng nhãn in đậm.
About the brand: đúng 2 đoạn văn, không có H3.
Giới hạn độ dài: các ý có ghi "max ... sentences" không vượt số câu cho phép.
7.3. Kiểm tra draft đúng thông tin đã chốt ở Bước 6
Mở lại BÁO CÁO ĐỐI CHIẾU và phản hồi của bạn ở Bước 6 để so:
Thông số: mọi thông số trong draft đều có trong bảng dữ liệu ở Mục 1, và đúng giá trị đã chốt.
Conflict: mỗi conflict ở Mục 2 được viết theo đúng nguồn đã chốt.
Thông tin đã bỏ: không còn thông tin nào đã bị bỏ ở Mục 3 và Mục 4.
Màu và size: khớp với trường Colours sold và Sizes sold.
Tổ chức thi đấu: chỉ nêu đúng các tổ chức đã liệt kê ở cuối báo cáo.
Writing focus: có trong câu mở đầu và Meta Description (nếu sản phẩm có Duplicate Risk).
Đoạn discount-equestrian.co.uk: đúng variant đã chốt, giữ nguyên văn như trong Phụ lục C, chỉ thay tên brand và loại sản phẩm.
7.4. Tự kiểm tra các lỗi AI hay mắc (AI vẫn có thể sai dù checklist ghi Đạt):
Dấu gạch ngang dài (— hoặc –): dùng Ctrl+F tìm trong draft.
Overlap giữa các H2: dùng Ctrl+F tìm các từ khoá dễ lặp (harness, liner, shell, EPS, replacement, silk, compatible) và kiểm tra mỗi thông tin chỉ nằm trong 1 H2.
Lặp ý giữa Short và Long description: Long description nhắc lại nguyên câu đã có ở Short description; Meta Description trùng câu mở đầu.
Trùng lặp với sản phẩm khác: so câu mở đầu, Meta Description và Key features với các sản phẩm cùng nhóm Duplicate Risk. AI chỉ tự so được với các bài trong thread hiện tại; nếu có sản phẩm cùng nhóm đã viết ở thread trước, bạn mở file lưu của sản phẩm đó (Bước 10) để so.
Brand paragraph: so với brand paragraph cùng brand đã viết trong thread, không được trùng câu hoặc cụm dài.
Độ dài Meta title: không quá 60 ký tự (tính cả " | Discount Equestrian").
Độ dài Meta Description: dán vào một công cụ đếm ký tự, phải từ 140 đến 155 ký tự.
Care & maintenance: không quá 80 từ; với Riding Hat phải có câu thay mũ sau va chạm.
Tên website: trong nội dung phải là "discount-equestrian.co.uk". Ngoại lệ duy nhất là phần đuôi " | Discount Equestrian" trong Meta title.
Sản phẩm Charles Owen: không có "made in the UK" hay "handmade in Britain", trừ khi đã xác nhận ở Bước 6.
Competition suitability: chỉ được nhắc British Eventing, Pony Club, British Riding Clubs, BHS và British Showjumping. Không được nhắc British Dressage.
Phụ kiện (Hat Silks & Covers, Liners & Parts, Helmet Accessories): không có câu nói sản phẩm giúp an toàn hơn, trừ khi brand nêu rõ; không nhắc tiêu chuẩn an toàn.
Nếu phát hiện lỗi, nhắn AI sửa cụ thể. Ví dụ: "Sửa lại: đoạn Ventilation đang lặp lại spec ở Short description, viết lại để bổ sung chi tiết mới."

### Bước 8: Kiểm tra internal link

So từng link trong draft với Phụ lục A trong File (1). Các vị trí link chính:
Riding Hat:
"riding hat" trong câu mở đầu Short description → Category Riding Hats & Helmets.
"jockey skull" trong bullet Type → Subcategory Jockey Skull Caps (chỉ khi mũ là jockey skull).
Cụm nói về tiêu chuẩn an toàn trong navigation bridge → Bài blog Riding hat safety standards.
"children's sizes" → Children's Riding Hats (chỉ khi mũ có size trẻ em).
"sparkly" → Sparkly Riding Hats (chỉ khi finish là sparkly hoặc glitter theo brand).
"custom design" → Custom Design Riding Hats (chỉ khi mũ có customisation theo brand).
"hat silks" trong Accessories & compatibility → Hat Silks & Covers (chỉ với jockey skull).
Hat Silks & Covers:
"hat silk" hoặc "hat cover" trong câu mở đầu → Hat Silks & Covers.
Hat Silks & Covers, Liners & Parts, Helmet Accessories:
Tên mũ tương thích trong Compatibility → Product URL của mũ đó trong File (2), chỉ với các mũ ghi ở trường Compatible product No.
Mọi template:
Tên brand ở lần nhắc đầu tiên trong About the brand → trang brand trong Phụ lục A3 (chỉ khi brand có trong A3).
Cụm nói về dung dịch vệ sinh hoặc khử mùi → Clothing Care (chỉ khi phần care có nhắc tới).
Không có link tới Riding Hats for Beginners và Premium Riding Hats.
Kiểm tra 3 điều:
URL đúng với Phụ lục A hoặc File (2) (copy URL trong draft ra so, không đoán).
Link nằm đúng vị trí và đủ điều kiện.
Không có URL nào bị gắn 2 lần.
Hiện tại chưa có care guide, nên phần Care & maintenance không được có link care guide. Nếu thấy link sai, yêu cầu AI sửa lại.

### Bước 9: Tạo bản HTML

Khi draft đã ổn, nhập prompt:
Tạo bản HTML
AI sẽ trả về 3 code block (H1, Short description, Long description), cùng Meta title và Meta Description dạng text thường.

### Bước 10: Lưu nội dung

Tạo 1 file doc cho mỗi sản phẩm, đặt tên theo dạng [No.] - [Tên sản phẩm]. File gồm 2 tab:
Tab 1 (Text): H1, Meta title, Meta Description, Short description, Long description (bản draft đã duyệt).
Tab 2 (HTML): Meta title và Meta Description (text thường), cùng 3 code block HTML.
Sau cùng, tạo link doc. của draft trong [Folder Riding Hat - PDPs](https://drive.google.com/drive/folders/1wrq_cc212XSywbmgGLK7JXj0G4l3D3F5?usp=drive_link) và điền link vào [File DE | CONTENT | ONPAGE | RIDING HATS](https://docs.google.com/spreadsheets/d/1J7asR-YQiNib3dj5idwLpLCNPFgVmO0jNYzzPcEbUZE/edit?gid=0#gid=0&range=I:I)
