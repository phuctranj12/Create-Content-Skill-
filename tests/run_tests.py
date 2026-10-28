# -*- coding: utf-8 -*-
"""Self-checks for the pdp-content skill.

Run from anywhere:
    py -3 tests/run_tests.py          (Windows)
    python3 tests/run_tests.py        (macOS / Linux)

Standard library only, no test framework required.
"""

import json
import os
import re
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(ROOT, "plugins", "create-content")
SKILL = os.path.join(PLUGIN, "skills", "pdp-content")
FIX = os.path.join(ROOT, "tests", "fixtures")
sys.path.insert(0, os.path.join(SKILL, "scripts"))

import pdplib  # noqa: E402
import check_draft  # noqa: E402
import generic  # noqa: E402
import to_html  # noqa: E402
import product  # noqa: E402
import import_template  # noqa: E402

pdplib.utf8_stdio()

FILE2 = os.path.join(FIX, "file2-sample.xlsx")
TEMPLATE = os.path.join(ROOT, "source", "PDP Template - RIDING BODY PROTECTOR.docx")
SPEC_FRONTMATTER_FIELDS = {"name", "description", "license", "compatibility",
                           "metadata", "allowed-tools"}


def read(name):
    with open(os.path.join(FIX, name), encoding="utf-8") as fh:
        return fh.read()


CFG = pdplib.load_category("riding-body-protector")
PRODUCTS, LABELS = pdplib.load_products(FILE2, CFG)
GOOD = read("good-draft-stt2.md")
BRAND = read("brand-info-stt2.txt")


def fake(stt, name, brand="Racesafe", type_="Body protector", subtype="", focus="Fit & sizing",
         cert="BETA 2018 Level 3, EN 13158:2018", **extra):
    p = {k: "x" for k in CFG["columns"]}
    p.update(stt=stt, name=name, brand=brand, type=type_, subtype=subtype, focus=focus,
             cert=cert, differentiator="/", brand_url="", type_url="/", finder="Y")
    p.update(extra)
    return p


def analysed(stt=2):
    p = pdplib.find_product(PRODUCTS, stt)
    return p, pdplib.analyse(p, PRODUCTS, CFG, type_override="air")


def errors(text, stt=2, brand=BRAND, history=None):
    p, a = analysed(stt)
    return check_draft.check(text, p, a, CFG, brand, history).errors()


class File2Tests(unittest.TestCase):
    def test_reads_sample(self):
        self.assertEqual([p["stt"] for p in PRODUCTS], [1, 2])
        self.assertEqual(PRODUCTS[0]["name"], "Helite Zip'in 2 Child Airbag System")

    def test_sample_type_is_unclear(self):
        # Both rows say Product Type "Body protector(s)" but are air vests: File (1)
        # Step 0 says stop and ask, so the card must BLOCK until --type is given.
        for p in PRODUCTS:
            a = pdplib.analyse(p, PRODUCTS, CFG)
            self.assertEqual(a["type"], "air")
            self.assertTrue(any("--type air" in m for m in a["block"]))
            self.assertFalse(pdplib.analyse(p, PRODUCTS, CFG, type_override="air")["block"])

    def test_rules_on_sample(self):
        a1 = pdplib.analyse(PRODUCTS[0], PRODUCTS, CFG, type_override="air")
        a2 = pdplib.analyse(PRODUCTS[1], PRODUCTS, CFG, type_override="air")
        self.assertEqual((a1["outline"], a1["about_version"], a1["brand"], a1["role"]),
                         ("C", "A1", "Helite", "an official Helite retailer and"))
        self.assertEqual((a2["outline"], a2["about_version"], a2["role"]),
                         ("C", "A2", "an authorised Racesafe stockist and"))
        self.assertEqual(a1["h2"][-1], "About Helite & discount-equestrian.co.uk")
        self.assertTrue(a1["supplier"].startswith(
            "The Helite Zip'in 2 Child Airbag System is supplied by [discount-equestrian.co.uk]"
            "(https://www.discount-equestrian.co.uk/), an official Helite retailer and UK "))
        self.assertTrue(any("back-protectors" in m for m in a1["check"]))

    def test_list_exit_code(self):
        self.assertEqual(product.main(["--file2", FILE2, "--list"]), 2)
        self.assertEqual(product.main(["--file2", FILE2, "--stt", "2", "--type", "air",
                                       "--brief"]), 0)


