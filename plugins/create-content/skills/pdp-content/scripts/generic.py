# -*- coding: utf-8 -*-
"""Config-driven engine for categories whose category.json has "engine": "generic".

product.py and check_draft.py hand over to this module, so the commands stay
the same for every category. Everything category-specific (column names,
templates, H2 / bullet lists, variant rules, links, banned wording) lives in
category.json + variants.json; nothing here names a product family.

Card: template, type word, H2 and bullet lists, DE paragraph variant (already
filled, site name linked to the home page), links with conditions, the fields
DE owns (colours, sizes) with a ready-made size phrase, Mục 4 issues.

Check: blocks, em/en dash, site name, H1 / Meta title / Meta Description,
Short description shape, H2 names and order, sentence limits, colours and sizes
against File (2), children's sizes, Care, About (2 paragraphs, brand paragraph
length, DE paragraph word for word, home link), links, banned wording,
British spelling, wording reused from earlier drafts (--history).
"""

import json
import os
import re
import unicodedata

import pdplib

LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
BULLET_RE = re.compile(r"^\s*[-*]\s+(.*)$")
LABEL_RE = re.compile(r"^\*\*([^*:]+?):?\*\*:?\s*(.*)$")
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\[])")
FRACTIONS = "⅛¼⅜½⅝¾⅞"


# --- Small helpers ----------------------------------------------------------
def load_variants(cfg):
    path = os.path.join(cfg["_dir"], "variants.json")
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def yes(value):
    first = pdplib.words(value or "")[:1]
    return bool(first) and first[0] in ("y", "yes", "co", "true")


def filled(value):
    return not (pdplib.is_empty(value) or pdplib.is_na(value))


def split_list(value):
    items = [x.strip(" \t.") for x in re.split(r"[;\n]+", value or "")]
    return [x for x in items if x and x != pdplib.NA]


def plain(text):
    text = LINK_RE.sub(lambda m: m.group(1), text or "")
    return text.replace("**", "").strip()


def norm(text):
    text = unicodedata.normalize("NFC", plain(text)).replace("’", "'").replace("‘", "'")
    return re.sub(r"\s+", " ", text).strip()


def word_count(text):
    return len(re.findall(r"[A-Za-z0-9£'’&-]+", plain(text)))


def sentences(text):
    t = plain(text)
    return [s for s in SENT_SPLIT.split(t) if s.strip()] if t else []


def contains_phrase(text, phrase):
    return re.search(r"(?<![a-z0-9])%s(?![a-z0-9])" % re.escape(phrase.lower()),
                     (text or "").lower()) is not None


def brand_of(p, cfg):
    """Appendix A3 name of the brand (longest match wins: 'EQx by Charles Owen')."""
    brand = p.get("brand", "")
    for name in sorted(cfg.get("brand_urls", {}), key=len, reverse=True):
        if pdplib._match_alias(brand, [name]):
            return name
    return brand.strip()


def ranges_of(p):
    return [r.lower() for r in split_list(p.get("ranges", ""))]


def children_flag(p):
    if filled(p.get("children")):
        return yes(p["children"])
    return yes(p.get("children_range", ""))


# --- Sizes ------------------------------------------------------------------
def parse_sizes(value):
    """'52CM; 53CM; 59CM ROUND' or '56R' -> [(52, False), (53, False), (59, True)]."""
    out = []
    for item in split_list(value):
        m = re.match(r"^\s*(\d{2})(?:\.\d)?\s*(R\b|cm\b)?\s*(round)?", item, re.I)
        if m:
            rnd = bool(m.group(3)) or (m.group(2) or "").upper() == "R"
            out.append((int(m.group(1)), rnd))
    return out


def uk_sizes(p):
    """cm -> UK hat size from a brand size guide written as '52 = 6 ⅜; 53 = 6 ½'."""
    text = " ".join(p.get(k, "") for k in ("head", "size_guide", "sizes"))
    pairs = re.findall(r"\b(\d{2})\s*=\s*(\d)\s*([%s])" % FRACTIONS, text)
    return {int(cm): whole + frac for cm, whole, frac in pairs}


def _runs(values):
    runs = []
    for v in sorted(set(values)):
        if runs and v == runs[-1][1] + 1:
            runs[-1][1] = v
        else:
            runs.append([v, v])
    return runs


def _run_text(run, uk):
    a, b = run
    cm = ("%dcm" % a) if a == b else ("%d to %dcm" % (a, b))
    if a in uk and b in uk:
        size = uk[a] if a == b else "%s to %s" % (uk[a], uk[b])
        return "%s (%s)" % (size, cm)
    return cm


