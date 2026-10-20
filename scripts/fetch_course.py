#!/usr/bin/env python3
"""Fetch a Bilibili multi-part course manifest (page list + audio stream URLs).

No login required. Writes course.json describing every part (cid, title,
duration) plus the best available audio URL for each.

Usage:
  python fetch_course.py <bvid_or_url> [outdir]

Example:
  python fetch_course.py BV1rc411t71D ./work
  python fetch_course.py "https://www.bilibili.com/video/BV1rc411t71D/?p=5" ./work

Run with PYTHONUTF8=1 on Windows Chinese-locale machines so that the
non-ASCII part titles are written/read correctly.
"""
import json
import os
import re
import sys
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
HEADERS = {"User-Agent": UA, "Referer": "https://www.bilibili.com/"}


def get_json(url, headers=None):
    req = urllib.request.Request(url, headers=headers or HEADERS)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def parse_bvid(arg):
    m = re.search(r"(BV[0-9A-Za-z]{10})", arg)
    if not m:
        raise SystemExit("Could not find a BV id in: %r" % arg)
    return m.group(1)


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    bvid = parse_bvid(sys.argv[1])
    outdir = sys.argv[2] if len(sys.argv) > 2 else "."
    os.makedirs(outdir, exist_ok=True)

    view = get_json("https://api.bilibili.com/x/web-interface/view?bvid=" + bvid)
    if view.get("code") != 0:
        raise SystemExit("view API failed: %s" % view.get("message"))
    data = view["data"]
    pages = []
    for p in data["pages"]:
        pu = ("https://api.bilibili.com/x/player/playurl?bvid=%s&cid=%d&fnval=16&fourk=0"
              % (bvid, p["cid"]))
        d = get_json(pu).get("data", {})
        audios = (d.get("dash") or {}).get("audio") or []
        best = max(audios, key=lambda a: a.get("bandwidth", 0)) if audios else None
        pages.append({
            "page": p["page"],
            "cid": p["cid"],
            "part": p["part"],
            "duration": p["duration"],
            "audio_url": best["baseUrl"] if best else None,
            "bandwidth": best.get("bandwidth", 0) if best else 0,
        })

    manifest = {
        "bvid": bvid,
        "aid": data["aid"],
        "title": data["title"],
        "owner": data["owner"]["name"],
        "duration": data["duration"],
        "n_pages": len(pages),
        "pages": pages,
    }
    path = os.path.join(outdir, "course.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print("wrote %s (%d parts, %.1f h total)" % (path, len(pages), data["duration"] / 3600.0))
    for p in pages:
        flag = "" if p["audio_url"] else "   <-- NO AUDIO"
        print("  P%-3d %5.1f min  %s%s" % (p["page"], p["duration"] / 60.0, p["part"], flag))


if __name__ == "__main__":
    main()
