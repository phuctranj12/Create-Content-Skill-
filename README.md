# Create Content — PDP hàng loạt

Skill cho [Claude Code](https://claude.com/claude-code) giúp **sản xuất nội dung trang sản phẩm
(PDP) hàng loạt** cho discount-equestrian.co.uk theo đúng quy trình của team content (PDP
Template, File (1), File (2), First Prompt). Ngành hàng hiện có: **Riding Body Protector**
(body protector, back protector, air vest, phụ kiện) và **Riding Hat** (Riding Hat, Hat Silks &
Covers, Liners & Parts, Helmet Accessories). Ngành mới thêm bằng một thư mục cấu hình trong
`categories/` (engine `generic`, không sửa code); luật áp dụng cho mọi ngành nằm ở
`common/universal-rules.md`.

Skill chuyển phần việc lặp lại sang script, để Claude chỉ làm phần cần phán đoán:

| Việc | Quy trình thủ công | Với skill |
| --- | --- | --- |
| Dán First Prompt + File (1) + File (2) vào thread | Mỗi lần mở thread mới | Skill tự nạp; mỗi sản phẩm chỉ đọc đúng 1 outline |
| Outline, tên H2, nhãn bullet, phiên bản About, {Role}, link | AI suy ra, writer soát | `product.py` tính theo luật |
| Đoạn discount-equestrian.co.uk | AI chép Appendix 2, hay lệch chữ | Dựng sẵn nguyên văn, `check_draft.py` so từng chữ |
| Sản phẩm gần giống, trùng focus, đẩy phiên bản About | Writer tự dò | `product.py` báo BLOCK/CHECK |
| Chống trùng với 9 sản phẩm liền trước | Phải ở cùng một thread | `--history` đọc draft đã lưu |
| Soát lỗi thường gặp + internal link | Writer đọc tay | `check_draft.py` tự bắt |
| Bản HTML | AI sinh lại | `to_html.py` chuyển bằng code |

```
Bạn:    Phân tích sản phẩm số 2
Claude: Thẻ: Air vest · Outline C · About A2 · {Role} "an authorised Racesafe stockist and"
        BLOCK: Product Type = 'Body Protectors' nhưng Sub type = 'Air Jackets and Air Vests' …
Bạn:    Đúng là air vest.
Claude: (lấy THÔNG TIN TỪ BRAND từ racesafe.co.uk + trang DE) → phân tích 7 mục … Cần bạn quyết: …
Bạn:    Tạo nội dung
Claude: (draft.md → check_draft.py: 0 ERROR) …
Bạn:    Tạo bản HTML
```

## Cài đặt (mỗi máy làm một lần)

### Claude Code: terminal, VS Code, hoặc tab Code của Claude Desktop

Ba nơi này dùng chung một bộ cài đặt plugin trên máy, nên cài ở một nơi là dùng được ở cả ba.

```
/plugin marketplace add phuctranj12/Create-Content-Skill-
/plugin install create-content@hawee-content
```

Sau đó **bật tự cập nhật**: gõ `/plugin`, vào tab **Marketplaces**, chọn **hawee-content**, rồi chọn
**Enable auto-update**. Với marketplace bên ngoài, tính năng này mặc định **tắt**, nên nếu bỏ bước
này máy sẽ không tự nhận bản mới.

Gọi skill bằng `/create-content:pdp-content`, hoặc cứ nói việc cần làm ("phân tích sản phẩm số 5",
"làm hàng loạt STT 5–20"). Yêu cầu Python 3.8+ (`py -3` trên Windows), không cần cài thư viện.

Nếu repo để **private**, máy cần đăng nhập GitHub qua git (Git for Windows có sẵn Git Credential
Manager: chạy `git clone` repo một lần để đăng nhập). Bước tự cập nhật chạy ngầm, không hỏi mật
khẩu; nếu chưa đăng nhập, nó lặng lẽ giữ bản cũ.

### Chat trên claude.ai / Claude Desktop

Chế độ Chat không cài plugin từ GitHub. Thay vào đó:
1. Tải `pdp-content.zip` từ release **skill-latest** của repo (GitHub Actions tự build lại mỗi khi
   main đổi).
2. Upload ở **Customize › Skills**.

Chế độ này **không tự cập nhật**: có bản mới thì tải zip và upload lại.

## Cập nhật tự động hoạt động thế nào

- Plugin **không ghi trường `version`**. Claude Code khi đó lấy **commit SHA của thư mục
  `plugins/create-content/`** làm phiên bản, nên mỗi commit trên main có sửa plugin là một phiên bản
  mới. Sửa README, test hay `source/` thì không tạo bản mới.
- Máy đã bật auto-update: sau tin nhắn đầu tiên của một phiên, Claude Code chờ ngẫu nhiên tối đa 10
  phút, rồi kéo bản mới về. Phiên đang chạy hiện thông báo *Plugin updated … Run /reload-plugins*.
  Gõ `/reload-plugins` hoặc mở phiên mới để dùng bản mới.
- Muốn cập nhật ngay: `/plugin marketplace update hawee-content`, sau đó `/reload-plugins`.
- **Đừng thêm `"version"`** vào `plugin.json` hay `marketplace.json`. Có trường này mà quên tăng số
  thì mọi máy sẽ đứng yên ở bản cũ. Test sẽ báo lỗi nếu trường này xuất hiện.

## Phát hành bản mới

Mọi máy bật auto-update đều nhận ngay những gì vào main, nên **main phải luôn chạy được**:

1. Sửa trên nhánh riêng, chạy `py -3 tests/run_tests.py` trên máy.
2. Mở pull request. GitHub Actions chạy test trên Windows và Ubuntu, và `claude plugin validate`.
3. Test xanh thì merge vào main. Từ đó các máy tự cập nhật, và release `skill-latest` được build lại.

Nên bật branch protection cho main (Settings › Branches) với điều kiện test phải qua, để không ai
đẩy thẳng một bản lỗi.

## Dùng thế nào

1. Nói cho Claude đường dẫn File (2).
2. Một sản phẩm: `Phân tích sản phẩm số N` (kèm `THÔNG TIN TỪ BRAND: …` nếu muốn tự dán; không có
   thì Claude tự lấy từ website hãng; trang DE chặn máy nên thường phải dán) → duyệt conflict →
   `Tạo nội dung` → `Tạo bản HTML`.
3. Hàng loạt: `Làm STT 5–20`. Mọi vấn đề của File (2) và mọi conflict được gom thành **một** danh
   sách để quyết một lần; draft được viết tuần tự theo STT.

Trước khi làm hàng loạt, đọc [Hạn chế của skill và cách chuẩn bị dữ liệu](docs/han-che-va-chuan-bi-du-lieu.md):
web DE chặn máy nên dữ liệu phải nằm sẵn trong File (2), và bài dán vào Google Doc nên gửi lại link
để kiểm.

Kết quả mỗi sản phẩm nằm ở `output/<ngành>/<STT>-<tên>/`:
- `card.md`, `brand-info.txt`, `analysis.md`, `draft.md`, `draft.html`;
- hai tệp nộp `ban-text.html` (dán vào tab Text) và `ban-html.txt` (dán vào tab HTML).

```bash
cd plugins/create-content/skills/pdp-content/scripts
py -3 product.py --file2 "File (2).xlsx" --list                    # tổng quan, sản phẩm bị BLOCK
py -3 product.py --file2 "File (2).xlsx" --stt 4                   # thẻ một sản phẩm
py -3 product.py --file2 "File (2).xlsx" --stt 2 --type air        # khi đã xác nhận loại
py -3 check_draft.py --draft d.md --file2 "File (2).xlsx" --stt 4 --brand-info b.txt --history <output>
py -3 to_html.py d.md --submit                                     # draft.html + 2 tệp nộp
```

## Cấu trúc

```
Create-Content-Skill-/                     ← marketplace "hawee-content"
├── .claude-plugin/marketplace.json        # liệt kê plugin, source: ./plugins/create-content
├── plugins/create-content/                ← plugin "create-content" (chỉ thư mục này được cài)
│   ├── .claude-plugin/plugin.json         # KHÔNG có "version": cập nhật theo commit
│   └── skills/pdp-content/
│       ├── SKILL.md                       # quy trình 6 bước + hàng loạt + kỷ luật token
│       ├── categories/riding-body-protector/
│       │   ├── category.json              # cột File (2), loại→outline, H2, bullet, URL, {Role}, luật kiểm
│       │   ├── first-prompt.md, file1-general.md, outline-A…D.md, about-versions.json,
│       │   │   writer-guide.md, file2-columns.md   # sinh bởi import_template.py từ PDP Template
│       │   ├── rules.md                   # conflict phải hỏi, kinh nghiệm nguồn
│       │   ├── analysis-template.md, draft-format.md
│       └── scripts/                       # pdplib, product, check_draft, to_html, import_template
├── source/PDP Template - RIDING BODY PROTECTOR.docx   # nguồn, không cài sang máy người dùng
├── tests/                                 # self-check, chỉ dùng thư viện chuẩn
├── tools/build_skill_zip.py               # zip cho claude.ai
└── .github/workflows/
    ├── tests.yml                          # test + claude plugin validate cho mọi PR/push
    └── skill-zip.yml                      # build pdp-content.zip vào release skill-latest
```

## Cập nhật template / thêm ngành hàng

Khi team sửa PDP Template: tải lại .docx **đủ các tab** (Tệp → Tải xuống → .docx), đặt vào
`source/`, rồi:

```bash
py -3 plugins/create-content/skills/pdp-content/scripts/import_template.py \
   "source/PDP Template - RIDING BODY PROTECTOR.docx" \
   --out plugins/create-content/skills/pdp-content/categories/riding-body-protector
py -3 tests/run_tests.py
```

Nếu tên H2, nhãn bullet, URL hay danh sách brand/{Role} đổi thì sửa `category.json` cho khớp. Test
báo khi tệp sinh tự động lệch với .docx.

Ngành hàng mới (horse rug, riding hat…): chép thư mục category, sửa `category.json` và `rules.md`,
rồi chạy import với `--out` là thư mục mới. Không phải sửa code. Đẩy lên main là mọi máy tự có ngành
mới.

## Kiểm thử

```bash
py -3 tests/run_tests.py
claude plugin validate .                     # cảnh báo "No version specified" là có chủ đích
```

## Lưu ý

- `source/` và `categories/` chứa quy trình nội bộ của dự án content (prompt, đoạn About, URL). Nên
  để repo **private**; auto-update vẫn chạy nếu máy đã đăng nhập GitHub qua git.
- Skill hỗ trợ writer, không thay bước duyệt: conflict về chuẩn an toàn luôn dừng chờ người phụ
  trách, và draft vẫn cần người đọc lại trước khi đăng.

## Giấy phép

[MIT](LICENSE)