class RuleTests(unittest.TestCase):
    def test_about_rotation(self):
        self.assertEqual([pdplib.base_version(n, "B") for n in range(1, 7)],
                         ["B1", "B2", "B3", "B1", "B2", "B3"])
        self.assertEqual([pdplib.base_version(n, "K") for n in range(1, 5)],
                         ["K1", "K2", "K1", "K2"])

    def test_sibling_takes_next_version(self):
        prods = [fake(1, "Racesafe Motion3 Adults Body Protector", focus="Fit & sizing"),
                 fake(4, "Racesafe Motion3 Young Rider Body Protector", focus="Competition use")]
        a = pdplib.analyse(prods[1], prods, CFG)
        self.assertEqual(a["about_version"], "B2")  # base B1 already used by STT 1
        self.assertTrue(any("B1 sang B2" in m for m in a["check"]))

    def test_type_resolution(self):
        cases = [
            (fake(1, "A", type_="Air vest", subtype="Air Jackets and Air Vests"), ("air", False)),
            (fake(1, "A", type_="Back protector"), ("back", False)),
            (fake(1, "A", type_="Accessory", subtype="Air Jackets and Air Vests"), ("accessory", False)),
            (fake(1, "A", type_="Back protector", subtype="Body Protectors"), ("back", False)),
            (fake(1, "A", type_="Body protector"), ("body", False)),
            (fake(1, "A", type_="Body Protectors", subtype="Air Jackets and Air Vests"), ("air", True)),
            (fake(1, "A", type_="Gloves"), (None, True)),
        ]
        for p, (want, unclear) in cases:
            got, msg = pdplib.resolve_type(p, CFG)
            self.assertEqual((got, bool(msg)), (want, unclear), p["type"])

    def test_accessory_serves(self):
        prods = [fake(4, "Helite CO2 Canister 60cc", brand="Helite", type_="Accessory",
                      focus="Function"),
                 fake(5, "Racesafe Shoulder Protectors", type_="Accessory", focus="Function"),
                 fake(6, "Mystery Strap", brand="Other", type_="Accessory", focus="Function")]
        got = [pdplib.analyse(p, prods, CFG) for p in prods]
        self.assertEqual([g["about_version"] for g in got[:2]], ["A1", "B2"])
        self.assertTrue(any("--serves" in m for m in got[2]["block"]))
        self.assertEqual(pdplib.analyse(prods[2], prods, CFG, "back")["about_version"], "K2")

    def test_roles(self):
        self.assertEqual(pdplib.brand_role("Charles Owen", CFG), "an authorised Charles Owen stockist and")
        self.assertEqual(pdplib.brand_role("Freejump", CFG), "an official Freejump retailer and")
        self.assertEqual(pdplib.brand_role("Rhinegold", CFG), "a")

    def test_brand_url_fallback(self):
        p = fake(1, "Charles Owen Kontour", brand="Charles Owen")
        a = pdplib.analyse(p, [p], CFG)
        self.assertEqual(a["brand_url"], CFG["brand_urls"]["Charles Owen"])
        p = fake(1, "X", brand="Unknown Brand")
        self.assertTrue(any("URL brand" in m for m in pdplib.analyse(p, [p], CFG)["block"]))

    def test_similar_and_focus_clash(self):
        prods = [fake(1, "Racesafe Motion3 Adults Body Protector", focus="Fit & sizing"),
                 fake(2, "Racesafe Motion3 Junior Body Protector", focus="Fit & sizing"),
                 fake(3, "Charles Owen Kontour", brand="Charles Owen")]
        a = pdplib.analyse(prods[1], prods, CFG)
        self.assertEqual([s[0] for s in a["similar"]], [1])
        self.assertTrue(any("trùng với STT 1" in m for m in a["block"]))
        self.assertFalse(pdplib.analyse(prods[0], prods, CFG)["block"])

    def test_blocks(self):
        def blocked(p, needle):
            return any(needle in m for m in pdplib.analyse(p, [p], CFG)["block"])
        self.assertTrue(blocked(fake(1, "X", brand_bg=""), "Brand background"))
        self.assertTrue(blocked(fake(1, "X", cert="BETA Level 3"), "BETA"))
        self.assertTrue(blocked(fake(1, "X", focus="Style"), "Writing focus"))

    def test_competition_flag(self):
        self.assertTrue(pdplib.certification_facts("BETA 2018 Level 3")["competition_ok"])
        self.assertFalse(pdplib.certification_facts("BETA 2009 Level 3")["competition_ok"])
        self.assertFalse(pdplib.certification_facts("NF S72-800:2022")["competition_ok"])


