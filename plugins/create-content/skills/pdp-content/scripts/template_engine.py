# -*- coding: utf-8 -*-
"""Template-driven pipeline: the rules come from the team's Word file, not from code.

    py -3 template_engine.py init --template "T.docx" --file2 "F.xlsx" --workdir output/x
    (Claude reads output/x/template.txt, writes output/x/rules.json)
    py -3 template_engine.py validate --workdir output/x
    py -3 template_engine.py confirm  --workdir output/x      (after the user agrees)
    py -3 template_engine.py preflight --workdir output/x [--pic "Name"] [--no 94,95]
    py -3 template_engine.py card  --workdir output/x --no 94
    py -3 template_engine.py check --workdir output/x --no 94
    py -3 template_engine.py html  --workdir output/x --no 94

rules.json is schema-checked and every quoted text, H2, bullet label and URL is
looked up in the Word file, so a rule cannot be invented or retyped wrongly
unnoticed. Nothing here names a product family. Layout: common/rules-schema.md.
Exit codes: 0 ok, 1 errors in rules or draft, 2 not confirmed / template changed,
3 preflight found rows that cannot be written yet.
"""

import argparse
import difflib
import hashlib
import json
import os
import re
import sys
import unicodedata
import zipfile
from xml.etree import ElementTree as ET

import generic
import pdplib
import to_html

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R_ID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
PASTE_HEADERS = ("nội dung trang web (dán)", "nội dung trang web", "page content")
CELL_LIMIT = 32767
DEFAULT_BLOCKS = {"h1": "H1", "meta_title": "META TITLE", "meta": "META DESCRIPTION",
                  "short": "SHORT DESCRIPTION", "long": "LONG DESCRIPTION", "notes": "NOTES"}
REMINDER = """## Trước khi viết: cột nội dung trang web

Skill chỉ viết điều có trong file. Trang DE chặn máy truy cập, trang brand máy thường chỉ đọc được
bản tóm tắt, nên phần này phải do bạn dán:

1. Thêm **một cột cuối cùng** vào sheet sản phẩm, tiêu đề đúng là `Nội dung trang web (dán)`.
2. Với **mỗi** sản phẩm, dán vào ô của dòng đó các trang theo đúng thứ tự file Word quy định (trang
   sản phẩm của brand, trang sản phẩm trên DE, size chart, hướng dẫn giặt). Mỗi trang mở đầu bằng
   một dòng URL.
3. Size chart hoặc hướng dẫn giặt ở dạng ảnh thì gõ lại. Không có thì skill bỏ phần đó.
4. Mỗi ô tối đa 32.767 ký tự: chỉ bôi đen phần nội dung, đừng lấy menu và footer.

Dán xong, tải lại file Excel rồi gửi đường dẫn."""


# --- Text -------------------------------------------------------------------
def norm(text):
    text = unicodedata.normalize("NFC", text or "")
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'), (" ", " ")):
        text = text.replace(a, b)
    return re.sub(r"\s+", " ", text).strip()


def in_doc(needle, doc_norm):
    return norm(needle) in doc_norm


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def list_cell(value):
    items = [x.strip().lstrip("•-* \t").strip() for x in re.split(r"[;\n]+", value or "")]
    return [x for x in items if x and x != pdplib.NA]


def filled(value):
    return generic.filled(value)


# --- Word -------------------------------------------------------------------
def _para_text(p):
    return "".join(t.text or "" for t in p.iter(W + "t"))


def _cell_text(tc):
    return " / ".join(t for t in (_para_text(p) for p in tc.iter(W + "p")) if t.strip())


def extract_docx(path):
    """Body text in reading order, tables as 'a | b', then comments and link targets."""
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        body = ET.fromstring(z.read("word/document.xml"))[0]
        out = []
        for el in body:
            if el.tag == W + "p":
                text = _para_text(el)
                if text.strip():
                    out.append(text)
            elif el.tag == W + "tbl":
                for tr in el.iter(W + "tr"):
                    out.append(" | ".join(_cell_text(tc) for tc in tr.findall(W + "tc")))
        if "word/comments.xml" in names:
            comments = ET.fromstring(z.read("word/comments.xml"))
            lines = ["[%s] %s" % (c.get(W + "author"), _para_text(c)) for c in comments]
            if lines:
                out += ["", "=== COMMENTS TRONG FILE WORD ==="] + lines
        if "word/_rels/document.xml.rels" in names:
            rels = {r.get("Id"): r.get("Target")
                    for r in ET.fromstring(z.read("word/_rels/document.xml.rels"))}
            links = []
            for h in body.iter(W + "hyperlink"):
                target = rels.get(h.get(R_ID))
                if target and target.startswith("http"):
                    links.append("%s -> %s" % (_para_text(h), target))
            if links:
                out += ["", "=== LINK ẨN SAU CHỮ TRONG FILE WORD ==="] + sorted(set(links))
    return "\n".join(out) + "\n"


# --- Excel ------------------------------------------------------------------
def first_line(header):
    return pdplib.norm_header((header or "").split("\n")[0])


def letter_index(letters):
    n = 0
    for ch in letters.upper():
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def col_letter(i):
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def sheet_names(path):
    with zipfile.ZipFile(path) as z:
        wb = ET.fromstring(z.read("xl/workbook.xml"))
    return [s.get("name") for s in wb.find(pdplib.NS + "sheets")]


def describe_file2(path):
    """Sheets, columns and how many cells each column has, for Claude to map."""
    out = []
    for name in sheet_names(path):
        rows = pdplib.read_sheet(path, name)
        out.append("=== SHEET %s (%d dòng) ===" % (name, len(rows)))
        if not rows:
            continue
        for i, h in enumerate(rows[0]):
            n = sum(1 for r in rows[1:] if i < len(r) and r[i].strip())
            out.append("%s | %r | %d ô có dữ liệu" % (col_letter(i), (h or "").strip(), n))
    return "\n".join(out) + "\n"


def resolve_column(spec, header):
    """Index of a column from {"letter": "A"} or {"header": "...", "occurrence": 2}."""
    if "letter" in spec:
        return letter_index(spec["letter"])
    wanted = pdplib.norm_header(spec["header"])
    hits = [i for i, h in enumerate(header)
            if first_line(h) == wanted or pdplib.norm_header(h) == wanted]
    n = spec.get("occurrence", 1)
    return hits[n - 1] if len(hits) >= n else None


