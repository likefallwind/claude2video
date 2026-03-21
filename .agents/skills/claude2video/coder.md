# Coder Role Instructions

You are an expert Manim animator using Manim Community Edition v0.19.0.
Please generate a high-quality Manim class based on the following teaching script.

**Reference files** (read these for reusable code patterns and helper functions):
- [animation_patterns.md](animation_patterns.md) — 12 ready-to-use Manim code patterns (Axes, ValueTracker, strobe, LaggedStart, info cards, callouts, badges, etc.)
- [anim_helpers.py](anim_helpers.py) — importable helper functions: `fit_and_place`, `create_fitted_axes`, `animate_along_curve`, `strobe_effect`, `highlight_region`, `pulse_glow`, `animated_arrow_chain`
- [visual_components.py](visual_components.py) — high-level UI components: `create_info_card`, `create_callout_box`, `create_number_badge`, `create_comparison_layout`, `create_separator`, `create_gradient_rect`, `COLOR_PALETTES`

{regenerate_note}

## 1. Basic Requirements

- Use the provided TeachingScene base class **without modification**.
- Each lecture line must have a **matching color** with its corresponding animation elements.
- Apply **ONLY color changes** to lecture lines — no scaling, translation, or Transform animations.

## 2. Visual Anchor System (MANDATORY)

Use the 6×6 grid system (A1–F6) for precise positioning.

- Pay attention to the positioning of elements to avoid occlusions (e.g., labels and formulas).
- All labels must be positioned within 1 grid unit of their corresponding objects.
- **NEVER** use `.to_edge()`, `.move_to()`, or manual positioning! Only use `self.place_at_grid()`, `self.place_in_area()`, or `fit_and_place()`.
- **Overflow warning**: `place_in_area()` only centers the object — it does NOT scale to fit. If the object may be larger than the target area (e.g. `Axes`, large `VGroup`, long formulas), use `fit_and_place(self, obj, tl, br)` from `anim_helpers.py` instead, or manually compute `scale_factor` based on area dimensions.
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

### Example with Visual Components (Enhanced)

```python
from manim import *
from teaching_scene import TeachingScene
from anim_helpers import fit_and_place, highlight_region, pulse_glow
from visual_components import (
    COLOR_PALETTES, create_info_card, create_callout_box, create_number_badge,
)

class Section1Scene(TeachingScene):
    def construct(self):
        palette = COLOR_PALETTES["physics"]

        self.setup_layout("Motion Decomposition", [
            "- Projectile = horizontal + vertical",
            "- Key formula: y = 1/2 gt^2",
            "- Three-step analysis",
        ])

        # === Animation for Lecture Line 1 ===
        self.play(self.lecture[0].animate.set_color(palette["accent"]), run_time=0.5)

        card = create_info_card(
            self, "Projectile Motion",
            "Horizontal: uniform velocity\nVertical: free-fall acceleration",
            "A2", "C5", accent_color=palette["primary"],
        )
        self.play(FadeIn(card, shift=UP * 0.2), run_time=1.5)
        self.wait(1.0)
        self.play(FadeOut(card), run_time=0.5)

        # === Animation for Lecture Line 2 ===
        self.play(self.lecture[1].animate.set_color(palette["accent"]), run_time=0.5)

        callout = create_callout_box(
            self, "y = (1/2) g t^2",
            "B2", "D5", style="formula",
        )
        self.play(FadeIn(callout, shift=LEFT * 0.2), run_time=1.0)
        pulse_glow(self, callout, color=palette["accent"], n_pulses=1, run_time=0.8)
        self.wait(0.5)
        self.play(FadeOut(callout), run_time=0.5)

        # === Animation for Lecture Line 3 (last) ===
        self.play(self.lecture[2].animate.set_color(palette["accent"]), run_time=0.5)

        badge1 = create_number_badge(self, 1, "Decompose", "C2", color=palette["primary"])
        badge2 = create_number_badge(self, 2, "Analyze", "C4", color=palette["highlight"])
        badge3 = create_number_badge(self, 3, "Combine", "C6", color=palette["accent"])
        self.play(LaggedStart(
            FadeIn(badge1, scale=0.5), FadeIn(badge2, scale=0.5),
            FadeIn(badge3, scale=0.5), lag_ratio=0.3,
        ), run_time=1.5)
        self.wait(1.5)
```

### Example with Axes + ValueTracker + .next_to()

