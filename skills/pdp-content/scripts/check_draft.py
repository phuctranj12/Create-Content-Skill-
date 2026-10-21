# -*- coding: utf-8 -*-
"""Lint a PDP draft against File (1), the First Prompt self-check and the
writer checklist.

    py -3 check_draft.py --draft output/004-x/draft.md --file2 "File (2).xlsx" --stt 4 \
        --brand-info output/004-x/brand-info.txt --history output

Machine checks, so the writer (and Claude) only judge what a script cannot:
draft header, H1, H2 names/order, em dash, cross-references, British spelling,
Meta Description, bullet shape/labels, measuring instructions, claim words
missing from the brand text, competition wording, back-only notice, Riding Use
Cases closing sentence, Sizing & Fit closing, Colours, Other Highlights,
links (set, place, anchor, duplicates), the discount-equestrian.co.uk
paragraph word for word, {Role}, Differentiator placement, and wording copied
from earlier drafts (exact sentences; 8-word runs vs similar products), read
from --history so no earlier draft has to stay in the context window.

Exit code 1 when any ERROR is found.
"""

import argparse
import os
import re
import sys

import pdplib

LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
BULLET_RE = re.compile(r"^\s*[-*]\s+(.*)$")
TABLE_RE = re.compile(r"^\s*\|")
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")
STANDARD_RE = re.compile(r"\b(BETA|EN ?\d{3,5}(-\d)?|NF ?S ?\d{2}-\d{3}|CE)\b"
                         r"([ :]*\d{4})?( ?Level \d)?", re.I)


# --- Draft parsing ----------------------------------------------------------
class Draft(object):
    def __init__(self, text, cfg):
        names = {pdplib.norm_header(v): k for k, v in cfg["draft"]["blocks"].items()}
        self.lines = list(enumerate(text.splitlines(), start=1))
        self.blocks = {k: [] for k in cfg["draft"]["blocks"]}
        self.h2s = []  # (title, lineno, [(n, line)])
        current = None
        for n, line in self.lines:
            m = re.match(r"^#\s+(.+?)\s*$", line)
            if m and pdplib.norm_header(m.group(1)) in names:
                current = names[pdplib.norm_header(m.group(1))]
                continue
            if current is None:
                continue
            m2 = re.match(r"^##\s+(.+?)\s*$", line)
            if m2 and current == "long":
                self.h2s.append((m2.group(1), n, []))
                continue
            self.blocks[current].append((n, line))
            if current == "long" and self.h2s:
                self.h2s[-1][2].append((n, line))
        prefix = cfg["draft"]["h2_about_prefix"]
        self.about = next((h for h in self.h2s if h[0].startswith(prefix)), None)
        self.content = [x for k in ("h1", "meta", "short", "long") for x in self.blocks[k]]

    def h2(self, title):
        return next((h for h in self.h2s if h[0] == title), None)


def plain(line):
    return LINK_RE.sub(lambda m: m.group(1), line).replace("**", "")


def paragraphs(lines):
    out, buf = [], []
    for n, line in lines:
        if not line.strip() or TABLE_RE.match(line):
            if buf:
                out.append(buf)
                buf = []
        else:
            buf.append((n, line))
    if buf:
        out.append(buf)
    return out


def text_of(lines):
    return plain(" ".join(l.strip() for _, l in lines))


def has_words(haystack, needle, plural=False):
    norm = (lambda ws: [w[:-1] if w.endswith("s") and len(w) > 3 else w for w in ws]) \
        if plural else (lambda ws: ws)
    return (" %s " % " ".join(norm(pdplib.words(needle)))) in \
        (" %s " % " ".join(norm(pdplib.words(haystack))))


def masked_segments(text, mask_terms):
    """Token runs with product names, colours and standards cut out, so those
    allowed repeats never count towards an n-gram overlap."""
    for term in sorted(set(mask_terms), key=len, reverse=True):
        if term and len(term) > 2:
            text = re.sub(re.escape(term), " § ", text, flags=re.I)
    text = STANDARD_RE.sub(" § ", text)
    segments, seg = [], []
    for tok in re.findall(r"§|\n|[A-Za-z0-9]+", pdplib.strip_accents(text).lower()):
        if tok in ("§", "\n"):
            if seg:
                segments.append(seg)
            seg = []
        else:
            seg.append(tok)
    if seg:
        segments.append(seg)
    return segments