def load_products(path, rules):
    f2 = rules["file2"]
    rows = pdplib.read_sheet(path, f2.get("sheet"))
    start = f2.get("header_row", 1) - 1
    if len(rows) <= start:
        raise SystemExit("Sheet sản phẩm trống.")
    header = rows[start]
    index, missing = {}, []
    for key, spec in f2["columns"].items():
        pos = resolve_column(spec, header)
        if pos is None:
            missing.append("%s (%s)" % (key, spec.get("header") or spec.get("letter")))
        else:
            index[key] = pos
    if missing:
        raise SystemExit("File Excel thiếu cột: %s" % ", ".join(missing))
    for i, h in enumerate(header):
        if first_line(h) in PASTE_HEADERS:
            index["page_content"] = i
    products = []
    for rownum, row in enumerate(rows[start + 1:], start=start + 2):
        cell = lambda k: (row[index[k]] if index[k] < len(row) else "").strip()
        p = {k: cell(k) for k in index}
        if pdplib.is_empty(p.get("name")):
            continue
        p["_row"] = rownum
        p["_order"] = len(products)
        try:
            p["stt"] = int(float(p.get("no") or ""))
        except ValueError:
            p["stt"] = len(products) + 1  # no No. column: the first product is number 1
        products.append(p)
    return products, "page_content" in index


def when_ok(cond, p):
    if not cond:
        return True
    value = p.get(cond["column"], "")
    if "equals" in cond:
        return norm(value).lower() == norm(cond["equals"]).lower()
    if "contains" in cond:
        return norm(cond["contains"]).lower() in norm(value).lower()
    if "filled" in cond:
        return filled(value) == bool(cond["filled"])
    return True


def type_of(p, rules):
    value = norm(p.get("type", "")).lower()
    for key, t in rules["types"].items():
        names = [norm(m).lower() for m in t.get("match", [key])]
        if value in names and when_ok(t.get("when"), p):
            return key
    return None


# --- Rules validation -------------------------------------------------------
REQUIRED_KEYS = ("schema", "name", "file2", "types", "links", "pools", "draft")


def validate_rules(rules, template, products_error=None):
    """(errors, warnings). Everything checkable against the Word text is checked."""
    errs, warns = [], []
    for key in REQUIRED_KEYS:
        if key not in rules:
            errs.append("rules.json thiếu khoá '%s'." % key)
    if errs:
        return errs, warns
    doc = norm(template)
    doc_low = doc.lower()

    def quoted(where, text):
        if not in_doc(text, doc):
            errs.append("%s: không tìm thấy nguyên văn trong file Word: %r" % (where, text[:90]))

    def named(where, text):
        if norm(text).lower() not in doc_low:
            errs.append("%s: '%s' không có trong file Word." % (where, text))

    for k in ("name", "type"):
        if k not in rules["file2"].get("columns", {}):
            errs.append("file2.columns phải có khoá '%s'." % k)
    for key, t in rules["types"].items():
        named("Type", key)
        if not t.get("h2"):
            errs.append("Type '%s' không có danh sách H2." % key)
        for h in t.get("h2", []):
            named("H2 của %s" % key, h["name"])
            if h.get("kind") not in ("specific", "common"):
                errs.append("H2 '%s' của %s: kind phải là specific hoặc common." % (h["name"], key))
        for b in t.get("bullets", []):
            named("Bullet của %s" % key, b)
        if "source" in t:
            quoted("source của type %s" % key, t["source"])
    for m in rules.get("modules", []):
        for h in m.get("h2", []):
            named("H2 module %s" % m["id"], h["name"])
    for h in rules.get("closing_h2", []):
        named("H2 closing", h["name"])
    urls = set()
    for link in rules["links"]:
        if "url" in link:
            urls.add(link["url"].rstrip("/"))
            if link["url"].rstrip("/") not in template:
                errs.append("Link %s: URL %s không có trong file Word." % (link.get("key"), link["url"]))
        elif "url_column" not in link:
            errs.append("Link %s phải có url hoặc url_column." % link.get("key"))
        elif link["url_column"] not in rules["file2"]["columns"]:
            errs.append("Link %s: cột '%s' chưa khai báo." % (link.get("key"), link["url_column"]))
        for ty in link.get("types", []):
            if ty not in rules["types"]:
                errs.append("Link %s: type '%s' không có." % (link.get("key"), ty))
    ignored = set(u.rstrip("/") for u in rules.get("ignored_urls", []))
    for url in sorted(set(u.rstrip("/.,;)") for u in re.findall(r"https?://[^\s|]+", template))):
        if url not in urls and url not in ignored:
            warns.append("URL trong file Word chưa dùng ở luật nào (thêm vào links hoặc "
                         "ignored_urls): %s" % url)
    ids = set()
    for pool in rules["pools"]:
        if not pool.get("items"):
            errs.append("Pool '%s' không có item." % pool.get("id"))
        if pool.get("match", "verbatim") not in ("verbatim", "reorderable_after_first", "contains"):
            errs.append("Pool '%s': match không hợp lệ." % pool.get("id"))
        for item in pool.get("items", []):
            quoted("Pool %s, item %s" % (pool.get("id"), item.get("id")), item.get("text", ""))
            if item["id"] in ids:
                errs.append("Item trùng id: %s" % item["id"])
            ids.add(item["id"])
            for ty in item.get("types", []):
                if ty not in rules["types"]:
                    errs.append("Pool %s, item %s: type '%s' không có." % (pool["id"], item["id"], ty))
    for c in rules.get("corrections", []):
        quoted("corrections", c["find"])
        if not c.get("why"):
            errs.append("corrections '%s' phải có lý do (why)." % c["find"])
    cl = rules.get("checklist_section")
    if cl:
        quoted("checklist_section.from", cl["from"])
        if cl.get("to"):
            quoted("checklist_section.to", cl["to"])
    for item in rules.get("judgement", []):
        quoted("judgement", item)
    return errs, warns


