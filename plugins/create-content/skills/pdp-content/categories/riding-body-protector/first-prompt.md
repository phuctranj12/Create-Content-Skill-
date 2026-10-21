<!-- Sinh tự động bởi import_template.py từ PDP Template - RIDING BODY PROTECTOR.docx. Không sửa tay. -->

# First Prompt – Riding Body Protector

**Bối cảnh:** Tôi đang cần tạo nội dung cho các trang sản phẩm thuộc category Riding Body Protector (body protector, back protector, air vest và phụ kiện) của website https://www.discount-equestrian.co.uk/

Điều quan trọng nhất mà tôi cần là: nội dung được tạo ra theo đúng format, và thông tin sản phẩm được sử dụng phải chính xác với thông tin của nhà sản xuất. Đây là sản phẩm bảo hộ an toàn, nên mọi thông tin về chứng nhận, level, khả năng bảo vệ và khả năng tương thích đều phải chính xác tuyệt đối.

## Cách thực hiện

### Bước 1: FILE (1) – Format

Đầu tiên tôi sẽ cung cấp cho bạn format của một bài PDP tiêu chuẩn. Bước này tôi chỉ thực hiện 1 lần; bạn cần nắm rõ và đảm bảo tất cả các bài PDP bạn tạo ra đều theo format này. Tôi sẽ gọi file này là **FILE (1)**.

- FILE (1) có 4 outline riêng: **Outline A** (Body protector), **Outline B** (Back protector), **Outline C** (Air vest), **Outline D** (Accessory). Bạn phải xác định đúng loại sản phẩm theo cột **Product Type** trong FILE (2) và dùng đúng outline. Nếu loại sản phẩm trống hoặc không rõ, dừng lại và hỏi tôi.
- **Tên các H2 phải giữ đúng như trong FILE (1).** Không thêm tên sản phẩm vào H2, không đổi cách gọi. Riêng H2 About chỉ thay [Brand] bằng tên brand.
- Trong mỗi outline có nhiều Heading 2. Nếu FILE (2) và THÔNG TIN TỪ BRAND không có nội dung liên quan đến Heading 2 đó (hay nói cách khác sản phẩm không có feature đó), bạn hãy chủ động loại bỏ Heading 2 đó.
- Trong mỗi Heading 2 có nhiều ý. Nếu FILE (2) và THÔNG TIN TỪ BRAND không có nội dung liên quan đến ý đó, bạn hãy chủ động loại bỏ ý đó, không tự bịa nội dung.
- **Phân bổ thông tin** theo **Section ownership rule** trong FILE (1): mỗi thông tin chỉ có một H2 "nhà", không lặp ở H2 khác. Outline D có bảng phân bổ riêng.
- **Other features:** chọn và hiển thị theo **Other features rule** trong FILE (1). Với Outline A, B, C: chỉ tạo H2 Other Highlights khi có từ 2 other feature hợp lệ trở lên. Với Outline D: không tạo H2 Other Highlights, chỉ hiển thị bằng bullet.
- **Không viết hướng dẫn cách đo chung** (cách đo ngực, qua vai, chiều dài lưng) ở bất kỳ phần nào, vì nội dung này lặp lại giữa các sản phẩm. H2 Sizing & Fit chỉ gồm size, chiều dài, size chart (chỉ số liệu), điểm điều chỉnh, và một câu ngắn dẫn đến hỗ trợ chọn size.
- **Không có ngoại lệ cho phần Care.** Heading về care, bảo quản và thay thế chỉ được viết từ thông tin của hãng. Nếu không có dữ liệu thì loại bỏ ý hoặc loại bỏ Heading, không tự suy ra cách vệ sinh hay tuổi thọ.
- **Ngoại lệ với phần Brand:** chỉ dùng thông tin trong cột **Brand background** của FILE (2), theo Brand rule trong FILE (1). Không tự tìm hiểu thêm.
- **Đoạn About discount-equestrian.co.uk:** dùng một phiên bản trong Appendix 2 của FILE (1), chọn theo About rotation rule. **Chỉ thay [Product] và {Role}** theo Supplier paragraph rule; không sửa bất kỳ từ nào khác. Với phụ kiện, dùng bộ phiên bản của loại sản phẩm mà phụ kiện phục vụ (A, B hoặc K), theo Outline D.

### Bước 2: FILE (2) – Data sản phẩm

Sau đó tôi sẽ cung cấp cho bạn file data PDP. File này chứa thông tin các sản phẩm mà tôi tự thu thập, gọi là **FILE (2)**. Mỗi khi tôi đưa ra prompt cho 1 sản phẩm, bạn cần tìm đúng dòng có **STT** của sản phẩm đó để tham khảo thông tin.

