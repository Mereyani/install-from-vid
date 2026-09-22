#!/usr/bin/env python3
"""Local transcription of a video's audio. Frames are a separate, opt-in pass.

  extract.py <URL> <outdir>            audio + transcript (local, zero token cost)
  extract.py <URL> <outdir> --frames   also fetch the video and tile its frames

Everything runs on your machine. Nothing is uploaded anywhere.
"""
import argparse
import glob
import subprocess
import sys
from pathlib import Path

REQUIRED = {
    "yt_dlp": "yt-dlp",
    "faster_whisper": "faster-whisper",
    "av": "av",
    "PIL": "pillow",
}


def check_deps(need_frames):
    """Fail with an actionable message instead of a bare ImportError."""
    import importlib.util
    wanted = REQUIRED if need_frames else {k: v for k, v in REQUIRED.items()
                                           if k in ("yt_dlp", "faster_whisper")}
    missing = [pkg for mod, pkg in wanted.items()
               if importlib.util.find_spec(mod) is None]
    if missing:
        sys.exit(
            f"Missing dependencies: {', '.join(missing)}\n"
            f"Install them into THIS interpreter:\n"
            f"  {sys.executable} -m pip install {' '.join(missing)}"
        )


def download(url, out, kind):
    """kind='audio' grabs bestaudio as-is — no re-encode, so no ffmpeg needed."""
    fmt = "bestaudio/best" if kind == "audio" else "best[ext=mp4]/best"
    name = "audio" if kind == "audio" else "video"
    # Call yt-dlp as a module so it always matches the running interpreter,
    # rather than whatever `yt-dlp` happens to be on PATH (or is not).
    subprocess.run([sys.executable, "-m", "yt_dlp", "--no-warnings", "-f", fmt,
                    "-o", str(out / f"{name}.%(ext)s"), url], check=True)
    found = sorted(out.glob(f"{name}.*"))
    if not found:
        sys.exit(f"yt-dlp produced no {name} file — the post may be private or region-locked.")
    return found[0]


def transcribe(path, out, model, lang):
    from faster_whisper import WhisperModel
    m = WhisperModel(model, device="cpu", compute_type="int8")
    segs, info = m.transcribe(
        str(path), language=lang, vad_filter=True, beam_size=5,
        condition_on_previous_text=False,   # stops hallucination loops
    )
    lines = [f"[{s.start:6.1f}] {s.text.strip()}" for s in segs]
    dest = out / "transcript.txt"
    dest.write_text(f"# model={model} lang={info.language} "
                    f"dur={info.duration:.1f}s\n" + "\n".join(lines))
    return dest, info.duration


def sheets(video, out):
    """Tile ~40 frames into 4x2 contact sheets, each stamped with its timestamp.

    One sheet costs a fraction of the context that 8 separate images would.
    The timestamp lets you go back and crop a single frame when you need to
    read something small, like a URL bar.
    """
    import av
    from PIL import Image, ImageDraw
    c = av.open(str(video))
    vs = c.streams.video[0]
    dur = float(c.duration / av.time_base) if c.duration else 0
    step = max(1.0, dur / 40)
    shots, next_t = [], 0.0
    for f in c.decode(video=0):
        t = float(f.pts * vs.time_base)
        if t >= next_t:
            im = f.to_image()
            im.thumbnail((400, 711))
            shots.append((t, im))
            next_t += step

    COLS, ROWS, W, H = 4, 2, 400, 711
    for i in range(0, len(shots), COLS * ROWS):
        sheet = Image.new("RGB", (COLS * W, ROWS * H), "black")
        d = ImageDraw.Draw(sheet)
        for j, (t, im) in enumerate(shots[i:i + COLS * ROWS]):
            x, y = (j % COLS) * W, (j // COLS) * H
            sheet.paste(im.resize((W, H)), (x, y))
            d.rectangle([x, y, x + 70, y + 22], fill="red")
            d.text((x + 6, y + 6), f"{t:.1f}s", fill="white")
        sheet.save(out / f"sheet{i // (COLS * ROWS)}.jpg", quality=88)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("url")
    p.add_argument("outdir")
    p.add_argument("--model", default="large-v3",
                   help="faster-whisper model. large-v3 (default) is markedly better "
                        "on non-English audio and on English names inside it.")
    p.add_argument("--lang", default=None,
                   help="force a language code, e.g. ar, tr, en. Omit to auto-detect.")
    p.add_argument("--frames", action="store_true",
                   help="also download the video and tile frames (costs context to read)")
    a = p.parse_args()

    check_deps(a.frames)
    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)

    audio = download(a.url, out, "audio")
    print(f"audio: {audio.name} ({audio.stat().st_size / 1e6:.1f} MB)")

    dest, dur = transcribe(audio, out, a.model, a.lang)
    print(f"duration: {dur:.1f}s")
    print(f"transcript: {dest}")

    if a.frames:
        sheets(download(a.url, out, "video"), out)
        for s in sorted(glob.glob(str(out / "sheet*.jpg"))):
            print(f"sheet: {s}")
    else:
        print("frames: skipped (re-run with --frames if a name is unclear)")


if __name__ == "__main__":
    main()
