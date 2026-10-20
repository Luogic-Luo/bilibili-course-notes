#!/usr/bin/env python3
"""Batch-transcribe a downloaded course into per-part plain-text transcripts.

Decodes audio with PyAV manually and feeds a numpy array to faster-whisper.
This deliberately avoids faster-whisper's own decode_audio(), which calls
av.open(..., metadata_errors=...) and breaks on PyAV >= 14.

Modes (--mode):
  head  first --minutes minutes of every part   -> the teacher's outline fast
  rest  everything AFTER --minutes minutes       -> full body, no re-work
  full  the entire part (ignores --minutes)

Usage:
  python transcribe.py <workdir> <model_dir> <outdir> [--mode head] [--minutes 6]
                       [--only 5,7,12] [--threads 14] [--prompt "term,term"]

Writes <outdir>/pNN.txt, one block per part:
  ### P5 2.1 xxx
  [12.4] transcript line ...
Already-finished parts are skipped, so the job is resumable.
"""
import argparse
import json
import os
import sys
import time

import numpy as np
import av


def decode_to_16k_mono(path):
    """Decode any container/codec to a 16 kHz mono float32 numpy array."""
    container = av.open(path)
    stream = container.streams.audio[0]
    resampler = av.audio.resampler.AudioResampler(format="s16", layout="mono", rate=16000)
    chunks = []
    for frame in container.decode(stream):
        for out in resampler.resample(frame):
            chunks.append(out.to_ndarray())
    container.close()
    if not chunks:
        return np.zeros(0, dtype=np.float32)
    return np.concatenate(chunks, axis=1).astype(np.float32).reshape(-1) / 32768.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("workdir")
    ap.add_argument("model_dir")
    ap.add_argument("outdir")
    ap.add_argument("--mode", default="head", choices=["head", "rest", "full"])
    ap.add_argument("--minutes", type=float, default=6.0)
    ap.add_argument("--only", default="")
    ap.add_argument("--threads", type=int, default=0)
    ap.add_argument("--prompt", default="")
    args = ap.parse_args()

    from faster_whisper import WhisperModel

    with open(os.path.join(args.workdir, "course.json"), encoding="utf-8") as f:
        man = json.load(f)
    os.makedirs(args.outdir, exist_ok=True)
    only = {int(x) for x in args.only.split(",") if x.strip()}

    threads = args.threads or max(1, (os.cpu_count() or 4) - 2)
    model = WhisperModel(args.model_dir, device="cpu", compute_type="int8", cpu_threads=threads)
    print("model=%s threads=%d mode=%s" % (args.model_dir, threads, args.mode), flush=True)

    for page in man["pages"]:
        n = page["page"]
        if only and n not in only:
            continue
        out_path = os.path.join(args.outdir, "p%02d.txt" % n)
        if os.path.exists(out_path) and os.path.getsize(out_path) > 50:
            print("P%-3d skip (exists)" % n, flush=True)
            continue
        audio_path = os.path.join(args.workdir, "audio", "p%02d.m4a" % n)
        if not os.path.exists(audio_path) or os.path.getsize(audio_path) < 10000:
            print("P%-3d MISSING AUDIO" % n, flush=True)
            continue

        t0 = time.time()
        audio = decode_to_16k_mono(audio_path)
        if args.mode == "head":
            audio = audio[: int(args.minutes * 60) * 16000]
        elif args.mode == "rest":
            audio = audio[int(args.minutes * 60) * 16000:]
        if audio.size == 0:
            print("P%-3d no audio" % n, flush=True)
            continue

        segs, _ = model.transcribe(
            audio, language="zh", beam_size=1, vad_filter=False,
            initial_prompt=args.prompt or None, condition_on_previous_text=False)
        offset = 0.0 if args.mode != "rest" else args.minutes * 60
        lines = ["[%0.1f] %s" % (s.start + offset, s.text.strip()) for s in segs]
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("### P%d %s\n" % (n, page["part"]) + "\n".join(lines))
        dur = (time.time() - t0) / 60.0
        print("P%-3d %-40s lines=%-4d %.1fs (%.1f min audio)" % (
            n, page["part"][:40], len(lines), time.time() - t0, audio.size / 16000 / 60.0), flush=True)
    print("ALLDONE", flush=True)


if __name__ == "__main__":
    main()
