#!/usr/bin/env python3
"""TTS tool for Code2Video pipeline.

Generates narration audio from storyboard.json using edge-tts,
produces per-line mp3 files, merged section audio, and a durations.json.
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

import edge_tts

VOICE = "zh-CN-YunxiNeural"
SILENCE_GAP = 0.5  # seconds of silence between lines


def get_duration(mp3_path: str) -> float:
    """Get audio duration in seconds using ffprobe."""
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "quiet",
            "-show_entries", "format=duration",
            "-of", "csv=p=0",
            mp3_path,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(result.stdout.strip())


async def synthesize_line(text: str, output_path: str) -> None:
    """Synthesize a single narration line to mp3."""
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(output_path)


def generate_silence(duration: float, output_path: str) -> None:
    """Generate a silent audio file of given duration."""
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"anullsrc=r=24000:cl=mono",
            "-t", str(duration),
            "-c:a", "libmp3lame",
            "-q:a", "9",
            output_path,
        ],
        capture_output=True,
        check=True,
    )


def concat_audio_files(file_list: list[str], output_path: str) -> None:
    """Concatenate audio files using ffmpeg concat demuxer."""
    list_path = Path(output_path).parent / "concat_list.txt"
    with open(list_path, "w") as f:
        for fpath in file_list:
            f.write(f"file '{Path(fpath).resolve()}'\n")
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(list_path),
            "-c:a", "libmp3lame",
            "-q:a", "2",
            output_path,
        ],
        capture_output=True,
        check=True,
    )
    list_path.unlink()


def main(storyboard_path: str, output_dir: str) -> None:
    """Generate TTS audio for all sections in the storyboard.

    Args:
        storyboard_path: Path to storyboard.json
        output_dir: Directory to write audio/ output
    """
    with open(storyboard_path, "r", encoding="utf-8") as f:
        storyboard = json.load(f)

    audio_dir = Path(output_dir)
    audio_dir.mkdir(parents=True, exist_ok=True)

    durations: dict = {}

    for section in storyboard["sections"]:
        section_id = section["id"]
        narrations = section.get("narrations", [])
        if not narrations:
            # Fallback: derive narrations from lecture_lines
            narrations = [
                line.lstrip("- ").strip() for line in section.get("lecture_lines", [])
            ]

        section_dir = audio_dir / section_id
        section_dir.mkdir(parents=True, exist_ok=True)

        line_durations = []
        line_files = []

        for i, text in enumerate(narrations, start=1):
            line_path = str(section_dir / f"line_{i}.mp3")
            print(f"  Synthesizing {section_id}/line_{i}: {text[:40]}...")
            asyncio.run(synthesize_line(text, line_path))

            dur = get_duration(line_path)
            line_durations.append(round(dur, 2))
            line_files.append(line_path)

        # Merge lines with silence gaps into section audio
        if line_files:
            silence_path = str(section_dir / "silence.mp3")
            generate_silence(SILENCE_GAP, silence_path)

            concat_parts = []
            for j, lf in enumerate(line_files):
                concat_parts.append(lf)
                if j < len(line_files) - 1:
                    concat_parts.append(silence_path)

            merged_path = str(section_dir / f"{section_id}.mp3")
            concat_audio_files(concat_parts, merged_path)

            # Clean up silence file
            Path(silence_path).unlink(missing_ok=True)

            total = round(sum(line_durations) + SILENCE_GAP * (len(line_files) - 1), 2)
        else:
            total = 0.0

        durations[section_id] = {
            "line_durations": line_durations,
            "total": total,
        }

    # Write durations.json
    durations_path = audio_dir / "durations.json"
    with open(durations_path, "w", encoding="utf-8") as f:
        json.dump(durations, f, indent=2, ensure_ascii=False)

    print(f"\nDurations saved to {durations_path}")
    print(json.dumps(durations, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <storyboard.json> <output_audio_dir>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