def summary(rules, products):
    """What was understood, for the user to confirm once."""
    out = ["## Luật đã đọc từ file Word: %s" % rules["name"], ""]
    out.append("**Excel:** sheet `%s`, %d sản phẩm. Cột: %s" % (
        rules["file2"].get("sheet") or "(đầu tiên)", len(products),
        ", ".join("%s=%s" % (k, s.get("header") or s.get("letter"))
                  for k, s in rules["file2"]["columns"].items())))
    out += ["", "| Type | Bullet | H2 theo thứ tự |", "| --- | --- | --- |"]
    for key, t in rules["types"].items():
        out.append("| %s | %s | %s |" % (key, " · ".join(t.get("bullets", [])),
                                        " → ".join(h["name"] for h in t["h2"])))
    for m in rules.get("modules", []):
        out.append("\n**Module %s:** khi %s; thêm H2 %s."
                   % (m["id"], json.dumps(m.get("when"), ensure_ascii=False),
                      ", ".join(h["name"] for h in m.get("h2", []))))
    out.append("\n**H2 cuối bài:** " + " → ".join(h["name"] for h in rules.get("closing_h2", [])))
    out.append("\n**Link:**")
    for link in rules["links"]:
        out.append("- %s: %s · %s%s" % (
            link["key"], link.get("url") or ("cột " + link["url_column"]),
            link.get("section") or link.get("block"), "" if link.get("required", True) else " · nếu có"))
    out.append("\n**Đoạn nguyên văn và cách chọn:**")
    for pool in rules["pools"]:
        out.append("- %s: %d mục, chọn theo `%s`, ghi ở dòng \"%s\"" % (
            pool["id"], len(pool["items"]), pool.get("selection", {}).get("method", "least_used"),
            pool.get("footer", "")))
    for s in rules.get("sequences", []):
        out.append("- %s: xoay vòng %s, ghi ở dòng \"%s\"" % (s["id"], "/".join(s["values"]), s["footer"]))
    d = rules["draft"]
    for key in ("meta_title", "meta"):
        if key in d:
            out.append("- %s: %s–%s ký tự (%s)" % (key, d[key].get("min"), d[key].get("max"),
                                                  d[key].get("severity", "error")))
    for c in rules.get("corrections", []):
        out.append("\n**Sửa so với file Word:** `%s` → `%s` (%s)" % (c["find"], c["replace"], c["why"]))
    if rules.get("questions"):
        out.append("\n**Chỗ file Word mơ hồ, cần bạn chốt:**")
        out += ["- " + q for q in rules["questions"]]
    if rules.get("judgement"):
        out.append("\n**Máy không kiểm được, Claude tự rà theo checklist:** %d luật." % len(rules["judgement"]))
    return "\n".join(out)


# --- Session ----------------------------------------------------------------
class Session(object):
    def __init__(self, workdir):
        self.dir = workdir
        path = os.path.join(workdir, "session.json")
        if not os.path.isfile(path):
            raise SystemExit("Chưa có %s: chạy init trước." % path)
        with open(path, encoding="utf-8") as fh:
            self.info = json.load(fh)
        self.template = self.read("template.txt")

    def read(self, name):
        with open(os.path.join(self.dir, name), encoding="utf-8") as fh:
            return fh.read()

    def rules(self):
        path = os.path.join(self.dir, "rules.json")
        if not os.path.isfile(path):
            raise SystemExit("Chưa có rules.json: Claude phải đọc template.txt và viết file này.")
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)

    def confirmed_rules(self):
        """Rules, only if the user confirmed them against this very template."""
        rules = self.rules()
        path = os.path.join(self.dir, "confirmed.json")
        state = {}
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as fh:
                state = json.load(fh)
        if state.get("template") != sha(self.template):
            print("Luật chưa được xác nhận hoặc file Word đã đổi. Chạy validate, cho người dùng "
                  "xem bảng luật, rồi confirm.")
            sys.exit(2)
        if state.get("rules") != sha(json.dumps(rules, sort_keys=True, ensure_ascii=False)):
            print("rules.json đã đổi sau khi xác nhận. Chạy validate, cho người dùng xem lại, "
                  "rồi confirm.")
            sys.exit(2)
        return rules

    def products(self, rules):
        """Products with the user's answers on top: answers.json is {"116": {"type": "...",
        "ok": true}}. Values replace the cell; "ok" records that HỎI items were settled."""
        products, has_paste = load_products(self.info["file2"], rules)
        path = os.path.join(self.dir, "answers.json")
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as fh:
                answers = json.load(fh)
            for p in products:
                for key, value in answers.get(str(p["stt"]), {}).items():
                    p["_answered" if key == "ok" else key] = value
        return products, has_paste


