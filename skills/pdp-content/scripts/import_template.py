# -*- coding: utf-8 -*-
"""Split a "PDP Template - <CATEGORY>.docx" (all tabs) into small reference files.

    py -3 import_template.py "PDP Template - RIDING BODY PROTECTOR.docx" \
        --out ../categories/riding-body-protector

The team's template is one Google Doc with tabs: Hướng dẫn (writer guide),
File (1) (format), First Prompt, and example drafts. Claude needs only the
outline of the product in hand, so File (1) is split:

    file1-general.md       Step 0, general/ownership/other-features rules, meta,
                           brand/supplier/rotation rules, Appendix 1
    outline-A.md ...       one file per "OUTLINE <L> – ..." section
    about-versions.json    Appendix 2 paragraphs keyed B1..A3, verbatim
    first-prompt.md        the First Prompt tab
    writer-guide.md        the Hướng dẫn tab (for people; Claude reads only on demand)

Standard library only. Re-run after the template changes, then review the diff.
"""

import argparse
import json
import os
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


def _flag(rpr, tag):
    el = rpr.find(W + tag) if rpr is not None else None
    return el is not None and el.get(W + "val") not in ("0", "false")


def _runs_md(parent, links):
    out = []
    for child in parent:
        tag = child.tag.replace(W, "")
        if tag == "r":
            text = "".join((t.text or "") if t.tag == W + "t" else "\n"
                           for t in child if t.tag in (W + "t", W + "br"))
            if not text:
                continue
            rpr = child.find(W + "rPr")
            core = text.strip()
            if core and _flag(rpr, "b"):
                text = text.replace(core, "**%s**" % core, 1)
            elif core and _flag(rpr, "i"):
                text = text.replace(core, "*%s*" % core, 1)
            out.append(text)
        elif tag == "hyperlink":
            raw = _runs_md(child, links)
            inner = raw.strip()
            url = links.get(child.get(R + "id"))
            if inner and url and url.startswith("http") and inner != url:
                out.append("[%s](%s)" % (inner, url))
            else:
                out.append(raw)  # keep the spaces an empty link may carry
    md = "".join(out).replace("\n", " ")
    md = re.sub(r"\*\*\s*\*\*", "", md).replace("****", "")
    return re.sub(r"[ \t]{2,}", " ", md)


def read_blocks(path):
    """[(kind, level, text)] with kind in heading/title/para/list/table."""
    with zipfile.ZipFile(path) as z:
        doc = ET.fromstring(z.read("word/document.xml"))
        rels = ET.fromstring(z.read("word/_rels/document.xml.rels"))
    links = {r.get("Id"): r.get("Target") for r in rels}
    blocks = []
    for el in doc.find(W + "body"):
        if el.tag == W + "p":
            ppr = el.find(W + "pPr")
            style = ""
            if ppr is not None and ppr.find(W + "pStyle") is not None:
                style = ppr.find(W + "pStyle").get(W + "val")
            text = _runs_md(el, links).strip()
            if not text:
                continue
            m = re.match(r"Heading(\d)", style)
            if style == "Title":
                blocks.append(("title", 1, text))
            elif m:
                blocks.append(("heading", int(m.group(1)), text.replace("**", "").strip()))
            elif ppr is not None and ppr.find(W + "numPr") is not None:
                lvl = ppr.find(W + "numPr").find(W + "ilvl")
                blocks.append(("list", int(lvl.get(W + "val")) if lvl is not None else 0, text))
            else:
                blocks.append(("para", 0, text))
        elif el.tag == W + "tbl":
            rows = []
            for tr in el.iter(W + "tr"):
                cells = [" ".join(_runs_md(p, links).strip() for p in tc.iter(W + "p")).strip()
                         for tc in tr.iter(W + "tc")]
                rows.append([c.replace("|", "/") for c in cells])
            blocks.append(("table", 0, rows))
    return blocks


