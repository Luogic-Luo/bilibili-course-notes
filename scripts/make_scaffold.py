#!/usr/bin/env python3
"""Build the notes scaffold for a course: a part index table + one section per part.

Usage:
  python make_scaffold.py <workdir> <out_md> [--title "Course notes"]

Fills a Markdown file with a title, a course overview block, a per-part index
table (P / title / duration / notes link), and a placeholder heading per part.
Then the agent fills each section from the transcript.
"""
import argparse
import json
import os
import re


def slug(part):
    """ASCII-safe anchor; keeps CJK but strips characters that break links."""
    s = part.strip()
    s = re.sub(r"[\\`*_\[\]#|]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("workdir")
    ap.add_argument("out_md")
    ap.add_argument("--title", default="Course notes")
    args = ap.parse_args()

    with open(os.path.join(args.workdir, "course.json"), encoding="utf-8") as f:
        man = json.load(f)

    lines = []
    lines.append("# %s" % args.title)
    lines.append("")
    lines.append("> Source: <https://www.bilibili.com/video/%s/> - uploader: %s" % (man["bvid"], man["owner"]))
    lines.append("> %d parts, %.1f h total." % (man["n_pages"], man["duration"] / 3600.0))
    lines.append("")
    lines.append("## Part index")
    lines.append("")
    lines.append("| P | Part | Length | Notes |")
    lines.append("|---|---|---|---|")
    for p in man["pages"]:
        m, s = divmod(int(p["duration"]), 60)
        lines.append("| %d | %s | %d:%02d | [[#%s]] |" % (p["page"], p["part"], m, s, slug(p["part"])))
    lines.append("")
    for p in man["pages"]:
        lines.append("## %s" % p["part"])
        lines.append("")
        lines.append("<!-- TODO: summarize from transcripts/p%02d.txt -->" % p["page"])
        lines.append("")
        lines.append("")

    with open(args.out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("wrote %s" % args.out_md)


if __name__ == "__main__":
    main()
