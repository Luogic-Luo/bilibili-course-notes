# ASR environment setup

Target: local, offline-capable Chinese ASR via `faster-whisper` (CTranslate2).
No GPU required; CPU int8 is fast enough for a 13 h course in ~2.5-3 h.

## Python

Use a Python **3.10-3.13** interpreter. The bundled Codex runtime
(`load_workspace_dependencies` -> `dependencies/python/python.exe`) is 3.12 and
works. A bare system Python 3.14 may lack wheels for `ctranslate2`/`av`.

```bash
pip install faster-whisper av numpy
```

`faster-whisper` pulls `ctranslate2`, `huggingface_hub`, `tokenizers`, `onnxruntime`.

## Model

`small` is the sweet spot for Chinese technical speech: 483 MB, RTF ~0.2 on
16 cores, and far better on jargon than `base`/`tiny`.

```bash
python scripts/ensure_model.py small
```

Order of attempts inside the script:

1. **ModelScope** - `pengzhendong/faster-whisper-small` mirrors the
   CTranslate2 files (`config.json`, `model.bin`, `tokenizer.json`,
   `vocabulary.txt`). Downloads at 10-25 MB/s from a mainland-China CDN
   (483 MB in ~20 s). The mirror omits `preprocessor_config.json`; the script
   writes a standard one.
2. **Hugging Face via `hf-mirror.com`** - needs `HF_ENDPOINT=https://hf-mirror.com`
   **and** `HF_HUB_DISABLE_XET=1` (the xet CAS backend returns 401; plain HTTP
   through the mirror works, just slowly, ~400 KB/s).
3. Direct `huggingface.co` - often unreachable; slowest.

## PyAV / faster-whisper incompatibility

`faster-whisper`'s `decode_audio()` calls `av.open(..., metadata_errors=...)`.
PyAV 14 dropped that keyword, so it raises:

```
TypeError: open() got an unexpected keyword argument 'metadata_errors'
```

`scripts/transcribe.py` does **not** use it. It decodes manually:

```python
container = av.open(path)
stream = container.streams.audio[0]
resampler = av.audio.resampler.AudioResampler(format="s16", layout="mono", rate=16000)
chunks = [out.to_ndarray() for frame in container.decode(stream) for out in resampler.resample(frame)]
audio = np.concatenate(chunks, axis=1).astype(np.float32).reshape(-1) / 32768.0
```

This gives a 16 kHz mono float32 array that `model.transcribe()` accepts
directly, and it also lets you slice a time range without re-decoding.

## Encoding on Windows / Chinese locale

Always run the scripts with `PYTHONUTF8=1`:

- Without it, Python writes stdout in the system codepage (cp936) and the
  Chinese output shows as mojibake in PowerShell.
- Chinese path literals inside a `.py` file can also fail to open files.

`PYTHONIOENCODING=utf-8` fixes stdout only; `PYTHONUTF8=1` covers both and
also makes the filesystem encoding UTF-8.

For PowerShell pipelines, do **not** pipe python output through
`Set-Content -Encoding UTF8` (that decodes cp936 bytes as UTF-8 and mangles
the text). Either set `PYTHONIOENCODING=utf-8`, or have the script write its
own file with `encoding="utf-8"` (the bundled scripts do).

## Speed reference

Measured on 16 logical cores, `small` + int8 + `cpu_threads=14`:

| Audio | Wall time | RTF |
|---|---|---|
| 6 min | ~70-95 s | 0.19-0.26 |
| 11 min | ~150 s | 0.23 |

Rule of thumb: **total wall time ~= total audio duration / 5**. Two
transcription processes on the same box roughly halve each other's speed.

## ASR quality notes

- `beam_size=1`, `vad_filter=False`, `condition_on_previous_text=False` is a
  good fast configuration for lecture audio.
- `initial_prompt` with a comma-separated list of domain terms measurably
  improves recognition of those terms.
- Chinese homophone errors are common ("精讲"->"经讲", "数据项"->"数据相").
  Always read the transcript with that in mind; do not copy its wording
  verbatim into notes.
