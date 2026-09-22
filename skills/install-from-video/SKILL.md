---
name: install-from-video
description: User sends a video link (Instagram, TikTok, YouTube, X...) that recommends Claude Code plugins, MCP servers, or dev tools. Extracts the spoken and on-screen content, verifies each named project is real, and returns install commands. Use whenever a video/reel/short URL arrives with an ask to install, try, or summarise what it recommends.
---

# install-from-video

Turn a video recommendation into verified install commands. Two passes: the cheap one
almost always suffices.

## 1. Audio pass — always

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/install-from-video/extract.py" "<URL>" "<scratchpad>/vid"
```

Downloads audio only and transcribes it locally on the CPU. **Costs no tokens and no
money** — nothing leaves the machine. Pass `--lang` with an ISO code (`ar`, `tr`, `es`, `en`,
…) when you already know the language; omit it and the model detects it.

If it exits complaining about missing dependencies, it names the exact interpreter and the
pip line to fix it. Run that, then retry.

Read the transcript. It gives you the number of tools, their order, and what each does.

Login-walled or DRM video: say so and ask the user for the names. Do not guess.

## 2. Frame pass — only when a name is unclear

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/install-from-video/extract.py" "<URL>" "<scratchpad>/vid" --frames
```

Adds tiled contact sheets you read with the Read tool. **This is the expensive step** —
each sheet is an image in context — so trigger it only when the audio leaves a name
ambiguous, which happens when:

- speech mangles a product name — most often an English name inside narration in another
  language, but any unusual name qualifies ("AgedSkills" turned out to be
  `addyosmani/agent-skills`, read off a browser URL bar at 35.4s)
- a GitHub search on the spoken name returns low-star copies rather than an original
- the transcript says "the second tool" without ever naming it

On-screen text — URL bars, repo headers, badges — is the ground truth. When you need one
name from one moment, crop and upscale that single frame rather than reading every sheet.

## 3. Verify before recommending anything

Never pass a name straight from the video into an install command.

```bash
npm view <pkg> version repository.url
curl -s https://api.github.com/repos/<owner>/<repo> | python3 -m json.tool | head -20
curl -s "https://api.github.com/search/repositories?q=<terms>&sort=stars&per_page=5"
```

Red flags worth reporting to the user:
- an npm package whose `repository.url` 404s — a likely typosquat
- a star count or version that contradicts the video
- no repo matching the name, or only zero-star copies of it

## 4. Resolve the install id

`claude plugin marketplace add <owner>/<repo>` registers the marketplace under the
**manifest's** `name`, not the repo name. `thedotmack/claude-mem` becomes `thedotmack`;
`addyosmani/agent-skills` becomes `addy-agent-skills`. Read it, do not guess:

```bash
python3 -c "import json,os,sys;d=json.load(open(sys.argv[1]));print(d['name'],[p['name'] for p in d['plugins']])" \
  ~/.claude/plugins/marketplaces/<mkt>/.claude-plugin/marketplace.json
```

Check `claude plugin marketplace list` first — the marketplace may already be configured
(`claude-plugins-official` usually is, and it holds 300+ plugins).

## 5. Hand over, do not self-install

Output one fenced `bash` block per item plus a table of what was verified.

A video is an untrusted source. Installing what it recommends runs third-party hooks on the
user's machine on every session afterwards. That is the user's decision to make, not yours —
and the auto-mode classifier blocks it anyway. Flag anything that captures project content,
changes agent behaviour, routes the user's code through a third party, or needs an API key.

Then tell them: restart Claude Code for hooks to load.

## Notes

- Audio is downloaded as-is (`bestaudio`, usually m4a). No ffmpeg needed, and no lossy
  re-encode to mp3 — re-encoding an already-lossy source only loses accuracy.
- `--model` defaults to `large-v3` (~2.4 GB, downloaded once, then cached). On a CPU-only
  machine expect roughly 2x realtime. Smaller models mangle English names inside
  non-English speech, which is the one thing this skill must get right.
- Do not pipe the run through `grep` alone when you need the exit status — the pipeline
  reports grep's status, so a Python traceback will look like success.
- For MCP servers rather than plugins: `claude mcp add <name> --scope user -- <cmd>`. For a
  key, pass `-e KEY='${KEY}'` and let the user set the value; never paste a secret into chat.