def cmd_init(args):
    os.makedirs(args.workdir, exist_ok=True)
    text = extract_docx(args.template)
    path = os.path.join(args.workdir, "template.txt")
    old = None
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as fh:
            old = fh.read()
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    with open(os.path.join(args.workdir, "file2-columns.txt"), "w", encoding="utf-8") as fh:
        fh.write(describe_file2(args.file2))
    with open(os.path.join(args.workdir, "session.json"), "w", encoding="utf-8") as fh:
        json.dump({"template": os.path.abspath(args.template),
                   "file2": os.path.abspath(args.file2)}, fh, ensure_ascii=False, indent=1)
    has_rules = os.path.isfile(os.path.join(args.workdir, "rules.json"))
    print("→ %s (%d dòng)" % (path, text.count("\n")))
    print("→ %s" % os.path.join(args.workdir, "file2-columns.txt"))
    if old is None or not has_rules:
        print("TRẠNG THÁI: MỚI. Đọc toàn bộ template.txt và file2-columns.txt, viết rules.json "
              "theo common/rules-schema.md, rồi chạy validate.")
    elif old == text:
        print("TRẠNG THÁI: KHÔNG ĐỔI. Dùng lại rules.json, chạy preflight.")
    else:
        diff = list(difflib.unified_diff(old.splitlines(), text.splitlines(), "cũ", "mới", lineterm="", n=1))
        with open(os.path.join(args.workdir, "template.diff"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(diff) + "\n")
        print("TRẠNG THÁI: FILE WORD ĐÃ ĐỔI (%d dòng khác). Đọc template.diff, cập nhật rules.json, "
              "báo người dùng luật nào đổi, rồi validate và confirm lại." % len(diff))
    return 0


def cmd_validate(args):
    s = Session(args.workdir)
    rules = s.rules()
    errs, warns = validate_rules(rules, s.template)
    products = []
    if not errs:
        try:
            products, _ = s.products(rules)
        except SystemExit as e:
            errs.append(str(e))
    unknown = sorted(set(p.get("type", "") for p in products if type_of(p, rules) is None))
    for name in unknown:
        warns.append("Product type trong Excel không khớp type nào: '%s'" % name)
    for e in errs:
        print("ERROR: " + e)
    for w in warns:
        print("WARN: " + w)
    if errs:
        print("\n%d ERROR: sửa rules.json rồi chạy lại." % len(errs))
        return 1
    print(summary(rules, products))
    print("\nHợp lệ. Cho người dùng xem bảng trên; họ đồng ý thì chạy confirm.")
    return 0


def cmd_confirm(args):
    s = Session(args.workdir)
    rules = s.rules()
    errs, _ = validate_rules(rules, s.template)
    if errs:
        print("Chưa hợp lệ, chạy validate.")
        return 1
    with open(os.path.join(args.workdir, "confirmed.json"), "w", encoding="utf-8") as fh:
        json.dump({"template": sha(s.template),
                   "rules": sha(json.dumps(rules, sort_keys=True, ensure_ascii=False))}, fh)
    cl = rules.get("checklist_section")
    if cl:
        with open(os.path.join(args.workdir, "checklist.txt"), "w", encoding="utf-8") as fh:
            fh.write(checklist_text(s.template, cl))
    print("Đã xác nhận luật cho file Word này.")
    return 0


def checklist_text(template, cl):
    lines = template.splitlines()
    start = next((i for i, l in enumerate(lines) if norm(cl["from"]) in norm(l)), 0)
    end = len(lines)
    if cl.get("to"):
        end = next((i for i, l in enumerate(lines) if i > start and norm(cl["to"]) in norm(l)), end)
    else:
        end = next((i for i, l in enumerate(lines) if i > start and l.startswith("=== ")), end)
    return "\n".join(lines[start:end]) + "\n"


# --- Preflight --------------------------------------------------------------
def select(products, args, rules):
    out = products
    if getattr(args, "no", None):
        wanted = pdplib.parse_stt_list(args.no)
        out = [p for p in products if p["stt"] in wanted]
        gone = [n for n in wanted if n not in [p["stt"] for p in products]]
        if gone:
            raise SystemExit("Không có sản phẩm No.: %s" % ", ".join(map(str, gone)))
    if getattr(args, "pic", None):
        cols = rules["file2"].get("pic_columns", [])
        if not cols:
            raise SystemExit("rules.json chưa khai báo file2.pic_columns.")
        name = norm(args.pic).lower()
        out = [p for p in out if any(name in norm(p.get(c, "")).lower() for c in cols)]
    return out


def preflight_issues(p, rules, has_paste):
    out = []
    for cond in rules["file2"].get("skip_when", []):
        if when_ok(cond, p):
            return [("BỎ QUA", "dòng này được đánh dấu không cần viết")]
    for key in rules["file2"].get("required", []):
        if pdplib.is_empty(p.get(key)):
            out.append(("THIẾU", "ô '%s' trống" % key))
    tkey = type_of(p, rules)
    if tkey is None:
        out.append(("THIẾU", "Product type '%s' không khớp type nào trong file Word" % p.get("type", "")))
    else:
        low = norm(p.get("name", "")).lower()
        for other, t in rules["types"].items():
            if other != tkey and any(norm(w).lower() in low for w in t.get("name_keywords", [])):
                out.append(("HỎI", "tên sản phẩm gợi ý type %s nhưng Excel ghi %s" % (other, tkey)))
        for link in rules["links"]:
            if "url_column" in link and link.get("required", True) and applies(link, p, tkey) \
                    and not filled(p.get(link["url_column"])):
                out.append(("THIẾU", "thiếu URL cột '%s'" % link["url_column"]))
    paste = p.get("page_content") or ""
    if not has_paste:
        out.append(("THIẾU", "chưa có cột 'Nội dung trang web (dán)'"))
    elif not filled(paste):
        out.append(("THIẾU", "chưa dán nội dung trang web"))
    else:
        if not re.search(r"https?://", paste):
            out.append(("LƯU Ý", "phần dán không có dòng URL, không biết câu nào từ trang nào"))
        if len(paste) >= CELL_LIMIT - 1000:
            out.append(("LƯU Ý", "phần dán gần giới hạn %d ký tự của ô Excel, có thể đã bị cắt"
                        % CELL_LIMIT))
    odd = [c for c in list_cell(p.get("colours", "")) if "(" in c]
    if odd:
        out.append(("HỎI", "tên màu có vẻ kèm mô tả, xác nhận đúng như trên website: %s"
                    % "; ".join(odd)))
    if p.get("_answered"):
        out = [i for i in out if i[0] != "HỎI"]
    return out


def cmd_preflight(args):
    s = Session(args.workdir)
    rules = s.confirmed_rules()
    products, has_paste = s.products(rules)
    chosen = select(products, args, rules)
    if not chosen:
        print("Không có sản phẩm nào khớp lựa chọn.")
        return 3
    rows, details, ready = [], [], 0
    for p in chosen:
        issues = preflight_issues(p, rules, has_paste)
        counts = {}
        for lvl, _ in issues:
            counts[lvl] = counts.get(lvl, 0) + 1
        if counts.get("THIẾU"):
            status = "THIẾU %d" % counts["THIẾU"]
        elif counts.get("BỎ QUA"):
            status = "bỏ qua"
        elif counts.get("HỎI"):
            status = "HỎI %d" % counts["HỎI"]
        else:
            status = "sẵn sàng"
            ready += 1
        rows.append("%d | %s | %s | %s | %s" % (
            p["stt"], p["name"], type_of(p, rules) or "?",
            "có" if filled(p.get("page_content")) else "chưa", status))
        if issues:
            details.append("- **No. %d**: " % p["stt"] + "; ".join("%s: %s" % i for i in issues))
    if not has_paste or any(not filled(p.get("page_content")) for p in chosen):
        print(REMINDER + "\n")
    print("No. | Sản phẩm | Type | Dán trang | Trạng thái")
    print("--- | --- | --- | --- | ---")
    print("\n".join(rows))
    if details:
        print("\n### Cần bổ sung hoặc trả lời trước khi viết\n")
        print("\n".join(details))
    print("\n%d/%d sản phẩm sẵn sàng." % (ready, len(chosen)))
    return 0 if ready == len(chosen) else 3


# --- Plans: everything the card and the checker agree on ---------------------
def applies(link, p, tkey):
    return (not link.get("types") or tkey in link["types"]) and when_ok(link.get("when"), p)


def link_plan(p, tkey, rules):
    plan = []
    for link in rules["links"]:
        if not applies(link, p, tkey):
            continue
        url = link.get("url") or p.get(link.get("url_column", ""), "")
        if not filled(url):
            continue
        anchors = list(link.get("anchors", []))
        if link.get("anchor_from"):
            anchors.append(p.get(link["anchor_from"], ""))
        plan.append(dict(link, url=url.strip(), anchors=anchors))
    return plan


def h2_plan(p, tkey, rules):
    """(ordered [(name, required, mode)], index where free-named H2s may sit)."""
    items = list(rules["types"][tkey]["h2"])
    split = sum(1 for h in items if h["kind"] == "specific")
    for m in rules.get("modules", []):
        if when_ok(m.get("when"), p):
            items[split:split] = m.get("h2", [])
            split += len(m.get("h2", []))
    slot = len(items)
    items += rules["types"][tkey].get("closing_h2", rules.get("closing_h2", []))
    return [(fill_name(h["name"], p, rules), h.get("required", False), h.get("mode", ""))
            for h in items], slot


def fill_name(name, p, rules):
    """H2 names with a slot, e.g. 'About [Brand] & ...' when Word names it that way."""
    for mark, col in rules.get("name_placeholders", {}).items():
        name = name.replace(mark, p.get(col, ""))
    return name


def footer_value(text, label):
    m = re.search(r"^[\s*>-]*%s\**\s*:\**\s*(.+?)\s*$" % re.escape(label), text, re.M)
    return m.group(1).replace("*", "").strip() if m else None


def drafts_before(p, products, workdir):
    """[(product, text)] for saved drafts earlier in file order (the 'thread')."""
    out = []
    for q in products:
        if q["_order"] >= p["_order"]:
            break
        path = os.path.join(pdplib.product_dir(workdir, q), "draft.md")
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as fh:
                out.append((q, fh.read()))
    return out


def eligible_items(pool, p, tkey):
    return [i for i in pool["items"]
            if (not i.get("types") or tkey in i["types"]) and when_ok(i.get("when"), p)]


def pick_item(pool, p, tkey, history):
    """(item or None, table text). least_used: fewest uses in this workdir, never the
    previous one when another is eligible, first by id on a tie."""
    items = eligible_items(pool, p, tkey)
    if not items:
        return None, "không có mục phù hợp"
    ids = [i["id"] for i in items]
    used = {i: 0 for i in ids}
    prev = None
    for q, text in history:
        value = footer_value(text, pool["footer"])
        if value in used:
            used[value] += 1
            prev = value
        elif pool.get("previous_scope", "any") == "any":
            prev = value
    table = "đã dùng: %s · liền trước: %s" % (", ".join("%s=%d" % kv for kv in used.items()), prev or "-")
    if pool.get("selection", {}).get("method") == "writer":
        return None, table + " · Claude chọn theo file Word"
    cand = [i for i in items if i["id"] != prev] or items
    return min(cand, key=lambda i: used[i["id"]]), table


def pool_text(item, pool, p, rules):
    text = item["text"]
    for c in rules.get("corrections", []):
        text = text.replace(c["find"], c["replace"])
    # Lookups first: a looked-up value may itself hold a placeholder ("an official [Brand] retailer")
    for mark, table in pool.get("lookups", {}).items():
        value = norm(p.get(table["column"], "")).lower()
        found = next((v for k, v in table["values"].items() if norm(k).lower() == value),
                     table.get("default", ""))
        text = text.replace(mark, found)
    for mark, col in pool.get("placeholders", {}).items():
        text = text.replace(mark, p.get(col, ""))
    return text


def plain_pool(text):
    return norm(text.replace("[", "").replace("]", ""))


def pick_sequence(seq, p, history):
    if not when_ok(seq.get("when"), p):
        return seq.get("not_applicable")
    last, column = None, seq.get("restart_when_changed")
    for q, text in reversed(history):
        value = footer_value(text, seq["footer"])
        if value in seq["values"]:
            if not column or norm(q.get(column, "")) == norm(p.get(column, "")):
                last = value
            break
    if last is None:
        return seq["values"][0]
    return seq["values"][(seq["values"].index(last) + 1) % len(seq["values"])]


def focus_targets(p, rules):
    fm = rules.get("focus_map", {})
    return [(f, fm.get(f, "?")) for f in list_cell(p.get("focus", ""))]


# --- Card -------------------------------------------------------------------
def card_markdown(p, products, s, rules):
    tkey = type_of(p, rules)
    out = ["## No. %d · %s" % (p["stt"], p["name"])]
    if tkey is None:
        out.append("**BLOCK:** Product type '%s' không khớp type nào." % p.get("type", ""))
        return "\n".join(out), False
    t = rules["types"][tkey]
    history = drafts_before(p, products, s.dir)
    mods = [m["id"] for m in rules.get("modules", []) if when_ok(m.get("when"), p)]
    out.append("Type **%s**%s" % (tkey, (" · Module: **%s**" % ", ".join(mods)) if mods else ""))
    if t.get("lead"):
        out.append("Lead: %s" % t["lead"])
    plan, slot = h2_plan(p, tkey, rules)
    out.append("H2 đúng thứ tự: " + " | ".join(
        "%s%s%s" % (n, "*" if r else "", (" (%s)" % m) if m else "") for n, r, m in plan))
    out.append("(* = bắt buộc; không có dữ liệu thì bỏ H2. H2 tính năng riêng đặt trước %s.)"
               % (plan[slot][0] if slot < len(plan) else "cuối bài"))
    out.append("Bullet đúng thứ tự: " + " | ".join(t.get("bullets", [])))
    for f, h in focus_targets(p, rules):
        out.append("Writing focus **%s** → viết sâu: %s" % (f, h))
    if filled(p.get("differentiator")):
        out.append("Differentiator: %s" % p["differentiator"])
    for seq in rules.get("sequences", []):
        value = pick_sequence(seq, p, history)
        out.append("%s: **%s**%s" % (seq["footer"], value,
                                     (" · " + seq.get("guidance", {}).get(value, ""))
                                     if seq.get("guidance", {}).get(value) else ""))
    out.append("\n**Màu (đúng tên):** %s" % ("; ".join(list_cell(p.get("colours", ""))) or "-"))
    out.append("**Size (đủ, kể cả hết hàng):** %s" % ("; ".join(list_cell(p.get("sizes", ""))) or "-"))
    out.append("\n**Đoạn nguyên văn** (dấu [ ] là chỗ gắn link):")
    for pool in rules["pools"]:
        item, table = pick_item(pool, p, tkey, history)
        if item:
            out.append("- %s **%s** (%s): %s" % (pool["footer"], item["id"], table, pool_text(item, pool, p, rules)))
        else:
            out.append("- %s: %s. Nếu không có mục nào, ghi `%s: %s`." % (
                pool["footer"], table, pool["footer"], pool.get("absent_value", "")))
    out.append("\n**Link** (mỗi URL đúng 1 lần, không có link khác):")
    for link in link_plan(p, tkey, rules):
        out.append("- [%s] \"%s\" → %s · %s" % (
            "BẮT BUỘC" if link.get("required", True) else "được phép",
            " / ".join(a for a in link["anchors"] if a), link["url"],
            link.get("where") or link.get("section") or link.get("block")))
    labels = rules["file2"]["columns"]
    out.append("\n**Dữ liệu Excel** (lệch với web thì theo Excel và ghi vào phần Conflict):")
    for key in rules["file2"].get("card_columns", []) + t.get("columns", []):
        if filled(p.get(key)):
            out.append("- **%s:** %s" % (labels.get(key, {}).get("header", key), p[key].replace("\n", " ⏎ ")))
    if os.path.isfile(os.path.join(s.dir, "checklist.txt")):
        out.append("\nChecklist cuối bài: `checklist.txt`. Luật đầy đủ: `template.txt`.")
    return "\n".join(out), True


def cmd_card(args):
    s = Session(args.workdir)
    rules = s.confirmed_rules()
    products, _ = s.products(rules)
    blocked = False
    for p in select(products, args, rules):
        text, ok = card_markdown(p, products, s, rules)
        print(text + "\n")
        blocked = blocked or not ok
        if not ok:
            continue
        d = pdplib.product_dir(args.workdir, p)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "card.md"), "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        pasted = generic.brand_info_from_row(p)
        if pasted:
            with open(os.path.join(d, "brand-info.txt"), "w", encoding="utf-8") as fh:
                fh.write(pasted)
        print("→ %s" % d)
    return 2 if blocked else 0


