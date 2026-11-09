# -*- coding: utf-8 -*-
"""Shared helpers for the category-content skill (wholesalehats.com)."""
import csv, io, re, sys

HOME_URL = "https://www.wholesalehats.com/"

FACT_BANK = [
    "Trusted source for wholesale hats in the USA since 1979, nearly five decades of experience, a loyal customer base of 10,000+.",
    "600+ styles across all major headwear categories.",
    "Sourced directly from New Era, Flexfit, Imperial and 30+ other leading brands; 100% authentic, brand-verified merchandise.",
    "Supplies both blank (bulk) hats and custom embroidered hats.",
    "Orders from 24 units to tens of thousands, supported by ready-to-ship inventory and reliable fulfillment.",
]
# numbers that must never change (QA)
FACT_NUMBERS = ["1979", "10,000", "600", "24", "30"]

BANNED_PHRASES = [
    "the best", "#1", "number one", "unbeatable", "world's best", "world’s best",
    "looking for", "click here", "see more", "this style",
]
# Phần 1 mục 6.2: hạn chế cấu trúc so sánh phủ định (chỉ WARN, không cấm tuyệt đối)
SOFT_PHRASES = ["rather than", "instead of"]

LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")

def entity_format(stt):
    """Phần 1 mục 5.2: STT lẻ -> văn xuôi, STT chẵn -> bullet."""
    if stt is None:
        return None
    return "bullet" if stt % 2 == 0 else "prose"

def sections(text):
    """Split a draft into [(h2_title or '', [lines])] by '## ' headings."""
    out, cur, buf = [], "", []
    for ln in text.splitlines():
        if ln.startswith("## "):
            out.append((cur, buf)); cur, buf = ln[3:].strip(), []
        elif ln.startswith("# "):
            continue
        else:
            buf.append(ln)
    out.append((cur, buf))
    return out

def utf8():
    try:
        sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def load_csv(path):
    with io.open(path, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    # normalise header keys we care about via substring match
    return [Row(r) for r in rows]

class Row(object):
    def __init__(self, d):
        self.d = {(_k or "").strip(): (v or "").strip() for _k, v in d.items()}
    def get(self, *subs):
        for key, val in self.d.items():
            kl = key.lower()
            if all(s.lower() in kl for s in subs):
                return val
        return ""
    def getall(self, *subs):
        out = []
        for key, val in self.d.items():
            kl = key.lower()
            if all(s.lower() in kl for s in subs) and val:
                out.append(val)
        return out
    def getprefix(self, prefix):
        """Values of columns whose header STARTS with prefix, in column order.
        ('Link Brand con 1..12' but not 'Số link Brand con')."""
        p = prefix.lower()
        return [v for k, v in self.d.items() if k.lower().startswith(p) and v]
    @property
    def brand_cons(self): return self.getprefix("link brand con")
    @property
    def stt(self):
        try:
            return int(float(self.get("stt") or self.get("no.")))
        except ValueError:
            return None
    @property
    def name(self): return self.get("tên danh mục") or self.get("category name")
    @property
    def url(self): return self.get("url danh mục") or self.get("urls")
    @property
    def brand_url(self): return self.get("url brand")
    @property
    def anchor_home(self): return self.get("anchor home")
    @property
    def kind(self): return self.get("loại danh mục") or self.get("content type")
    @property
    def parent(self): return self.get("danh mục cha")

def norm(s):
    return re.sub(r"\s+", " ", (s or "").strip().lower())

def sentence_case_ok(heading):
    """Heading should be sentence case: no Title Case runs of capitalised words
    except brand/proper nouns. Heuristic: flag if >=3 words start uppercase and
    it's not all-proper-noun. Returns True if looks OK."""
    words = re.findall(r"[A-Za-z][A-Za-z’'®&-]*", heading)
    caps = [w for w in words[1:] if w[:1].isupper()]
    return len(caps) < 3  # lenient; brand names allowed
