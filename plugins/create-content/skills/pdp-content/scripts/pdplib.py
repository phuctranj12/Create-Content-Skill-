# -*- coding: utf-8 -*-
"""Shared helpers for the pdp-content skill.

Standard library only: reads File (2) (.xlsx) without openpyxl, loads the
category config, and derives every value the workflow fixes by rule (outline,
About version, {Role}, required links, near-duplicate products) so Claude
never spends tokens re-deriving them or gets them wrong.
"""

import json
import os
import re
import sys
import unicodedata
import zipfile
from xml.etree import ElementTree as ET

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATEGORIES_DIR = os.path.join(SKILL_DIR, "categories")

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
REL_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"

NA = "/"  # File (2) convention: "/" = not applicable (different from empty)


def utf8_stdio():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


# --- Minimal xlsx reader ----------------------------------------------------
def _col_index(ref):
    letters = re.match(r"([A-Z]+)", ref).group(1)
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def _si_text(si):
    # Plain <t> or rich-text runs <r><t>; skip phonetic <rPh>.
    parts = []
    for child in si:
        tag = child.tag.replace(NS, "")
        if tag == "t":
            parts.append(child.text or "")
        elif tag == "r":
            parts.extend(t.text or "" for t in child.iter(NS + "t"))
    return "".join(parts)


def read_sheet(path, sheet_name=None):
    """Rows of one worksheet (default: the first) as lists of strings."""
    with zipfile.ZipFile(path) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            shared = [_si_text(si) for si in root.findall(NS + "si")]
        workbook = ET.fromstring(z.read("xl/workbook.xml"))
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        targets = {r.get("Id"): r.get("Target") for r in rels}
        sheets = list(workbook.find(NS + "sheets"))
        chosen = sheets[0] if sheet_name is None else next(
            (s for s in sheets if s.get("name") == sheet_name), None)
        if chosen is None:
            raise SystemExit("Không thấy sheet: %s" % sheet_name)
        target = targets[chosen.get(REL_NS + "id")]
        target = target.lstrip("/")
        if not target.startswith("xl/"):
            target = "xl/" + target
        sheet_xml = ET.fromstring(z.read(target))

    rows = []
    for row in sheet_xml.find(NS + "sheetData").findall(NS + "row"):
        cells = {}
        for cell in row.findall(NS + "c"):
            kind = cell.get("t")
            value = cell.find(NS + "v")
            inline = cell.find(NS + "is")
            if kind == "s" and value is not None:
                text = shared[int(value.text)]
            elif kind == "inlineStr" and inline is not None:
                text = "".join(t.text or "" for t in inline.iter(NS + "t"))
            elif value is not None:
                text = value.text or ""
            else:
                text = ""
            cells[_col_index(cell.get("r"))] = text
        width = max(cells) + 1 if cells else 0
        rows.append([cells.get(i, "") for i in range(width)])
    return rows


# --- Text helpers -----------------------------------------------------------
def norm_header(text):
    text = unicodedata.normalize("NFC", text or "")
    text = text.replace("’", "'").replace("‘", "'")
    return re.sub(r"\s+", " ", text).strip().lower()


def strip_accents(text):
    text = unicodedata.normalize("NFD", text or "")
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


def words(text):
    return re.findall(r"[a-z0-9]+", strip_accents(text).lower())


def slugify(text, limit=60):
    return "-".join(words(text))[:limit].strip("-") or "product"


def is_empty(value):
    return not (value or "").strip()


def is_na(value):
    return (value or "").strip() == NA


# --- Category config --------------------------------------------------------
def list_categories():
    return sorted(d for d in os.listdir(CATEGORIES_DIR)
                  if os.path.isfile(os.path.join(CATEGORIES_DIR, d, "category.json")))


def load_category(slug):
    path = os.path.join(CATEGORIES_DIR, slug, "category.json")
    if not os.path.isfile(path):
        raise SystemExit("Không có category '%s'. Hiện có: %s"
                         % (slug, ", ".join(list_categories())))
    with open(path, encoding="utf-8") as fh:
        cfg = json.load(fh)
    cfg["_dir"] = os.path.dirname(path)
    cfg["_slug"] = slug
    versions = os.path.join(cfg["_dir"], "about-versions.json")
    cfg["about_versions"] = {}
    if os.path.isfile(versions):
        with open(versions, encoding="utf-8") as fh:
            cfg["about_versions"] = json.load(fh)
    return cfg


