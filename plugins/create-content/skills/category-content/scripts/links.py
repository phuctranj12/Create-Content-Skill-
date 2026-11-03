# -*- coding: utf-8 -*-
"""Resolve the internal-link model for a wholesalehats.com category page
from FILE (2) (internal linking CSV). The single source of truth for links.

    py -3 links.py --file2 file2.csv --page "Richardson Beanies"
    py -3 links.py --file2 file2.csv --url https://www.wholesalehats.com/custom-richardson-beanies

Prints a LINK CARD: template, homepage anchor, and every required link with its
anchor and the H2 it belongs in. URLs come only from the CSV; a target named in
the CSV but missing a row/URL is flagged, never invented (Phần 8.1).
"""
import argparse, sys
import wlib

USE_CASE = {"summer hats", "workwear hats", "promotional hats"}

def template_of(row):
    k = wlib.norm(row.kind)
    if "brand cha" in k: return "T1", "Brand cha"
    if "brand con" in k: return "T2", "Brand con"
    if "product type con" in k: return "T5", "Product type con"
    if "product type cha" in k or "use-case" in k:
        if wlib.norm(row.name) in USE_CASE: return "T4", "Product type cha (use-case)"
        return "T3", "Product type cha (construction/pattern)"
    return "?", row.kind

def find(rows, page=None, url=None):
    for r in rows:
        if page and wlib.norm(r.name) == wlib.norm(page): return r
        if url and r.url and r.url.rstrip("/") == url.rstrip("/"): return r
    return None

def url_of(rows, name):
    for r in rows:
        if wlib.norm(r.name) == wlib.norm(name): return r.url
    return None

def resolve(rows, row):
    tpl, branch = template_of(row)
    links = []  # (anchor_hint, name, url, h2, required)
    def add(name, h2, anchor=None):
        u = url_of(rows, name)
        links.append((anchor or name, name, u, h2, True))
    others = row.getall("brand cha khác")
    ptypes = row.getall("product type 1") + row.getall("product type 2") + row.getall("product type 3")
    ptypes = [p for p in dict.fromkeys(ptypes)]
    children = [r.name for r in rows if wlib.norm(r.parent) == wlib.norm(row.name)]
    siblings = [r.name for r in rows if wlib.norm(r.parent) == wlib.norm(row.parent)
                and wlib.norm(r.name) != wlib.norm(row.name) and row.parent]

    if tpl == "T1":   # Brand cha
        for n in ptypes[:3]: add(n, "H2-1 What are [Brand] hats?")
        for n in children: add(n, "H2-2 Shop [Brand] hats by style")
        links.append((row.anchor_home or "homepage", "Homepage", wlib.HOME_URL,
                      "H2-5 entity", True))
        for n in others[:3]: add(n, "H2-6 Explore other hat brands")
    elif tpl == "T2":  # Brand con
        links.append((row.anchor_home or "homepage", "Homepage", wlib.HOME_URL, "H2-6 entity", True))
        if row.parent: add(row.parent, "H2-6 entity")
        for n in ptypes[:3]: add(n, "H2-1 What is/defines")
        for n in siblings: add(n, "H2-8 Other [Brand] styles to explore")
    elif tpl == "T3":  # Product type cha (construction/pattern)
        links.append((row.anchor_home or "homepage", "Homepage", wlib.HOME_URL, "H2-6 entity", True))
        for n in children: add(n, "H2-4 Shop [Type] by brand / H2-5 top styles")
    elif tpl == "T4":  # Product type cha (use-case)
        links.append((row.anchor_home or "homepage", "Homepage", wlib.HOME_URL, "H2-6 entity", True))
        for n in children: add(n, "H2-4 Shop [Use-case] by brand / H2-5 top styles")
    elif tpl == "T5":  # Product type con
        links.append((row.anchor_home or "homepage", "Homepage", wlib.HOME_URL, "H2-3 entity", True))
        if row.parent: add(row.parent, "H2-2 Shop [Sub-variant] by brand")
        for r in rows:  # suitable brand con assigned to this page (explicit brand-con cols)
            pass
        for n in [r.name for r in rows if wlib.norm(r.parent) == wlib.norm(row.parent)
                  and wlib.norm(r.name) != wlib.norm(row.name)]:
            add(n, "H2-4 Other [Type] styles to explore")
    return tpl, branch, links

def main(argv=None):
    wlib.utf8()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--file2", required=True)
    ap.add_argument("--page"); ap.add_argument("--url")
    a = ap.parse_args(argv)
    rows = wlib.load_csv(a.file2)
    row = find(rows, a.page, a.url)
    if not row:
        print("KHÔNG tìm thấy trang trong FILE (2). Ghi vào mục F và bỏ qua trang này.")
        return 2
    tpl, branch, links = resolve(rows, row)
    print("=== LINK CARD: %s ===" % row.name)
    print("URL: %s" % (row.url or "[THIẾU URL trong FILE (2)]"))
    print("Template: %s (%s)" % (tpl, branch))
    print("Brand URL (research): %s" % (row.brand_url or "-"))
    print("Anchor homepage (cột E): %s" % (row.anchor_home or "[trống]"))
    print("Số link bắt buộc: %d" % len(links))
    print("")
    print("| Anchor | Trang đích | URL | Đặt ở H2 |")
    print("| --- | --- | --- | --- |")
    miss = 0
    for anchor, name, url, h2, _req in links:
        if not url and name != "Homepage":
            url = "[THIẾU URL — tra cột C FILE (2)]"; miss += 1
        print("| %s | %s | %s | %s |" % (anchor, name, url, h2))
    print("")
    if miss:
        print("⚠ %d link thiếu URL trong CSV: flag [INPUT] cho người giao task." % miss)
    print("Quy tắc đặt: mỗi URL 1 lần; không link trong heading; không link PDP/chính trang; "
          "≤2 link/đoạn, ≤1 link/câu.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
