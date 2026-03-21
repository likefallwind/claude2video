"""
Example section scene demonstrating correct TeachingScene usage.

Showcases: Axes coordinate system, ValueTracker dynamic animation,
.next_to() label positioning, LaggedStart staggered appearance,
and fit_and_place() safe scaling.

Run with: manim render -ql example_section.py ExampleScene
"""

from manim import *
from teaching_scene import TeachingScene
from anim_helpers import create_fitted_axes, fit_and_place, animate_along_curve


class ExampleScene(TeachingScene):
    def construct(self):
        # Setup layout with title and lecture lines
        self.setup_layout(
            "Projectile Motion",
            [
                "- Horizontal: uniform velocity",
                "- Vertical: free-fall acceleration",
                "- Trajectory is a parabola",
                "- Velocity components combine",
            ]
        )

        # === Animation for Lecture Line 1 ===
        self.play(self.lecture[0].animate.set_color("#FFD700"))

        # Create fitted axes in grid area B2–E5
        axes = create_fitted_axes(
            self, "B2", "E5",
            x_range=[0, 50, 10], y_range=[0, 30, 10],
            axis_config={"include_numbers": True, "font_size": 16},
        )
        ax_labels = axes.get_axis_labels(
            x_label=MathTex("x/m", font_size=18),
            y_label=MathTex("y/m", font_size=18),
        )
        self.play(Create(axes), Write(ax_labels), run_time=1.5)

        # Plot horizontal displacement: x = v0 * t  (shown as straight line on x-axis)
        h_line = axes.plot(lambda x: 0, x_range=[0, 40], color="#4FC3F7",
                           stroke_width=3)
        h_label = MathTex("x = v_0 t", font_size=20, color="#4FC3F7")
        h_label.next_to(h_line, UP, buff=0.15)
        self.play(Create(h_line), FadeIn(h_label), run_time=1.0)

        self.wait(0.5)
        block1 = VGroup(h_line, h_label)
        self.play(FadeOut(block1), run_time=0.5)

        # === Animation for Lecture Line 2 ===
        self.play(self.lecture[1].animate.set_color("#FFD700"))

        # Free-fall graph: y = 0.5 * g * t^2  plotted as y vs t conceptually
        g_val = 9.8
        fall_graph = axes.plot(lambda x: 0.5 * g_val * (x / 10) ** 2,
                               x_range=[0, 40], color="#FF6B6B",
                               stroke_width=3)
        fall_label = axes.get_graph_label(
            fall_graph,
            label=MathTex(r"y=\frac{1}{2}gt^2", font_size=20),
            x_val=30, direction=UP + LEFT,
        )
        # Animate the graph being drawn progressively
        self.play(Create(fall_graph), run_time=1.5)
        self.play(FadeIn(fall_label), run_time=0.5)

        self.wait(0.5)
        block2 = VGroup(fall_graph, fall_label)
        self.play(FadeOut(block2), run_time=0.5)

        # === Animation for Lecture Line 3 ===
        self.play(self.lecture[2].animate.set_color("#FFD700"))

        # Dynamic projectile: ball moves along parabolic path with traced trail
        v0 = 20
        parabola = axes.plot(
            lambda x: 0.5 * g_val * (x / v0) ** 2,
            x_range=[0, 40], color="#81C784", stroke_width=2,
        )
        self.play(Create(parabola), run_time=1.0)

        ball = Dot(color="#FFD700", radius=0.08)

        def proj_path(t):
            return (v0 * t, 0.5 * g_val * t ** 2)

        tracker, trace = animate_along_curve(
            self, ball, proj_path, axes,
            t_range=[0, 2.0], run_time=2.0, trace_color="#FFD700",
        )

        self.wait(0.5)
        block3_items = [parabola, ball]
        if trace is not None:
            block3_items.append(trace)
        block3 = VGroup(*block3_items)
        self.play(FadeOut(block3), run_time=0.5)

        # === Animation for Lecture Line 4 ===
        self.play(self.lecture[3].animate.set_color("#FFD700"))

        # Staggered appearance of velocity component labels
        items = VGroup(
            MathTex(r"v_x = v_0", font_size=22, color="#4FC3F7"),
            MathTex(r"v_y = g t", font_size=22, color="#FF6B6B"),
            MathTex(r"v = \sqrt{v_x^2 + v_y^2}", font_size=22, color="#FFD700"),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        fit_and_place(self, items, "B2", "E5")

        self.play(
            LaggedStart(
                *[FadeIn(item, shift=RIGHT * 0.3) for item in items],
                lag_ratio=0.35,
            ),
            run_time=2.0,
        )

        # Highlight the resultant formula
        rect = SurroundingRectangle(items[2], color="#FFD700", buff=0.1)
        self.play(Create(rect), run_time=0.5)

        self.wait(1)
        # Last block — no FadeOut needed