FILE (2) có thể bị sai sót, nên chỉ mang tính tham khảo. Bạn phải đối chiếu FILE (2) với THÔNG TIN TỪ BRAND theo 2 nguyên tắc:

- **Thông tin bị conflict** giữa FILE (2) và THÔNG TIN TỪ BRAND: **ưu tiên chọn THÔNG TIN TỪ BRAND.**
- **Thông tin có trong FILE (2) mà THÔNG TIN TỪ BRAND không có: bỏ**, không đưa vào nội dung.

**Ngoại lệ, luôn lấy từ FILE (2)** (không áp dụng 2 nguyên tắc trên), vì đây là các thông tin chỉ FILE (2) cung cấp:

- Product Type (Body protector / Back protector / Air vest / Accessory), Colours, Size (đang bán trên site)
- Body Protector Finder (Y/N)
- Brand background (nguồn duy nhất cho đoạn brand)
- Product URL, DE Brand URL, Product type URL
- Differentiator, Writing focus

Các cột thông tin sản phẩm khác, kể cả hai cột **Type-specific (Accessory): Compatibility** và **Type-specific (Accessory): Specification**, là thông tin từ hãng, nên áp dụng 2 nguyên tắc conflict ở trên.

**Không dùng cột How to measure** (nếu có trong FILE (2)) để viết nội dung. Cột này chỉ để writer tham khảo khi kiểm tra size chart.

### Bước 3: Phân tích và tạo nội dung cho từng sản phẩm

Mỗi lần làm một sản phẩm, tôi sẽ gửi theo cú pháp:

Phân tích sản phẩm số [STT] THÔNG TIN TỪ BRAND: [nội dung copy từ trang sản phẩm của hãng và trang sản phẩm trên discount-equestrian.co.uk]

THÔNG TIN TỪ BRAND là nguồn đáng tin cậy nhất. Bạn cần sử dụng mọi data từ đó, nhưng:

- Phải đưa data vào đúng vị trí phù hợp theo FILE (1).
- Không copy paste mà phải paraphrase lại nội dung.

**Lượt 1: Chỉ phân tích, CHƯA tạo nội dung.** Khi nhận lệnh "Phân tích sản phẩm số [STT]", bạn **chỉ trả về phần phân tích** dưới đây, **tuyệt đối không viết** H1, Meta Description, Short description hay Long description:

- Loại sản phẩm và outline sẽ dùng (A, B, C hoặc D)
- Danh sách conflict giữa FILE (2) và THÔNG TIN TỪ BRAND, kèm thông tin sẽ chọn (theo nguyên tắc ưu tiên THÔNG TIN TỪ BRAND). Liệt kê riêng **các thông tin chỉ có trong FILE (2) sẽ bị bỏ**. **Bắt buộc kiểm tra kỹ:**
  - Outline A, B, C: tên chuẩn và năm (đặc biệt 2009 hay 2018), level, size và chiều dài, màu, vùng bảo vệ, khả năng tương thích với air vest hoặc body protector, bình CO₂ có kèm không
  - Outline D: sản phẩm và size tương thích, thông số (dung tích bình CO₂, kiểu lắp bayonet hay screw, kích thước), số lượng trong gói, chứng nhận (nếu có)
- Các Heading 2 sẽ bị loại bỏ vì thiếu dữ liệu
- Phiên bản About discount-equestrian.co.uk sẽ dùng (theo About rotation rule), và **giá trị {Role}** sẽ dùng cho brand này (authorised stockist / official retailer / không gắn danh xưng), theo Supplier paragraph rule. Với phụ kiện: ghi rõ phụ kiện phục vụ loại sản phẩm nào, và vì vậy dùng bộ phiên bản nào (A, B hoặc K)
- Báo nếu ô **Brand background** trống, hoặc không có URL brand ở cột DE Brand URL lẫn Appendix 1
- **Sản phẩm gần giống:** các sản phẩm trong 9 sản phẩm liền trước có cùng model, chỉ khác màu, size, phiên bản hoặc một chi tiết nhỏ. Với mỗi sản phẩm gần giống, ghi Differentiator và Writing focus của cả hai. Báo nếu **Writing focus bị trùng** giữa các sản phẩm gần giống
- Danh sách other feature hợp lệ (theo Other features rule), thứ tự ưu tiên, và quyết định: không hiển thị / chỉ bullet trong Short / bullet trong Short và H2 Other Highlights (Outline D chỉ có thể là không hiển thị hoặc chỉ bullet)

Kết thúc phần phân tích, chờ tôi phản hồi.

**Lượt 2: Chỉ tạo nội dung khi tôi gửi lệnh "Tạo nội dung".**

