# -*- coding: utf-8 -*-
"""Mechanical QA for a category draft (Phần 4, the machine-checkable parts).

    py -3 check.py --file2 file2.csv --page "Richardson Beanies" draft.md

Draft format: '# H1', '## H2', paragraphs, '- bullet', links '[anchor](url)'.

ERROR (phải sửa): em/en dash; brand viết sai 'wholesalehats.com'; link trong heading;
URL link 2 lần; link tới chính trang; thiếu link bắt buộc theo FILE (2); link không có
trong link card (link ngoài file internal linking); anchor homepage khác cột "Anchor home
page"; >2 link trong 1 đoạn; >1 link trong 1 câu.
WARN (xét từng cái): sentence case heading; thiếu số fact bank; cụm nên tránh; format
section entity lệch STT (lẻ văn xuôi / chẵn bullet); link trong FAQ; độ dài ngoài 700-1200.
Judgement-only rules (anti-duplication, source grounding, SKU limits) stay manual.
"""
import argparse, re, sys
import wlib, links as linkmod

LINK_RE = wlib.LINK_RE
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z\[*])")


def check_text(text, rows, page=None, url=None):
    """Return (errors, warns, word_count). Usable from tests."""
    errors, warns = [], []

    # dashes (Phần 1 mục 6.2)
    for ch in ("—", "–"):
        if ch in text: errors.append("Còn dấu dash '%s' trong bài." % ch)
    # brand spelling (5.2)
    if re.search(r"WholesaleHats|Wholesalehats\.com|WHOLESALEHATS", text):
        errors.append("Tên brand phải viết 'wholesalehats.com' (chữ thường).")
    # headings (6.4)
    lines = text.splitlines()
    if not any(l.startswith("# ") for l in lines):
        warns.append("Không thấy H1 (dòng '# ...'): giữ nguyên H1 gốc của trang.")
    for h in re.findall(r"^#{1,6}\s+(.+)$", text, re.M):
        if LINK_RE.search(h): errors.append("Link nằm trong heading: '%s'." % h)
        if not wlib.sentence_case_ok(h): warns.append("Heading có thể không sentence case: '%s'." % h)
    # fact bank numbers (5.1)
    for n in wlib.FACT_NUMBERS:
        if n not in text: warns.append("Thiếu số fact bank '%s' (kiểm section entity)." % n)
    # phrases (6.2)
    low = text.lower()
    for ph in wlib.BANNED_PHRASES:
        if ph in low: warns.append("Cụm nên tránh: '%s'." % ph)
    for ph in wlib.SOFT_PHRASES:
        c = low.count(ph)
        if c: warns.append("Cấu trúc so sánh phủ định '%s' xuất hiện %d lần: mô tả trực tiếp nếu được." % (ph, c))

    # links per paragraph / sentence (8.3)
    for ln in lines:
        if ln.startswith("#") or not ln.strip():
            continue
        n = len(LINK_RE.findall(ln))
        if n > 2:
            errors.append("Đoạn có %d link (tối đa 2): '%s…'" % (n, ln.strip()[:70]))
        for sent in SENT_SPLIT.split(ln):
            if len(LINK_RE.findall(sent)) > 1:
                errors.append("Câu có hơn 1 link: '%s…'" % sent.strip()[:70])

    # link inventory
    found, anchors = {}, {}
    for m in LINK_RE.finditer(text):
        u = m.group(2).rstrip("/")
        found[u] = found.get(u, 0) + 1
        anchors.setdefault(u, []).append(m.group(1))
    for u, c in found.items():
        if c > 1: errors.append("URL link %d lần (chỉ 1 lần): %s" % (c, u))
        if "utm_" in u: errors.append("URL có tham số utm (dán thừa): %s" % u)

    row = linkmod.find(rows, page, url)
    if row:
        if row.url and row.url.rstrip("/") in found:
            errors.append("Link trỏ về chính trang đang viết: %s" % row.url)
        req = linkmod.required_urls(rows, row)
        for u, (anchor, name, h2) in req.items():
            if u not in found:
                errors.append("Thiếu link bắt buộc: %s (%s, %s)" % (name, u, h2))
        for u in found:
            if u not in req:
                errors.append("Link không có trong link card / FILE (2): %s" % u)
        home = wlib.HOME_URL.rstrip("/")
        if home in anchors and row.anchor_home:
            for a in anchors[home]:
                if wlib.norm(a) != wlib.norm(row.anchor_home):
                    errors.append("Anchor homepage '%s' khác cột Anchor home page '%s'." % (a, row.anchor_home))
        # entity format by STT (5.2): the section holding the homepage link
        fmt = wlib.entity_format(row.stt)
        if fmt:
            for title, body in wlib.sections(text):
                if any("](%s/)" % home in l or "](%s)" % home in l for l in body):
                    bullets = sum(1 for l in body if re.match(r"^\s*-\s+", l))
                    if fmt == "prose" and bullets:
                        warns.append("STT %d lẻ: section entity '%s' phải viết văn xuôi (đang có bullet)." % (row.stt, title))
                    if fmt == "bullet" and bullets < 3:
                        warns.append("STT %d chẵn: section entity '%s' phải viết bullet." % (row.stt, title))
        # FAQ must not link (T2 H2-7)
        for title, body in wlib.sections(text):
            if "faq" in title.lower() and any(LINK_RE.search(l) for l in body):
                warns.append("Có link trong section FAQ '%s' (T2: không gắn link ở FAQ)." % title)
    else:
        warns.append("Không tra được trang trong FILE (2) để đối chiếu link.")

    # word count (6.5) — body only, link markup removed
    body = LINK_RE.sub(lambda m: m.group(1), text)
    body = "\n".join(l for l in body.splitlines() if not l.startswith("# "))
    wc = len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’®™/.-]*", body))
    if not (650 <= wc <= 1300): warns.append("Độ dài %d từ (tham chiếu 700-1200)." % wc)
    return errors, warns, wc


def main(argv=None):
    wlib.utf8()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("draft"); ap.add_argument("--file2", required=True)
    ap.add_argument("--page"); ap.add_argument("--url")
    a = ap.parse_args(argv)
    text = open(a.draft, encoding="utf-8").read()
    rows = wlib.load_csv(a.file2)
    page = a.page
    if not page and not a.url:
        h1 = re.search(r"^# (.+)$", text, re.M)
        page = h1.group(1).strip() if h1 else None
    errors, warns, wc = check_text(text, rows, page, a.url)
    for e in errors: print("ERROR %s" % e)
    for w in warns: print("WARN  %s" % w)
    print("\n%d ERROR, %d WARN. (word count ~%d)" % (len(errors), len(warns), wc))
    print("Rà tay (máy không kiểm, xem common/qa.md): chống trùng giữa/trong trang (9.1-9.3); "
          "mọi spec/số truy được về website brand; SKU ở section chính tối đa 3 và có lý do; "
          "SKU ở FAQ có trong Onpage_PDPs; fact bank thu hẹp theo trang; câu phân biệt ở "
          "'Other/Shop by' lấy từ chính trang category và có kèm lợi ích.")
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
