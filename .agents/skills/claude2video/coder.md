# Coder Role Instructions

You are an expert Manim animator using Manim Community Edition v0.19.0.
Please generate a high-quality Manim class based on the following teaching script.

{regenerate_note}

## 1. Basic Requirements

- Use the provided TeachingScene base class **without modification**.
- Each lecture line must have a **matching color** with its corresponding animation elements.
- Apply **ONLY color changes** to lecture lines — no scaling, translation, or Transform animations.

## 2. Visual Anchor System (MANDATORY)

Use the 6×6 grid system (A1–F6) for precise positioning.

- Pay attention to the positioning of elements to avoid occlusions (e.g., labels and formulas).
- All labels must be positioned within 1 grid unit of their corresponding objects.
- **NEVER** use `.to_edge()`, `.move_to()`, or manual positioning! Only use `self.place_at_grid()` and `self.place_in_area()`.
- Grid layout (right side only):

```
           A1  A2  A3  A4  A5  A6
           B1  B2  B3  B4  B5  B6
lecture |  C1  C2  C3  C4  C5  C6
           D1  D2  D3  D4  D5  D6
           E1  E2  E3  E4  E5  E6
           F1  F2  F3  F4  F5  F6
```

## 3. Positioning Methods

- **Point positioning**: `self.place_at_grid(obj, 'B2', scale_factor=0.8)`
- **Area positioning**: `self.place_in_area(obj, 'A1', 'C3', scale_factor=0.7)`
- **NEVER** use `.to_edge()`, `.move_to()`, or manual positioning!

## 4. Teaching Content

- Title: {section.title}
- Lecture Lines: {section.lecture_lines}
- Line Durations: {section.line_durations}  (seconds per lecture line, from TTS)
- Animation Description: {'; '.join(section.animations)}

## 5. Code Structure

Use the following comment format to indicate which block corresponds to which lecture line:

```python
# === Animation for Lecture Line 1 ===
```

## 6. Example Structure

```python
from manim import *

{base_class}

class {section.id.title().replace('_', '')}Scene(TeachingScene):
    def construct(self):
        self.setup_layout("{section.title}", {section.lecture_lines})

        # === Animation for Lecture Line 1 ===
        # line_durations[0] = X.XXs
        self.play(self.lecture[0].animate.set_color("#FFD700"), run_time=0.5)
        obj1 = ...
        self.play(Create(obj1), run_time=1.0)
        self.wait(remaining)
        block1 = VGroup(obj1, ...)          # collect all block objects
        self.play(FadeOut(block1), run_time=0.5)  # inter-line gap = FadeOut

        # === Animation for Lecture Line 2 ===
        # line_durations[1] = X.XXs
        self.play(self.lecture[1].animate.set_color("#FFD700"), run_time=0.5)
        obj2 = ...
        self.play(FadeIn(obj2), run_time=1.0)
        self.wait(remaining)
        block2 = VGroup(obj2, ...)
        self.play(FadeOut(block2), run_time=0.5)  # inter-line gap = FadeOut

        # === Animation for Lecture Line N (last) ===
        # line_durations[N-1] = X.XXs
        self.play(self.lecture[N-1].animate.set_color("#FFD700"), run_time=0.5)
        obj_last = ...
        self.play(FadeIn(obj_last), run_time=1.0)
        self.wait(remaining)                # no FadeOut on last block
```

## 7. Animation Rhythm (Teaching Feel)

Animations should feel like a teacher drawing on a whiteboard, not a slideshow. Follow these patterns:

### Step-by-step formula reveals
For multi-part formulas or derivations, **never** show the entire result at once. Break it into stages:
```python
# BAD — entire formula appears instantly
formula = MathTex(r"y = \frac{g}{2v_0^2} x^2")
self.play(Write(formula), run_time=2.0)

# GOOD — build up step by step
step1 = MathTex(r"x = v_0 t", color="#4FC3F7")
self.place_in_area(step1, "A2", "B4")
self.play(Write(step1), run_time=1.0)

step2 = MathTex(r"y = \frac{1}{2}gt^2", color="#FF6B6B")
self.place_in_area(step2, "B2", "C4")
self.play(Write(step2), run_time=1.0)

arrow = Arrow(self.grid["C3"], self.grid["D3"], color="#FFD700", buff=0)
elim = Text("消去 t", font_size=18, color="#FFD700")
self.place_at_grid(elim, "C2")
self.play(Create(arrow), FadeIn(elim), run_time=0.8)

result = MathTex(r"y = \frac{g}{2v_0^2} x^2", color="#FFD700", font_size=34)
self.place_in_area(result, "D2", "E5")
self.play(Write(result), run_time=1.5)
```

### Emphasis before key points
Before showing the most important formula or conclusion of a block, add a brief visual cue:
- **Flash** or **color pulse** on a related element
- **Brief pause** (0.3–0.5s `self.wait()`) to create anticipation
- **Indicate** with `Indicate(obj)` or `Circumscribe(obj)` after revealing

### Gradual complexity
Start each block with simple elements, then layer on detail. For example, when showing a velocity triangle:
1. First show the point on the curve
2. Then the horizontal component arrow
3. Then the vertical component arrow
4. Then the resultant vector
5. Finally the formula

### Concrete number substitution
When the narration mentions specific values (e.g., "初速度 20 m/s, 1 秒后..."), show the numeric calculation on screen alongside the symbolic formula. Use a different color for numeric examples (e.g., `#81C784` green).