def _join(parts):
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]


def size_phrase(p):
    """Only the sizes DE sells, grouped into unbroken runs; round fits named
    separately, e.g. '6⅜ to 6⅝ (52 to 54cm), plus 7¼ (59cm) in a round fit'."""
    sizes = parse_sizes(p.get("sizes", ""))
    if not sizes:
        return None
    uk = uk_sizes(p)
    regular = [_run_text(r, uk) for r in _runs([c for c, rnd in sizes if not rnd])]
    rounds = [_run_text(r, uk) for r in _runs([c for c, rnd in sizes if rnd])]
    if regular and rounds:
        return "%s, plus %s in a round fit" % (_join(regular), _join(rounds))
    if rounds:
        return "%s in a round fit" % _join(rounds)
    return _join(regular)


# --- Rules ------------------------------------------------------------------
def detect_type(text, cfg):
    for key in cfg["detect_order"]:
        if pdplib._match_alias(text, cfg["types"][key]["detect"]):
            return key
    return None


def product_type_words(p, t, type_key):
    shape = (p.get("shape") or "").lower()
    name = (p.get("name") or "").lower()
    for word, alt in t.get("product_type_alt", {}).items():
        if word in shape or word in name:
            return alt
    src = t.get("product_type_from")
    if src and filled(p.get(src)):
        part = split_list(p[src])[0].lower()
        part = part if part.endswith("s") else part + "s"
        return part if "replacement" in part else "replacement " + part
    return t["product_type"]


def choose_variant(p, cfg, type_key, brand):
    stt = p["stt"]
    ranges = ranges_of(p)
    for rule in cfg["variant_rules"]:
        if "brands" in rule:
            if any(pdplib._match_alias(brand, [b]) for b in rule["brands"]) and \
                    ((stt % 2 == 1) if rule.get("stt") == "odd" else True):
                return rule["variant"], rule
        elif rule.get("children"):
            if children_flag(p) or any(r.lower() in ranges for r in rule.get("ranges", [])):
                return rule["variant"], rule
        elif "types" in rule:
            if type_key in rule["types"] and (
                    rule.get("shape", "~") in (p.get("shape") or "").lower()
                    or any(r.lower() in ranges for r in rule.get("ranges", []))):
                return rule["variant"], rule
        elif "mod3" in rule:
            return rule["mod3"][str(stt % 3)], rule
    return None, None


def variant_text(cfg, variant, brand, product_type, link_home=True):
    text = load_variants(cfg).get(variant)
    if not text:
        return None
    if variant == "E":
        brand = cfg.get("variant_brand_alias", {}).get(brand, brand)
    text = text.replace("[Brand]", brand).replace("[product type]", product_type)
    if link_home:
        text = text.replace(cfg["site"], "[%s](%s)" % (cfg["site"], cfg["site_home"]), 1)
    return text


def link_plan(p, cfg, type_key, brand):
    """[(key, url, anchor, where, block, status)] with status required / allowed /
    forbidden, plus the brand page, compatible products and the home page."""
    ranges = ranges_of(p)
    has_ranges = "ranges" in p
    jockey = "jockey skull" in (p.get("shape") or "").lower()
    plan = []
    for link in cfg["links"]:
        if type_key not in link["types"]:
            continue
        when = link["when"]
        if when == "always":
            status = "required"
        elif when == "optional":
            status = "allowed"
        elif when == "shape:jockey skull":
            status = "required" if jockey else "forbidden"
        elif when == "children":
            ok = children_flag(p) and (not has_ranges or "children's riding hats" in ranges)
            status = "required" if ok else "forbidden"
        elif when.startswith("range:"):
            wanted = when.split(":", 1)[1].lower()
            status = "allowed" if (wanted in ranges or not has_ranges) else "forbidden"
        else:
            status = "allowed"
        plan.append((link["key"], link["url"], link["anchor"], link["where"], link["block"],
                     status))
    if brand in cfg.get("brand_urls", {}):
        plan.append(("brand", cfg["brand_urls"][brand], brand,
                     "tên brand, lần nhắc đầu trong About the brand", "long", "required"))
    if type_key in cfg.get("accessory_types", []):
        for url in re.findall(r"https?://\S+", p.get("compat_urls", "")):
            plan.append(("compat", url.rstrip(";,"), "tên mũ tương thích", "Compatibility",
                         "long", "allowed"))
    plan.append(("home", cfg["site_home"], cfg["site"],
                 "đoạn discount-equestrian.co.uk trong About the brand", "long", "required"))
    return plan


