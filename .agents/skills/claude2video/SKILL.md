---
name: claude2video
description: Code-centric framework for educational video generation via executable Manim Python code.
---

# Code2Video Skill

This skill implements the Code2Video pipeline: **Planner → TTS → Coder → Critic**. It takes either a **Markdown course outline file** or a **topic string**, and produces an educational Manim video with narrated audio.

## Prerequisites

Run the one-command installer from the repo root:

```bash
bash setup.sh          # installs system deps + Python packages + LaTeX
bash setup.sh --no-latex  # skip LaTeX (~800 MB) if you don't need math formulas
```

The script supports Ubuntu/Debian (including WSL2), Fedora, and macOS. Windows users without WSL should follow the [Manim Windows guide](https://docs.manim.community/en/stable/installation/windows.html) and then run `pip install -r requirements.txt`.

Full dependency list (see `requirements.txt`):
- Python 3.9+
- Manim Community Edition v0.19.0+
- numpy, edge-tts, google-genai, Pillow
- System: ffmpeg, Cairo, Pango, (optional) LaTeX
- Environment: `GOOGLE_API_KEY` (for AI image generation, optional — falls back to web search)

## Project File Organization

```
output/{topic}/
├── outline.json              # Phase 1 output
├── storyboard.json           # Phase 2 output
├── assets.txt                # Phase 3 output (asset keywords + descriptions)
├── teaching_scene.py         # Base class (copied from skill directory)
├── sections/
│   ├── section_1.py          # Manim scene for section 1
│   ├── section_2.py          # Manim scene for section 2
│   └── ...
├── assets/
│   ├── {keyword}/
│   │   └── {keyword}.png     # AI-generated or downloaded asset images
│   ├── section_N/
│   │   └── illustration.png  # AI-generated section illustration (optional)
│   ├── manifest.json          # Image generation manifest (prompts, model, paths)
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
2. Generate the storyboard JSON with lecture_lines, narrations, and animations per section.
3. Apply content structure rules:
   - **Key sections**: 5 lecture lines + 5 animations
   - **Other sections**: 3 lecture lines + 3 animations
4. **Narration quality check** (CRITICAL): Before saving, verify each narration against planner.md's "Narration Style" rules:
   - Is it conversational teacher-speech, NOT a rewording of the lecture line?
   - Does it include the 4-part structure: Hook → Explain why → Concrete numbers → Bridge?
   - Does the first narration of each section (except section 1) bridge from the previous section?
   - Is each narration **≥ 60 Chinese characters**? (MANDATORY — shorter narrations must be rewritten)
   - Does each narration contain at least one causal sentence (因为…所以… / 这意味着…)?
   If any narration fails these checks, rewrite it before proceeding.
5. **Animation type tag check**: Verify every animation description starts with `[STATIC]`, `[DYNAMIC]`, or `[GRAPH]`. If a tag is missing, infer the correct one from the description and prepend it.
6. Save to `output/{topic}/storyboard.json`.
6. **User review** (MANDATORY): Present a summary of the storyboard to the user and **wait for approval before proceeding**. The summary should include:
   - Section count and titles
   - For each section: the lecture_lines list and the first narration (as a quality sample)
   - Ask: "请确认以上 storyboard 内容，如需修改请告知，确认后将继续 Stage 3。"
   - Do NOT proceed to Stage 3 until the user explicitly confirms (e.g., "确认", "好的", "继续", "ok").

### Stage 3a: Asset Selection

Follow [planner.md](planner.md) Phase 3 (P_asset).

1. Analyze the storyboard for essential visual elements needing real images.
2. Output asset keywords (in `keyword: description` format, one per line) to `output/{topic}/assets.txt`.
3. Include `section_illustrations: true/false` at the end of `assets.txt`.
4. Only select concrete, real-world objects — never abstract concepts or geometric shapes.

### Stage 3b: AI Image Generation

Generate asset images using [gen_images.py](gen_images.py) (requires `GOOGLE_API_KEY` environment variable).

1. Run the image generation tool:
   ```bash
   python .agents/skills/claude2video/gen_images.py \
       output/{topic}/storyboard.json \
       output/{topic}/assets.txt \
       output/{topic}/assets/ \
       --section-illustrations   # if assets.txt contains "section_illustrations: true"
   ```
2. This produces:
   - `assets/{keyword}/{keyword}.png` — AI-generated asset icons (512×512, 1:1)
   - `assets/section_N/illustration.png` — Section illustrations (16:9, if requested)
   - `assets/manifest.json` — Records prompts, model, and paths for each generated image
3. Verify generated images exist and are reasonable. If `GOOGLE_API_KEY` is not set, fall back to web search download (Stage 3a legacy behavior).

### Stage 4: TTS Narration Synthesis

Generate narration audio from the storyboard's `narrations` field using [tts.py](tts.py).

1. Run the TTS tool:
   ```bash
   python .agents/skills/claude2video/tts.py \
       output/{topic}/storyboard.json \
       output/{topic}/audio/
   ```
2. This produces:
   - `audio/section_N/line_M.mp3` — individual narration clips
   - `audio/section_N/section_N.mp3` — merged section audio (with 0.5s gaps between lines)
   - `audio/durations.json` — per-line durations for timing control
3. Verify `durations.json` contains reasonable durations (typically 1–8 seconds per line).

### Stage 5: Code Generation (per section)

Follow [coder.md](coder.md). Read [animation_patterns.md](animation_patterns.md) for reusable code patterns before generating code.

1. Copy infrastructure files from the skill directory to `output/{topic}/`:
   ```bash
   cp .agents/skills/claude2video/teaching_scene.py output/{topic}/teaching_scene.py
   cp .agents/skills/claude2video/anim_helpers.py output/{topic}/anim_helpers.py
   cp .agents/skills/claude2video/visual_components.py output/{topic}/visual_components.py
   ```
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
   cd output/{topic} && manim render -qh sections/section_N.py
   ```
7. For any section that fails to render, apply **ScopeRefine** debugging (see coder.md §12):
   - **Before every retry**: kill all existing manim processes — `pkill -f "manim render" 2>/dev/null; sleep 1` — to avoid multiple competing processes that get OOM-killed (exit code 144).
   - Line scope (up to 3 attempts) → Block scope (up to 2 attempts) → Global scope (full regeneration).
   - Fix and re-render failed sections; successfully rendered sections are not re-touched.

### Stage 6: Critic Visual Refinement

Follow [critic.md](critic.md) Mode 1 (P_refine). This stage now checks both **layout** and **animation quality**.

Since Claude Code cannot directly view video files, use frame extraction and source code analysis:

1. **Extract frames** from the rendered video:
   ```bash
   ffmpeg -i media/videos/section_N/1080p60/SectionNScene.mp4 \
          -vf "select='not(mod(n\,15))'" -vsync vfr \
          output/{topic}/frames/section_N_frame_%03d.png
   ```
2. **Analyze the extracted PNG frames** for layout issues (obstruction, overlap, off-screen, grid violations, lingering elements).
3. **Read the section source code** and check animation quality (static-only blocks, missing dynamic animations, raw Arrow axes, manual label positioning, overflow risks). See critic.md §4b.
4. **Apply fixes** using grid coordinates and animation pattern improvements, then re-render.
5. **Maximum 3 refinement rounds** per section. Stop early if both `layout.has_issues` and `animation_quality.has_issues` are `false`.

### Stage 7: Audio-Video Merge

Merge each section's rendered video with its TTS audio:

1. Create the output directory:
   ```bash
   mkdir -p output/{topic}/sections_with_audio
   ```
2. For each section, merge video and audio:
   ```bash
   ffmpeg -i media/videos/section_N/1080p60/SectionNScene.mp4 \
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
| 3a | Planner | [planner.md](planner.md) | P_asset |
| 3b | Image Gen | [gen_images.py](gen_images.py) | CLI tool |
| 4 | TTS | [tts.py](tts.py) | CLI tool |
| 5 | Coder | [coder.md](coder.md) | P_coder + P_vis + Duration Control + ScopeRefine |
| 6 | Critic | [critic.md](critic.md) | P_refine |
| 7 | — | — | ffmpeg audio-video merge |
| 8 | Critic | [critic.md](critic.md) | P_aesth (optional) + concat |

## Core Infrastructure

- **[teaching_scene.py](teaching_scene.py)** — TeachingScene base class with 6×6 grid system. **DO NOT MODIFY.** All section scenes must inherit from this class.
- **[anim_helpers.py](anim_helpers.py)** — Animation helper utilities: `fit_and_place`, `create_fitted_axes`, `animate_along_curve`, `strobe_effect`, `highlight_region`, `pulse_glow`, `animated_arrow_chain`. Copied to output directory at Stage 5.
- **[visual_components.py](visual_components.py)** — High-level UI components (`create_info_card`, `create_callout_box`, `create_number_badge`, `create_comparison_layout`, `create_separator`, `create_gradient_rect`) and `COLOR_PALETTES` subject-based color system. Copied to output directory at Stage 5.
- **[gen_images.py](gen_images.py)** — AI image generation CLI tool using Google Gemini API. Generates asset icons and optional section illustrations from storyboard context. Run at Stage 3b.
- **[animation_patterns.md](animation_patterns.md)** — 12 reusable Manim code patterns (Axes, ValueTracker, strobe, LaggedStart, info cards, callouts, badges, comparison layouts, etc.) for the Coder to reference.
- **[example_section.py](example_section.py)** — Working examples demonstrating correct usage of TeachingScene, grid positioning, Axes, ValueTracker, LaggedStart, fit_and_place, and enhanced visual components (`EnhancedExampleScene`).
