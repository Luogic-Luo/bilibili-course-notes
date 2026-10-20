# bilibili-course-notes

A Codex skill that turns a **multi-part Bilibili course into structured per-chapter study notes**, by pulling the audio down and transcribing it locally.

Bilibili exposes no subtitles and no AI summaries without a login
(`x/player/v2` returns an empty `subtitles` list, `view/conclusion/get` returns
`-403`), so local ASR is the only way to capture what the teacher actually
says. This skill does that, then writes the notes.

## What it produces

```
<vault>/<course-slug>.md             the notes
<vault>/<course-slug>-transcripts/    raw ASR transcripts (pNN.txt) + README
```

One `##` section per video part, a bold "考点主线" line, numbered points with
the key terms bolded, comparison tables, exam-weight tags
(`计算题` / `概念辨析` / `下午题`), plus three appendices: a part index, a
high-frequency-and-error-prone checklist, and a revision route.

## Pipeline

| Step | Script | What it does |
|---|---|---|
| 1 | `scripts/fetch_course.py` | Bilibili public API -> `course.json` (every part: `cid`, title, duration, audio URL). No login needed. |
| 2 | `scripts/download_audio.py` | Parallel, resumable download of each part's audio. |
| 3 | `scripts/ensure_model.py` | Fetches a `faster-whisper` model (ModelScope first, then `hf-mirror.com`, then Hugging Face). |
| 4 | `scripts/transcribe.py` | Local ASR -> one `pNN.txt` per part, `[seconds] text` lines, resumable. |
| 5 | `scripts/make_scaffold.py` | Writes the notes skeleton with the part index table filled in. |

Then Codex fills each section from the transcripts.

### Two-pass transcription

`faster-whisper` `small` on a 16-core CPU runs at **RTF ~0.2** (6 min of audio
in ~70 s), so a 13.5 h course costs ~2.7 h of CPU for a full pass.

- `--mode head --minutes 6` transcribes the first 6 minutes of every part:
  ~30 min of compute for a 24-part course, and disproportionately useful
  because teachers open a part by enumerating its 考点 list. Use it to get the
  skeleton of the whole course fast.
- `--mode rest --minutes 6` picks up everything after that, so the two modes
  together equal a full pass with no duplicated work.
- `--mode full` transcribes one part end to end.

## Install

The skill needs a Python 3.10-3.13 with:

```bash
pip install faster-whisper av numpy
```

Drop the folder into `~/.codex/skills/` (or `~/.agents/skills/`) and it is
discovered automatically. Invoke it with `$bilibili-course-notes`.

## Gotchas this skill already handles

| Symptom | Cause / fix |
|---|---|
| `TypeError: open() got an unexpected keyword argument 'metadata_errors'` | PyAV >= 14 removed that kwarg; `transcribe.py` decodes with PyAV directly instead of `faster_whisper.decode_audio`. |
| Model download times out | `ensure_model.py` prefers ModelScope (fast from a mainland-China CDN); `hf-mirror.com` needs `HF_HUB_DISABLE_XET=1`. |
| Chinese text is mojibake / Chinese paths fail to open | Run the scripts with `PYTHONUTF8=1`. |
| `pNN.m4a` is 0 bytes | The stream URL expired - re-run `fetch_course.py`, then `download_audio.py`. |
| A part has no audio URL | The video is paid/exclusive; that part cannot be transcribed. |

## Notes

- Transcripts are ASR output: expect Chinese homophone slips
  ("精讲"->"经讲", "数据项"->"数据相"). Read them with that in mind and do not
  copy their wording verbatim into notes.
- `--prompt` takes a comma-separated list of domain terms and measurably
  improves recognition of those terms.
- Drafting a chapter from a syllabus rather than a transcript invites subtle
  errors. Cross-check every formula and comparison against the transcript
  before shipping, and say which pass a section is based on.

## License

MIT