class DraftTests(unittest.TestCase):
    def test_good_draft_passes(self):
        p, a = analysed()
        rep = check_draft.check(GOOD, p, a, CFG, BRAND)
        self.assertEqual([x for x in rep.items if x[0] != "NOTE"], [])

    def assertCaught(self, text, needle, **kw):
        errs = errors(text, **kw)
        self.assertTrue(any(needle in e for e in errs), "%r not in %r" % (needle, errs))

    def test_info_and_h1(self):
        self.assertCaught(GOOD.replace("About: A2", "About: A3"), "phiên bản About A2")
        self.assertCaught(GOOD.replace("\nRacesafe VeloAir Air Gilet\n", "\nVeloAir\n", 1), "H1")

    def test_em_dash(self):
        self.assertCaught(GOOD.replace("everyday riding.", "everyday riding — daily."), "ký tự cấm")

    def test_h2_rules(self):
        self.assertCaught(GOOD.replace("## Sizing & Fit", "## VeloAir Sizing & Fit"), "tên sản phẩm")
        self.assertCaught(GOOD.replace("## Colours", "## Colour Options"), "không có trong Outline")
        self.assertCaught(GOOD.replace("## Colours", "## FAQs"), "FAQs")

    def test_bullet_shape(self):
        self.assertCaught(GOOD.replace("- Fastening: waterproof zip", "- Fastening waterproof zip"),
                          "Nhãn: nội dung")

    def test_measuring_instructions(self):
        self.assertCaught(GOOD.replace("Eight sizes", "Measure around your chest. Eight sizes"),
                          "cách đo")

    def test_invented_feature(self):
        self.assertCaught(GOOD.replace("everyday riding.", "everyday, lightweight riding."),
                          "lightweight")

    def test_competition_claim(self):
        self.assertCaught(GOOD.replace("Racesafe designed the VeloAir Air Gilet for everyday riding.",
                                       "It is ideal for competition."), "body protector")

    def test_use_cases_closing(self):
        self.assertCaught(GOOD.replace(" Always check the current rules of your governing body "
                                       "before competing.", ""), "kết thúc bằng")

    def test_sizing_closing_and_finder(self):
        self.assertCaught(GOOD.replace(" or call our advice line on 01429 864112", ""), "01429 864112")
        self.assertCaught(GOOD.replace("For help choosing", "Our Body Protector Finder helps. For help choosing"),
                          "Body Protector Finder")

    def test_colours(self):
        self.assertCaught(GOOD.replace("Black and Midnight Navy", "Black and Navy"), "Midnight Navy")

    def test_links(self):
        no_brand = GOOD.replace("[Racesafe](https://www.discount-equestrian.co.uk/shop-by-brand/"
                                "hows-racesafe.html)", "Racesafe")
        self.assertCaught(no_brand, "Thiếu link brand")
        dup = GOOD.replace("Eight sizes", "[riding body protectors](https://www.discount-equestrian"
                           ".co.uk/rider/riding-wear/body-protectors.html) Eight sizes")
        self.assertCaught(dup, "ngoài Short description")
        self.assertCaught(dup, "lặp lại")
        self.assertCaught(GOOD.replace("hows-racesafe.html", "racesafe.html"), "không thuộc bộ link")

    def test_supplier_paragraph(self):
        self.assertCaught(GOOD.replace("an authorised Racesafe stockist and", "an official Racesafe retailer and"),
                          "lệch nguyên văn")
        self.assertCaught(GOOD.replace("90% of our reviewers recommend us", "most reviewers recommend us"),
                          "lệch nguyên văn")
        a3 = CFG["about_versions"]["A3"].replace("[Product]", "Racesafe VeloAir Air Gilet").replace(
            "{Role}", "an authorised Racesafe stockist and")
        start = GOOD.index("The Racesafe VeloAir Air Gilet is supplied by")
        end = GOOD.index("\n", start)
        self.assertCaught(GOOD[:start] + a3 + GOOD[end:], "đang dùng A3, đúng là A2")

    def test_differentiator(self):
        self.assertCaught(GOOD.replace("Air Gilet: a standalone air gilet", "Air Gilet: an air gilet"),
                          "Meta Description")

    def test_other_highlights(self):
        text = GOOD.replace("## Colours", "## Other Highlights\nHex key included.\n\n## Colours")
        self.assertCaught(text, "Other Highlights")

    def test_cross_reference(self):
        self.assertCaught(GOOD.replace("Eight sizes", "As mentioned above, eight sizes"), "chéo")

    def test_history_similar_product(self):
        p1 = dict(PRODUCTS[0], stt=1, name="Racesafe VeloAir Junior Air Gilet", brand="Racesafe")
        p, a = analysed()
        a = dict(a, similar=[(1, p1["name"], "Fit & sizing", "Junior")])
        sentence = ("Eight sizes run from Young Rider 1 to Adult 4 Tall, and an adjustable "
                    "waistband tailors the fit around you.")
        rep = check_draft.check(GOOD, p, a, CFG, BRAND, [(p1, "# LONG DESCRIPTION\n## Sizing & Fit\n"
                                                           + sentence)])
        self.assertTrue(any("trùng hệt" in e for e in rep.errors()))
        run = "and an adjustable waistband tailors the fit around you nicely"
        rep = check_draft.check(GOOD, p, a, CFG, BRAND, [(p1, "# LONG DESCRIPTION\n## Sizing & Fit\n"
                                                           "Our version has " + run + ".")])
        self.assertTrue(any("cụm ≥8 từ" in e for e in rep.errors()), rep.errors())

    def test_history_allows_fixed_text(self):
        p1 = dict(PRODUCTS[0], stt=1, name="Racesafe VeloAir Junior Air Gilet", brand="Racesafe")
        p, a = analysed()
        a = dict(a, similar=[(1, p1["name"], "Fit & sizing", "Junior")])
        # Allowed repeats: governing body sentence, tables, H2 names, standard,
        # colour names, product name, bullet labels and the supplier paragraph.
        supplier = [l for l in GOOD.splitlines() if "is supplied by" in l][0]
        other = "\n".join([
            "# SHORT DESCRIPTION", "Junior intro text here.",
            "- Certification: NF S72-800:2022", "- Fastening: waterproof zip",
            "# LONG DESCRIPTION",
            "## Riding Use Cases", "Junior riders only. " + CFG["draft"]["use_cases_closing"],
            "## What You Need",
            "| Jacket size | Canister |", "| --- | --- |", "| YR1 / YR2 | 30g |",
            "## Colours", "The %s comes in Black and Midnight Navy." % p1["name"],
            "## About Racesafe & discount-equestrian.co.uk", "Other brand words.", "",
            supplier.replace("Racesafe VeloAir Air Gilet", p1["name"])])
        rep = check_draft.check(GOOD, p, a, CFG, BRAND, [(p1, other)])
        self.assertFalse([e for e in rep.errors() if "trùng" in e.lower() or "cụm" in e], rep.errors())

    def test_history_loader(self):
        tmp = tempfile.mkdtemp()
        try:
            p, a = analysed()
            os.makedirs(os.path.join(tmp, "001-helite"))
            with open(os.path.join(tmp, "001-helite", "draft.md"), "w", encoding="utf-8") as fh:
                fh.write("x")
            os.makedirs(os.path.join(tmp, "002-self"))
            got = check_draft.load_history(tmp, p, a, PRODUCTS)
            self.assertEqual([q["stt"] for q, _ in got], [1])
        finally:
            shutil.rmtree(tmp)


