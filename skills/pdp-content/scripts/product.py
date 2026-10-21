# -*- coding: utf-8 -*-
"""Product card from File (2), with every rule-fixed value pre-computed.

    py -3 product.py --file2 "File (2).xlsx" --list
    py -3 product.py --file2 "File (2).xlsx" --stt 4
    py -3 product.py --file2 "File (2).xlsx" --stt 4-12 --brief
    py -3 product.py --file2 "File (2).xlsx" --stt 7 --type air --serves air --workdir output

The card prints the rules (outline, H2 list, bullet labels, About version,
{Role}, the ready-made discount-equestrian.co.uk paragraph, links and where
they go, brand-paragraph opening, similar products) and then only the filled
columns of the product's own type ("/" and other types' columns are dropped).
Exit code 2 when any product has a BLOCK issue.
"""

import argparse
import json
import os
import sys

import pdplib


def rules_markdown(p, a, cfg):
    out = ["## STT %d · %s" % (p["stt"], p["name"])]
    if a["type"] is None:
        out.append("**BLOCK:** " + " ".join(a["block"]))
        return "\n".join(out)
    serves = (" (phụ kiện phục vụ %s)" % cfg["types"][a["serves"]]["label"]) if a["serves"] else ""
    out.append("Loại **%s** → Outline **%s** · Focus **%s** · About **%s**%s · {Role} **\"%s\"**"
               % (a["type_label"], a["outline"], a["focus"], a["about_version"] or "?",
                  serves, a["role"]))
    out.append("Thi đấu: **%s** · Body Protector Finder: **%s** · Đoạn brand mở bằng: **%s**"
               % ("được khẳng định (BETA 2018 Level 3)" if a["competition_ok"] else
                  ("chỉ theo dạng mặc kèm body protector BETA Level 3" if a["type"] == "air"
                   else "KHÔNG được nói"),
                  "nhắc ở câu chốt Sizing & Fit" if a["finder"] and a["type"] == "body"
                  else "không nhắc", a["brand_opening"]))
    out.append("H2 (đúng tên, đúng thứ tự, bỏ H2 thiếu dữ liệu): " + " | ".join(a["h2"]))
    out.append("Nhãn bullet (đúng thứ tự): " + " | ".join(a["bullets"])
               + " | [Other feature]")
    out.append("Link (mỗi URL 1 lần, chỉ ở Short/About): " + a["link_placement"])
    for key, url, anchor in a["links"]:
        out.append("- %s: %s → %s" % (key, url, anchor))
    if a["supplier"]:
        out.append("Đoạn discount-equestrian.co.uk (%s, chép nguyên văn; được rút gọn tên "
                   "sản phẩm nếu cần):" % a["about_version"])
        out.append("> " + a["supplier"])
    if a["similar"]:
        out.append("Sản phẩm gần giống (±9 STT): " + "; ".join(
            "STT %d %s [focus: %s · diff: %s]" % s for s in a["similar"]))
    for msg in a["block"]:
        out.append("**BLOCK:** " + msg)
    for msg in a["check"]:
        out.append("**CHECK:** " + msg)
    return "\n".join(out)


def data_markdown(p, a, cfg, labels):
    out = []
    t = cfg["types"][a["type"]]
    for key in cfg["card_columns"] + t["type_columns"]:
        value = p.get(key, "")
        if pdplib.is_empty(value) or pdplib.is_na(value):
            continue
        out.append("- **%s:** %s" % (labels.get(key, key), value.replace("\n", " ⏎ ")))
    if not pdplib.is_empty(p.get("how_to_measure")) and not pdplib.is_na(p.get("how_to_measure")):
        out.append("- (How to measure: có trong File (2), KHÔNG dùng để viết)")
    return "\n".join(out)


def card_markdown(p, a, cfg, labels, brief=False):
    text = rules_markdown(p, a, cfg)
    if not brief and a["type"] is not None:
        text += "\n\n" + data_markdown(p, a, cfg, labels)
    return text


def main(argv=None):
    pdplib.utf8_stdio()
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file2", required=True, help="File (2) .xlsx")
    ap.add_argument("--category", default="riding-body-protector")
    ap.add_argument("--list", action="store_true", help="một dòng mỗi sản phẩm")
    ap.add_argument("--stt", help="ví dụ 4 | 4,5,9 | 4-12")
    ap.add_argument("--brief", action="store_true", help="chỉ phần luật, không in cột dữ liệu")
    ap.add_argument("--type", choices=["body", "back", "air", "accessory"],
                    help="loại sản phẩm đã được người duyệt chốt (khi Product Type không rõ)")
    ap.add_argument("--serves", choices=["body", "back", "air"],
                    help="phụ kiện phục vụ loại nào (khi script không tự suy ra)")
    ap.add_argument("--format", choices=["md", "json"], default="md")
    ap.add_argument("--workdir", help="tạo thư mục <workdir>/<STT>-<slug>/ và ghi card.md")
    args = ap.parse_args(argv)

    cfg = pdplib.load_category(args.category)
    products, labels = pdplib.load_products(args.file2, cfg)

    if args.list or not args.stt:
        blocked = 0
        print("STT | Loại→Outline | About | Focus | Sản phẩm | Vấn đề")
        for p in products:
            a = pdplib.analyse(p, products, cfg)
            blocked += bool(a["block"])
            flag = ("BLOCK %d" % len(a["block"])) if a["block"] else ""
            if a["check"]:
                flag += (" " if flag else "") + "CHECK %d" % len(a["check"])
            print("%d | %s→%s | %s | %s | %s | %s" % (
                p["stt"], a.get("type_label", "?"), a.get("outline", "?"),
                a.get("about_version") or "?", p.get("focus", ""), p["name"], flag or "ok"))
        print("\n%d sản phẩm, %d bị BLOCK." % (len(products), blocked))
        return 2 if blocked else 0

    stts = pdplib.parse_stt_list(args.stt)
    if (args.serves or args.type) and len(stts) != 1:
        ap.error("--type/--serves chỉ dùng với một STT")
    blocked = False
    results = []
    for stt in stts:
        p = pdplib.find_product(products, stt)
        a = pdplib.analyse(p, products, cfg, serves_override=args.serves,
                           type_override=args.type)
        blocked = blocked or bool(a["block"])
        if args.format == "json":
            results.append({"product": {k: v for k, v in p.items() if not k.startswith("_")},
                            "rules": a})
            continue
        print(card_markdown(p, a, cfg, labels, brief=args.brief) + "\n")
        if args.workdir and a["type"] is not None:
            d = pdplib.product_dir(args.workdir, p)
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "card.md"), "w", encoding="utf-8") as fh:
                fh.write(card_markdown(p, a, cfg, labels) + "\n")
            print("→ %s" % d)
    if args.format == "json":
        print(json.dumps(results, ensure_ascii=False, indent=1))
    return 2 if blocked else 0


if __name__ == "__main__":
    sys.exit(main())