def to_md(blocks, base_level=1):
    out = []
    for kind, level, text in blocks:
        if kind in ("heading", "title"):
            out.append("\n%s %s\n" % ("#" * max(1, level - base_level + 1), text))
        elif kind == "list":
            out.append("%s- %s" % ("  " * level, text))
        elif kind == "para":
            out.append("\n%s\n" % text)
        elif kind == "table":
            width = max(len(r) for r in text)
            rows = [r + [""] * (width - len(r)) for r in text]
            out.append("")
            out.append("| %s |" % " | ".join(c.replace("**", "") for c in rows[0]))
            out.append("|%s" % (" --- |" * width))
            out.extend("| %s |" % " | ".join(r) for r in rows[1:])
            out.append("")
    md = "\n".join(out)
    return re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"


TABS = [("guide", r"^Hướng dẫn"), ("file1", r"^File \(1\)"), ("prompt", r"^First Prompt")]


def split_tabs(blocks):
    tabs, current = {}, None
    for b in blocks:
        if b[0] == "title":
            current = "example"
        elif b[0] == "table" and b[2] and b[2][0][0].replace("*", "").strip() == "#":
            tabs.setdefault("columns", []).append(b)  # File (2) column guide
            continue
        elif b[0] == "heading" and b[1] == 1:
            for key, pat in TABS:
                if re.search(pat, b[2], re.I):
                    current = key
                    break
        if current:
            tabs.setdefault(current, []).append(b)
    return tabs


def split_file1(blocks):
    general, outlines, appendix2 = [], {}, []
    target = general
    for b in blocks:
        if b[0] == "heading" and b[1] == 2:
            m = re.match(r"OUTLINE\s+([A-Z])\b", b[2], re.I)
            if m:
                target = outlines.setdefault(m.group(1).upper(), [])
            elif re.match(r"Appendix 2", b[2], re.I):
                target = appendix2
            else:
                target = general
        target.append(b)
    return general, outlines, appendix2


def about_versions(blocks):
    versions = {}
    for kind, _, text in blocks:
        m = re.match(r"^\*\*([A-Z]\d):\*\*\s*(.+)$", text) if kind == "para" else None
        if m:
            body = re.sub(r"\[(discount-equestrian\.co\.uk)\]\([^)]+\)", r"\1", m.group(2))
            versions[m.group(1)] = body.replace("**", "").strip()
    return versions


def main(argv=None):
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("docx")
    ap.add_argument("--out", required=True, help="thư mục category")
    args = ap.parse_args(argv)

    tabs = split_tabs(read_blocks(args.docx))
    missing = [k for k in ("file1", "prompt") if k not in tabs]
    if missing:
        raise SystemExit("Không thấy tab: %s (tải lại docx với đủ các tab)." % ", ".join(missing))
    general, outlines, appendix2 = split_file1(tabs["file1"])
    os.makedirs(args.out, exist_ok=True)
    note = "<!-- Sinh tự động bởi import_template.py từ %s. Không sửa tay. -->\n\n" \
        % os.path.basename(args.docx)
    files = {"file1-general.md": to_md(general), "first-prompt.md": to_md(tabs["prompt"])}
    for letter, blocks in outlines.items():
        files["outline-%s.md" % letter] = to_md(blocks, base_level=2)
    if "guide" in tabs:
        files["writer-guide.md"] = to_md(tabs["guide"])
    if "columns" in tabs:
        # Keep #, column, guidance; the example column is misaligned in the source.
        rows, seen = [], set()
        for _, _, table in tabs["columns"]:
            for r in table:
                if r[0] not in seen:
                    seen.add(r[0])
                    rows.append(r[:3])
        files["file2-columns.md"] = "# Hướng dẫn điền từng cột File (2)\n\n" + \
            to_md([("table", 0, rows)])
    for name, text in files.items():
        with open(os.path.join(args.out, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(note + text)
        print("→ %s (%d ký tự)" % (name, len(text)))
    versions = about_versions(appendix2)
    with open(os.path.join(args.out, "about-versions.json"), "w", encoding="utf-8",
              newline="\n") as fh:
        json.dump(versions, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("→ about-versions.json (%s)" % ", ".join(sorted(versions)))
    if "example" in tabs:
        print("Bỏ qua %d khối ví dụ (draft mẫu cũ)." % len(tabs["example"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
