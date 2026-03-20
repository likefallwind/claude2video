# claude2video

An AI agent skill for generating educational videos from a topic or Markdown outline. Built on [Manim Community Edition](https://www.manim.community/) with TTS narration via edge-tts.

Adapted from the [Code2Video](https://github.com/showlab/Code2Video) paradigm (arXiv:2510.01174) into a Claude Code skill format.

---

## Installation

**Step 1 — Install the skill into your project:**

```bash
npm install claude2video
```

This copies the skill files into `.agents/skills/claude2video/` in your project.

**Step 2 — Install Python and system dependencies:**

```bash
bash node_modules/claude2video/setup.sh
```

Supports Ubuntu/Debian (including WSL2), Fedora, and macOS.

**Step 3 — Use the skill in Claude Code:**

```
@claude2video 生成一个讲解「光合作用」的教学视频
```

---

## Overview

The skill takes a **learning topic string** or a **Markdown course outline file** as input and produces a fully narrated educational video (MP4) through an 8-stage pipeline:

```
Planner → TTS → Coder → Critic → Audio-Video Merge → Final Assembly
```

Each section of the course becomes a separate Manim animation scene. Narration audio is synthesized first, and animation timing is then paced to match the audio exactly.

---

## Prerequisites

| Dependency | Install |
|---|---|
| Python 3.9+ | — |
| Manim Community v0.19+ | `pip install manim` |
| edge-tts | `pip install edge-tts` |
| ffmpeg | system package |

---

## Repository Structure

```
.
├── .agents/skills/claude2video/   # The skill (copied to user project on npm install)
│   ├── SKILL.md                   # Entry point — 8-stage pipeline execution guide
│   ├── planner.md                 # P_parse / P_outline / P_storyboard / P_asset prompts
│   ├── coder.md                   # P_coder + Duration Control + ScopeRefine prompts
│   ├── critic.md                  # P_refine (layout) + P_aesth (scoring) prompts
│   ├── tts.py                     # CLI: storyboard.json → audio/ + durations.json
│   ├── teaching_scene.py          # TeachingScene base class (6×6 grid system)
│   └── example_section.py         # Working example — manim render -ql example_section.py
├── examples/
│   └── biology_cells.md           # Sample Markdown course outline (7th grade biology)
├── scripts/
│   └── install.js                 # npm postinstall — copies skill to .agents/skills/
├── package.json
├── requirements.txt               # Python dependencies
├── setup.sh                       # System dependency installer
├── CLAUDE.md                      # Project instructions for Claude Code
├── .gitignore
└── README.md
```

Output is written to `output/{topic}/` (gitignored):

```
output/{topic}/
├── outline.json                 # Stage 1 output
├── storyboard.json              # Stage 2 output (includes narrations)
├── teaching_scene.py            # Copied from skill dir
├── sections/
│   ├── section_1.py             # Generated Manim scene
│   └── ...
├── audio/
│   ├── section_1/
│   │   ├── line_1.mp3           # Per-line TTS audio
│   │   └── section_1.mp3        # Merged section audio (with 0.5s gaps)
│   └── durations.json           # Per-line durations for animation sync
├── sections_with_audio/
│   ├── section_1.mp4            # Video + audio merged
│   └── ...
├── media/                       # Manim render output
└── final_video.mp4              # Final output
```

---

## Usage

Invoke the skill from Claude Code:

```
/claude2video
```

Or reference it directly in a prompt:

> 请用 claude2video skill 生成一个讲解「勾股定理」的教学视频

The skill will ask whether to generate sections in **parallel** (faster) or **sequential** (step-by-step review) before starting.

### Input options

**Option A — Topic string:**
> 生成一个讲解「自由落体」的教学视频

**Option B — Markdown outline file:**
> 用这个大纲文件生成视频：`my_course.md`

The Markdown outline format:
```markdown
# 课程标题
目标受众：高中生

## 第一节：概念介绍
内容...

## 第二节：公式推导
内容...
```

Section count in the outline is preserved exactly.

---

## Pipeline Stages

| Stage | Role | Description |
|---|---|---|
| 1 | Planner | Parse Markdown outline or generate outline from topic |
| 2 | Planner | Build storyboard (lecture_lines + narrations + animations) |
| 3 | Planner | Select & download reference image assets |
| 4 | TTS | Synthesize narration audio, output durations.json |
| 5 | Coder | Generate + render Manim section code (parallel or sequential) |
| 6 | Critic | Visual layout refinement via frame extraction (up to 3 rounds) |
| 7 | — | Merge section video + audio via ffmpeg |
| 8 | Critic | Optional aesthetic scoring + final concatenation |

---

## Core Design

### 6×6 Visual Anchor Grid

All animations are placed using a named grid (`A1`–`F6`). The left column is reserved for lecture notes; the right area is the animation canvas.

```
           A1  A2  A3  A4  A5  A6
           B1  B2  B3  B4  B5  B6
lecture |  C1  C2  C3  C4  C5  C6
           D1  D2  D3  D4  D5  D6
           E1  E2  E3  E4  E5  E6
           F1  F2  F3  F4  F5  F6
```

Two positioning methods (no manual coordinates):
- `self.place_at_grid(obj, 'B2')` — snap to grid point
- `self.place_in_area(obj, 'A1', 'C3')` — fit within grid region

### Audio-First TTS Sync

TTS durations are generated **before** code generation. The Coder receives `line_durations` and pads each animation block with `self.wait()` so video duration matches audio exactly.

### ScopeRefine Debugging

Render failures are resolved through escalating scope:
1. **Line scope** — fix the offending line (≤3 attempts)
2. **Block scope** — rewrite the animation block (≤2 attempts)
3. **Global scope** — regenerate the entire scene from scratch

---

## References

- Paper: [Code2Video: Automated Educational Video Generation Leveraging AI Coding Agents](https://arxiv.org/abs/2510.01174)
- Reference implementation: https://github.com/showlab/Code2Video
