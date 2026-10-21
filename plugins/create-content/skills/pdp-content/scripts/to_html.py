# -*- coding: utf-8 -*-
"""Draft Markdown -> HTML for the site (Step 9, "Tạo bản HTML").

    py -3 to_html.py output/004-x/draft.md            # writes draft.html beside it
    py -3 to_html.py output/004-x/draft.md --stdout

Converts by code so the HTML is a faithful copy of the checked draft and
costs no output tokens. DRAFT INFO and SELF-CHECK are dropped, H1 -> <h1>,
Meta Description -> a comment on top; ## -> <h2>, paragraphs -> <p>, - -> <ul><li>,
pipe tables -> <table>, **b** -> <strong>, [text](url) -> <a href>. No styling.

    py -3 to_html.py output/004-x/draft.md --submit  # + ban-text.html, ban-html.txt

--submit writes the two files to hand in (Step 10): ban-text.html to open in a
browser and copy into the "Text" tab of the Google Doc, and ban-html.txt (clean
code: h1, short and long description, no comments) for the "HTML" tab.
"""

import argparse
import html
import os
import re
import sys

import pdplib

LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")


def inline(text):
    out, pos = [], 0
    for m in LINK_RE.finditer(text):
        out.append(_fmt(text[pos:m.start()]))
        out.append('<a href="%s">%s</a>' % (html.escape(m.group(2), quote=True), _fmt(m.group(1))))
        pos = m.end()
    out.append(_fmt(text[pos:]))
    return "".join(out)


def _fmt(text):
    text = html.escape(text, quote=False)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)


def _row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def block_html(lines):
    out, i = [], 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
        elif line.startswith("## "):
            out.append("<h2>%s</h2>" % inline(line[3:].strip()))
            i += 1
        elif re.match(r"^\s*[-*]\s+", line):
            items = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append("<li>%s</li>" % inline(re.sub(r"^\s*[-*]\s+", "", lines[i]).strip()))
                i += 1
            out.append("<ul>\n%s\n</ul>" % "\n".join(items))
        elif line.lstrip().startswith("|"):
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                if not re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i]):
                    rows.append(_row(lines[i]))
                i += 1
            head, body = rows[0], rows[1:]
            t = ["<table>", "<thead><tr>%s</tr></thead>" % "".join(
                "<th>%s</th>" % inline(c) for c in head), "<tbody>"]
            t += ["<tr>%s</tr>" % "".join("<td>%s</td>" % inline(c) for c in r) for r in body]
            t += ["</tbody>", "</table>"]
            out.append("\n".join(t))
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not lines[i].startswith("## ") \
                    and not re.match(r"^\s*[-*]\s+", lines[i]) and not lines[i].lstrip().startswith("|"):
                para.append(lines[i].strip())
                i += 1
            out.append("<p>%s</p>" % inline(" ".join(para)))
    return "\n".join(out)


def sections_of(text, cfg):
    names = {pdplib.norm_header(v): (k, v) for k, v in cfg["draft"]["blocks"].items()}
    sections, current = [], None
    for line in text.splitlines():
        m = re.match(r"^#\s+(.+?)\s*$", line)
        if m and pdplib.norm_header(m.group(1)) in names:
            current = names[pdplib.norm_header(m.group(1))]
            sections.append((current, []))
        elif current:
            sections[-1][1].append(line)
    return sections


def convert(text, cfg, clean=False):
    """Review HTML (section comments, Meta Description as a comment) or, with
    clean=True, the code to submit: only h1, short and long description."""
    out = []
    keep = cfg["draft"]["html_blocks"]
    for (key, title), lines in sections_of(text, cfg):
        text = " ".join(l.strip() for l in lines if l.strip())
        if key == "meta":
            if not clean:
                out.insert(0, "<!-- Meta Description: %s -->\n" % text.replace("--", "-"))
        elif key == "h1":
            out.append("<h1>%s</h1>" % inline(text) + ("" if clean else "\n"))
        elif key in keep:
            if not clean:
                out.append("<!-- ===== %s ===== -->" % title)
            out.append(block_html(lines))
            if not clean:
                out.append("")
    return "\n".join(out).strip() + "\n"


PAGE = """<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8"><title>%s</title>
<style>body{font-family:Arial,sans-serif;max-width:860px;margin:32px auto;padding:0 16px;line-height:1.5}
table{border-collapse:collapse}td,th{border:1px solid #999;padding:4px 8px;text-align:left}</style>
</head><body>
%s
</body></html>
"""


def submit_text_page(text, cfg):
    """A page to open in a browser and copy (Ctrl+A, Ctrl+C) into the Text tab
    of the Google Doc: H1, a 'Meta Description:' line, then the content."""
    meta, title = "", ""
    for (key, _), lines in sections_of(text, cfg):
        if key == "meta":
            meta = " ".join(l.strip() for l in lines if l.strip())
        elif key == "h1":
            title = " ".join(l.strip() for l in lines if l.strip())
    body = convert(text, cfg, clean=True)
    body = body.replace("</h1>", "</h1>\n<p><strong>Meta Description:</strong> %s</p>"
                        % html.escape(meta, quote=False), 1)
    return PAGE % (html.escape(title), body)


def main(argv=None):
    pdplib.utf8_stdio()
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("draft")
    ap.add_argument("--category", default="riding-body-protector")
    ap.add_argument("--out", help="mặc định: draft.html cạnh draft.md")
    ap.add_argument("--stdout", action="store_true")
    ap.add_argument("--submit", action="store_true",
                    help="ghi thêm ban-text.html (dán vào tab Text) và ban-html.txt (tab HTML)")
    args = ap.parse_args(argv)
    cfg = pdplib.load_category(args.category)
    with open(args.draft, encoding="utf-8") as fh:
        source = fh.read()
    result = convert(source, cfg)
    if args.submit:
        folder = os.path.dirname(os.path.abspath(args.draft))
        for name, content in (("ban-text.html", submit_text_page(source, cfg)),
                              ("ban-html.txt", convert(source, cfg, clean=True))):
            with open(os.path.join(folder, name), "w", encoding="utf-8") as fh:
                fh.write(content)
            print("→ %s" % os.path.join(folder, name))
    if args.stdout:
        print(result)
        return 0
    out = args.out or os.path.splitext(args.draft)[0] + ".html"
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(result)
    print("→ %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