# --- Draft check ------------------------------------------------------------
def shim(rules):
    """The parts of a category config the block parser and to_html.py read."""
    blocks = dict(DEFAULT_BLOCKS)
    wanted = rules["draft"].get("blocks", ["meta_title", "meta", "short", "long"])
    blocks = {k: v for k, v in blocks.items() if k in wanted or k == "notes"}
    return {"draft": {"blocks": blocks,
                      "html_blocks": [k for k in ("short", "long") if k in wanted]}}


def _located_links(blocks):
    """Every link with (block, section, paragraph index, line number, raw paragraph)."""
    out = []
    for block in ("short", "long"):
        section, para, cur = None, 0, []
        for n, line in blocks.get(block, []) + [(0, "")]:
            if line.startswith("## "):
                section, para = generic.plain(line[3:]).strip(), 0
                continue
            if not line.strip():
                if cur:
                    para += 1
                cur = []
                continue
            cur.append(line)
            for m in generic.LINK_RE.finditer(line):
                out.append(dict(block=block, section=section, para=para, line=n, raw=line,
                                anchor=m.group(1), url=m.group(2).rstrip("/")))
    return out


def _length(rep, value, spec, what):
    if not value or not spec:
        return
    lo, hi = spec.get("min", 0), spec.get("max", 10 ** 6)
    if not lo <= len(value) <= hi:
        msg = "%s dài %d ký tự (cần %d–%d)." % (what, len(value), lo, hi)
        (rep.error if spec.get("severity", "error") == "error" else rep.warn)(0, msg)