def analyse(p, products, cfg, type_override=None):
    block, check = [], []
    by_col = detect_type(p.get("type", ""), cfg)
    by_name = detect_type(p.get("name", ""), cfg)
    type_key = type_override or by_col
    if not type_override:
        if by_col is None:
            block.append("Product type '%s' trống hoặc không khớp template nào%s. Chạy lại với "
                         "--type <%s> sau khi người dùng xác nhận."
                         % (p.get("type", ""), (" (tên gợi ý %s)" % cfg["types"][by_name]["label"])
                            if by_name else "", "|".join(cfg["types"])))
            type_key = by_name
        elif by_name and by_name != by_col:
            check.append("Template theo Product type là %s nhưng tên sản phẩm gợi ý %s: hỏi "
                         "người dùng (Mục 4)." % (cfg["types"][by_col]["label"],
                                                  cfg["types"][by_name]["label"]))
    if type_key is None:
        return {"type": None, "block": block, "check": check}
    t = cfg["types"][type_key]

    for key in cfg["required_columns"]:
        if pdplib.is_empty(p.get(key)):
            block.append("Cột '%s' đang trống." % pdplib.column_label(cfg, key))
    brand = brand_of(p, cfg)
    variant, rule = choose_variant(p, cfg, type_key, brand)
    ptype = product_type_words(p, t, type_key)

    shape = (p.get("shape") or "").lower()
    type_word = t["type_word"]
    for word, alt in t.get("type_word_alt", {}).items():
        if word in shape:
            type_word = alt
    if type_key == "riding_hat" and not any(s in shape for s in ("peaked", "wide peak",
                                                                 "jockey skull")):
        check.append("Không xác định được dáng mũ (peaked / wide peak / jockey skull) từ "
                     "cột Shape: xác nhận từ ảnh trang brand (Mục 4).")
    if yes(p.get("care_guide")):
        check.append("Shared care guide = Y và chưa có URL care guide: Care & maintenance chỉ "
                     "viết mục (always included), không câu link, không hướng dẫn chi tiết; "
                     "ghi đề xuất chủ đề blog cho content lead (Mục 4).")
    if brand not in cfg.get("brand_urls", {}):
        check.append("Brand '%s' không có trong Appendix A3: không link tên brand." % brand)
    banned = [ph for b, phs in cfg.get("brand_banned_phrases", {}).items()
              if pdplib._match_alias(brand, [b]) for ph in phs]
    hits = sorted(set(ph for ph in banned for v in p.values()
                      if isinstance(v, str) and contains_phrase(v, ph)))
    if hits:
        check.append("File (2) có '%s': %s chưa xác nhận ngày sản xuất thì KHÔNG viết "
                     "made in UK / handmade in Britain (Mục 4)." % (", ".join(hits), brand))
    elif banned:
        check.append("%s: chưa xác định ngày sản xuất → không viết made in UK / handmade in "
                     "Britain." % brand)
    dup = p.get("dup", "")
    if re.match(r"^\d{4}-\d{2}-\d{2}", dup) or re.match(r"^\d{5}(\.0)?$", dup):
        check.append("Duplicate Risk '%s' trông như ngày Excel tự đổi (vd '1, 2'): hỏi lại "
                     "số No. thật." % dup)
    if filled(dup) and not filled(p.get("focus")):
        check.append("Có Duplicate Risk nhưng Writing focus trống.")
    if filled(p.get("standards")) and not filled(p.get("quality")) and type_key == "riding_hat":
        check.append("Có tiêu chuẩn nhưng không có quality mark: không viết Competition "
                     "suitability nếu brand cũng không nêu (Mục 4).")
    if "ranges" not in p:
        check.append("File (2) không có cột DE ranges: link range (Children's, Sparkly, "
                     "Custom design) chỉ gắn khi người dùng xác nhận sản phẩm thuộc range.")

    return {
        "type": type_key,
        "type_label": t["label"],
        "type_word": type_word,
        "brand": brand,
        "variant": variant,
        "variant_rule": rule,
        "product_type": ptype,
        "supplier": variant_text(cfg, variant, brand, ptype) if variant else None,
        "h2": t["h2"],
        "bullets": t["bullets"],
        "links": link_plan(p, cfg, type_key, brand),
        "size_phrase": size_phrase(p),
        "colours": split_list(p.get("colours", "")),
        "children": children_flag(p),
        "care_guide": yes(p.get("care_guide")),
        "block": block,
        "check": check,
        # kept for the shared tooling (history lookup, list view)
        "similar": [],
        "outline": t["label"],
        "about_version": variant,
    }