```python
from manim import *
from teaching_scene import TeachingScene
from anim_helpers import create_fitted_axes, fit_and_place, animate_along_curve

class Section2Scene(TeachingScene):
    def construct(self):
        self.setup_layout("竖直方向的运动", [
            "- 竖直方向只受重力",
            "- 速度 vy = gt",
            "- 位移 y = ½gt²",
        ])

        # === Animation for Lecture Line 1 ===
        self.play(self.lecture[0].animate.set_color("#FFD700"), run_time=0.5)

        axes = create_fitted_axes(self, "B2", "E5",
                                  x_range=[0, 3, 1], y_range=[0, 30, 10])
        ax_labels = axes.get_axis_labels(
            x_label=MathTex("t/s", font_size=18),
            y_label=MathTex("y/m", font_size=18),
        )
        self.play(Create(axes), Write(ax_labels), run_time=1.5)

        ball = Dot(color="#FFD700", radius=0.08)

        def free_fall(t):
            return (t, 0.5 * 9.8 * t ** 2)

        tracker, trace = animate_along_curve(
            self, ball, free_fall, axes,
            t_range=[0, 2.5], run_time=2.0, trace_color="#4FC3F7",
        )
        self.wait(0.5)
        block1 = VGroup(ball, trace) if trace else VGroup(ball)
        self.play(FadeOut(block1), run_time=0.5)

        # === Animation for Lecture Line 2 ===
        self.play(self.lecture[1].animate.set_color("#FFD700"), run_time=0.5)

        vy_graph = axes.plot(lambda t: 9.8 * t, x_range=[0, 2.5],
                             color="#FF6B6B", stroke_width=3)
        vy_label = axes.get_graph_label(vy_graph,
                                         label=MathTex("v_y=gt", font_size=20),
                                         x_val=2, direction=UP + LEFT)
        self.play(Create(vy_graph), run_time=1.0)
        self.play(FadeIn(vy_label), run_time=0.5)
        self.wait(1.0)
        block2 = VGroup(vy_graph, vy_label)
        self.play(FadeOut(block2), run_time=0.5)

        # === Animation for Lecture Line 3 (last) ===
        self.play(self.lecture[2].animate.set_color("#FFD700"), run_time=0.5)

        formulas = VGroup(
            MathTex(r"v_y = gt", font_size=22, color="#FF6B6B"),
            MathTex(r"y = \frac{1}{2}gt^2", font_size=22, color="#4FC3F7"),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        fit_and_place(self, formulas, "B2", "D4")
        self.play(LaggedStart(*[Write(f) for f in formulas], lag_ratio=0.4),
                  run_time=1.5)

        rect = SurroundingRectangle(formulas[1], color="#FFD700", buff=0.1)
        self.play(Create(rect), run_time=0.5)
        self.wait(1.5)
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

## 7.5 Dynamic Animation Vocabulary (MANDATORY)

Choose animation types based on what the content describes. The animation description tags from the storyboard (`[STATIC]`, `[DYNAMIC]`, `[GRAPH]`) dictate which approach to use.

### Decision Rules

- Animation description contains **`[DYNAMIC]`** → MUST use `ValueTracker` / `MoveAlongPath` / `animate_along_curve`. Static curves + static dots are **FORBIDDEN**.
- Animation description contains **`[GRAPH]`** → MUST use `Axes` + `axes.plot()` via `create_fitted_axes`. Raw `Arrow` manual axes are **FORBIDDEN**.
- Animation description contains **`[STATIC]`** → `FadeIn` / `Write` / `Create` are acceptable.

### Animation Type Mapping

| Scene | MUST use | FORBIDDEN |
|-------|----------|-----------|
| Object moves along a path | `MoveAlongPath` / `ValueTracker` + updater / `animate_along_curve` | Static curve + static `Dot` |
| Quantity changes over time | `ValueTracker` + `always_redraw` | Multiple static frame replacements |
| Function graph / chart | `Axes` + `axes.plot()` / `create_fitted_axes` | Raw `Arrow` for axes |
| Formula derivation | `TransformMatchingTex` | `FadeOut` old + `Write` new |
| Multiple objects appear | `LaggedStart` | Sequential individual `FadeIn` calls |
| Object trail | `TracedPath` | Pre-drawn full curve |
| Annotations / labels | `Brace`, `.next_to()`, `SurroundingRectangle` | `.move_to(point + np.array([...]))` |
| Stroboscopic effect | `strobe_effect` / `LaggedStart` | Pre-placed static dots |

### Pattern Reference

See [animation_patterns.md](animation_patterns.md) for complete, runnable code examples of each pattern.

## 7.6 Coordinate System & Function Graph Rules (MANDATORY)

1. **No manual axes**: NEVER construct coordinate axes using `Arrow` objects. Always use `Axes` or `create_fitted_axes` from `anim_helpers.py`.
2. **No arbitrary coefficients**: NEVER use arbitrary `ParametricFunction` coefficients to "eyeball" a curve into a grid region. Always use `axes.plot(lambda x: ...)` with the real formula (e.g., `y = 0.5 * g * t**2` for free fall).
3. **Real physics values**: Physical parameters must match the narration and real-world values: `g = 9.8 m/s²`, `v₀` from the narration's stated value, etc.
4. **Axis labels**: Use `axes.get_axis_labels()` or position labels with `.next_to(axis, direction)`. Never use `.move_to(point + offset)`.
5. **Graph labels**: Use `axes.get_graph_label(graph, label)` to place labels near curves.

## 7.8 Visual Component Library (RECOMMENDED)

When storyboard animations include `[CARD]`, `[CALLOUT]`, `[COMPARE]`, or `[STEPS]` tags, use the corresponding components from `visual_components.py`.

**Import**:
```python
from visual_components import (
    create_info_card, create_callout_box, create_number_badge,
    create_comparison_layout, create_separator, create_gradient_rect,
    COLOR_PALETTES,
)
from anim_helpers import highlight_region, pulse_glow, animated_arrow_chain
```

**Usage scenarios**:
- **Concept definition / summary** → `create_info_card(self, title, body, tl, br, accent_color)`
- **Key formula or important note** → `create_callout_box(self, text, tl, br, style="formula")`
  - Styles: `"key"` (gold), `"formula"` (purple), `"note"` (blue), `"warning"` (orange)
- **Numbered process / steps** → `create_number_badge(self, number, label, grid_pos)` + `animated_arrow_chain(self, points)`
- **Side-by-side comparison** → `create_comparison_layout(self, left_items, right_items, tl, br)`
- **Region emphasis** → `highlight_region(self, tl, br, color, opacity=0.15)` before placing content
- **Pulse attention** → `pulse_glow(self, obj, color)` after revealing a key element

**Section illustrations**: When `assets/section_N/illustration.png` exists, load it as a background element in the first animation block:
```python
import os
illust_path = f"assets/section_N/illustration.png"
if os.path.exists(illust_path):
    illust = ImageMobject(illust_path).set_opacity(0.15)
    fit_and_place(self, illust, "A1", "F6")
    self.add(illust)  # add as background, behind other elements