# --- Products ---------------------------------------------------------------
def load_products(file2, cfg):
    """Products of File (2) as dicts keyed by the canonical column keys."""
    rows = read_sheet(file2, cfg.get("file2_sheet"))
    if not rows:
        raise SystemExit("File (2) trống.")
    header = [norm_header(h) for h in rows[0]]
    labels = {}
    index = {}
    for key, wanted in cfg["columns"].items():
        wanted = norm_header(wanted)
        pos = next((i for i, h in enumerate(header) if h == wanted), None)
        if pos is None:
            pos = next((i for i, h in enumerate(header) if h.startswith(wanted)), None)
        if pos is not None:
            index[key] = pos
            labels[key] = rows[0][pos].strip()
    missing = [k for k in cfg["required_columns"] if k not in index]
    if missing:
        raise SystemExit("File (2) thiếu cột: %s" % ", ".join(
            cfg["columns"][k] for k in missing))

    products = []
    order = 0
    for rownum, row in enumerate(rows[1:], start=2):
        get = lambda k: (row[index[k]] if k in index and index[k] < len(row) else "").strip()
        if is_empty(get("name")):
            continue
        order += 1
        p = {k: get(k) for k in index}
        stt = p.get("stt", "")
        try:
            p["stt"] = int(float(stt)) if stt else order
        except ValueError:
            p["stt"] = order
        p["_row"] = rownum
        products.append(p)
    return products, labels


def find_product(products, stt):
    for p in products:
        if p["stt"] == stt:
            return p
    raise SystemExit("Không có sản phẩm STT %s trong File (2)." % stt)


def parse_stt_list(spec):
    out = []
    for part in str(spec).split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


# --- Rule engine ------------------------------------------------------------
def _match_alias(text, aliases):
    t = " %s " % " ".join(words(text))
    return any(" %s " % " ".join(words(a)) in t for a in aliases)


def type_votes(p, cfg):
    by_sub = by_type = None
    for key, t in cfg["types"].items():
        if by_sub is None and _match_alias(p.get("subtype", ""), t["aliases"]):
            by_sub = key
        if by_type is None and _match_alias(p.get("type", ""), t["aliases"]):
            by_type = key
    return by_type, by_sub


def resolve_type(p, cfg, override=None):
    """Return (type_key, unclear_message). File (1) Step 0: the outline follows
    Product Type; if it is missing, or is the generic 'Body protector' while
    Sub type names a more specific type, stop and ask. The suggested type is
    still returned so the card can be shown."""
    if override:
        return override, None
    by_type, by_sub = type_votes(p, cfg)
    if by_type and (by_type != cfg["default_type"] or by_sub in (None, by_type)):
        return by_type, None
    suggested = by_sub or by_type
    if by_type is None:
        msg = "Product Type '%s' không rõ" % p.get("type", "")
    else:
        msg = "Product Type = '%s' nhưng Sub type = '%s'" % (p.get("type"), p.get("subtype"))
    if suggested:
        msg += "; đề xuất %s. Sửa cột Product Type trong File (2) hoặc chạy lại với --type %s." \
            % (cfg["types"][suggested]["label"], suggested)
    return suggested, msg


def accessory_serves(p, cfg):
    text = " ".join([p.get("name", ""), p.get("subtype", ""), p.get("ts_acc_compat", "")])
    for serves, aliases in cfg["accessory_serves_keywords"]:
        if _match_alias(text, aliases):
            return serves
    return None


SETS = {"B": ["B1", "B2", "B3"], "K": ["K1", "K2"], "A": ["A1", "A2", "A3"]}


def base_version(stt, set_letter):
    """About rotation rule: B/A by STT mod 3, K by odd/even."""
    if set_letter == "K":
        return "K1" if stt % 2 else "K2"
    return "%s%d" % (set_letter, {1: 1, 2: 2, 0: 3}[stt % 3])


