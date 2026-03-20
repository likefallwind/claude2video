---
name: code2video
description: Code-centric framework for educational video generation via executable Manim Python code.
---

# Code2Video Skill

This skill implements the Code2Video pipeline: **Planner → TTS → Coder → Critic**. It takes either a **Markdown course outline file** or a **topic string**, and produces an educational Manim video with narrated audio.

## Prerequisites

- Python 3.9+
- Manim Community Edition v0.19.0+ (`pip install manim`)
- numpy
- ffmpeg (for frame extraction, audio processing, and final concatenation)
- edge-tts (`pip install edge-tts`) — for TTS narration synthesis

## Project File Organization

```
output/{topic}/
├── outline.json              # Phase 1 output
├── storyboard.json           # Phase 2 output
├── assets.txt                # Phase 3 output (asset keywords)
├── teaching_scene.py         # Base class (copied from skill directory)
├── sections/
│   ├── section_1.py          # Manim scene for section 1
│   ├── section_2.py          # Manim scene for section 2
│   └── ...
├── assets/
│   ├── {keyword}/
│   │   └── {keyword}.png     # Downloaded asset images
│   └── ...
├── audio/                    # TTS output
│   ├── section_1/
│   │   ├── line_1.mp3        # Per-line narration
│   │   ├── line_2.mp3
│   │   └── section_1.mp3     # Merged section audio
│   ├── section_2/
│   │   └── ...
│   └── durations.json        # Per-line durations for timing sync
├── sections_with_audio/      # Video+audio merged sections
│   ├── section_1.mp4
│   └── ...
└── media/                    # Manim render output
    └── videos/
        └── ...
```

## Execution Pipeline

### Stage 1: Outline

Two paths depending on input:

**Path A — Markdown outline provided** (follow [planner.md](planner.md) Phase 0, P_parse):

1. User provides a Markdown file path, e.g. `my_course.md`.
2. Read the file. Parse sections, topic, and target audience from the Markdown structure.
3. Map directly to `outline.json` — section count must match the Markdown exactly.
4. Save to `output/{topic}/outline.json`.

**Path B — Topic string only** (follow [planner.md](planner.md) Phase 1, P_outline):

1. Take the user's topic as `{knowledge_point}`.
2. If a reference image is available, provide it to guide the outline.
3. Generate the outline JSON with sections, titles, content, and examples.
4. Save to `output/{topic}/outline.json`.

### Stage 2: Storyboard Construction

Follow [planner.md](planner.md) Phase 2 (P_storyboard).

1. Take the outline JSON and reference image as input.
2. Generate the storyboard JSON with lecture_lines and animations per section.
3. Apply content structure rules:
   - **Key sections**: 5 lecture lines + 5 animations
   - **Other sections**: 3 lecture lines + 3 animations
4. Save to `output/{topic}/storyboard.json`.

### Stage 3: Asset Selection & Download

Follow [planner.md](planner.md) Phase 3 (P_asset).

1. Analyze the storyboard for essential visual elements needing real images.
2. Output asset keywords (one per line) to `output/{topic}/assets.txt`.
3. For each keyword, search and download a PNG image to `output/{topic}/assets/{keyword}/{keyword}.png`.
4. Only select concrete, real-world objects — never abstract concepts or geometric shapes.

### Stage 4: TTS Narration Synthesis

Generate narration audio from the storyboard's `narrations` field using [tts.py](tts.py).

1. Run the TTS tool:
   ```bash
   python .agents/skills/code2video/tts.py \
       output/{topic}/storyboard.json \
       output/{topic}/audio/
   ```
2. This produces:
   - `audio/section_N/line_M.mp3` — individual narration clips
   - `audio/section_N/section_N.mp3` — merged section audio (with 0.5s gaps between lines)
   - `audio/durations.json` — per-line durations for timing control
3. Verify `durations.json` contains reasonable durations (typically 1–8 seconds per line).

### Stage 5: Code Generation (per section)

Follow [coder.md](coder.md).

1. Copy `teaching_scene.py` from the skill directory to `output/{topic}/teaching_scene.py`.
2. Load `audio/durations.json` to get `line_durations` for each section.
3. **Ask the user** before generating:
   > "准备生成 {N} 个 section 的代码。请问您希望：
   > - **并发生成**（所有 section 同时生成，速度更快，约快 {N}×）
   > - **逐个生成**（顺序生成，每个 section 完成后可以即时查看结果）"

   Wait for the user's answer before proceeding.

