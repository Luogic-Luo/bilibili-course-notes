---
name: bilibili-course-notes
description: Turn a multi-part Bilibili video course into structured per-chapter study notes (Markdown) by downloading the audio, transcribing it locally with faster-whisper, and writing exam-point summaries. Use when the user asks to summarize/notes/transcript a Bilibili course, a multi-P video series, or lecture videos, especially when the course has no public subtitles.
---

# Bilibili course -> structured chapter notes

Pipeline: **fetch manifest -> download audio -> transcribe locally -> write per-part notes**.

Bilibili does not expose subtitles or AI summaries without a login
(`x/player/v2` returns an empty `subtitles` list; `view/conclusion/get` returns
`-403`), so local ASR is the only way to get the teacher's actual wording.
Plan for that cost up front - see [Transcription strategy](#transcription-strategy).

## 1. Set up the environment (once per machine)

See [references/asr-setup.md](references/asr-setup.md) for installs, mirrors and
troubleshooting. The two non-obvious ones:

- **Set `PYTHONUTF8=1` when invoking the scripts.** On a Chinese-locale
  Windows box, without it, Chinese paths fail to open and Chinese stdout comes
  out as mojibake. (`PYTHONIOENCODING=utf-8` fixes stdout only.)
- **Model download**: huggingface.co is unreachable from many networks.
  `scripts/ensure_model.py` tries ModelScope first (fast in mainland China),
  then `hf-mirror.com` with `HF_HUB_DISABLE_XET=1`.

## 2. Fetch the course manifest

```bash
python scripts/fetch_course.py <bvid_or_url> <workdir>
```

Writes `<workdir>/course.json`: every part with `page`, `cid`, `part` (title),
`duration`, and the best `audio_url`. Prints a per-part table so you can spot
parts with no audio stream. Accepts a full video URL - the `?p=` parameter is
irrelevant, the whole series is fetched.

## 3. Download the audio

```bash
python scripts/download_audio.py <workdir> [threads]
```

Writes `<workdir>/audio/pNN.m4a`, resumable (skips complete files). Verify the
file count equals the part count - a zero-byte file means the stream URL
expired, so re-run `fetch_course.py` and download again.

## 4. Transcribe

```bash
python scripts/ensure_model.py small                      # prints the model dir
python scripts/transcribe.py <workdir> <model_dir> <outdir> \
    --mode head --minutes 6 --prompt "term1,term2"
```

`--mode head` = first N minutes of every part; `--mode rest` = everything
after N minutes; `--mode full` = the whole part. Output is one `pNN.txt` per
part with `[seconds] text` lines, written incrementally and skipped if the file
already exists, so the job is resumable and can run in the background.

`--prompt` is a comma-separated list of domain terms (course jargon, proper
nouns). It measurably improves recognition of those words - use it.

### Transcription strategy

On a 16-core CPU, `faster-whisper` `small` + int8 runs at **RTF ~0.2**
(6 min of audio in ~70 s), i.e. roughly 5x realtime.

- **A 24-part, 13.5 h course costs ~2.7 h of pure CPU for a full pass.**
- A `head` pass of 6 min/part is **144 min of audio, ~30 min of compute**, and
  is disproportionately informative: teachers usually open a part by
  enumerating that part's 考点 list ("我把它分为这九个考点"). That gives you the
  **skeleton of what the course covers**, cheaply, for every part.

Recommended order:

1. Run the `head` pass for all parts. Write the first version of the notes
   from it plus authoritative subject-matter sources for the course's syllabus.
2. Start a `rest` pass in the background (`--mode rest --minutes 6`).
3. As each part's full transcript lands, **rewrite that section to follow the
   teacher's actual teaching order**, and keep his examples, his emphasis
   ("这个要考"), and any correction he makes to common mistakes.

Do not claim a section is a faithful account of the video until its full
transcript exists - a head-only pass gives correct coverage but textbook
ordering, not the teacher's ordering. Say which pass a section is based on.

## 5. Write the notes

Follow the conventions in [references/note-style.md](references/note-style.md):
one section per part, a bold "考点主线" line, numbered points, bolded
keywords, an index table appendix, and a high-frequency/error-prone appendix.

Where the notes go is the user's call - if they mention a vault, notebook or
folder, write the Markdown there and tell them the path. Keep the raw
transcripts next to the notes in a clearly-named subfolder so they can grep
them, and add a short README explaining that the transcripts are ASR output
with possible homophone errors.

## Quality bar

- **Check your own facts.** Drafting a chapter from a syllabus invites subtle
  errors (e.g. "先序 + 后序 uniquely determines a binary tree" is false - it
  needs 中序). Cross-check every property, formula and comparison against the
  transcript before shipping, and re-verify anything you wrote from memory.
- **Mark the exam weight** of each point (计算题 / 概念辨析 / 下午题) so the
  user knows what to spend time on.
- **Report honestly** what the notes are based on: full transcript, head
  transcript, or subject-matter knowledge.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `TypeError: open() got an unexpected keyword argument 'metadata_errors'` | PyAV >= 14 removed that kwarg. `transcribe.py` avoids it by decoding with PyAV directly; do not call `faster_whisper.decode_audio` on PyAV >= 14. |
| Model download times out | Use `ensure_model.py` (ModelScope first), or set `HF_ENDPOINT=https://hf-mirror.com` and `HF_HUB_DISABLE_XET=1`. |
| Chinese text is mojibake in the terminal | Run with `PYTHONUTF8=1`. |
| `pNN.m4a` is 0 bytes | The stream URL expired; re-run `fetch_course.py`, then `download_audio.py`. |
| `subtitles: []` from the player API | Expected without a login; use local ASR. |
| A part has no audio URL | The video may be paid/exclusive; that part cannot be transcribed - say so instead of guessing its content. |
