# Animation Patterns Reference

Reusable Manim code patterns for the Coder skill. Each pattern includes an applicable scenario, complete runnable code, and grid-positioning example. Import helpers from `anim_helpers.py`.

---

## Pattern 1: Axes Coordinate System

**When to use**: Any scene requiring a function graph, data plot, or coordinate system.

```python
from anim_helpers import create_fitted_axes, fit_and_place

# Create axes fitted to grid area B2–E5
axes = create_fitted_axes(self, "B2", "E5",
                          x_range=[0, 5, 1], y_range=[0, 10, 2])
labels = axes.get_axis_labels(x_label="t/s", y_label="v/(m/s)")
self.play(Create(axes), Write(labels), run_time=1.5)

# Plot a function with real physics formula
graph = axes.plot(lambda x: 9.8 * x, color="#FF6B6B")
graph_label = axes.get_graph_label(graph, label=MathTex("v=gt"), x_val=3,
                                    direction=UP + LEFT)
self.play(Create(graph), run_time=1.5)
self.play(FadeIn(graph_label), run_time=0.5)
```

---

## Pattern 2: Dynamic Trajectory (Projectile Motion)

**When to use**: An object must visibly move along a path (projectile, free fall, circular motion).

```python
from anim_helpers import create_fitted_axes, animate_along_curve

v0, g = 20, 9.8  # real physics values

axes = create_fitted_axes(self, "B2", "F6",
                          x_range=[0, 50, 10], y_range=[-30, 0, 5])
self.play(Create(axes), run_time=1.0)

ball = Dot(color="#FFD700", radius=0.08)

def projectile(t):
    return (v0 * t, -0.5 * g * t ** 2)

tracker, trace = animate_along_curve(
    self, ball, projectile, axes,
    t_range=[0, 2.5], run_time=3.0,
    trace_color="#4FC3F7"
)
```

---

## Pattern 3: Free-Fall Twin-Ball Experiment

**When to use**: Comparing two motions side-by-side (e.g., horizontal throw vs free fall).

```python
g = 9.8
tracker = ValueTracker(0)

ball_proj = Dot(color="#4FC3F7", radius=0.08)
ball_free = Dot(color="#FF6B6B", radius=0.08)

v0 = 15  # horizontal initial speed

def update_proj(m):
    t = tracker.get_value()
    m.move_to(axes.c2p(v0 * t, -0.5 * g * t ** 2))

def update_free(m):
    t = tracker.get_value()
    m.move_to(axes.c2p(0, -0.5 * g * t ** 2))

ball_proj.add_updater(update_proj)
ball_free.add_updater(update_free)
update_proj(ball_proj)
update_free(ball_free)

trace_proj = TracedPath(ball_proj.get_center, stroke_color="#4FC3F7")
trace_free = TracedPath(ball_free.get_center, stroke_color="#FF6B6B")
self.add(trace_proj, trace_free, ball_proj, ball_free)

self.play(tracker.animate.set_value(2.0), run_time=3.0, rate_func=linear)

ball_proj.remove_updater(update_proj)
ball_free.remove_updater(update_free)
```

---

## Pattern 4: Strobe Effect

**When to use**: Showing equal-time-interval positions (multi-exposure photo effect).

```python
from anim_helpers import create_fitted_axes, strobe_effect

axes = create_fitted_axes(self, "B2", "F5",
                          x_range=[0, 5, 1], y_range=[0, 50, 10])
self.play(Create(axes), run_time=1.0)

g = 9.8
dots = strobe_effect(
    self,
    path_func=lambda t: (0.5, 0.5 * g * t ** 2),  # free fall
    axes=axes, n=8, t_range=[0, 3],
    dot_color="#FFD700", stagger=0.2
)
# Notice: dots are spaced closer at top (slow) and farther at bottom (fast)
```

---

## Pattern 5: Dynamic Vector (changes with time)

**When to use**: A vector/arrow that grows or rotates over time (e.g., vy = gt increasing).

```python
tracker = ValueTracker(0)
g = 9.8

# Starting point on the curve
start_point = axes.c2p(2, 0)

def get_vy_arrow():
    t = tracker.get_value()
    vy = g * t
    tip = axes.c2p(2, -vy)
    arrow = Arrow(start_point, tip, color="#FF6B6B", buff=0,
                  stroke_width=3, max_tip_length_to_length_ratio=0.15)
    label = MathTex(f"v_y={vy:.1f}", font_size=20, color="#FF6B6B")
    label.next_to(arrow, RIGHT, buff=0.1)
    return VGroup(arrow, label)

dynamic_arrow = always_redraw(get_vy_arrow)
self.add(dynamic_arrow)

self.play(tracker.animate.set_value(2.0), run_time=3.0, rate_func=linear)
```

---

## Pattern 6: Formula Derivation with TransformMatchingTex

**When to use**: Showing how two equations combine or simplify into a result.

```python
eq1 = MathTex(r"x", r"=", r"v_0", r"t", color="#4FC3F7")
fit_and_place(self, eq1, "A2", "B4")
self.play(Write(eq1), run_time=1.0)

eq2 = MathTex(r"y", r"=", r"\frac{1}{2}", r"g", r"t^2", color="#FF6B6B")
fit_and_place(self, eq2, "B2", "C4")
self.play(Write(eq2), run_time=1.0)

# Eliminate t → combined formula
result = MathTex(r"y", r"=", r"\frac{g}{2v_0^2}", r"x^2", color="#FFD700")
fit_and_place(self, result, "D2", "E5")

# TransformMatchingTex morphs matching sub-expressions
self.play(TransformMatchingTex(VGroup(eq1, eq2), result), run_time=2.0)
```

---

## Pattern 7: Annotation Tools (Brace, SurroundingRectangle, DashedLine, Angle)

**When to use**: Highlighting, measuring, or annotating parts of a diagram.

```python
# Brace with label
brace = Brace(some_line, direction=DOWN, color="#81C784")
brace_label = brace.get_text("距离 = 20m", font_size=20)
self.play(GrowFromCenter(brace), FadeIn(brace_label), run_time=1.0)

# Surrounding rectangle to highlight
rect = SurroundingRectangle(formula, color="#FFD700", buff=0.1)
self.play(Create(rect), run_time=0.5)

# Dashed line for reference
dashed = DashedLine(self.grid["B2"], self.grid["E2"],
                     color=GREY, stroke_width=1)
self.play(Create(dashed), run_time=0.5)

# Angle mark
angle = Angle(line1, line2, radius=0.3, color="#FF8A65")
angle_label = MathTex(r"\theta", font_size=18, color="#FF8A65")
angle_label.next_to(angle, RIGHT, buff=0.1)
self.play(Create(angle), FadeIn(angle_label), run_time=0.5)
```

---

## Pattern 8: Staggered Appearance (LaggedStart + AnimationGroup)

**When to use**: Multiple objects should appear one after another with overlap (bullet points, diagram parts, table rows).

```python
items = VGroup(
    Text("步骤 1: 分解运动", font_size=20, color="#4FC3F7"),
    Text("步骤 2: 分析水平方向", font_size=20, color="#81C784"),
    Text("步骤 3: 分析竖直方向", font_size=20, color="#FF8A65"),
    Text("步骤 4: 合成运动", font_size=20, color="#FFD700"),
).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
fit_and_place(self, items, "B2", "E5")

# Each item fades in 0.4s after the previous one starts
self.play(LaggedStart(*[FadeIn(item, shift=RIGHT * 0.3) for item in items],
                       lag_ratio=0.3),
          run_time=2.5)
```