class HtmlTests(unittest.TestCase):
    def test_convert(self):
        out = to_html.convert(GOOD, CFG)
        self.assertIn("<h1>Racesafe VeloAir Air Gilet</h1>", out)
        self.assertIn("<h2>Sizing &amp; Fit</h2>", out)
        self.assertIn('<a href="https://www.discount-equestrian.co.uk/shop-by-brand/'
                      'hows-racesafe.html">Racesafe</a>', out)
        self.assertIn("<li>Fastening: waterproof zip</li>", out)
        self.assertIn("<td>86.4-91.4</td>", out)
        self.assertTrue(out.startswith("<!-- Meta Description: "))
        self.assertNotIn("DRAFT INFO", out)
        self.assertNotIn("check_draft.py", out)

    def test_submit_files(self):
        code = to_html.convert(GOOD, CFG, clean=True)
        self.assertTrue(code.startswith("<h1>Racesafe VeloAir Air Gilet</h1>"))
        self.assertNotIn("<!--", code)
        self.assertNotIn("Meta Description", code)
        page = to_html.submit_text_page(GOOD, CFG)
        self.assertIn("<p><strong>Meta Description:</strong> Racesafe VeloAir Air Gilet:", page)
        self.assertNotIn("DRAFT INFO", page)
        self.assertNotIn("check_draft.py", page)
        self.assertIn("<td>86.4-91.4</td>", page)