- Khi nhận lệnh "Tạo nội dung" (có thể kèm cách xử lý conflict), bạn mới viết nội dung theo đúng outline trong FILE (1), gồm H1, Meta Description, Short description và Long description. Ngay sau khi tạo, tự kiểm tra theo mục "Tự kiểm tra" và sửa trước khi gửi.
- Nếu tôi chỉ phản hồi về conflict mà chưa gửi "Tạo nội dung", bạn chỉ cập nhật lại phần phân tích, không viết nội dung.

### Bước 4: Tạo bản HTML

Khi tôi gửi lệnh "**Tạo bản HTML**", chuyển nội dung đã được xác nhận thành HTML mà tôi có thể copy code được. HTML chỉ đơn thuần set heading, đoạn văn, bullet, bảng (cho size chart, bảng tương thích hoặc thông số) và gắn link; không quy định gì khác về style; giữ HTML thật đơn giản.

## Yêu cầu về đầu ra

**Chung**

- Bước 1 và bước 2 không cho ra đầu ra nào cả, bạn chỉ nhận thông tin và hỏi lại nếu cần.
- Sử dụng Anh-Anh.
- **Không sử dụng dấu gạch dài (—)** trong nội dung.
- Ngắn gọn, xúc tích, đi thẳng vào thông tin. Không dùng câu dẫn lòng vòng.
- Đầu bản draft ghi rõ: outline đã dùng, phiên bản About đã dùng, và giá trị {Role}.

**Độ chính xác**

- **Không được bịa bất kỳ thông tin nào về feature của sản phẩm.** Ví dụ: THÔNG TIN TỪ BRAND chỉ ghi là "foam" thì không được tự viết thành "multi-density foam"; hãng không ghi trọng lượng thì không viết "lightweight".
- Với những Heading mà dữ liệu quá ít hoặc không insightful, bạn được phép dựa vào dữ liệu đó để suy ra **lợi ích** cho người dùng. Chỉ được suy ra lợi ích, không được bịa thông tin.

**Thông tin an toàn**

- Chỉ ghi chuẩn, level và năm đúng như hãng công bố.
- Chỉ khẳng định dùng được cho thi đấu với sản phẩm BETA 2018 Level 3.
- Back protector luôn ghi rõ chỉ bảo vệ lưng, không dùng cho cross-country, trừ khi hãng nói khác.
- Heading "Riding Use Cases" luôn kết thúc bằng câu cố định: "Always check the current rules of your governing body before competing."
- **Phụ kiện:** chỉ ghi khả năng tương thích (sản phẩm, model, size) khi hãng xác nhận. Chỉ ghi chứng nhận khi hãng có công bố (ví dụ shoulder protector). Không suy ra tương thích từ việc cùng brand.

**Trình bày**

- **Tên H2:** giữ đúng như FILE (1), không thêm tên sản phẩm.
- **Short description:** feature bullets trình bày dạng **"Nhãn: nội dung"**, dùng đúng các nhãn trong FILE (1). Nội dung sau dấu ":" ngắn gọn, dễ hiểu và đủ thông tin (khoảng 4–12 từ), là một cụm từ chứ không phải câu đầy đủ, không viết rườm rà.
- **Long description:**
  - Viết từng ý dưới dạng đoạn văn, hạn chế bullet point. Ngoại lệ: size chart, bảng tương thích và bảng thông số trình bày dạng bảng (chỉ số liệu, không kèm hướng dẫn cách đo).
  - Nếu có nhiều ý trong một Heading, tách thành các đoạn khác nhau.
  - Viết đoạn văn có ngữ cảnh: có câu nối giữa heading và đoạn văn, giữa các đoạn văn trong cùng một Heading, và đưa tên sản phẩm vào nội dung.
- **Không overlap giữa các phần:** mỗi phần chỉ tập trung vào nội dung chính của phần đó. Không nhắc lại, không tham chiếu đến nội dung của phần khác (không dùng các câu như "as mentioned above", "in addition to its breathable design"). Phân bổ thông tin đúng theo Section ownership rule trong FILE (1).
- **Không tạo FAQs.**

**Internal link**

- Chỉ chèn theo Appendix 1 của FILE (1), chỉ ở Short description và phần About, mỗi URL một lần, chỉ dùng URL có trong Appendix 1 hoặc FILE (2).
  - Outline A (Body protector) và Outline D (Accessory): 1 link category mẹ + 1 link brand.
  - Outline B (Back protector) và Outline C (Air vest): 1 link category type + 1 link category mẹ + 1 link brand.

**H2 About [Brand] & discount-equestrian.co.uk**