def brand_display(brand, cfg):
    """Appendix 1 name when the File (2) brand matches one ('Helite Airbag Systems' -> 'Helite')."""
    for name in cfg.get("brand_urls", {}):
        if _match_alias(brand, [name]):
            return name
    return (brand or "").strip()


def brand_role(brand, cfg):
    """{Role} text, already filled with the brand name."""
    for role, brands in cfg["roles"].items():
        for b in brands:
            if _match_alias(brand, [b]):
                return role.format(brand=b)
    return cfg["role_default"]


def name_tokens(p):
    brand = set(words(p.get("brand", "")))
    return set(w for w in words(p.get("name", "")) if w not in brand)


def similar_products(p, products, threshold=0.5, window=9):
    """Same brand, >= threshold Jaccard overlap on the name, within +-window STT."""
    mine = name_tokens(p)
    out = []
    for q in products:
        if q is p or abs(q["stt"] - p["stt"]) > window:
            continue
        if words(q.get("brand", ""))[:1] != words(p.get("brand", ""))[:1]:
            continue
        theirs = name_tokens(q)
        if mine and theirs and len(mine & theirs) / float(len(mine | theirs)) >= threshold:
            out.append(q)
    return out


def certification_facts(cert):
    text = cert or ""
    beta = re.search(r"\bBETA\b", text, re.I)
    beta_year = re.search(r"BETA[^.;\n]*?(2009|2018)", text, re.I)
    level3 = re.search(r"level\s*3", text, re.I)
    year = re.search(r"\b(19|20)\d{2}\b", text)
    return {
        "beta": bool(beta),
        "beta_year": beta_year.group(1) if beta_year else None,
        "has_year": bool(year),
        "competition_ok": bool(beta_year and beta_year.group(1) == "2018" and level3),
    }


def about_set_of(p, cfg, type_override=None, serves_override=None):
    type_key, _ = resolve_type(p, cfg, type_override)
    if type_key is None:
        return None, None
    if type_key == "accessory":
        serves = serves_override or accessory_serves(p, cfg)
        return (cfg["types"][serves]["about_set"] if serves else None), serves
    return cfg["types"][type_key]["about_set"], None


def final_version(p, products, cfg, set_letter, memo=None):
    """About rotation rule + sibling rule: if a sibling among the previous 9
    already used this version, take the next one in the set."""
    memo = {} if memo is None else memo
    if p["stt"] in memo:
        return memo[p["stt"]]
    version = base_version(p["stt"], set_letter)
    taken = set()
    for q in similar_products(p, products):
        if q["stt"] < p["stt"] and about_set_of(q, cfg)[0] == set_letter:
            taken.add(final_version(q, products, cfg, set_letter, memo))
    order = SETS[set_letter]
    i = order.index(version)
    for step in range(len(order)):
        cand = order[(i + step) % len(order)]
        if cand not in taken:
            version = cand
            break
    memo[p["stt"]] = version
    return version


def supplier_paragraph(version, product_name, role, cfg):
    """Appendix 2 paragraph with only [Product] and {Role} replaced."""
    text = cfg["about_versions"].get(version)
    if not text:
        return None
    text = text.replace("[Product]", product_name).replace("{Role}", role)
    return text.replace(cfg["site"], "[%s](%s)" % (cfg["site"], cfg["site_home"]), 1)


