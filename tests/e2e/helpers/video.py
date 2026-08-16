"""Title/result cards rendered outside the recording and joined with ffmpeg.

Playwright records WebM natively. After the run we prepend/append the cards and
emit a lighter, shareable MP4 (H.264). The raw WebM is discarded on success.
"""

from __future__ import annotations

import html
import shutil
import subprocess
from fractions import Fraction
from pathlib import Path

CARD_VIEWPORT = {"width": 1280, "height": 720}
INTRO_SECONDS = 1.5
RESULT_SECONDS = 1.0

INTRO_FILE = ".intro.png"
RESULT_FILE = ".resultado.png"
# Playwright always writes WebM; final artifact delivered to the team is MP4.
RAW_VIDEO_FILE = "video.webm"
OUTPUT_VIDEO_FILE = "video.mp4"


def card_html(scenario_id: str, heading: str, detail: str, background: str) -> str:
    return f"""<!doctype html>
<html lang="pt">
  <head>
    <meta charset="utf-8">
    <title>{html.escape(scenario_id)}</title>
    <style>
      *, *::before, *::after {{ box-sizing: border-box; }}
      html, body {{
        width: 100%;
        height: 100%;
        margin: 0;
        overflow: hidden;
        background: {background};
      }}
      body {{
        display: flex;
        align-items: center;
        justify-content: center;
        color: #ffffff;
        font-family: Arial, Helvetica, sans-serif;
        text-align: center;
        padding: 3rem;
      }}
      .id {{
        opacity: .8;
        letter-spacing: .14em;
        text-transform: uppercase;
        font-size: 1.1rem;
        margin: 0 0 1.25rem;
      }}
      h1 {{
        font-size: 3rem;
        line-height: 1.2;
        max-width: 52rem;
        margin: 0;
      }}
      .detail {{
        font-size: 1.35rem;
        line-height: 1.5;
        max-width: 48rem;
        margin: 1.25rem auto 0;
        opacity: .9;
      }}
    </style>
  </head>
  <body>
    <main>
      <p class="id">{html.escape(scenario_id)}</p>
      <h1>{html.escape(heading)}</h1>
      <p class="detail">{html.escape(detail)}</p>
    </main>
  </body>
</html>"""


def render_card(browser, path: Path, scenario_id: str, heading: str, detail: str, background: str) -> None:
    """Screenshot a card in a throwaway context (never recorded)."""
    context = browser.new_context(viewport=CARD_VIEWPORT)
    try:
        page = context.new_page()
        page.set_content(card_html(scenario_id, heading, detail, background))
        page.wait_for_selector("h1", state="visible")
        path.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(path), type="png")
    finally:
        context.close()


def _ffmpeg() -> str | None:
    return shutil.which("ffmpeg")


def _even(value: int) -> int:
    """H.264 yuv420p requires even frame dimensions."""
    return value if value % 2 == 0 else value + 1


def _video_geometry(video: Path) -> tuple[int, int, int] | None:
    ffprobe = shutil.which("ffprobe")
    if ffprobe is None:
        return None
    result = subprocess.run(
        [
            ffprobe,
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,r_frame_rate",
            "-of", "csv=p=0",
            str(video),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    width, height, rate = result.stdout.strip().split(",")[:3]
    fps = Fraction(rate) if "/" in rate else Fraction(float(rate))
    return _even(int(width)), _even(int(height)), max(1, round(float(fps)))


def attach_cards(scenario_dir: Path) -> bool:
    """
    Build video.mp4 as: intro card + Playwright WebM + result card.

    On success the raw video.webm is removed so only the shareable MP4 remains.
    """
    raw_video = scenario_dir / RAW_VIDEO_FILE
    output_video = scenario_dir / OUTPUT_VIDEO_FILE
    intro = scenario_dir / INTRO_FILE
    result_card = scenario_dir / RESULT_FILE
    ffmpeg = _ffmpeg()

    if ffmpeg is None or not raw_video.exists() or not intro.exists():
        return False

    geometry = _video_geometry(raw_video)
    if geometry is None:
        return False
    width, height, fps = geometry

    inputs = [
        "-loop", "1", "-t", str(INTRO_SECONDS), "-i", str(intro),
        "-i", str(raw_video),
    ]
    parts = 2
    if result_card.exists():
        inputs += ["-loop", "1", "-t", str(RESULT_SECONDS), "-i", str(result_card)]
        parts = 3

    chains = "".join(
        f"[{index}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps},format=yuv420p[v{index}];"
        for index in range(parts)
    )
    streams = "".join(f"[v{index}]" for index in range(parts))
    filter_complex = f"{chains}{streams}concat=n={parts}:v=1:a=0[out]"

    composed = scenario_dir / ".video-composed.mp4"
    completed = subprocess.run(
        [
            ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
            *inputs,
            "-filter_complex", filter_complex,
            "-map", "[out]",
            "-an",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "28",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            str(composed),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    if completed.returncode != 0 or not composed.exists():
        composed.unlink(missing_ok=True)
        return False

    composed.replace(output_video)
    raw_video.unlink(missing_ok=True)
    intro.unlink(missing_ok=True)
    result_card.unlink(missing_ok=True)
    return True