def supplier_regex(template, role):
    parts = re.split(r"(\[Product\]|\{Role\})", template)
    rx = ""
    for part in parts:
        if part == "[Product]":
            rx += r"(.+?)"
        elif part == "{Role}":
            rx += re.escape(role)
        else:
            rx += re.escape(part)
    return re.compile("^" + rx + "$")


def norm_quotes(text):
    return re.sub(r"\s+", " ", text.replace("’", "'").replace("‘", "'")).strip()


# --- Report -----------------------------------------------------------------
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


# --- Wording comparison -----------------------------------------------------
def comparable(draft, cfg, mask_terms):
    """(sentences, token segments) of prose that must not repeat. Tables, H2
    titles, bullet labels, the supplier paragraph and the fixed governing body
    sentence are allowed to repeat; product names, standards and colours are
    masked so they never form part of a repeated run."""
    d = cfg["draft"]
    skip = set()
    if draft.about:
        for para in paragraphs(draft.about[2]):
            if "is supplied by" in text_of(para):
                skip.update(n for n, _ in para)
    texts = []
    for n, line in draft.content:
        if n in skip or not line.strip() or TABLE_RE.match(line) or line.startswith("#"):
            continue
        m = BULLET_RE.match(line)
        if m:
            body = plain(m.group(1))
            line = body.split(":", 1)[1] if ":" in body else body
        texts.append(plain(line).replace(d["use_cases_closing"], " "))
    sentences = []
    for t in texts:
        sentences.extend(s.strip() for s in SENT_SPLIT.split(t) if len(pdplib.words(s)) >= 6)
    return sentences, masked_segments(" \n ".join(texts), mask_terms)


def ngrams(segments, n):
    out = set()
    for seg in segments:
        for i in range(len(seg) - n + 1):
            out.add(" ".join(seg[i:i + n]))
    return out


def sent_key(s):
    return " ".join(pdplib.words(s))


def mask_terms_for(*products):
    terms = []
    for p in products:
        terms.append(p.get("name", ""))
        terms.extend(x.strip() for x in re.split(r"[,;/]", p.get("colours", "")))
    return terms


