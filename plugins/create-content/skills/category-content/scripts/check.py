# -*- coding: utf-8 -*-
"""Mechanical QA for a category draft (Phần 4, the machine-checkable parts).

    py -3 check.py --file2 file2.csv --page "Richardson Beanies" draft.md

Draft format: '# H1', '## H2', paragraphs, '- bullet', links '[anchor](url)'.
Checks: no em/en dash; brand spelled 'wholesalehats.com'; fact-bank numbers present;
banned phrases; required links from FILE(2) each present exactly once; no link in a
heading; no link to the page's own URL; word count 700-1200. Judgement-only rules
(anti-duplication, source grounding, SKU limits) are listed for manual review.
"""
import argparse, re, sys
import wlib, links as linkmod

LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")

def main(argv=None):
    wlib.utf8()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("draft"); ap.add_argument("--file2", required=True)
    ap.add_argument("--page"); ap.add_argument("--url")
    a = ap.parse_args(argv)
    text = open(a.draft, encoding="utf-8").read()
    errors, warns = [], []

    # dashes
    for ch in ("—", "–"):
        if ch in text: errors.append("Còn dấu dash '%s' trong bài." % ch)
    # brand spelling
    if re.search(r"WholesaleHats|Wholesalehats\.com|WHOLESALEHATS", text):
        errors.append("Tên brand phải viết 'wholesalehats.com' (chữ thường).")
    # headings
    heads = re.findall(r"^#{1,6}\s+(.+)$", text, re.M)
    if not any(l.startswith("# ") for l in text.splitlines()):
        warns.append("Không thấy H1 (dòng '# ...'): giữ nguyên H1 gốc của trang.")
    for h in heads:
        if LINK_RE.search(h): errors.append("Link nằm trong heading: '%s'." % h)
        if not wlib.sentence_case_ok(h): warns.append("Heading có thể không sentence case: '%s'." % h)
    # fact bank numbers
    for n in wlib.FACT_NUMBERS:
        if n not in text: warns.append("Thiếu số fact bank '%s' (kiểm section entity)." % n)
    # banned phrases
    low = text.lower()
    for ph in wlib.BANNED_PHRASES:
        if ph in low: warns.append("Cụm nên tránh: '%s'." % ph)
    # links present
    found = {}
    for m in LINK_RE.finditer(text):
        found[m.group(2).rstrip("/")] = found.get(m.group(2).rstrip("/"), 0) + 1
    for u, c in found.items():
        if c > 1: errors.append("URL link %d lần (chỉ 1 lần): %s" % (c, u))
    # required links from FILE(2)
    rows = wlib.load_csv(a.file2)
    row = linkmod.find(rows, a.page, a.url)
    if row:
        if row.url and row.url.rstrip("/") in found:
            errors.append("Link trỏ về chính trang đang viết: %s" % row.url)
        _t, _b, req = linkmod.resolve(rows, row)
        for anchor, name, url, h2, _r in req:
            if url and url.startswith("http") and url.rstrip("/") not in found:
                warns.append("Chưa đặt link bắt buộc: %s (%s, %s)" % (name, url, h2))
    else:
        warns.append("Không tra được trang trong FILE (2) để đối chiếu link.")
    # word count
    wc = len(re.sub(r"\[[^\]]*\]\([^)]*\)", " ", text).split())
    if not (650 <= wc <= 1300): warns.append("Độ dài %d từ (tham chiếu 700-1200)." % wc)

    for e in errors: print("ERROR %s" % e)
    for w in warns: print("WARN  %s" % w)
    print("\n%d ERROR, %d WARN. (word count ~%d)" % (len(errors), len(warns), wc))
    print("Rà tay (máy không kiểm): chống trùng giữa/ trong trang (9.1-9.3); mọi spec/số "
          "truy được về brand site; không nêu SKU ở section chính; fact bank thu hẹp theo trang; "
          "format entity theo STT (lẻ văn xuôi / chẵn bullet).")
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