def check_draft(text, p, products, s, rules):
    rep = generic.Report()
    cfg = shim(rules)
    d = rules["draft"]
    tkey = type_of(p, rules)
    t = rules["types"][tkey]
    blocks = generic.parse_blocks(text, cfg)
    for key in d.get("blocks", ["meta_title", "meta", "short", "long"]):
        if key not in blocks:
            rep.error(0, "Thiếu khối '# %s'." % DEFAULT_BLOCKS[key])
    content = [(n, l) for k in ("h1", "meta_title", "meta", "short", "long") for n, l in blocks.get(k, [])]
    for n, line in content:
        for ch in d.get("banned_chars", []):
            if ch in line:
                rep.error(n, "Ký tự bị cấm '%s'." % ch)
        bare = generic.plain(line)
        for ph in d.get("banned_phrases", []):
            if generic.contains_phrase(bare, ph):
                rep.error(n, "Cụm bị cấm: '%s'." % ph)
        for us, uk in d.get("spelling", {}).items():
            if re.search(r"\b%s\b" % re.escape(us), bare, re.I):
                rep.error(n, "Chính tả: '%s' → '%s'." % (us, uk))

    title = generic.joined(blocks.get("meta_title", []))
    meta = generic.joined(blocks.get("meta", []))
    _length(rep, title, d.get("meta_title"), "Meta title")
    _length(rep, meta, d.get("meta"), "Meta description")
    for key, value in (("meta_title", title), ("meta", meta)):
        for col in d.get(key, {}).get("must_include", []):
            if value and norm(p.get(col, "")).lower() not in norm(value).lower():
                rep.warn(0, "%s nên có '%s'." % (key, p.get(col, "")))

    # Short description
    sd = d.get("short", {})
    short = blocks.get("short", [])
    paras = generic.paragraphs(short)
    bullets = [(n, generic.BULLET_RE.match(l).group(1)) for n, l in short if generic.BULLET_RE.match(l)]
    non_bullet = [pp for pp in paras if not generic.BULLET_RE.match(pp[0][1])]
    opening = generic.joined(non_bullet[0]) if non_bullet else ""
    if "short" in blocks and not opening:
        rep.error(0, "Short description thiếu đoạn mở đầu.")
    if opening and sd.get("opening_sentences"):
        lo, hi = sd["opening_sentences"]
        if not lo <= len(generic.sentences(opening)) <= hi:
            rep.error(non_bullet[0][0][0], "Đoạn mở đầu %d câu (cần %d–%d)."
                      % (len(generic.sentences(opening)), lo, hi))
    allowed = t.get("bullets", [])
    seen = []
    for n, body in bullets:
        m = generic.LABEL_RE.match(body.strip())
        label = (m.group(1) if m else body.split(":", 1)[0]).strip()
        if ":" not in body:
            rep.error(n, "Bullet phải dạng 'Label: value'.")
        if label == sd.get("no_link_bullet") and generic.LINK_RE.search(body):
            rep.error(n, "Bullet '%s' không được có link." % label)
        if not allowed:
            continue  # Word gives no fixed label list for this type
        if label not in allowed:
            rep.error(n, "Nhãn bullet '%s' không có trong type này (%s)." % (label, " | ".join(allowed)))
            continue
        seen.append((n, allowed.index(label), label))
    for (_, i1, l1), (n2, i2, l2) in zip(seen, seen[1:]):
        if i2 <= i1:
            rep.error(n2, "Thứ tự bullet sai: '%s' phải đứng trước '%s'." % (l2, l1))
    if sd.get("bridge_sentences") and bullets:
        after = non_bullet[1:]
        if not after:
            rep.error(0, "Short description thiếu câu dẫn sau bullet.")
        else:
            lo, hi = sd["bridge_sentences"]
            count = sum(len(generic.sentences(generic.joined(pp))) for pp in after)
            if not lo <= count <= hi:
                rep.error(after[0][0][0], "Câu dẫn %d câu (cần %d–%d)." % (count, lo, hi))
    for m in rules.get("modules", []):
        if when_ok(m.get("when"), p):
            for key, words in m.get("must_mention", {}).items():
                value = generic.plain(" ".join(l for _, l in blocks.get(key, [])))
                if value and not any(generic.contains_phrase(value, w) for w in words):
                    rep.error(0, "Module %s: khối %s phải nhắc %s." % (m["id"], key, " / ".join(words)))

    # H2
    plan, slot = h2_plan(p, tkey, rules)
    names = [n.lower() for n, _, _ in plan]
    secs = generic.h2_sections(blocks.get("long", []))
    last = -1.0
    for n, title_, _ in secs:
        low = title_.lower()
        if low in names:
            i = float(names.index(low))
        elif rules.get("extra_h2"):
            rep.warn(n, "H2 tự đặt '%s': chỉ hợp lệ nếu là tính năng đủ dữ liệu theo file Word." % title_)
            i = slot - 0.5
            if last > i:
                rep.error(n, "H2 '%s' phải đứng trước %s." % (title_, plan[slot][0]))
        else:
            rep.error(n, "H2 '%s' không có trong type %s." % (title_, tkey))
            continue
        if i < last:
            rep.error(n, "H2 '%s' sai thứ tự." % title_)
        last = max(last, i)
    present = set(x.lower() for _, x, _ in secs)
    for name, required, _ in plan:
        if required and name.lower() not in present:
            rep.error(0, "Thiếu H2 bắt buộc '%s'." % name)
    for n, line in blocks.get("long", []):
        if line.startswith("#") and generic.LINK_RE.search(line):
            rep.error(n, "Không đặt link trong heading.")

    # Links
    plan_links = link_plan(p, tkey, rules)
    by_url = {x["url"].rstrip("/"): x for x in plan_links}
    located = _located_links(blocks)
    first = {}
    for loc in located:
        if loc["url"] in first:
            rep.error(loc["line"], "URL bị link 2 lần: %s" % loc["url"])
            continue
        first[loc["url"]] = loc
        link = by_url.get(loc["url"])
        if link is None:
            if rules.get("no_other_links", True):
                rep.error(loc["line"], "Link không có trong danh sách: %s" % loc["url"])
            continue
        if norm(loc["anchor"]).lower() == norm(p.get("name", "")).lower():
            rep.error(loc["line"], "Không dùng tên sản phẩm làm anchor.")
        if link.get("block") and link["block"] != loc["block"]:
            rep.error(loc["line"], "Link %s phải nằm ở %s." % (loc["url"], link.get("where") or link["block"]))
        section = fill_name(link.get("section") or "", p, rules)
        if section and (loc["section"] or "").lower() != section.lower():
            rep.error(loc["line"], "Link %s phải nằm trong H2 %s." % (loc["url"], section))
        if "paragraph" in link and loc["para"] != link["paragraph"]:
            rep.error(loc["line"], "Link %s sai đoạn (cần đoạn %d)." % (loc["url"], link["paragraph"] + 1))
        anchors = [a for a in link["anchors"] if a]
        if anchors and not any(norm(a).lower() in norm(loc["anchor"]).lower() for a in anchors):
            rep.error(loc["line"], "Anchor '%s' không đúng (%s)." % (loc["anchor"], " / ".join(anchors)))
    for link in plan_links:
        if link.get("required", True) and link["url"].rstrip("/") not in first:
            rep.error(0, "Thiếu link \"%s\" → %s." % (" / ".join(a for a in link["anchors"] if a), link["url"]))
        other = next((x for x in plan_links if x["key"] == link.get("not_same_sentence_as")), None)
        loc = first.get(link["url"].rstrip("/"))
        if other is not None and loc:
            for sent in generic.SENT_SPLIT.split(loc["raw"]):
                if link["url"].rstrip("/") in sent and other["url"].rstrip("/") in sent:
                    rep.error(loc["line"], "Link %s và %s không được cùng một câu." % (link["key"], other["key"]))

    # Word-for-word paragraphs and the rotation counters
    history = drafts_before(p, products, s.dir)
    by_section = {x.lower(): lines for _, x, lines in secs}
    for pool in rules["pools"]:
        value = footer_value(text, pool["footer"])
        if value is None:
            rep.error(0, "Thiếu dòng cuối bài '%s: …'." % pool["footer"])
            continue
        items = eligible_items(pool, p, tkey)
        if not items and value == pool.get("absent_value"):
            continue
        item = next((i for i in items if i["id"] == value), None)
        if item is None:
            rep.error(0, "%s '%s' không hợp lệ cho sản phẩm này (hợp lệ: %s)."
                      % (pool["footer"], value, ", ".join(i["id"] for i in items) or "không có"))
            continue
        want, _ = pick_item(pool, p, tkey, history)
        if want is not None and want["id"] != value:
            rep.warn(0, "%s nên là %s theo số lần dùng (đang %s): chỉ đổi khi người dùng chỉ định "
                     "hoặc file Word cho phép." % (pool["footer"], want["id"], value))
        section = fill_name(pool["section"], p, rules)
        lines = by_section.get(section.lower())
        pp = generic.paragraphs(lines) if lines else []
        idx = pool.get("paragraph", 0)
        if len(pp) <= idx:
            rep.error(0, "H2 %s thiếu đoạn thứ %d (%s)." % (section, idx + 1, pool["id"]))
            continue
        got = norm(generic.plain(generic.joined(pp[idx])))
        expected = plain_pool(pool_text(item, pool, p, rules))
        mode = pool.get("match", "verbatim")
        if mode == "contains":
            good = expected in got
        elif mode == "reorderable_after_first":
            a, b = generic.sentences(expected), generic.sentences(got)
            good = bool(b) and a[0] == b[0] and sorted(a) == sorted(b)
        else:
            good = expected == got
        if not good:
            rep.error(pp[idx][0][0], "Đoạn %s không khớp nguyên văn mục %s. Đúng là:\n    %s"
                      % (pool["id"], value, expected))
    for seq in rules.get("sequences", []):
        value = footer_value(text, seq["footer"])
        want = pick_sequence(seq, p, history)
        if value is None:
            rep.error(0, "Thiếu dòng cuối bài '%s: …'." % seq["footer"])
        elif value != want:
            rep.error(0, "%s phải là %s (đang %s)." % (seq["footer"], want, value))

    # Colours and sizes from the sheet; numbers from a source
    data = rules.get("data", {})
    body_text = generic.plain(" ".join(l for k in ("short", "long") for _, l in blocks.get(k, [])))
    body_norm = norm(body_text)
    if data.get("colours_exact", True):
        missing = [c for c in list_cell(p.get("colours", "")) if norm(c).lower() not in body_norm.lower()]
        if missing:
            rep.error(0, "Thiếu màu đúng tên File (2): %s." % "; ".join(missing))
    sold = list_cell(p.get("sizes", ""))
    if data.get("sizes_all", True):
        missing = [c for c in sold if norm(c).lower() not in body_norm.lower()]
        if missing:
            rep.error(0, "Thiếu size trong bài: %s." % "; ".join(missing))
    if data.get("size_pattern"):
        known = set(norm(c).lower() for c in sold)
        for m in sorted(set(re.findall(data["size_pattern"], body_norm))):
            if norm(m).lower() not in known and not any(m in x for x in pool_texts(rules, p, tkey)):
                rep.error(0, "Size '%s' không có trong size DE bán (%s)." % (m, "; ".join(sold)))
    brand_info = ""
    info_path = os.path.join(pdplib.product_dir(s.dir, p), "brand-info.txt")
    if os.path.isfile(info_path):
        with open(info_path, encoding="utf-8") as fh:
            brand_info = fh.read()
    if data.get("numbers_source", "any") != "off":
        own = [brand_info, p.get("name", ""), p.get("sizes", ""), p.get("colours", "")]
        own += pool_texts(rules, p, tkey)
        if data.get("numbers_source", "any") == "any":
            own += [v for v in p.values() if isinstance(v, str)]
        known_nums = set(generic.numbers("\n".join(own)))
        for n, line in [(n, l) for k in ("meta_title", "meta", "short", "long") for n, l in blocks.get(k, [])]:
            for v in generic.numbers(generic.plain(line)):
                if v not in known_nums:
                    rep.warn(n, "Số '%s' không có trong nguồn được phép: kiểm tra, không có thì bỏ." % v)

    # Wording shared with earlier drafts
    dup = rules.get("duplicate_check")
    if dup:
        size = dup.get("ngram", 6)
        skip = set(x.lower() for x in dup.get("exclude_sections", []))
        own_name = set(pdplib.words(p.get("name", "")))
        mine = _section_words(secs, skip, own_name)
        for q, other in history:
            if not when_ok(dup.get("when"), p):
                break
            osecs = generic.h2_sections(generic.parse_blocks(other, cfg).get("long", []))
            theirs = _section_words(osecs, skip, set(pdplib.words(q.get("name", ""))))
            grams = set(tuple(theirs[i:i + size]) for i in range(len(theirs) - size + 1))
            hits = [" ".join(mine[i:i + size]) for i in range(len(mine) - size + 1)
                    if tuple(mine[i:i + size]) in grams]
            if hits:
                rep.warn(0, "Trùng cụm %d từ với No. %d: '%s' (%d chỗ)." % (size, q["stt"], hits[0], len(hits)))
            ofirst = {x.lower(): generic.sentences(generic.joined(ls))[:1] for _, x, ls in osecs}
            for _, x, ls in secs:
                if x.lower() in skip:
                    continue
                f = generic.sentences(generic.joined(ls))[:1]
                if f and f == ofirst.get(x.lower()):
                    rep.error(0, "Câu mở đầu H2 '%s' giống No. %d." % (x, q["stt"]))
    return rep