# --- Checks -----------------------------------------------------------------
def check(draft_text, p, a, cfg, brand_info=None, history=None, rep=None):
    """history: [(product_dict, draft_text)] of earlier products."""
    rep = rep or Report()
    d = cfg["draft"]
    dr = Draft(draft_text, cfg)
    content_text = "\n".join(l for _, l in dr.content)

    for key in ("info", "h1", "meta", "short", "long"):
        if not any(l.strip() for _, l in dr.blocks[key]):
            rep.error(0, "Thiếu khối '# %s'." % d["blocks"][key])
    if not any(l.strip() for _, l in dr.blocks["selfcheck"]):
        rep.warn(0, "Thiếu khối '# %s' (kết quả tự kiểm ở cuối draft)." % d["blocks"]["selfcheck"])

    # Header: outline, About version, {Role}
    info = text_of(dr.blocks["info"])
    if info:
        if not re.search(r"\bOutline:?\s*%s\b" % a["outline"], info, re.I):
            rep.error(0, "DRAFT INFO phải ghi Outline %s." % a["outline"])
        if a["about_version"] and a["about_version"] not in info:
            rep.error(0, "DRAFT INFO phải ghi phiên bản About %s." % a["about_version"])
        if a["role"] not in info:
            rep.error(0, "DRAFT INFO phải ghi {Role} \"%s\"." % a["role"])

    # H1
    h1 = text_of(dr.blocks["h1"]).strip()
    if h1 and h1 != p["name"]:
        rep.error(dr.blocks["h1"][0][0] if dr.blocks["h1"] else 0,
                  "H1 phải đúng tên sản phẩm: \"%s\"." % p["name"])

    # Characters, phrases, spelling
    for n, line in dr.content:
        for ch in d["banned_chars"]:
            if ch in line:
                rep.error(n, "Có ký tự cấm %r." % ch)
        low = plain(line).lower()
        for ph in d["banned_phrases"]:
            if ph in low:
                rep.error(n, "Cụm từ cấm / tham chiếu chéo: '%s'." % ph)
        for us, uk in d["american_spellings"].items():
            if re.search(r"\b%s\b" % us, low):
                rep.warn(n, "Chính tả Mỹ '%s' → Anh-Anh '%s'." % (us, uk))
        if re.search(r"\bFAQs?\b", line):
            rep.error(n, "Không tạo FAQs.")

    # H2 names, order, product name
    allowed = a["h2"]
    distinct = set(w for w in pdplib.name_tokens(p) - set(pdplib.words(" ".join(allowed)))
                   if len(w) >= 3 and not w.isdigit())
    seen, last_idx = set(), -1
    for title, n, _ in dr.h2s:
        if title not in allowed:
            rep.error(n, "H2 '%s' không có trong Outline %s." % (title, a["outline"]))
        else:
            idx = allowed.index(title)
            if idx < last_idx:
                rep.warn(n, "H2 '%s' sai thứ tự so với File (1)." % title)
            last_idx = max(last_idx, idx)
        hit = distinct & set(pdplib.words(title))
        if hit and not title.startswith(d["h2_about_prefix"]):
            rep.error(n, "H2 '%s' chứa tên sản phẩm (%s)." % (title, ", ".join(sorted(hit))))
        if title in seen:
            rep.error(n, "H2 '%s' lặp lại." % title)
        seen.add(title)
        if title not in (d["h2_other_highlights"],):
            for ln, line in dr.h2(title)[2] if dr.h2(title) else []:
                if BULLET_RE.match(line):
                    rep.warn(ln, "Long description nên viết đoạn văn, hạn chế bullet.")
                    break

    # Meta Description
    meta = text_of(dr.blocks["meta"])
    if meta:
        lo, hi = d["meta_chars"]
        if not (lo - 10 <= len(meta) <= hi + 10):
            rep.warn(dr.blocks["meta"][0][0], "Meta Description %d ký tự (nên khoảng %d–%d)."
                     % (len(meta), lo, hi))
        if not has_words(meta, a["brand"]):
            rep.warn(0, "Meta Description nên có tên brand.")
        if a["type"] != "accessory":
            type_words = cfg["types"][a["type"]]["aliases"]
            if not any(has_words(meta, w) for w in type_words):
                rep.warn(0, "Meta Description nên nêu loại sản phẩm (%s)." % type_words[0])
            if p.get("cert") and STANDARD_RE.search(p["cert"]) and not STANDARD_RE.search(meta):
                rep.warn(0, "Meta Description nên có chuẩn chứng nhận.")
        if a["type"] == "air" and re.search(r"canister", p.get("ts_air_included", ""), re.I) \
                and not re.search(r"canister", meta, re.I):
            rep.warn(0, "Air vest: Meta Description nên nói có kèm bình CO₂ hay không.")

    # Short description bullets
    lo, hi = d["bullet_words"]
    labels_seen = []
    for n, line in dr.blocks["short"]:
        m = BULLET_RE.match(line)
        if not m:
            continue
        body = plain(m.group(1))
        if ":" not in body:
            rep.error(n, "Bullet không có dạng 'Nhãn: nội dung'.")
            continue
        label, value = body.split(":", 1)
        label = label.strip()
        k = len(value.split())
        if k > hi or (k < lo and label not in d["bullet_short_ok"]):
            rep.warn(n, "Nội dung sau ':' có %d từ (nên %d–%d)." % (k, lo, hi))
        if label in a["bullets"]:
            labels_seen.append((n, a["bullets"].index(label), label))
        else:
            rep.warn(n, "Nhãn '%s' không có trong File (1) (chỉ hợp lệ nếu là other feature)."
                     % label)
    for (n1, i1, l1), (n2, i2, l2) in zip(labels_seen, labels_seen[1:]):
        if i2 < i1:
            rep.warn(n2, "Nhãn bullet '%s' đứng sau '%s': sai thứ tự File (1)." % (l2, l1))

    # Measuring instructions
    for n, line in dr.content:
        if any(re.search(pat, line, re.I) for pat in d["measure_patterns"]):
            rep.error(n, "Còn hướng dẫn cách đo (size chart chỉ để số liệu).")

    # Claim words not in brand information
    if brand_info is None:
        rep.note("Không có --brand-info: bỏ qua kiểm feature bịa.")
    else:
        for w in d["claim_words"]:
            if has_words(content_text, w) and not has_words(brand_info, w):
                line = next((n for n, l in dr.content if has_words(l, w)), 0)
                rep.error(line, "'%s' không có trong THÔNG TIN TỪ BRAND." % w)

    # Competition wording
    closing = d["use_cases_closing"]
    uc = dr.h2(d["h2_use_cases"])
    uc_lines = set(n for n, _ in uc[2]) if uc else set()
    about_lines = set(n for n, _ in dr.about[2]) if dr.about else set()
    for n, line in dr.content:
        text = plain(line).replace(closing, "")
        if not any(re.search(pat, text, re.I) for pat in d["competition_patterns"]):
            continue
        if a["type"] == "back" and any(re.search(x, text, re.I) for x in d["back_scope_patterns"]):
            continue  # "not for cross-country" is required wording, not a claim
        if n in about_lines:
            rep.warn(n, "Đoạn About nhắc thi đấu: chắc chắn không ngụ ý sản phẩm dùng thi đấu.")
            continue
        if a["competition_ok"]:
            if uc and n not in uc_lines and n not in set(x for x, _ in dr.blocks["short"] + dr.blocks["meta"]):
                rep.warn(n, "Thông tin thi đấu chỉ thuộc H2 %s." % d["h2_use_cases"])
            continue
        if a["type"] == "air":
            for s in SENT_SPLIT.split(text):
                if any(re.search(pat, s, re.I) for pat in d["competition_patterns"]) \
                        and not re.search(r"body protector", s, re.I):
                    rep.error(n, "Air vest: chỉ nói thi đấu theo dạng mặc kèm body protector "
                                 "BETA Level 3.")
            continue
        rep.error(n, "Nhắc thi đấu nhưng sản phẩm không phải BETA 2018 Level 3.")

    # Back protector notice
    if a["type"] == "back":
        if not any(re.search(x, content_text, re.I) for x in d["back_only_patterns"]):
            rep.error(0, "Back protector: phải ghi rõ chỉ bảo vệ lưng.")
        if not any(re.search(x, content_text, re.I) for x in d["back_scope_patterns"]):
            rep.error(0, "Back protector: phải ghi rõ không dùng cho cross-country (XC).")

    # Riding Use Cases closing
    if uc:
        last = [l for _, l in uc[2] if l.strip()]
        if not last or not plain(last[-1]).strip().endswith(closing):
            rep.error(uc[1], "H2 %s phải kết thúc bằng: \"%s\"" % (d["h2_use_cases"], closing))
    elif a["outline"] != "D":
        rep.warn(0, "Không có H2 %s." % d["h2_use_cases"])

    # Sizing & Fit closing, Body Protector Finder
    sz = dr.h2(d["h2_sizing"])
    finder_used = d["finder_phrase"].lower() in content_text.lower()
    if finder_used and not (a["type"] == "body" and a["finder"]):
        rep.error(0, "Chỉ nhắc %s khi File (2) ghi Y cho body protector." % d["finder_phrase"])
    if sz:
        sz_text = text_of(sz[2])
        if d["sizing_closing_phone"] not in sz_text:
            rep.error(sz[1], "Sizing & Fit phải kết bằng câu dẫn tới free in-store fitting và "
                             "advice line %s." % d["sizing_closing_phone"])
        if a["type"] == "body" and a["finder"] and d["finder_phrase"].lower() not in sz_text.lower():
            rep.warn(sz[1], "File (2) ghi Body Protector Finder = Y: nên nhắc trong câu chốt.")

    # Colours
    colours = [c.strip() for c in re.split(r"[,;/]", p.get("colours", "")) if c.strip()
               and not pdplib.is_na(c)]
    col = dr.h2(d["h2_colours"])
    if colours:
        if col is None:
            if a["outline"] != "D" or len(colours) > 1:
                rep.warn(0, "Không có H2 %s." % d["h2_colours"])
        else:
            col_text = text_of(col[2])
            for c in colours:
                if c not in col_text:
                    rep.error(col[1], "H2 %s thiếu màu '%s' (đúng tên như File (2))."
                              % (d["h2_colours"], c))

    # Other Highlights
    oh = dr.h2(d["h2_other_highlights"])
    if oh:
        if a["outline"] in d["no_other_highlights_outlines"]:
            rep.error(oh[1], "Outline %s không có H2 %s." % (a["outline"], d["h2_other_highlights"]))
        elif len(paragraphs(oh[2])) < d["other_highlights_min"]:
            rep.error(oh[1], "%s chỉ có %d feature (cần ≥ %d, nếu không thì bỏ H2)."
                      % (d["h2_other_highlights"], len(paragraphs(oh[2])), d["other_highlights_min"]))

    # Links
    want = {url.rstrip("/"): key for key, url, _ in a["links"]}
    home = cfg["site_home"].rstrip("/")
    allowed_lines = set(n for n, _ in dr.blocks["short"]) | about_lines
    intro_paras = paragraphs([x for x in dr.blocks["short"] if not BULLET_RE.match(x[1])])
    intro_lines = set(n for n, _ in intro_paras[0]) if intro_paras else set()
    seen = {}
    for n, line in dr.content:
        for m in LINK_RE.finditer(line):
            url, anchor = m.group(2).rstrip("/"), m.group(1)
            if n not in allowed_lines:
                rep.error(n, "Link ngoài Short description / About: %s" % url)
            if url in seen:
                rep.error(n, "URL lặp lại (đã có ở dòng %d): %s" % (seen[url], url))
            seen.setdefault(url, n)
            key = want.get(url)
            if key is None and url != home:
                rep.error(n, "URL không thuộc bộ link của Outline %s: %s" % (a["outline"], url))
            elif key in cfg["urls"]:
                words_ok = cfg["urls"][key]["anchor_words"]
                if not any(has_words(anchor, w, plural=True) for w in words_ok):
                    rep.warn(n, "Anchor '%s' của link %s nên chứa: %s."
                             % (anchor, key, " / ".join(words_ok)))
                if n not in intro_lines:
                    rep.warn(n, "Link %s nên nằm trong câu intro." % key)
            elif key == "brand":
                if n not in about_lines:
                    rep.error(n, "Link brand phải ở H2 About.")
                if not has_words(anchor, a["brand"]):
                    rep.warn(n, "Anchor link brand nên là tên brand.")
    for url, key in want.items():
        if url not in seen:
            rep.error(0, "Thiếu link %s: %s" % (key, url))

    # About: supplier paragraph word for word, brand paragraph
    if dr.about is None:
        rep.error(0, "Thiếu H2 \"%s\"." % a["h2"][-1])
    else:
        paras = paragraphs(dr.about[2])
        sup = next((x for x in paras if "is supplied by" in text_of(x)), None)
        if sup is None:
            rep.error(dr.about[1], "Thiếu đoạn \"The [Product] is supplied by "
                                   "discount-equestrian.co.uk…\".")
        else:
            got = norm_quotes(text_of(sup))
            right = a["about_version"]
            ok = supplier_regex(norm_quotes(cfg["about_versions"][right]), a["role"]).match(got)
            if not ok:
                other = next((v for v, t in cfg["about_versions"].items()
                              if v != right and supplier_regex(norm_quotes(t), a["role"]).match(got)),
                             None)
                if other:
                    rep.error(sup[0][0], "Đoạn discount-equestrian.co.uk đang dùng %s, đúng là %s."
                              % (other, right))
                else:
                    rep.error(sup[0][0], "Đoạn discount-equestrian.co.uk lệch nguyên văn %s "
                              "(chỉ được thay [Product] và {Role}): chép lại từ thẻ." % right)
            elif not has_words(ok.group(1), " ".join(list(pdplib.name_tokens(p))[:1])):
                rep.warn(sup[0][0], "[Product] trong đoạn discount-equestrian.co.uk không giống "
                                    "tên sản phẩm.")
            if "[%s](" % cfg["site"] not in " ".join(l for _, l in sup):
                rep.warn(sup[0][0], "Chữ discount-equestrian.co.uk nên link về trang chủ.")
        brand_para = next((x for x in paras if x is not sup), None)
        if brand_para is None:
            rep.error(dr.about[1], "Thiếu đoạn brand trong H2 About.")
        else:
            last = SENT_SPLIT.split(text_of(brand_para).strip())[-1]
            if not (pdplib.name_tokens(p) & set(pdplib.words(last))):
                rep.warn(brand_para[-1][0], "Đoạn brand phải kết thúc bằng câu gắn brand với sản phẩm.")

    # Differentiator in Meta Description and intro
    diff = p.get("differentiator", "")
    if diff and not pdplib.is_na(diff):
        intro = text_of(intro_paras[0]) if intro_paras else ""
        for part in [x.strip() for x in diff.split("|") if x.strip()]:
            if not has_words(meta, part):
                rep.error(0, "Differentiator '%s' chưa có trong Meta Description." % part)
            if not has_words(intro, part):
                rep.error(0, "Differentiator '%s' chưa có trong câu intro." % part)

    # Same 6-word run in two H2s (overlap between sections)
    owner = {}
    own_terms = mask_terms_for(p) + [a["brand"]]
    for title, n, lines in dr.h2s:
        body = text_of([x for x in lines if not TABLE_RE.match(x[1])])
        for g in sorted(ngrams(masked_segments(body, own_terms), 6)):
            if g in owner and owner[g] != title:
                rep.warn(n, "H2 '%s' lặp cụm \"%s\" của H2 '%s'." % (title, g, owner[g]))
                break
        for g in ngrams(masked_segments(body, own_terms), 6):
            owner.setdefault(g, title)

    # Wording vs earlier drafts
    similar = set(s[0] for s in a["similar"])
    lim = d["ngram_limit"]
    brand_sents = set()
    if dr.about:
        paras = paragraphs(dr.about[2])
        for para in paras:
            if "is supplied by" not in text_of(para):
                brand_sents.update(sent_key(s) for s in SENT_SPLIT.split(text_of(para)))
    for q, other_text in history or []:
        label = "STT %d" % q["stt"]
        other = Draft(other_text, cfg)
        terms = mask_terms_for(p, q) + [a["brand"]]
        mine_s, mine_g = comparable(dr, cfg, terms)
        theirs_s, theirs_g = comparable(other, cfg, terms)
        theirs_keys = set(sent_key(s) for s in theirs_s)
        same_brand = pdplib.brand_display(q.get("brand", ""), cfg) == a["brand"]
        for s in mine_s:
            if sent_key(s) not in theirs_keys:
                continue
            if q["stt"] in similar or (same_brand and sent_key(s) in brand_sents):
                rep.error(0, "Câu trùng hệt với %s: \"%s\"" % (label, s[:100]))
            else:
                rep.warn(0, "Câu trùng hệt với %s: \"%s\"" % (label, s[:100]))
        if q["stt"] in similar:
            shared = sorted(ngrams(mine_g, lim) & ngrams(theirs_g, lim))
            if shared:
                rep.error(0, "Trùng %d cụm ≥%d từ với %s (sản phẩm gần giống), ví dụ: \"%s\""
                          % (len(shared), lim, label, shared[0]))
    return rep


