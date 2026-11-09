# QA checklist (Phần 4). Máy chạy `check.py`; còn lại rà tay. "Không" nào thì sửa rồi mới nộp.

## check.py tự kiểm (chạy: `check.py --file2 <csv> --page "<tên>" <draft.md>`)
ERROR: em/en dash; `wholesalehats.com` viết sai; link trong heading; URL lặp; link tới chính trang; thiếu link bắt buộc theo FILE (2); link không có trong link card; anchor homepage khác cột "Anchor home page"; >2 link/đoạn; >1 link/câu; URL dính `utm_`.
WARN: sentence case heading; thiếu số fact bank (1979/10,000/600/24/30); cụm nên tránh và "rather than/instead of"; section entity lệch format theo STT; link trong FAQ; độ dài ngoài ~700–1200 từ.

## Bước 5 của quy trình — người viết soát nhanh các điểm rủi ro cao
- Section chính không nêu quá 3 SKU; SKU nào được nhắc (kể cả FAQ) đều có thật trên wholesalehats.com / FILE (3).
- Đoạn quá dài thì tách.
- Section entity: câu đầu khẳng định "wholesalehats.com is a trusted source for … hats in the USA since 1979, with nearly five decades of experience and a loyal customer base of 10,000+."
- Sentence case; giữ H1 gốc, heading trong bài là H2; không còn dash ngắt câu.
- Chạy Grammarly để bắt lỗi chính tả.

## Rà tay (judgement — máy không kiểm)
- Dữ liệu: mọi spec/số/màu/size truy được về website brand; mọi fact brand có trong bảng fact brand (lưu kèm); performance/lợi ích truy về đặc điểm thật; không còn [INPUT] chưa xử lý.
- Outline: đúng template & nhánh/dạng trang; đủ H2 đúng thứ tự; H2 bỏ chỉ khi đúng điều kiện; mỗi section đủ "Viết gì", không dính "Không viết gì"; H2 đã paraphrase, thể hiện wholesale; giữ H1 gốc.
- Chống trùng: không đoạn nào đúng nguyên khi đặt vào trang cha/anh em; mỗi ý 1 section; test hoán đổi cho câu mở/kết đoạn + entity; format entity theo STT (lẻ văn xuôi / chẵn bullet).
- SKU: section chính tối đa 3 SKU và chỉ khi sản phẩm đó có điểm khác biệt; FAQ chỉ nêu SKU xác nhận có trên wholesalehats.com (FILE 3).
- "Other/Shop by": câu phân biệt lấy từ chính trang category được nhắc, không dùng chung câu cho 2 trang, có kèm lý do/lợi ích.
- Fact bank thu hẹp đúng trang (Fact 2/3); dùng "we" cho wholesalehats.com, ngôi thứ ba cho brand.
