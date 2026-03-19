# CLAUDE.md

This repository implements **code2video**, a code-centric agent skill framework for generating educational videos via executable Manim code. It adapts the "Code2Video" paradigm (arXiv:2510.01174) into an AI Agent skill format.

Reference implementation: https://github.com/showlab/Code2Video
Reference paper: code2video-arxiv.pdf

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
- **`example_section.py`** — A complete working example demonstrating correct TeachingScene usage (grid positioning, lecture line color changes, comment structure). Run with `manim render -ql example_section.py`.

## Usage

This project contains an AI agent skill located in `.agents/skills/code2video/`. An AI agent can invoke this skill to execute the end-to-end video generation pipeline. See `SKILL.md` for the complete 6-stage execution workflow.