class TemplateImportTests(unittest.TestCase):
    @unittest.skipUnless(os.path.isfile(TEMPLATE), "source template not present")
    def test_import_matches_committed(self):
        tmp = tempfile.mkdtemp()
        try:
            import io
            import contextlib
            with contextlib.redirect_stdout(io.StringIO()):
                import_template.main([TEMPLATE, "--out", tmp])
            for name in os.listdir(tmp):
                with open(os.path.join(tmp, name), encoding="utf-8") as fh:
                    fresh = fh.read()
                with open(os.path.join(CFG["_dir"], name), encoding="utf-8") as fh:
                    self.assertEqual(fh.read(), fresh, "%s is stale: re-run import_template.py" % name)
        finally:
            shutil.rmtree(tmp)

    def test_about_versions_complete(self):
        self.assertEqual(sorted(CFG["about_versions"]),
                         ["A1", "A2", "A3", "B1", "B2", "B3", "K1", "K2"])
        for text in CFG["about_versions"].values():
            self.assertTrue(text.startswith("The [Product] is supplied by discount-equestrian.co.uk, {Role} "))


RH_CFG = pdplib.load_category("riding-hat")
RH_FILE2 = os.path.join(FIX, "riding-hat", "file2.xlsx")
RH_PRODUCTS, RH_LABELS = pdplib.load_products(RH_FILE2, RH_CFG)


def rh(stt):
    p = pdplib.find_product(RH_PRODUCTS, stt)
    return p, generic.analyse(p, RH_PRODUCTS, RH_CFG)


def rh_check(text, stt):
    p, a = rh(stt)
    return generic.check(text, p, a, RH_CFG)