def _section_words(secs, skip, drop):
    out = []
    for _, title, lines in secs:
        if title.lower() in skip:
            continue
        text = " ".join(l for _, l in lines if not l.lstrip().startswith("|"))
        out += [w for w in pdplib.words(generic.plain(text)) if w not in drop]
    return out


def pool_texts(rules, p, tkey):
    return [pool_text(i, pool, p, rules) for pool in rules["pools"] for i in eligible_items(pool, p, tkey)]


def one_product(args, products):
    wanted = pdplib.parse_stt_list(args.no)
    if len(wanted) != 1:
        raise SystemExit("Chỉ một sản phẩm mỗi lần.")
    return pdplib.find_product(products, wanted[0])


def cmd_check(args):
    s = Session(args.workdir)
    rules = s.confirmed_rules()
    products, _ = s.products(rules)
    p = one_product(args, products)
    if type_of(p, rules) is None:
        print("Product type không khớp type nào.")
        return 2
    path = args.draft or os.path.join(pdplib.product_dir(args.workdir, p), "draft.md")
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    rep = check_draft(text, p, products, s, rules)
    for kind, line, msg in rep.items:
        print("%s%s %s" % (kind, " L%d" % line if line else "", msg))
    errs = len(rep.errors())
    warns = sum(1 for k, _, _ in rep.items if k == "WARN")
    print("%d ERROR, %d WARN. %s" % (errs, warns, "Sửa đến 0 ERROR." if errs else
                                     "Xét từng WARN rồi rà checklist.txt từng dòng."))
    return 1 if errs else 0


