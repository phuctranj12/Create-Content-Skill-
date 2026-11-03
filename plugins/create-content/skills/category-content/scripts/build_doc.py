# -*- coding: utf-8 -*-
"""Build the submit .docx from a category draft.md (Bước 6).

    py -3 build_doc.py draft.md --out "Richardson Beanies.docx"

'# H1' -> Heading 1 (giữ nguyên H1 gốc), '## H2' -> Heading 2, '- ' -> bullet,
'[anchor](url)' -> real hyperlink. No styling beyond headings/links.
"""
import argparse, re, sys, os
try:
    import docx
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    from docx.shared import RGBColor
except Exception:
    print("Cần python-docx: pip install --break-system-packages python-docx"); raise

LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")

def add_runs(p, text):
    pos = 0
    for m in LINK_RE.finditer(text):
        if m.start() > pos: p.add_run(text[pos:m.start()])
        part = p.part
        rid = part.relate_to(m.group(2),
            "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
        hl = OxmlElement('w:hyperlink'); hl.set(qn('r:id'), rid)
        r = OxmlElement('w:r'); rpr = OxmlElement('w:rPr')
        c = OxmlElement('w:color'); c.set(qn('w:val'), '1155CC'); rpr.append(c)
        u = OxmlElement('w:u'); u.set(qn('w:val'), 'single'); rpr.append(u); r.append(rpr)
        t = OxmlElement('w:t'); t.text = m.group(1); r.append(t); hl.append(r); p._p.append(hl)
        pos = m.end()
    if pos < len(text): p.add_run(text[pos:])

def main(argv=None):
    try: sys.stdout.reconfigure(encoding="utf-8")
    except Exception: pass
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("draft"); ap.add_argument("--out")
    a = ap.parse_args(argv)
    lines = open(a.draft, encoding="utf-8").read().splitlines()
    d = docx.Document(); i = 0
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln.strip(): i += 1; continue
        if ln.startswith("# "): d.add_heading(ln[2:].strip(), 1)
        elif ln.startswith("## "): d.add_heading(ln[3:].strip(), 2)
        elif ln.startswith("### "): d.add_heading(ln[4:].strip(), 3)
        elif re.match(r"^\s*-\s+", ln):
            add_runs(d.add_paragraph(style="List Bullet"), re.sub(r"^\s*-\s+", "", ln))
        else:
            add_runs(d.add_paragraph(), ln)
        i += 1
    out = a.out or os.path.splitext(a.draft)[0] + ".docx"
    d.save(out); print("→ %s" % out)
    return 0

if __name__ == "__main__":
    sys.exit(main())
