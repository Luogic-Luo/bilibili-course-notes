#!/usr/bin/env python3
"""Make sure a local faster-whisper (CTranslate2) model is available.

Order of preference:
  1. ModelScope mirror  - fast in mainland China (~10-25 MB/s).
  2. Hugging Face mirror - hf-mirror.com, with xet disabled.
  3. Direct Hugging Face - may be unreachable on some networks.

Usage:
  python ensure_model.py <size> [<cache_dir>]

Prints the local model directory on stdout. Exit code 0 on success.
"""
import json
import os
import sys
import urllib.request

MS_REPO = "pengzhendong/faster-whisper-%s"
MS_URL = ("https://www.modelscope.cn/api/v1/models/%s/repo?Revision=master&FilePath=")
FILES = ["config.json", "model.bin", "tokenizer.json", "vocabulary.txt"]
# faster-whisper needs this; the ModelScope mirror does not ship it.
PREPROCESSOR = {
    "chunk_length": 30, "do_normalize": True, "do_pad": False,
    "do_stable_scale": False, "do_stft": False, "feature_size": 80,
    "hop_length": 160, "mel_filters": 80, "n_fft": 400,
    "padding_value": 0.0, "return_attention_mask": False, "sampling_rate": 16000,
}


def from_modelscope(size, dest):
    repo = MS_REPO % size
    for f in FILES:
        p = os.path.join(dest, f)
        if os.path.exists(p) and os.path.getsize(p) > 1000:
            print("have", f)
            continue
        print("downloading", f, "from ModelScope ...")
        with urllib.request.urlopen(urllib.request.Request(MS_URL % repo + f), timeout=300) as r:
            data = r.read()
        with open(p, "wb") as out:
            out.write(data)
        print("  got %.1f MB" % (len(data) / 1e6))
    with open(os.path.join(dest, "preprocessor_config.json"), "w", encoding="utf-8") as f:
        json.dump(PREPROCESSOR, f, indent=1)
    return dest


def from_hf(size, dest):
    os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
    os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
    from huggingface_hub import snapshot_download
    return snapshot_download("Systran/faster-whisper-%s" % size)


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    size = sys.argv[1] if len(sys.argv) > 1 else "small"
    cache = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        os.path.expanduser("~"), ".cache", "course-asr")
    dest = os.path.join(cache, "faster-whisper-" + size)
    os.makedirs(dest, exist_ok=True)
    try:
        print(from_modelscope(size, dest))
        return
    except Exception as e:
        print("ModelScope failed (%s), trying Hugging Face ..." % e)
    try:
        print(from_hf(size, dest))
    except Exception as e:
        raise SystemExit("All model sources failed: %s" % e)


if __name__ == "__main__":
    main()