class GenericEngineTests(unittest.TestCase):
    """Riding Hat category: config-driven card and checks."""

    def setUp(self):
        self.no1 = read(os.path.join("riding-hat", "good-draft-no1.md"))
        self.no2 = read(os.path.join("riding-hat", "good-draft-no2.md"))

    def test_columns_with_alternative_headers(self):
        p = RH_PRODUCTS[1]
        self.assertEqual(p["stt"], 2)
        self.assertEqual(p["brand"], "Charles Owen")
        self.assertIn("52CM", p["sizes"])
        self.assertIn("Navy", p["colours"])
        self.assertTrue(p["part_type"] == "/" and RH_PRODUCTS[0]["part_type"] == "headband")
        self.assertEqual(RH_PRODUCTS[0]["part_cleaning"][:4], "Wash")

    def test_template_and_variant(self):
        _, a1 = rh(1)
        _, a2 = rh(2)
        self.assertEqual((a1["type"], a1["variant"]), ("liners", "E"))
        self.assertEqual((a2["type"], a2["variant"]), ("riding_hat", "F"))
        self.assertEqual(a1["product_type"], "replacement headbands")
        self.assertIn("[discount-equestrian.co.uk](https://www.discount-equestrian.co.uk/)",
                      a2["supplier"])

    def test_variant_rules_order(self):
        base = dict(RH_PRODUCTS[1])
        for stt, brand, children, shape, want in (
                (7, "Charles Owen", "no", "peaked", "E"), (10, "Charles Owen", "no", "peaked", "A"),
                (8, "uvex", "yes", "peaked", "F"), (9, "KASK", "no", "jockey skull", "C"),
                (58, "uvex", "no", "peaked", "A"), (59, "uvex", "no", "peaked", "B"),
                (60, "uvex", "no", "peaked", "D")):
            p = dict(base, stt=stt, brand=brand, children_range=children, shape=shape)
            self.assertEqual(generic.analyse(p, RH_PRODUCTS, RH_CFG)["variant"], want, stt)

    def test_size_phrase_only_sold_sizes(self):
        _, a = rh(2)
        self.assertEqual(a["size_phrase"], "6⅜ to 6⅝ (52 to 54cm), plus 7¼ (59cm) in a round fit")
        _, a = rh(1)
        self.assertEqual(a["size_phrase"], "52 to 62cm, plus 56 to 58cm in a round fit")

    def test_good_drafts_pass(self):
        for text, stt in ((self.no1, 1), (self.no2, 2)):
            rep = rh_check(text, stt)
            self.assertEqual(rep.errors(), [], stt)

    def test_reviewer_findings_are_caught(self):
        bad = self.no2.replace("Available in sizes 6⅜ to 6⅝ (52 to 54cm), plus 7¼ (59cm) in a round fit,",
                               "Available in sizes from 52 to 59 cm (6⅜ to 7¼),")
        bad = bad.replace("**Colour:** Black, Black - Charcoal and Navy.",
                          "**Colour:** Choose from Black or Navy.")
        bad = bad.replace("[discount-equestrian.co.uk](https://www.discount-equestrian.co.uk/)",
                          "discount-equestrian.co.uk")
        errs = " | ".join(rh_check(bad, 2).errors())
        self.assertIn("ngụ ý DE bán cả 55cm", errs)
        self.assertIn("choose from", errs)
        self.assertIn("thiếu: Black - Charcoal", errs)
        self.assertIn("link về trang chủ", errs)

    def test_writer_edits_in_doc_are_caught(self):
        # what the writer pasted back: round fit dropped ("all round" elsewhere is not a mention),
        # home link auto-linked by Google Docs as http:// without www
        bad = self.no2.replace("plus 7¼ (59cm) in a round fit,", "plus 7¼ (59cm),")
        bad = bad.replace("(https://www.discount-equestrian.co.uk/)", "(http://discount-equestrian.co.uk)")
        self.assertIn("all round", bad)
        errs = " | ".join(rh_check(bad, 2).errors())
        self.assertIn("không nhắc round fit", errs)
        self.assertIn("link về trang chủ", errs)

    def test_meta_title_suffix_rule(self):
        errs = " | ".join(rh_check(self.no1.replace(
            "# META TITLE\nCharles Owen My PS Replacement Headband\n",
            "# META TITLE\nCharles Owen My PS Replacement Headband | Discount Equestrian\n"),
            1).errors())
        self.assertIn("Meta title phải là 'Charles Owen My PS Replacement Headband'", errs)

    def test_accessory_safety_wording_and_dash(self):
        bad = self.no1.replace("for a cleaner, fresher feel", "for a safer — fresher feel")
        errs = " | ".join(rh_check(bad, 1).errors())
        self.assertIn("gạch dài", errs)
        self.assertIn("Phụ kiện", errs)

    def test_made_in_uk_and_dressage(self):
        bad = self.no2.replace("smart, sophisticated look.",
                               "smart look, made in the UK and accepted by British Dressage.")
        errs = " | ".join(rh_check(bad, 2).errors())
        self.assertIn("made in the uk", errs)
        self.assertIn("British Dressage", errs)

    def test_card_and_submit_files(self):
        p, a = rh(2)
        card = generic.card_markdown(p, a, RH_CFG, RH_LABELS)
        self.assertIn("Black, Black - Charcoal, Navy", card)
        self.assertIn("DE variant **F**", card)
        page = to_html.submit_text_page(self.no2, RH_CFG)
        self.assertIn("<strong>Meta title:</strong>", page)
        self.assertIn("<h3>Safety standards &amp; certification</h3>", page)
        code = to_html.submit_html(self.no2, RH_CFG)
        self.assertTrue(code.startswith("Meta title: Charles Owen YR8 Riding Hat | Discount Equestrian"))
        self.assertNotIn("DRAFT INFO", code)


