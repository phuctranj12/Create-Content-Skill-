# Luật chung cho mọi ngành hàng

Áp dụng cho mọi category, **cộng thêm** First prompt / template riêng của category. Mỗi luật ở đây
đến từ một lỗi editor đã bắt thật; script kiểm được luật nào thì ghi rõ.

## 1. Nguồn nào quyết thông tin nào

| Loại thông tin | Nguồn quyết | Ghi chú |
| --- | --- | --- |
| Thông số, chất liệu, tính năng, tiêu chuẩn, compatibility, cách chăm sóc | **Brand** | Brand và File (2) lệch → dùng brand, ghi Conflict |
| Trọng lượng | Chỉ brand | Brand không ghi → bỏ |
| **Màu đang bán, size đang bán, size trẻ em, DE ranges** | **File (2)** | Brand chỉ để kiểm tên màu và quy đổi size. Brand có 5 màu, File (2) có 3 → bài chỉ có 3 |
| Brand info / Brand background, Duplicate Risk, Writing focus, Product type, link | File (2) / phụ lục | Dữ liệu workflow |

Hai lỗi hay gặp nhất đều thuộc dòng in đậm: viết màu/size theo trang brand thay vì File (2).

## 2. Màu (script kiểm)

- Liệt kê **đủ và đúng tên** mọi màu trong cột màu của File (2), giữ nguyên cách viết
  (vd `Black - Charcoal`).
- **Chỉ liệt kê**, không dẫn câu: viết `Colour: Black, Black - Charcoal and Navy.`, không viết
  `Choose from ...`, `Available in a choice of ...`.

## 3. Size (script kiểm)

- Chỉ nêu **size DE đang bán**. Không viết dải "from X to Y" nếu giữa X và Y có size DE không bán
  (vd DE bán 52, 53, 54 và 59 Round thì "52 to 59 cm" là sai vì ngụ ý có 55–58).
- Gom các size liền nhau thành một dải, size **round fit** nêu riêng; có bảng quy đổi của brand thì
  ghi size UK kèm cm: `6⅜ to 6⅝ (52 to 54cm), plus 7¼ (59cm) in a round fit`.
- Thẻ sản phẩm (`product.py`) đã tính sẵn câu này ở dòng "câu Size gợi ý": dùng nguyên câu đó.
  Không bỏ cụm **"in a round fit"** khi File (2) có size ROUND: bỏ đi là biến size round thành
  size thường (chữ "round" ở chỗ khác như "all round" không tính).

## 4. Link (script kiểm)

- Cụm **discount-equestrian.co.uk** trong đoạn giới thiệu cửa hàng (About) luôn link về **trang
  chủ** `https://www.discount-equestrian.co.uk/`. Thẻ sản phẩm đã dựng sẵn đoạn có link.
  Gõ tay trong Google Docs, Docs tự link thành `http://discount-equestrian.co.uk` (thiếu `https`
  và `www`): sai, phải sửa lại URL đầy đủ ở trên. Tốt nhất dán từ `ban-text.html`.
- Chỉ dùng URL trong phụ lục link của category (và URL tương thích trong File (2) nếu template
  cho phép); mỗi URL đúng một lần; đúng anchor, đúng vị trí, đúng điều kiện.

## 5. Sau mỗi draft: rà checklist

Sau **mỗi** draft (kể cả khi `check_draft.py` báo 0 ERROR), lia nhanh checklist của category
(`checklist.md` nếu có, hoặc mục "Tự kiểm tra" của First prompt) từng dòng, ghi kết quả vào
`# SELF-CHECK`. Script không thay được phần đọc ý: lặp ý giữa H2, lặp Short/Long, focus, nguồn
của từng câu.
