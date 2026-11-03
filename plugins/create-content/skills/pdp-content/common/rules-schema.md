# rules.json: luật đọc từ file Word

Claude đọc **toàn bộ** `template.txt` (gồm comment) và `file2-columns.txt`, rồi viết `rules.json`.
`validate` đối chiếu lại với file Word: đoạn nguyên văn, H2, nhãn bullet, URL không có trong Word thì
báo ERROR; URL trong Word chưa dùng thì báo WARN (đưa vào `links` hoặc `ignored_urls`).

Không suy luận luật ngoài file Word. Word không nói thì bỏ khoá đó. Word mơ hồ hoặc tự mâu thuẫn thì
ghi vào `questions` và hỏi người dùng, không tự chọn. Không chép tay đoạn dài: dùng nguyên văn từ
`template.txt`.

## Các khoá

| Khoá | Nội dung |
| --- | --- |
| `schema`, `name` | `1`; tên ngành |
| `file2` | `sheet`, `header_row`, `columns`, `required`, `card_columns`, `pic_columns`, `skip_when` |
| `types` | theo tên type trong Word; xem dưới |
| `modules` | phần thêm theo điều kiện: `id`, `when`, `h2`, `must_mention` (`{"meta": ["pony"]}`) |
| `closing_h2` | H2 cuối bài chung (type có thể ghi đè bằng `closing_h2` riêng) |
| `name_placeholders` | biến trong tên H2 và `section`: `{"[Brand]": "brand"}` |
| `extra_h2` | `true` nếu Word cho phép H2 tự đặt tên, nằm trước `closing_h2` |
| `links`, `no_other_links`, `ignored_urls` | link và URL không dùng làm link |
| `pools` | các bộ đoạn nguyên văn để chọn; xem dưới |
| `sequences` | xoay vòng: `id`, `values`, `footer`, `when`, `not_applicable`, `restart_when_changed`, `guidance` |
| `focus_map` | Writing focus → H2 cần viết sâu |
| `corrections` | sửa lỗi gõ trong Word: `find`, `replace`, `why` (báo người dùng khi xác nhận) |
| `data` | `colours_exact`, `sizes_all`, `size_pattern` (regex), `numbers_source` |
| `duplicate_check` | `ngram`, `when`, `exclude_sections` |
| `draft` | xem dưới |
| `checklist_section` | `from`, `to`: dòng mở và dòng sau cuối của checklist trong Word |
| `judgement` | câu nguyên văn của các luật máy không kiểm được |
| `questions` | chỗ cần người dùng chốt |

**Cột (`file2.columns`).** Bắt buộc có `name`, `type`; nên có `no`, `colours`, `sizes`, `brand`,
`focus`. Mỗi cột là `{"header": "Dòng đầu tiêu đề"}`, thêm `"occurrence": 2` nếu tên trùng, hoặc
`{"letter": "A"}` nếu cột không có tiêu đề. Cột `Nội dung trang web (dán)` script tự nhận.
Điều kiện `when` / `skip_when`: `{"column": "...", "equals" | "contains": "...", "filled": true}`.

**Type.** `match` (giá trị trong Excel), `when`, `lead`, `bullets`, `columns`, `name_keywords` (từ
trong tên gợi ý type này; lệch thì preflight HỎI), `h2` là danh sách đúng thứ tự trên trang:
`{"name", "kind": "specific" | "common", "required", "mode": "brief" | "highlight"}`. Chỉ liệt kê H2
type đó dùng; H2 "not used" hay bị thay thế thì không ghi.

**Link.** `key`, `url` hoặc `url_column`, `anchors` (cụm phải có trong anchor), `anchor_from` (cột),
`block` (`short` / `long`), `section` (tên H2), `paragraph` (0 = đoạn đầu), `types`, `when`,
`required`, `not_same_sentence_as` (key link khác), `where` (mô tả cho writer).

**Pool.** `id`, `section`, `paragraph`, `footer` (nhãn dòng cuối bài), `match`
(`verbatim` / `reorderable_after_first` / `contains`), `placeholders` (`{"[Product name]": "name"}`),
`lookups` (biến tra theo bảng trong Word: `{"{Role}": {"column": "brand", "values": {"Racesafe": "..."},
"default": "..."}}`), `selection` (`{"method": "least_used"}`, hoặc `"writer"` nếu Word có cách chọn khác: Claude chọn theo
Word, máy chỉ kiểm hợp lệ), `previous_scope` (`any` / `eligible`), `absent_value`, `items`:
`{"id", "text", "types", "when"}`.

**Draft.** `blocks` (trong `h1`, `meta_title`, `meta`, `short`, `long`), `meta_title` và `meta`:
`{"min", "max", "severity": "error" | "warn", "must_include": ["name"]}`, `banned_chars`,
`banned_phrases`, `spelling`, `short`: `{"opening_sentences": [2, 3], "bridge_sentences": [1, 2],
"no_link_bullet": "Type"}`. Word ghi "khoảng" thì dùng `severity: warn`.
`html_labels`: mặc định `false` — tab HTML (`ban-html.txt`) là một thân HTML sạch, chỉ thẻ
heading/đoạn/bullet/link, meta để text riêng ngoài HTML (đúng spec đa số team, gồm Horse Rugs). Đặt
`true` chỉ khi writer-guide của ngành yêu cầu chèn nhãn `[H1]` / `[Short description]` /
`[Long description]` và các dòng meta vào trong file HTML.

`numbers_source`: `any` (mặc định: Excel và phần dán đều là nguồn, theo quyết định ưu tiên Excel);
`brand_info` chỉ khi người dùng yêu cầu chỉ tính phần dán; `off` để tắt.

## Luật máy chưa kiểm được

Word có luật ngoài các khoá trên thì **vẫn làm theo**: Claude đọc `template.txt` khi viết. Ghi câu đó
vào `judgement` để nó xuất hiện khi xác nhận, và rà lại khi tự kiểm.

## Định dạng draft

```markdown
# META TITLE
# META DESCRIPTION
# SHORT DESCRIPTION
(đoạn mở đầu, bullet "- **Label:** value", câu dẫn)
# LONG DESCRIPTION
## Tên H2
...
# NOTES
(mỗi footer của pools / sequences một dòng, ví dụ "Variant đã dùng: A"; kết quả checklist)
```