class PackagingTests(unittest.TestCase):
    def test_frontmatter(self):
        with open(os.path.join(SKILL, "SKILL.md"), encoding="utf-8") as fh:
            text = fh.read()
        fm = text.split("---", 2)[1]
        fields = set(re.findall(r"^([a-z-]+):", fm, re.M))
        self.assertTrue(fields <= SPEC_FRONTMATTER_FIELDS, fields - SPEC_FRONTMATTER_FIELDS)
        desc = re.search(r"^description: (.+)$", fm, re.M).group(1)
        self.assertLessEqual(len(desc), 1024)
        self.assertEqual(re.search(r"^name: (.+)$", fm, re.M).group(1), "pdp-content")

    def test_skill_references_exist(self):
        with open(os.path.join(SKILL, "SKILL.md"), encoding="utf-8") as fh:
            text = fh.read()
        outputs = {"card.md", "analysis.md", "draft.md", "draft.html", "brand-info.txt"}
        for name in set(re.findall(r"`([\w.-]+\.(?:md|json|py))`", text)) - outputs:
            hits = [r for r, _, fs in os.walk(SKILL) if name in fs]
            self.assertTrue(hits, "SKILL.md nhắc tới %s nhưng không có tệp" % name)

    def test_category_config_consistent(self):
        for slug in pdplib.list_categories():
            cfg = pdplib.load_category(slug)
            cols = set(cfg["columns"])
            if cfg.get("engine") == "generic":
                self.check_generic_config(cfg, cols)
                continue
            for key in cfg["required_columns"] + cfg["card_columns"]:
                self.assertIn(key, cols)
            for key, t in cfg["types"].items():
                for col in t["required_columns"] + t["type_columns"]:
                    self.assertIn(col, cols)
                for link in t["links"]:
                    self.assertTrue(link == "brand" or link in cfg["urls"])
                self.assertIn(t["type_url"], cfg["urls"])
                self.assertIn(key, cfg["link_placement"])
                self.assertTrue(os.path.isfile(os.path.join(cfg["_dir"], "outline-%s.md" % t["outline"])))
            for name in ("first-prompt.md", "file1-general.md", "analysis-template.md",
                         "draft-format.md", "rules.md"):
                self.assertTrue(os.path.isfile(os.path.join(cfg["_dir"], name)), name)

    def check_generic_config(self, cfg, cols):
        for key in cfg["required_columns"] + cfg["common_card_columns"] + cfg["de_owned"]:
            self.assertIn(key, cols)
        self.assertEqual(sorted(cfg["detect_order"]), sorted(cfg["types"]))
        variants = generic.load_variants(cfg)
        for rule in cfg["variant_rules"]:
            for v in [rule.get("variant")] + list(rule.get("mod3", {}).values()):
                if v:
                    self.assertIn(v, variants)
        for key, t in cfg["types"].items():
            for col in t["columns"]:
                self.assertIn(col, cols)
            self.assertTrue(t["h2"][-1][0] == "About the brand" and t["h2"][-1][1])
            self.assertEqual(t["bullets"][0], "Type")
        for link in cfg["links"]:
            self.assertTrue(set(link["types"]) <= set(cfg["types"]), link["key"])
        for name in ("first-prompt.md", "template.md", "checklist.md", "analysis-template.md",
                     "draft-format.md", "rules.md", "variants.json"):
            self.assertTrue(os.path.isfile(os.path.join(cfg["_dir"], name)), name)

    def test_plugin_manifests(self):
        with open(os.path.join(ROOT, ".claude-plugin", "marketplace.json"), encoding="utf-8") as fh:
            market = json.load(fh)
        with open(os.path.join(PLUGIN, ".claude-plugin", "plugin.json"), encoding="utf-8") as fh:
            plugin = json.load(fh)
        entry = next(e for e in market["plugins"] if e["name"] == plugin["name"])
        self.assertEqual(os.path.normpath(os.path.join(ROOT, entry["source"])), os.path.normpath(PLUGIN))
        # No pinned version anywhere: Claude Code then versions the plugin by the
        # commit SHA of its directory, so every push to main that touches the
        # plugin reaches users with auto-update on. A pinned "version" would
        # freeze them until someone remembers to bump it.
        self.assertNotIn("version", plugin)
        self.assertNotIn("version", entry)
        # Only plugin files ship: tests, sources and tooling stay outside.
        self.assertFalse(os.path.exists(os.path.join(PLUGIN, "tests")))
        self.assertFalse(os.path.exists(os.path.join(PLUGIN, "source")))


if __name__ == "__main__":
    unittest.main(verbosity=1)