def load_history(history_dir, p, a, products):
    """[(product, draft_text)] for the 9 previous STT plus similar products."""
    if not history_dir or not os.path.isdir(history_dir):
        return []
    by_stt = dict((q["stt"], q) for q in products)
    targets = set(range(p["stt"] - 9, p["stt"])) | set(s[0] for s in a["similar"])
    out = []
    for name in sorted(os.listdir(history_dir)):
        m = re.match(r"^(\d+)-", name)
        if not m or int(m.group(1)) not in targets or int(m.group(1)) not in by_stt:
            continue
        path = os.path.join(history_dir, name, "draft.md")
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as fh:
                out.append((by_stt[int(m.group(1))], fh.read()))
    return out


def main(argv=None):
    pdplib.utf8_stdio()
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--draft", required=True)
    ap.add_argument("--file2", required=True)
    ap.add_argument("--stt", required=True, type=int)
    ap.add_argument("--category", default="riding-body-protector")
    ap.add_argument("--type", choices=["body", "back", "air", "accessory"])
    ap.add_argument("--serves", choices=["body", "back", "air"])
    ap.add_argument("--brand-info", help="tệp THÔNG TIN TỪ BRAND (để bắt feature bịa)")
    ap.add_argument("--history", help="thư mục output chứa các <STT>-*/draft.md đã làm")
    args = ap.parse_args(argv)

    cfg = pdplib.load_category(args.category)
    products, _ = pdplib.load_products(args.file2, cfg)
    p = pdplib.find_product(products, args.stt)
    a = pdplib.analyse(p, products, cfg, serves_override=args.serves, type_override=args.type)
    if a["type"] is None or a["block"]:
        print("BLOCK: " + " | ".join(a["block"]))
        return 1
    with open(args.draft, encoding="utf-8") as fh:
        text = fh.read()
    brand = None
    if args.brand_info:
        with open(args.brand_info, encoding="utf-8") as fh:
            brand = fh.read()
    rep = check(text, p, a, cfg, brand, load_history(args.history, p, a, products))
    order = {"ERROR": 0, "WARN": 1, "NOTE": 2}
    for kind, line, msg in sorted(rep.items, key=lambda x: (order[x[0]], x[1])):
        print("%s%s %s" % (kind, (" L%d" % line) if line else "", msg))
    errors = len(rep.errors())
    print("\n%d ERROR, %d WARN." % (errors, sum(1 for k, _, _ in rep.items if k == "WARN")))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
