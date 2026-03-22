# CLAUDE.md

This repository implements **claude2video**, a code-centric agent skill framework for generating educational videos via executable Manim code. It adapts the "Code2Video" paradigm (arXiv:2510.01174) into an AI Agent skill format.

Reference implementation: https://github.com/showlab/Code2Video
Reference paper: https://arxiv.org/abs/2510.01174

## Architecture (Skills Pipeline)

The project is structured as a tri-agent skill pipeline that takes a learning topic query and produces an educational video.

1. **Planner Skill** — Converts a learning topic into a structured storyboard with reference assets
   - Outline generation: decomposes topic into sections with titles, summaries, examples
   - Storyboard construction: adds lecture lines and animation descriptions per section
   - External database: retrieves reference images/assets

2. **Coder Skill** — Translates each storyboard section into executable Manim code
   - Generates Python animations adhering to a 6x6 visual anchor grid
   - Performs scope-guided auto-fix debugging

3. **Critic Skill** — Refines rendered video output for spatial coherence and clarity
   - Analyzes visual layout and anchor prompts
   - Identifies occlusions or layout imbalances and applies refinements

## Core Infrastructure

- **`teaching_scene.py`** — TeachingScene base class implementing the 6×6 Visual Anchor Grid positioning system. All generated section scenes inherit from this class. **Do not modify.**
- **`anim_helpers.py`** — Animation helper utilities (`fit_and_place`, `create_fitted_axes`, `animate_along_curve`, `strobe_effect`, `highlight_region`, `pulse_glow`, `animated_arrow_chain`) that ensure objects fit within grid areas and provide dynamic animation patterns. Copied alongside `teaching_scene.py` to the output directory at Stage 5.
- **`visual_components.py`** — High-level UI component library (`create_info_card`, `create_callout_box`, `create_number_badge`, `create_comparison_layout`, `create_separator`, `create_gradient_rect`) and subject-based `COLOR_PALETTES` system (physics, math, biology, chemistry, default). Copied to the output directory at Stage 5.
- **`gen_images.py`** — AI image generation CLI tool using Google Gemini API. Reads `assets.json` (containing Planner-generated prompts), generates images to `assets/` directory with `manifest.json`. Prompts are context-aware (background, style, composition tailored to each image's usage in the animation). Requires `GOOGLE_API_KEY` environment variable.
- **`animation_patterns.md`** — Reference library of 12 reusable Manim code patterns (Axes coordinate system, dynamic trajectory, strobe effect, formula derivation, annotations, staggered appearance, info cards, callout boxes, step badges, comparison layouts) for the Coder to consult during code generation.
- **`example_section.py`** — Complete working examples demonstrating correct TeachingScene usage: `ExampleScene` (Axes, ValueTracker, LaggedStart, fit_and_place) and `EnhancedExampleScene` (COLOR_PALETTES, info cards, callout boxes, number badges). Run with `manim render -ql example_section.py`.

## TTS Narration

The pipeline supports voice narration via `edge-tts` (strategy: audio-first, then video paced to match).

- **`tts.py`** — CLI tool that reads `storyboard.json`, synthesizes narration audio per section, and outputs `durations.json` with per-line timings.
- The Coder uses `line_durations` from `durations.json` to pace animations so video duration matches audio.
- After rendering, ffmpeg merges each section's video with its audio before final concatenation.
- Voice: `zh-CN-YunxiNeural` (configurable in `tts.py`).

## Usage

This project contains an AI agent skill located in `.agents/skills/claude2video/`. An AI agent can invoke this skill to execute the end-to-end video generation pipeline. See `SKILL.md` for the complete 8-stage execution workflow.
