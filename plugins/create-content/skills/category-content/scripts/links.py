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
    def home(h2):
        links.append((row.anchor_home or "homepage", "Homepage", wlib.HOME_URL, h2, True))
    others = row.getall("brand cha khác")
    ptypes = row.getall("product type 1") + row.getall("product type 2") + row.getall("product type 3")
    ptypes = [p for p in dict.fromkeys(ptypes)]
    brand_cons = [b for b in dict.fromkeys(row.brand_cons)]   # cột "Link Brand con 1–12"
    children = [r.name for r in rows if wlib.norm(r.parent) == wlib.norm(row.name)]
    siblings = [r.name for r in rows if wlib.norm(r.parent) == wlib.norm(row.parent)
                and wlib.norm(r.name) != wlib.norm(row.name) and row.parent
                and wlib.norm(r.kind) == wlib.norm(row.kind)]

    # Phần 1 mục 8.1 — link bắt buộc theo loại trang
    if tpl == "T1":   # Brand cha: Homepage; toàn bộ Brand con; 3 Brand cha khác; Product type 1–3
        for n in ptypes[:3]: add(n, "H2-1 What are [Brand] hats?")
        for n in children: add(n, "H2-2 Shop [Brand] hats by style (nhánh A)")
        home("H2-5 entity")
        for n in others[:3]: add(n, "H2-6 Explore other hat brands")
    elif tpl == "T2":  # Brand con: Homepage; Brand cha; Brand con anh em; Product type 1–3
        for n in ptypes[:3]: add(n, "H2-1 What is/defines")
        home("H2-6 entity")
        if row.parent: add(row.parent, "H2-6 entity")
        for n in siblings: add(n, "H2-8 Other [Brand] styles to explore")
        for n in children:  # Yupoong Hats: thêm các trang con của chính nó
            add(n, "H2-8 Other [Brand] styles to explore (trang con)")
    elif tpl in ("T3", "T4"):  # Product type cha: Homepage; Product type con; Brand con (cột Link Brand con)
        lbl = "[Type]" if tpl == "T3" else "[Use-case]"
        for n in brand_cons: add(n, "H2-4 Shop %s hats by brand" % lbl)
        for n in children: add(n, "H2-5 Top %s hat styles" % lbl)
        home("H2-6 entity")
    elif tpl == "T5":  # Product type con: Homepage; Product type cha; anh em; Brand con (cột Link Brand con)
        if row.parent: add(row.parent, "H2-2 Shop [Sub-variant] by brand (câu trang cha)")
        for n in brand_cons: add(n, "H2-2 Shop [Sub-variant] by brand")
        home("H2-3 entity")
        for n in siblings: add(n, "H2-4 Other [Type] styles to explore")
    return tpl, branch, links

def required_urls(rows, row):
    """{url_without_trailing_slash: (anchor_hint, name, h2)} for check.py."""
    _t, _b, req = resolve(rows, row)
    return {(u or "").rstrip("/"): (a, n, h) for a, n, u, h, _r in req if u}

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
    fmt = wlib.entity_format(row.stt)
    print("STT: %s -> section entity viết %s" % (
        row.stt if row.stt is not None else "[không có]",
        {"prose": "VĂN XUÔI (STT lẻ)", "bullet": "BULLET (STT chẵn)"}.get(fmt, "[kiểm tay]")))
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
          "≤2 link/đoạn, ≤1 link/câu; không link ngoài card này.")
    if tpl == "T3":
        print("Lưu ý: H2-5 (Top styles) template yêu cầu chỉ tên + link, mâu thuẫn luật 8.3 "
              "'không liệt kê link trần' — làm theo template và báo ở mục F.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
