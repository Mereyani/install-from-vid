# install-from-video

**Read the docs in another language:** [العربية](README.ar.md) · [Türkçe](README.tr.md)

A Claude Code skill. You send it a reel that recommends developer tools. It tells you what
those tools actually are, proves they exist, and hands you the install commands.

```
you:    https://instagram.com/reel/…   "install what's in this"
skill:  ✓ 4 tools found, 4 verified, 2 already installed
        here are the commands — you run them
```

---

## Why this exists

"Top 5 tools" clips are everywhere and almost none of them include links. You are expected
to pause the video, squint at a repo name, and type it into GitHub yourself.

That last step is where it breaks. Transcribing a name by ear puts you one letter away
from a typosquat, and a plugin you install runs its hooks in every session afterwards.

This skill closes that gap: it listens, it reads the screen, it checks, and then it stops
and lets you decide.

## What makes it different

**It runs on your machine.** The clip is transcribed locally with faster-whisper. No API
call, no upload, no per-minute cost. Only the reasoning about the result reaches a model.

**It reads the screen, not just the audio.** This is the part everyone skips, and it is the
part that matters — see the table below.

**It refuses to install anything.** A video is an untrusted source. The skill produces
commands; a human runs them.

**It is cheap by design.** Audio first. Frames only when a name is genuinely unclear —
because images, not transcription, are what actually cost you context.

## The one table that justifies the whole design

The skill is language-agnostic — it auto-detects, and the model covers 90-odd languages.
The example below happens to be Arabic because that is what it was first tested on; the
same failure appears in any narration that drops English product names into it.

The same 59-second clip, transcribed by two model sizes:

| What was said | `whisper-small` | `whisper-large-v3` | The truth |
|---|---|---|---|
| Agent Skills | `AgedSkills` ❌ | `agent skills` ✅ | `addyosmani/agent-skills` |
| OmniRoute | `أم نيروت` ❌ | `أومني راوت` ✅ | `diegosouzapw/OmniRoute` |
| Ponytail | `PonyTail` ⚠️ | `ponytail` ✅ | `DietrichGebert/ponytail` |
| the numbers | `"4.50%"` ❌ | `"22%"`, `"54%"` ✅ | 22% and 54% |

Searching GitHub for `AgedSkills` returns zero-star copies, not the 98k-star original.
The correct name came from **one frame at 35.4s**, where a browser URL bar read
`github.com/addyosmani/agent-skills`.

Audio tells you the shape of the list. The screen tells you the names. You need both.

## Install

```bash
claude plugin marketplace add Mereyani/install-from-video
claude plugin install install-from-video@install-from-video
```

Then the Python dependencies, into whichever interpreter Claude Code will use:

```bash
python3 -m pip install yt-dlp faster-whisper pillow av
```

If you get it wrong, the script tells you the exact interpreter and pip line to run. That
error message exists because this repo's author hit it first.

Restart Claude Code.

## Use

Just send a link:

> install the plugins from this https://www.tiktok.com/@someone/video/…

Or call it explicitly with `/install-from-video`. Anything yt-dlp supports works — Instagram,
TikTok, YouTube, X, Reddit.

## How it works

1. **Audio pass** — `yt-dlp` pulls audio only (~0.4 MB for a minute), `faster-whisper`
   transcribes it on the CPU. Free, local, no tokens.
2. **Frame pass, conditional** — if a name is still unclear, the video is fetched and ~40
   frames are tiled into timestamped contact sheets to read. This is the step that costs
   context, so it is opt-in.
3. **Verify** — every candidate is checked against npm and the GitHub API. A package whose
   `repository.url` 404s is reported as a likely typosquat.
4. **Resolve the id** — `plugin@marketplace` is read from the cloned manifest, because the
   marketplace registers under the manifest's `name`, not the repo's.
5. **Hand over** — one `bash` block per tool, plus a table of what was verified.

## Three things this repo learned the hard way

**A marketplace does not take the repo's name.** `claude plugin marketplace add` registers
it under the `name` field inside `.claude-plugin/marketplace.json`. So
`thedotmack/claude-mem` installs as `claude-mem@thedotmack`, and `addyosmani/agent-skills`
as `agent-skills@addy-agent-skills`. Guessing costs you a failed install every time.

**An npm package can point at a repository that no longer exists.** `obsidian-second-brain`
on npm resolves to a deleted GitHub repo. The real project lives at a different owner
entirely. Always read `repository.url`, and always open it.

**Speech recognition fails precisely where it hurts most.** A model transcribing one
language writes foreign product names phonetically. The failure is silent — you get a
plausible word, not an error. Only the screen corrects it.

## Choosing a model

`large-v3` is the default, and the tables above are why. On an 8-core Intel CPU it runs at
roughly 2x realtime — a one-minute clip takes about two minutes — and uses ~4.8 GB of RAM.

Measured alternatives, and why they lost:

| Model | Verdict |
|---|---|
| `small` | Mangles exactly the names you need. See the table. |
| `medium` | Smaller, and never beat large-v3 on real test clips. |
| `large-v3-turbo` | 6x faster but worse on Arabic (WER 40.05 vs 36.86). |
| `distil-large-v3` | English only. Disqualified. |

Override with `--model` if you only need the gist.

Two things that sound like improvements and are not: setting `cpu_threads=8` measured
**8% slower** than letting CTranslate2 choose, and slowing the audio to 0.9x has no
reliable support in the literature — the failure mode is code-switching, not tempo.

## Requirements

Python 3.9+, `yt-dlp`, `faster-whisper`, `pillow`, `av`. No ffmpeg: audio is downloaded in
its native container and never re-encoded, which is both simpler and more accurate than
converting to mp3.

First run downloads the `large-v3` weights (~2.4 GB), then caches them.

## Limits

- It cannot extract a name the video never states. If the creator says "the second tool" and
  never shows it, the skill says so instead of guessing.
- Login-walled or DRM-protected posts will not download.
- Transcription quality sets the ceiling on everything downstream.

## Responsible use

This tool downloads a copy of something someone else published, so a few things are worth
stating plainly.

- **It is for reading, not redistributing.** The audio and any frames are working files.
  Delete them when you are done — the bundled `.gitignore` keeps them out of git by default.
- **Respect the platform's terms.** Some sites restrict automated downloading. The terms you
  agreed to when you signed up are an agreement you made; honour it. This tool does not
  bypass login walls or DRM, and will not try to.
- **Credit the creator.** If a recommendation turns out to be useful, the person who made
  the clip did the work of finding it. Say where it came from.
- **The projects are other people's.** Read their licences before you build on them, and
  keep their attribution intact.

## License

MIT