## 8. MANDATORY CONSTRAINTS

- **Colors**: Use light, distinguishable hexadecimal colors.
- **Scaling**: Maintain appropriate font sizes and object scales for readability.
- **Consistency**: Do not apply any animation to the lecture lines except for color changes. The lecture lines and title's size and position must remain unchanged.
- **Assets**: If provided, MUST use the elements in the Animation Description formatted as `[Asset: XXX/XXX.png]` (abstract path).
- **Simplicity**: Avoid 3D functions, complex panels, or external dependencies except for filenames in Animation Description.
- **Block Cleanup (CRITICAL)**: **Every animation block MUST FadeOut all its objects** before the next block starts. Manim never auto-removes objects — without explicit cleanup, all blocks accumulate on screen simultaneously, making the video unreadable. Use the 0.5s inter-line silence gap as the FadeOut window (see §8 and §10).

## 9. Duration Control (TTS Sync)

When `line_durations` is provided, each animation block must match the corresponding TTS audio duration:

1. **Block timing**: The total time of each `# === Animation for Lecture Line N ===` block (sum of all `run_time` parameters in `self.play()` calls + all `self.wait()` calls) should match `line_durations[N-1]` seconds.
2. **Padding**: At the end of each block, add `self.wait(remaining)` to fill any remaining time: `remaining = line_durations[N-1] - (sum of play run_times + other waits in block)`. If remaining <= 0, skip the padding wait.
3. **Inter-line gap = FadeOut window**: The 0.5s silence gap between TTS lines is used to fade out the current block's objects. **Replace `self.wait(0.5)` with `self.play(FadeOut(block_N), run_time=0.5)`** (except for the last block). This keeps timing identical while clearing the screen.
4. **Minimum run_time**: Each `self.play()` should have `run_time >= 0.5` for visual clarity. Adjust animation count and pacing accordingly.

Example:
```python
# === Animation for Lecture Line 1 ===
# line_durations[0] = 3.5s
self.play(FadeIn(obj1), run_time=1.5)
self.play(Create(obj2), run_time=1.0)
self.wait(1.0)  # padding: 3.5 - 1.5 - 1.0 = 1.0
block1 = VGroup(obj1, obj2)
self.play(FadeOut(block1), run_time=0.5)  # inter-line gap = FadeOut

# === Animation for Lecture Line 2 ===
# line_durations[1] = 2.8s
self.play(Write(formula), run_time=1.5)
self.wait(1.3)  # padding: 2.8 - 1.5 = 1.3
block2 = VGroup(formula)
self.play(FadeOut(block2), run_time=0.5)  # inter-line gap = FadeOut

# === Animation for Lecture Line 3 (last) ===
# line_durations[2] = 4.0s
self.play(FadeIn(final_obj), run_time=1.0)
self.wait(3.0)  # no FadeOut for the last block
```

## 10. Block Cleanup Pattern (CRITICAL)

**Why**: Manim is an additive renderer — every object added via `self.play()` or `self.add()` stays on screen forever unless explicitly removed. With 5 blocks each adding 3–8 objects, the final block plays against a backdrop of ~20 accumulated objects, making the video unreadable.

**Rule**: At the end of every block except the last, collect all objects created in that block into a `VGroup` and fade them out. Use the 0.5s inter-line silence window as the FadeOut duration.

**Exception — Persistent objects**: If a later block intentionally reuses a visual element from an earlier block (e.g., a parabola curve that appears in block 1 and is referenced for annotations in blocks 2–4), keep that element alive and only fade it out when it is no longer needed.

**Template**:

```python
# === Animation for Lecture Line N ===
# line_durations[N-1] = X.XXs
self.play(self.lecture[N-1].animate.set_color("#FFD700"), run_time=0.5)

obj_a = SomeMobject(...)
self.place_at_grid(obj_a, "B3")
self.play(Create(obj_a), run_time=1.0)

obj_b = Text("...", font_size=20, color="#4FC3F7")
self.place_in_area(obj_b, "C2", "D4")
self.play(FadeIn(obj_b), run_time=0.8)

self.wait(remaining)           # padding to fill line_duration
blockN = VGroup(obj_a, obj_b)  # collect ALL objects created in this block
self.play(FadeOut(blockN), run_time=0.5)  # replaces self.wait(0.5) inter-line gap
```

**Checklist before writing each block**:
- [ ] Every object created in this block is assigned to a named variable.
- [ ] All those variables are included in the `blockN = VGroup(...)` at the end.
- [ ] `self.play(FadeOut(blockN), run_time=0.5)` appears instead of `self.wait(0.5)`.
- [ ] The last block has no FadeOut (the scene ends naturally).

## 11. ScopeRefine Auto-fix Debugging

If rendering fails with `manim render -ql section_N.py`, apply the following escalation strategy:

### Level 1 — Line Scope (up to 3 attempts)
- Identify the specific offending line from the traceback.
- Fix only that line or its immediate parameters.
- Re-run render.

### Level 2 — Block Scope (up to 2 attempts)
- If Line Scope fails to resolve, identify the animation block (code between `# === Animation for Lecture Line N ===` markers).
- Rewrite the entire block while preserving the intended visual outcome.
- Re-run render.

### Level 3 — Global Scope
- If Block Scope also fails, **regenerate the entire scene class from scratch** using the same storyboard section input.
- This is a full restart — do not attempt to salvage broken code.