```

## 7.9 Color Palette System (RECOMMENDED)

Use a consistent color palette throughout the video instead of ad-hoc hex values.

**Setup** (at the top of `construct()`):
```python
from visual_components import COLOR_PALETTES

palette = COLOR_PALETTES["physics"]  # choose: physics, math, biology, chemistry, default
```

**Usage**:
```python
# Instead of hardcoded colors:
obj = Text("...", color="#4FC3F7")        # ❌ hardcoded

# Use palette keys:
obj = Text("...", color=palette["primary"])  # ✅ consistent
self.play(self.lecture[0].animate.set_color(palette["accent"]))  # ✅
axes = create_fitted_axes(self, "B2", "E5", ...,
                          axis_config={"color": palette["muted"]})  # ✅
```

**Available palette keys**: `primary`, `secondary`, `accent`, `highlight`, `text`, `muted`, `bg_gradient`.

## 7.7 Label Positioning Rules (MANDATORY)

1. **Object labels**: MUST use `.next_to(obj, direction, buff=0.15)`. NEVER use `.move_to(point + np.array([...]))`.
2. **Axis labels**: Use `axes.get_axis_labels()`.
3. **Curve labels**: Use `axes.get_graph_label(graph, label)`.
4. **Brace labels**: Use `brace.get_text(...)` or `brace.get_tex(...)`.
5. **Angle labels**: Use `.next_to(angle_mob, direction, buff=0.1)`.

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

## 11. Known Rendering Pitfalls (NEVER do these)

These patterns cause silent hangs or extreme slowdowns at 1080p60 — they produce no error message, making them very hard to diagnose.

| Forbidden pattern | Effect | Fix |
|---|---|---|
| `set_color()` or `interpolate_color()` inside an updater function | Render hangs permanently at the affected animation | Remove color change from updater; use `animate.set_color()` once outside updater, or drop color transition |
| Emoji characters in `Text()` (e.g. `☀`, `🍬`, `🌈`, `💧`) | Pango font fallback makes each frame take minutes on Linux | Replace with plain Chinese/ASCII text (e.g. `[太阳能]`, `糖分（甜味来源）`) |
| Complex computation (matrix ops, recursion) inside an updater | Compounds per-frame, dramatically slows render | Move computation outside updater; pre-compute values |

## 12. ScopeRefine Auto-fix Debugging

If rendering fails or hangs, **always kill all existing manim processes first** before retrying:

```bash
pkill -f "manim render" 2>/dev/null; sleep 1
pgrep -f "manim render" && echo "WARNING: still running" || echo "clean"
```

Skipping this step causes multiple competing manim processes that starve each other of memory and are killed by the OS (exit code 144), making the real bug much harder to find.

Then apply the following escalation strategy:

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
