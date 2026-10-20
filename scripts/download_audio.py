#!/usr/bin/env python3
"""Download every part's audio for a course manifest (parallel, resumable).

Usage:
  python download_audio.py <workdir> [threads]

Reads <workdir>/course.json, writes <workdir>/audio/pNN.m4a.
Already-complete files are skipped, so re-running resumes.
"""
import concurrent.futures
import json
import os
import sys
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
HEADERS = {"User-Agent": UA, "Referer": "https://www.bilibili.com/"}


def fetch(page, outdir):
    dest = os.path.join(outdir, "p%02d.m4a" % page["page"])
    if os.path.exists(dest) and os.path.getsize(dest) > 10000:
        return page["page"], "skip"
    if not page.get("audio_url"):
        return page["page"], "NO-AUDIO-URL"
    req = urllib.request.Request(page["audio_url"], headers=HEADERS)
    tmp = dest + ".part"
    with urllib.request.urlopen(req, timeout=180) as r, open(tmp, "wb") as f:
        while True:
            b = r.read(1 << 16)
            if not b:
                break
            f.write(b)
    os.replace(tmp, dest)
    return page["page"], os.path.getsize(dest)


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    workdir = sys.argv[1]
    threads = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    with open(os.path.join(workdir, "course.json"), encoding="utf-8") as f:
        man = json.load(f)
    outdir = os.path.join(workdir, "audio")
    os.makedirs(outdir, exist_ok=True)
    total = 0
    with concurrent.futures.ThreadPoolExecutor(threads) as ex:
        for page, res in ex.map(lambda p: fetch(p, outdir), man["pages"]):
            if isinstance(res, int):
                total += res
                print("P%-3d %8.1f MB" % (page, res / 1e6), flush=True)
            else:
                print("P%-3d %s" % (page, res), flush=True)
    print("DONE total=%.1f MB" % (total / 1e6))


if __name__ == "__main__":
    main()