# --- Card -------------------------------------------------------------------
def card_markdown(p, a, cfg, labels, brief=False):
    out = ["## No. %d · %s" % (p["stt"], p["name"])]
    if a["type"] is None:
        out.append("**BLOCK:** " + " ".join(a["block"]))
        return "\n".join(out)
    t = cfg["types"][a["type"]]
    rule = a["variant_rule"] or {}
    out.append("Template **%s** · type word H1 **%s** · DE variant **%s** (quy tắc số %s: %s)"
               % (a["type_label"], a["type_word"], a["variant"], rule.get("rule", "?"),
                  rule.get("why", "")))
    out.append("H2 (đúng tên, đúng thứ tự; * = always included): " + " | ".join(
        ("%s*" % h) if always else h for h, always in a["h2"]))
    out.append("Nhãn Key features (Type luôn đầu, đúng thứ tự, bỏ nhãn thiếu dữ liệu): "
               + " | ".join(a["bullets"]))
    out.append("Câu mở đầu: `%s`" % t["opening_frame"])
    out.append("Navigation bridge: `%s`" % t["bridge"])
    out.append("Giới hạn câu: " + ", ".join("%s ≤%d" % kv for kv in t["max_sentences"].items()))
    out.append("Meta title: ≤%d ký tự kể cả '%s' (dài hơn thì bỏ đuôi) · Meta Description "
               "%d–%d ký tự" % (cfg["draft"]["meta_title_max"], cfg["site_suffix"].strip(),
                                cfg["draft"]["meta_chars"][0], cfg["draft"]["meta_chars"][1]))
    out.append("")
    out.append("**Thông tin DE quyết (lấy File (2), không lấy brand):**")
    out.append("- Màu (liệt kê đúng tên, không 'Choose from'): %s"
               % (", ".join(a["colours"]) or "—"))
    out.append("- Size DE bán: `%s` → câu Size gợi ý: **%s**"
               % (p.get("sizes", "").strip(), a["size_phrase"] or "—"))
    out.append("- Children's sizes: **%s**%s" % ("Y" if a["children"] else "N",
               " (nêu rõ 'children's sizes' + link Children's Riding Hats)" if a["children"]
               else ""))
    out.append("")
    out.append("**Đoạn discount-equestrian.co.uk (chép nguyên văn; [product type] = \"%s\" "
               "là đề xuất, chỉ được đổi đúng cụm này):**" % a["product_type"])
    out.append("")
    out.append(a["supplier"] or "(thiếu variants.json)")
    out.append("")
    out.append("**Link** (mỗi URL đúng 1 lần):")
    for key, url, anchor, where, block, status in a["links"]:
        mark = {"required": "BẮT BUỘC", "allowed": "được phép", "forbidden": "KHÔNG gắn"}[status]
        out.append("- [%s] \"%s\" → %s · %s" % (mark, anchor, url, where))
    if a["block"]:
        out.append("")
        out.extend("**BLOCK:** " + b for b in a["block"])
    if a["check"]:
        out.append("")
        out.extend("**CHECK:** " + c for c in a["check"])
    if brief:
        return "\n".join(out)
    out.append("")
    out.append("**Dữ liệu File (2)** (THÔNG TIN TỪ DE, phải đối chiếu brand; '/' đã bỏ):")
    for key in cfg["common_card_columns"] + t["columns"]:
        value = p.get(key, "")
        if filled(value):
            label = labels.get(key, key).split(":")[0].strip()
            out.append("- **%s:** %s" % (label, value.replace("\n", " ⏎ ")))
    return "\n".join(out)


# --- Draft ------------------------------------------------------------------
class Report(object):
    def __init__(self):
        self.items = []

    def error(self, line, msg):
        self.items.append(("ERROR", line, msg))

    def warn(self, line, msg):
        self.items.append(("WARN", line, msg))

    def note(self, msg):
        self.items.append(("NOTE", 0, msg))

    def errors(self):
        return [m for k, _, m in self.items if k == "ERROR"]


def parse_blocks(text, cfg):
    names = {pdplib.norm_header(v): k for k, v in cfg["draft"]["blocks"].items()}
    blocks, current = {}, None
    for n, line in enumerate(text.splitlines(), start=1):
        m = re.match(r"^#\s+(.+?)\s*$", line)
        if m and pdplib.norm_header(m.group(1)) in names:
            current = names[pdplib.norm_header(m.group(1))]
            blocks[current] = []
        elif current:
            blocks[current].append((n, line))
    return blocks


