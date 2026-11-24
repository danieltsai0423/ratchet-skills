"""Validate every skill folder: frontmatter name matches folder, description present,
relative Markdown links resolve. Exit 1 on any problem. Usage: python scripts/validate_skills.py"""
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
skills = root / "skills"
errors = []
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")

dirs = sorted(p for p in skills.iterdir() if p.is_dir())
if not dirs:
    errors.append("no skills found")
for d in dirs:
    md = d / "SKILL.md"
    if not md.is_file():
        errors.append(f"{d.name}: missing SKILL.md")
        continue
    text = md.read_text(encoding="utf-8")
    if text.startswith("﻿"):
        errors.append(f"{d.name}: SKILL.md has a UTF-8 BOM")
        text = text[1:]
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not m:
        errors.append(f"{d.name}: missing YAML frontmatter")
        continue
    fm = dict(
        (k.strip(), v.strip())
        for k, v in (line.split(":", 1) for line in m.group(1).splitlines() if ":" in line)
    )
    name = fm.get("name", "")
    if name != d.name:
        errors.append(f"{d.name}: frontmatter name '{name}' does not match folder")
    if not NAME_RE.match(d.name) or len(d.name) > 64:
        errors.append(f"{d.name}: name must be lowercase-hyphenated, max 64 chars")
    desc = fm.get("description", "")
    if not desc:
        errors.append(f"{d.name}: missing description")
    elif len(desc) > 1024:
        errors.append(f"{d.name}: description longer than 1024 chars")
    for f in d.rglob("*.md"):
        for target in LINK_RE.findall(f.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("mailto:"):
                continue
            if not (f.parent / target).exists():
                errors.append(f"{f.relative_to(root)}: broken link {target}")
    print(f"ok  {d.name}")

for e in errors:
    print(f"ERROR {e}", file=sys.stderr)
sys.exit(1 if errors else 0)
