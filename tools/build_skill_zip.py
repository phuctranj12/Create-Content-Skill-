# -*- coding: utf-8 -*-
"""Zip each skill of the plugin for upload to claude.ai (Customize > Skills).

    py -3 tools/build_skill_zip.py            # -> dist/pdp-content.zip, dist/category-content.zip

Claude Code installs the plugin straight from GitHub and updates itself; the
chat app on claude.ai takes a skill as a zip upload instead, so this builds
that zip from the same folder. Standard library only.
"""

import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "plugins", "create-content", "skills")
SKIP_DIRS = {"__pycache__"}
SKIP_EXT = {".pyc", ".pyo"}


def build(skill, out_dir):
    src = os.path.join(SKILLS, skill)
    out = os.path.join(out_dir, "%s.zip" % skill)
    count = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for folder, dirs, files in os.walk(src):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
            for name in sorted(files):
                if os.path.splitext(name)[1] in SKIP_EXT or name.endswith(".local.md"):
                    continue
                path = os.path.join(folder, name)
                arc = os.path.join(skill, os.path.relpath(path, src))
                z.write(path, arc.replace(os.sep, "/"))
                count += 1
    print("-> %s (%d files)" % (out, count))


def main(argv=None):
    out_dir = os.path.join(ROOT, "dist")
    os.makedirs(out_dir, exist_ok=True)
    for skill in sorted(os.listdir(SKILLS)):
        if os.path.isfile(os.path.join(SKILLS, skill, "SKILL.md")):
            build(skill, out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