def analyse(p, products, cfg, serves_override=None, type_override=None):
    """Everything the rules fix for one product, plus blocking issues."""
    block, check = [], []
    type_key, unclear = resolve_type(p, cfg, type_override)
    if unclear:
        block.append(unclear)
    if type_key is None:
        return {"type": None, "block": block or ["Không xác định được loại sản phẩm."],
                "check": check}
    t = cfg["types"][type_key]

    for key in cfg["required_columns"] + t.get("required_columns", []):
        if is_empty(p.get(key)):
            msg = "Cột '%s' đang trống." % cfg["columns"][key]
            if key == "brand_bg":
                msg = "Brand background trống: DỪNG, xin người phụ trách bổ sung."
            block.append(msg)

    brand = brand_display(p.get("brand", ""), cfg)
    url_file2 = "" if is_na(p.get("brand_url")) else (p.get("brand_url") or "").strip()
    url_app1 = cfg["brand_urls"].get(brand, "")
    brand_url = url_file2 or url_app1
    if not brand_url:
        block.append("Không có URL brand ở cột DE Brand URL lẫn Appendix 1: xin URL trang brand.")
    elif url_file2 and url_app1 and url_file2.rstrip("/") != url_app1.rstrip("/"):
        check.append("DE Brand URL trong File (2) khác Appendix 1 (%s): dùng File (2)." % url_app1)

    focus = p.get("focus", "")
    allowed = t["focus"]
    focus_ok = next((f for f in allowed if norm_header(f) == norm_header(focus)), None)
    if focus and not focus_ok:
        block.append("Writing focus '%s' không thuộc danh sách của %s: %s."
                     % (focus, t["label"], " / ".join(allowed)))

    set_letter, serves = about_set_of(p, cfg, type_override, serves_override)
    if type_key == "accessory" and serves is None:
        block.append("Phụ kiện: không suy ra được phục vụ loại nào (body/back/air). "
                     "Hỏi người dùng rồi chạy lại với --serves.")
    version = final_version(p, products, cfg, set_letter) if set_letter else None
    if version and version != base_version(p["stt"], set_letter):
        check.append("Phiên bản About đẩy từ %s sang %s vì sản phẩm gần giống đã dùng %s."
                     % (base_version(p["stt"], set_letter), version,
                        base_version(p["stt"], set_letter)))
    role = brand_role(p.get("brand", ""), cfg)

    links = []
    for link in t["links"]:
        if link == "brand":
            links.append(("brand", brand_url,
                          "tên brand, lần nhắc đầu tiên trong đoạn brand (H2 About)"))
        else:
            u = cfg["urls"][link]
            links.append((link, u["url"], u["anchor"]))

    expected_type_url = cfg["urls"][t["type_url"]]["url"]
    if p.get("type_url") and not is_na(p.get("type_url")) \
            and p["type_url"].rstrip() != expected_type_url:
        check.append("Product type URL trong File (2) là %s, Appendix 1 cho %s là %s."
                     % (p["type_url"], t["label"], expected_type_url))

    cert = certification_facts(p.get("cert", ""))
    if type_key != "accessory" and not is_na(p.get("cert")) and not is_empty(p.get("cert")):
        if cert["beta"] and not cert["beta_year"]:
            block.append("Chứng nhận BETA không ghi năm (2009/2018): KHÔNG tự quyết, "
                         "báo người phụ trách.")
        elif not cert["has_year"]:
            check.append("Certification & level không có năm: đối chiếu với nhãn của hãng.")
    if type_key == "air" and re.search(r"compet", p.get("use_cases", ""), re.I):
        check.append("Use cases có 'competition': air vest chỉ được nói thi đấu theo dạng "
                     "mặc kèm body protector BETA Level 3 khi luật giải yêu cầu.")

    sims = similar_products(p, products)
    if sims and is_na(p.get("differentiator")):
        check.append("Có sản phẩm gần giống nhưng Differentiator = '/'.")
    for q in sims:
        if q["stt"] < p["stt"] and norm_header(q.get("focus")) == norm_header(focus):
            block.append("Writing focus trùng với STT %d (%s): chọn focus khác."
                         % (q["stt"], q["name"]))

    rotation = cfg["brand_opening_rotation"]
    return {
        "type": type_key,
        "type_label": t["label"],
        "outline": t["outline"],
        "serves": serves,
        "about_version": version,
        "brand": brand,
        "brand_url": brand_url,
        "role": role,
        "supplier": supplier_paragraph(version, p.get("name", ""), role, cfg) if version else None,
        "brand_opening": rotation[(p["stt"] - 1) % len(rotation)],
        "links": links,
        "link_placement": cfg["link_placement"][type_key],
        "h2": [h.format(brand=brand) for h in t["h2"]],
        "bullets": t["bullets"],
        "focus": focus_ok or focus,
        "competition_ok": cert["competition_ok"],
        "finder": (p.get("finder") or "").strip().upper() == "Y",
        "similar": [(q["stt"], q["name"], q.get("focus", ""), q.get("differentiator", ""))
                    for q in sims],
        "block": block,
        "check": check,
    }


def product_dir(workdir, p):
    return os.path.join(workdir, "%03d-%s" % (p["stt"], slugify(p["name"])))