def paragraphs(lines):
    out, cur = [], []
    for n, line in lines:
        if line.strip():
            cur.append((n, line.strip()))
        elif cur:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def h2_sections(lines):
    secs = []
    for n, line in lines:
        if line.startswith("## "):
            secs.append((n, plain(line[3:]).strip(), []))
        elif secs:
            secs[-1][2].append((n, line))
    return secs


def joined(lines):
    return " ".join(l.strip() for _, l in lines if l.strip())


def variant_regex(cfg, variant, brand):
    text = load_variants(cfg)[variant]
    if variant == "E":
        brand = cfg.get("variant_brand_alias", {}).get(brand, brand)
    pattern = re.escape(norm(text))
    pattern = pattern.replace(re.escape("[Brand]"), re.escape(brand))
    pattern = pattern.replace(re.escape("[product type]"), r"(.+?)")
    return re.compile("^" + pattern + "$")


def size_mentions(text):
    """2-digit hat sizes (40-70) written as '52cm', '56R', '52 to 59 cm' or '56R to 58R'."""
    singles, ranges = set(), []
    for m in re.finditer(r"\b(\d{2})\s*(R?)\s*(?:to|-)\s*(\d{2})\s*(R?)\s*(cm|R)?\b", text):
        a, b = int(m.group(1)), int(m.group(3))
        if 40 <= a < b <= 70 and (m.group(5) or m.group(2) or m.group(4)):
            ranges.append((a, b, bool(m.group(2) or m.group(4)), m.group(0)))
    for m in re.finditer(r"\b(\d{2})\s*(cm|R)\b", text):
        v = int(m.group(1))
        if 40 <= v <= 70:
            singles.add(v)
    return singles, ranges