4. **If parallel**: in a single message, write all `section_N.py` files concurrently using parallel Write tool calls — one per section.
   **If sequential**: write and render each section one at a time, reporting progress after each.
5. Each generated file must:
   - Each file: a Manim scene class inheriting from `TeachingScene`.
   - Use ONLY `self.place_at_grid()` and `self.place_in_area()` for positioning.
   - Follow the `# === Animation for Lecture Line N ===` comment structure.
   - Apply duration control rules (coder.md §8) using `line_durations` from durations.json.
   - Save to `output/{topic}/sections/section_N.py`.
6. **Render** (follow same parallel/sequential choice as generation):
   - **If parallel**: launch all render commands in one message via parallel Bash tool calls.
   - **If sequential**: render each section immediately after generating it.
   ```bash
   cd output/{topic} && manim render -ql sections/section_N.py
   ```
7. For any section that fails to render, apply **ScopeRefine** debugging (see coder.md §9):
   - Line scope (up to 3 attempts) → Block scope (up to 2 attempts) → Global scope (full regeneration).
   - Fix and re-render failed sections; successfully rendered sections are not re-touched.

### Stage 6: Critic Visual Refinement

Follow [critic.md](critic.md) Mode 1 (P_refine).

Since Claude Code cannot directly view video files, use frame extraction:

1. **Extract frames** from the rendered video:
   ```bash
   ffmpeg -i media/videos/section_N/480p15/SectionNScene.mp4 \
          -vf "select='not(mod(n\,15))'" -vsync vfr \
          output/{topic}/frames/section_N_frame_%03d.png
   ```
2. **Analyze the extracted PNG frames** for layout issues (obstruction, overlap, off-screen, grid violations, lingering elements).
3. **Apply fixes** using grid coordinates, then re-render.
4. **Maximum 3 refinement rounds** per section. Stop early if `has_issues` is `false`.

### Stage 7: Audio-Video Merge

Merge each section's rendered video with its TTS audio:

1. Create the output directory:
   ```bash
   mkdir -p output/{topic}/sections_with_audio
   ```
2. For each section, merge video and audio:
   ```bash
   ffmpeg -i media/videos/section_N/480p15/SectionNScene.mp4 \
          -i audio/section_N/section_N.mp3 \
          -c:v copy -c:a aac -shortest \
          output/{topic}/sections_with_audio/section_N.mp4
   ```
3. Verify the merged files play correctly with synchronized audio.

### Stage 8: Final Assembly

1. Optionally run aesthetic evaluation (critic.md Mode 2, P_aesth) on the final sections.
2. Concatenate all section videos (with audio) into the final output:
   ```bash
   # Create file list
   for f in output/{topic}/sections_with_audio/section_*.mp4; do
     echo "file '$f'" >> output/{topic}/filelist.txt
   done
   # Concatenate
   ffmpeg -f concat -safe 0 -i output/{topic}/filelist.txt \
          -c copy output/{topic}/final_video.mp4
   ```

## Sub-skill Reference

| Stage | Role | Prompt File | Key Prompts |
|-------|------|-------------|-------------|
| 1 | Planner | [planner.md](planner.md) | P_outline |
| 2 | Planner | [planner.md](planner.md) | P_storyboard |
| 3 | Planner | [planner.md](planner.md) | P_asset |
| 4 | TTS | [tts.py](tts.py) | CLI tool |
| 5 | Coder | [coder.md](coder.md) | P_coder + P_vis + Duration Control + ScopeRefine |
| 6 | Critic | [critic.md](critic.md) | P_refine |
| 7 | — | — | ffmpeg audio-video merge |
| 8 | Critic | [critic.md](critic.md) | P_aesth (optional) + concat |

## Core Infrastructure

- **[teaching_scene.py](teaching_scene.py)** — TeachingScene base class with 6×6 grid system. **DO NOT MODIFY.** All section scenes must inherit from this class.
- **[example_section.py](example_section.py)** — Working example demonstrating correct usage of TeachingScene, grid positioning, lecture line color changes, and comment structure.