def cmd_html(args):
    s = Session(args.workdir)
    rules = s.confirmed_rules()
    products, _ = s.products(rules)
    p = one_product(args, products)
    folder = pdplib.product_dir(args.workdir, p)
    with open(os.path.join(folder, "draft.md"), encoding="utf-8") as fh:
        text = fh.read()
    rep = check_draft(text, p, products, s, rules)
    if rep.errors():
        print("Draft còn %d ERROR: chạy check và sửa trước khi xuất." % len(rep.errors()))
        return 1
    cfg = shim(rules)
    labels = [x["footer"] for x in rules["pools"]] + [x["footer"] for x in rules.get("sequences", [])]
    notes = ["%s: %s" % (l, footer_value(text, l)) for l in labels if footer_value(text, l)]
    for name, content in (("ban-text.html", to_html.submit_text_page(text, cfg)),
                          ("ban-html.txt", to_html.submit_html(text, cfg)),
                          ("ban-ghi-chu.txt", "\n".join(notes) + "\n")):
        with open(os.path.join(folder, name), "w", encoding="utf-8") as fh:
            fh.write(content)
        print("→ %s" % os.path.join(folder, name))
    return 0


def main(argv=None):
    pdplib.utf8_stdio()
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    init = sub.add_parser("init")
    init.add_argument("--template", required=True)
    init.add_argument("--file2", required=True)
    init.add_argument("--workdir", required=True)
    init.set_defaults(func=cmd_init)
    for name, func in (("validate", cmd_validate), ("confirm", cmd_confirm),
                       ("preflight", cmd_preflight), ("card", cmd_card),
                       ("check", cmd_check), ("html", cmd_html)):
        c = sub.add_parser(name)
        c.add_argument("--workdir", required=True)
        c.set_defaults(func=func)
        if name in ("preflight", "card", "check", "html"):
            c.add_argument("--no", required=name != "preflight", help="ví dụ 94 | 94,95 | 94-97")
        if name == "preflight":
            c.add_argument("--pic", help="chỉ các dòng có tên này ở cột PIC")
        if name == "check":
            c.add_argument("--draft")
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