def check(draft_text, p, a, cfg, brand_info=None, history=None, rep=None):
    rep = rep or Report()
    d = cfg["draft"]
    t = cfg["types"][a["type"]]
    blocks = parse_blocks(draft_text, cfg)
    for key in ("h1", "meta_title", "meta", "short", "long"):
        if key not in blocks:
            rep.error(0, "Thiếu khối '# %s'." % d["blocks"][key])
    content_keys = ("h1", "meta_title", "meta", "short", "long")
    content = [(n, l) for k in content_keys for n, l in blocks.get(k, [])]

    info = joined(blocks.get("info", []))
    if info and a["variant"] and not re.search(r"\b%s\b" % a["variant"], info):
        rep.warn(0, "DRAFT INFO nên ghi DE variant %s." % a["variant"])

    # Characters, site name, banned wording, spelling
    for n, line in content:
        for ch in d["banned_chars"]:
            if ch in line:
                rep.error(n, "Có dấu gạch dài '%s': thay bằng dấu phẩy, hai chấm hoặc tách câu." % ch)
        bare = LINK_RE.sub(lambda m: m.group(1), line)
        for ph in d["banned_phrases"]:
            if contains_phrase(bare, ph):
                rep.error(n, "Cụm bị cấm: '%s'." % ph)
        for us, uk in d["american_spellings"].items():
            if re.search(r"\b%s\b" % us, bare, re.I):
                rep.error(n, "Tiếng Anh - Mỹ '%s' → '%s'." % (us, uk))
    for n, line in [(n, l) for k in ("h1", "meta", "short", "long") for n, l in blocks.get(k, [])]:
        if "Discount Equestrian" in line:
            rep.error(n, "Tên website trong nội dung phải là '%s' (chỉ Meta title được có "
                      "'| Discount Equestrian')." % cfg["site"])
    for b, phrases in cfg.get("brand_banned_phrases", {}).items():
        if pdplib._match_alias(a["brand"], [b]):
            for n, line in content:
                for ph in phrases:
                    if contains_phrase(line, ph):
                        rep.error(n, "%s: không viết '%s' khi chưa xác nhận ngày sản xuất."
                                  % (b, ph))

    # H1 and meta
    h1 = joined(blocks.get("h1", []))
    if h1 and not contains_phrase(h1, a["brand"].split(" by ")[0]):
        rep.error(0, "H1 phải mở bằng tên brand (%s)." % a["brand"])
    if a["type"] == "riding_hat" and h1:
        if len(re.findall(re.escape(a["type_word"]), h1, re.I)) != 1:
            rep.error(0, "H1 phải có type word '%s' đúng 1 lần." % a["type_word"])
    mt = joined(blocks.get("meta_title", []))
    if h1 and mt:
        full = h1 + cfg["site_suffix"]
        expected = full if len(full) <= d["meta_title_max"] else h1
        if mt != expected:
            rep.error(0, "Meta title phải là '%s' (%d ký tự; '%s' dài %d)."
                      % (expected, len(expected), full, len(full)))
    meta = joined(blocks.get("meta", []))
    lo, hi = d["meta_chars"]
    if meta and not lo <= len(meta) <= hi:
        rep.error(0, "Meta Description dài %d ký tự (cần %d–%d)." % (len(meta), lo, hi))

    # Short description
    short = blocks.get("short", [])
    paras = paragraphs(short)
    if any(l.startswith("#") for _, l in short):
        rep.error(0, "Short description không có heading.")
    bullets = [(n, BULLET_RE.match(l).group(1)) for n, l in short if BULLET_RE.match(l)]
    opening = joined(paras[0]) if paras and not BULLET_RE.match(paras[0][0][1]) else ""
    if not opening:
        rep.error(0, "Short description thiếu câu mở đầu.")
    elif meta and norm(meta) == norm(opening):
        rep.error(0, "Meta Description trùng câu mở đầu Short description.")
    if len(sentences(opening)) > 2:
        rep.error(paras[0][0][0], "Câu mở đầu tối đa 2 câu.")
    if a["type"] == "riding_hat" and opening:
        for shape in ("peaked", "wide peak", "jockey skull"):
            if contains_phrase(plain(opening), shape):
                rep.error(paras[0][0][0], "Câu mở đầu chỉ dùng chữ 'riding hat', không ghi "
                          "dáng mũ ('%s' thuộc bullet Type)." % shape)
    labels_seen = []
    for n, body in bullets:
        m = LABEL_RE.match(body.strip())
        label = m.group(1).strip() if m else body.split(":", 1)[0].strip()
        rest = m.group(2) if m else body.split(":", 1)[-1]
        if label not in t["bullets"]:
            rep.error(n, "Nhãn bullet '%s' không có trong template (%s)."
                      % (label, " | ".join(t["bullets"])))
            continue
        labels_seen.append((n, t["bullets"].index(label), label))
        if "," not in rest:
            rep.warn(n, "Bullet '%s' nên theo 'Label: spec, benefit' (chưa thấy phần benefit)."
                     % label)
    if bullets and (not labels_seen or labels_seen[0][2] != "Type"):
        rep.error(bullets[0][0], "Bullet đầu tiên phải là Type.")
    for (n1, i1, l1), (n2, i2, l2) in zip(labels_seen, labels_seen[1:]):
        if i2 <= i1:
            rep.error(n2, "Thứ tự bullet sai: '%s' phải đứng trước '%s'." % (l2, l1))
    after = [pp for pp in paras if not BULLET_RE.match(pp[0][1])][1:]
    if bullets and not after:
        rep.error(0, "Short description thiếu navigation bridge sau Key features.")

    # Long description: H2 names, order, required
    secs = h2_sections(blocks.get("long", []))
    allowed = [h for h, _ in t["h2"]]
    idx = {h.lower(): i for i, h in enumerate(allowed)}
    last = -1
    for n, title, _ in secs:
        i = idx.get(title.lower())
        if i is None:
            rep.error(n, "H2 '%s' không có trong template %s." % (title, t["label"]))
            continue
        if i <= last:
            rep.error(n, "H2 '%s' sai thứ tự." % title)
        last = max(last, i)
    present = set(title.lower() for _, title, _ in secs)
    for h, always in t["h2"]:
        if always and h.lower() not in present:
            rep.error(0, "Thiếu H2 (always included) '%s'." % h)
    by_title = {title.lower(): (n, lines) for n, title, lines in secs}

    # Labelled items: sentence limits, colours
    for n, line in blocks.get("long", []):
        m = LABEL_RE.match(line.strip())
        if not m:
            continue
        label, body = m.group(1).strip(), m.group(2)
        limit = t["max_sentences"].get(label)
        if limit and len(sentences(body)) > limit:
            rep.error(n, "'%s' tối đa %d câu (đang %d)." % (label, limit, len(sentences(body))))
        if label.lower().startswith("colour"):
            missing = [c for c in a["colours"] if not contains_phrase(plain(body), c)]
            if missing:
                rep.error(n, "Màu phải đúng File (2) (%s); thiếu: %s."
                          % (", ".join(a["colours"]), ", ".join(missing)))

    # Sizes: only what DE sells, no range that implies unsold sizes
    sold = parse_sizes(p.get("sizes", ""))
    sold_all = set(c for c, _ in sold)
    if sold:
        text_lines = [(n, l) for k in ("meta", "short", "long") for n, l in blocks.get(k, [])]
        # "round fit" / "56R" only: "all round", "round up" do not name the fit
        mentioned_round = any(re.search(r"\bround[- ]fit|\bround (?:sizes?|shape)\b|\b\d{2}R\b", plain(l), re.I)
                              for _, l in text_lines)
        for n, line in text_lines:
            singles, rngs = size_mentions(plain(line))
            for v in sorted(singles - sold_all):
                rep.error(n, "Size %dcm không có trong Size DE bán (%s)." % (v, p["sizes"].strip()))
            for lo_, hi_, rnd, raw in rngs:
                gap = [v for v in range(lo_, hi_ + 1) if v not in sold_all]
                if gap:
                    rep.error(n, "'%s' ngụ ý DE bán cả %s nhưng File (2) chỉ có %s. Viết: \"%s\"."
                              % (raw, ", ".join("%dcm" % g for g in gap), p["sizes"].strip(),
                                 a["size_phrase"]))
        if any(r for _, r in sold) and not mentioned_round:
            rep.error(0, "File (2) có size ROUND nhưng bài không nhắc round fit.")
    if a["children"] and not re.search(r"children'?s sizes", draft_text, re.I):
        rep.error(0, "Children's sizes = Y: phải nêu rõ 'children's sizes'.")

    # Care & maintenance
    care = by_title.get("care & maintenance")
    if care:
        cn, clines = care
        if word_count(joined(clines)) > d["care_words"]:
            rep.error(cn, "Care & maintenance quá %d từ." % d["care_words"])
        if a["type"] == "riding_hat" and not re.search(r"\bimpact\b", joined(clines), re.I):
            rep.error(cn, "Riding Hat: Care & maintenance phải có câu thay mũ sau va chạm.")
        if a["care_guide"]:
            extra = [LABEL_RE.match(l.strip()).group(1) for _, l in clines
                     if LABEL_RE.match(l.strip())]
            extra = [x for x in extra if "impact" not in x.lower()]
            if extra or (a["type"] != "riding_hat"):
                rep.error(cn, "Shared care guide = Y: chỉ viết mục (always included)%s."
                          % (" (Post-impact replacement)" if a["type"] == "riding_hat"
                             else "; loại này không có mục nào nên bỏ H2 Care"))

    # About the brand
    about = by_title.get("about the brand")
    if about:
        an, alines = about
        if any(l.startswith("###") for _, l in alines):
            rep.error(an, "About the brand không có H3.")
        aparas = paragraphs(alines)
        if len(aparas) != 2:
            rep.error(an, "About the brand phải đúng 2 đoạn (đang %d)." % len(aparas))
        if aparas:
            brand_para = joined(aparas[0])
            wlo, whi = d["brand_words"]
            wc = word_count(brand_para)
            if not wlo <= wc <= whi:
                rep.error(aparas[0][0][0], "Brand paragraph %d từ (cần %d–%d)." % (wc, wlo, whi))
            first = LINK_RE.search(brand_para)
            brand_url = cfg.get("brand_urls", {}).get(a["brand"])
            if brand_url and not (first and first.group(2).rstrip("/") == brand_url.rstrip("/")):
                rep.error(aparas[0][0][0], "Tên brand ở lần nhắc đầu phải link tới %s." % brand_url)
        if len(aparas) >= 2 and a["variant"]:
            de_para = joined(aparas[1])
            got = norm(de_para)
            if not variant_regex(cfg, a["variant"], a["brand"]).match(got):
                rep.error(aparas[1][0][0], "Đoạn %s không khớp nguyên văn variant %s. Đúng là:\n"
                          "    %s" % (cfg["site"], a["variant"], a["supplier"]))
            home = "[%s](%s)" % (cfg["site"], cfg["site_home"])
            if home not in de_para.replace(cfg["site_home"].rstrip("/") + ")", cfg["site_home"] + ")"):
                rep.error(aparas[1][0][0], "'%s' trong đoạn này phải link về trang chủ %s."
                          % (cfg["site"], cfg["site_home"]))

    # Links
    plan = {url.rstrip("/"): (key, anchor, where, blk, status)
            for key, url, anchor, where, blk, status in a["links"]}
    banned_urls = set(u.rstrip("/") for u in cfg.get("banned_urls", []))
    seen = {}
    for k in ("short", "long"):
        for n, line in blocks.get(k, []):
            for m in LINK_RE.finditer(line):
                anchor, url = m.group(1), m.group(2).rstrip("/")
                if url in seen:
                    rep.error(n, "URL bị link 2 lần (lần đầu L%d): %s" % (seen[url], url))
                seen.setdefault(url, n)
                if url in banned_urls:
                    rep.error(n, "Không link tới %s." % url)
                    continue
                if url not in plan:
                    rep.error(n, "URL không có trong Phụ lục A / Compatible product URL: %s" % url)
                    continue
                key, want_anchor, where, blk, status = plan[url]
                if status == "forbidden":
                    rep.error(n, "Link '%s' không đủ điều kiện ở sản phẩm này." % anchor)
                if blk != k:
                    rep.error(n, "Link %s phải nằm ở %s." % (url, where))
                if not want_anchor.startswith("(") and key not in ("compat",) and not any(
                        w.lower() in anchor.lower() for w in want_anchor.split("|")):
                    rep.warn(n, "Anchor '%s' nên là \"%s\"." % (anchor, want_anchor))
    for url, (key, anchor, where, blk, status) in plan.items():
        if status == "required" and url not in seen and not (key == "home" and about):
            rep.error(0, "Thiếu link bắt buộc \"%s\" → %s (%s)." % (anchor, url, where))

    # Safety wording
    body_lines = [(n, l) for k in ("meta", "short") for n, l in blocks.get(k, [])]
    for n, title, lines in secs:
        if title.lower() != "about the brand":
            body_lines += lines
    for n, line in body_lines:
        for b in cfg.get("banned_bodies", []):
            if contains_phrase(line, b):
                rep.error(n, "Không nêu '%s' (ngoài danh sách tổ chức được phép)." % b)
        if a["type"] in cfg.get("accessory_types", []):
            for pat in cfg.get("accessory_banned_patterns", []):
                if re.search(pat, plain(line), re.I):
                    rep.error(n, "Phụ kiện: không nhắc tiêu chuẩn an toàn / không nói an toàn hơn "
                              "('%s')." % re.search(pat, plain(line), re.I).group(0))
        else:
            for w in cfg.get("standard_ranking_words", []):
                if contains_phrase(line, w):
                    rep.error(n, "Không xếp hạng / so sánh tiêu chuẩn ('%s')." % w)

    # Earlier drafts (same thread replacement)
    for q, other in history or []:
        oblocks = parse_blocks(other, cfg)
        ometa = joined(oblocks.get("meta", []))
        if meta and ometa and norm(meta).replace(p["name"], "") == norm(ometa).replace(q["name"], ""):
            rep.error(0, "Meta Description giống No. %d." % q["stt"])
        if brand_of(q, cfg) == a["brand"] and about:
            osecs = {t_.lower(): ls for _, t_, ls in h2_sections(oblocks.get("long", []))}
            opar = paragraphs(osecs.get("about the brand", []))
            mine = paragraphs(about[1])
            if opar and mine:
                n_ = d["brand_ngram"]
                a_w = pdplib.words(plain(joined(mine[0])))
                b_w = pdplib.words(plain(joined(opar[0])))
                grams = set(tuple(b_w[i:i + n_]) for i in range(len(b_w) - n_ + 1))
                hit = [" ".join(a_w[i:i + n_]) for i in range(len(a_w) - n_ + 1)
                       if tuple(a_w[i:i + n_]) in grams]
                if hit:
                    rep.error(mine[0][0][0], "Brand paragraph trùng cụm %d từ với No. %d: '%s'."
                              % (n_, q["stt"], hit[0]))
                if pdplib.words(plain(joined(mine[0])))[:3] == b_w[:3]:
                    rep.error(mine[0][0][0], "Brand paragraph mở đầu giống No. %d." % q["stt"])
    return rep


def load_history(history_dir, p, products, draft_path=None):
    """[(product, draft_text)] for every saved draft except this one."""
    if not history_dir or not os.path.isdir(history_dir):
        return []
    by_stt = dict((q["stt"], q) for q in products)
    out = []
    for name in sorted(os.listdir(history_dir)):
        m = re.match(r"^(\d+)-", name)
        if not m or int(m.group(1)) == p["stt"] or int(m.group(1)) not in by_stt:
            continue
        path = os.path.join(history_dir, name, "draft.md")
        if os.path.isfile(path) and (not draft_path or
                                     os.path.abspath(path) != os.path.abspath(draft_path)):
            with open(path, encoding="utf-8") as fh:
                out.append((by_stt[int(m.group(1))], fh.read()))
    return out