- **Đoạn brand:** theo Brand rule trong FILE (1). Câu cuối đoạn brand phải gắn brand với sản phẩm đang viết, để tạo chuyển tiếp tự nhiên sang đoạn discount-equestrian.co.uk. Không lặp câu giống hệt với đoạn brand của sản phẩm cùng hãng trong 9 sản phẩm liền trước.
- **Đoạn discount-equestrian.co.uk:** luôn mở đầu bằng việc giới thiệu discount-equestrian.co.uk là nhà cung cấp sản phẩm này ("The [Product] is supplied by discount-equestrian.co.uk…"). Chỉ dùng danh xưng "authorised stockist" hoặc "official retailer" đúng theo bảng {Role} trong Supplier paragraph rule.

**Chống trùng wording giữa các sản phẩm gần giống (trong 10 sản phẩm liền kề)**

- **Thông tin giữ nguyên, chỉ thay đổi cách diễn đạt.** Không được tạo ra khác biệt không có thật để nội dung trông khác đi.
- **Differentiator:** nội dung cột Differentiator trong FILE (2) phải xuất hiện trong **Meta Description** và **câu intro** của Short description.
- **Writing focus:** dùng cột Writing focus trong FILE (2) để quyết định góc mở đầu của câu intro và điểm nhấn trong Long description. Ví dụ: focus "Freedom of movement" thì intro mở đầu bằng khả năng cử động, và phần Freedom of Movement được viết chi tiết hơn.
  - Outline A, B, C dùng 5 focus: Protection & certification / Fit & sizing / Freedom of movement / Comfort & breathability / Competition use.
  - Outline D dùng 3 focus: Compatibility / Function / Ease of use.
- **Không có câu nào giống hệt**, và không có cụm từ trùng từ **8 từ liên tiếp trở lên**, so với nội dung của các sản phẩm gần giống trong 9 sản phẩm liền trước. Áp dụng cho Meta Description, intro, Long description và đoạn brand.
- **Feature bullets:** giữ nguyên nhãn và thứ tự theo FILE (1); nội dung sau dấu ":" diễn đạt khác đi khi thông tin cho phép.
- **Ngoại lệ được phép giống nhau:** tên sản phẩm, tên H2, nhãn bullet, tên chuẩn và level, số liệu trong size chart và bảng thông số, tên màu, câu cố định về governing body, và đoạn About discount-equestrian.co.uk.

## Tự kiểm tra (sau khi tạo nội dung, trước khi gửi)

- Không có ý nào bị trùng giữa các đoạn văn và giữa các Heading.
- Không có dấu gạch dài (—).
- Đúng số lượng internal link theo outline, đúng vị trí, đúng URL, mỗi URL một lần.
- Chuẩn, level, size, màu và thông số khớp nhau giữa Meta Description, Short description và Long description.
- Không có thông tin nào nằm ngoài THÔNG TIN TỪ BRAND và các ngoại lệ được phép lấy từ FILE (2).
- Đoạn About discount-equestrian.co.uk đúng phiên bản; chỉ thay [Product] và {Role}; mở đầu bằng vai trò nhà cung cấp; {Role} đúng theo brand.
- Đoạn brand kết thúc bằng câu gắn với sản phẩm; không lặp câu với sản phẩm cùng hãng trong 9 sản phẩm liền trước.
- So với các sản phẩm gần giống trong 9 sản phẩm liền trước: không có câu nào giống hệt, không có cụm trùng từ 8 từ liên tiếp trở lên (trừ các ngoại lệ được phép); Differentiator đã xuất hiện trong Meta Description và câu intro; nội dung đi đúng Writing focus.
- Other features đúng theo Other features rule: chỉ tính feature hợp lệ, đúng thứ tự ưu tiên, H2 Other Highlights chỉ xuất hiện ở Outline A, B, C khi có từ 2 feature trở lên.
- Mỗi thông tin chỉ xuất hiện ở đúng một H2 theo Section ownership rule; không có câu tham chiếu chéo giữa các phần (ngoại trừ phần tóm tắt trong Short description).
- Feature bullets đúng dạng "Nhãn: nội dung", nội dung sau dấu ":" ngắn gọn (khoảng 4–12 từ).
- Tên H2 đúng như FILE (1), không chứa tên sản phẩm.
- Không có hướng dẫn cách đo trong bất kỳ phần nào; size chart chỉ có số liệu.
- **Với phụ kiện (Outline D):** thông tin tương thích chỉ lấy từ hãng; không có H2 Other Highlights; dùng đúng bộ phiên bản About theo loại sản phẩm mà phụ kiện phục vụ; chỉ có 1 link category mẹ và 1 link brand.

Ở cuối draft, liệt kê ngắn kết quả tự kiểm tra (đạt hoặc đã sửa gì).
