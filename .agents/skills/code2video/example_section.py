"""
Example section scene demonstrating correct TeachingScene usage.

Run with: manim render -ql example_section.py ExampleScene
"""

from manim import *
from teaching_scene import TeachingScene


class ExampleScene(TeachingScene):
    def construct(self):
        # Setup layout with title and lecture lines
        self.setup_layout(
            "Pythagorean Theorem",
            [
                "- A right triangle has sides a, b, c",
                "- The hypotenuse is the longest side",
                "- The relationship: a² + b² = c²",
            ]
        )

        # === Animation for Lecture Line 1 ===
        # Highlight the current lecture line
        self.play(self.lecture[0].animate.set_color("#FFD700"))

        # Draw a right triangle using grid positioning
        triangle = Polygon(
            self.grid["C2"], self.grid["E2"], self.grid["E5"],
            color="#4FC3F7", stroke_width=2
        )
        self.play(Create(triangle))

        # Label the sides
        label_a = Text("a", font_size=20, color="#4FC3F7")
        self.place_at_grid(label_a, "D1", scale_factor=0.8)
        self.play(FadeIn(label_a))

        label_b = Text("b", font_size=20, color="#81C784")
        self.place_at_grid(label_b, "F4", scale_factor=0.8)
        self.play(FadeIn(label_b))

        label_c = Text("c", font_size=20, color="#FF8A65")
        self.place_at_grid(label_c, "C4", scale_factor=0.8)
        self.play(FadeIn(label_c))

        self.wait(1)

        # === Animation for Lecture Line 2 ===
        self.play(self.lecture[1].animate.set_color("#FFD700"))

        # Highlight the hypotenuse
        hypotenuse = Line(
            self.grid["C2"], self.grid["E5"],
            color="#FF8A65", stroke_width=4
        )
        self.play(Create(hypotenuse))
        self.play(label_c.animate.set_color("#FF8A65"))
        self.wait(1)

        # === Animation for Lecture Line 3 ===
        self.play(self.lecture[2].animate.set_color("#FFD700"))

        # Show the formula
        formula = MathTex("a^2 + b^2 = c^2", font_size=36, color="#FFFFFF")
        self.place_in_area(formula, "B2", "B5", scale_factor=1.0)
        self.play(Write(formula))

        # Draw squares on each side to visualize
        sq_a = Square(side_length=0.6, color="#4FC3F7", fill_opacity=0.3)
        self.place_at_grid(sq_a, "D1", scale_factor=0.8)
        sq_b = Square(side_length=0.8, color="#81C784", fill_opacity=0.3)
        self.place_at_grid(sq_b, "F4", scale_factor=0.8)
        sq_c = Square(side_length=1.0, color="#FF8A65", fill_opacity=0.3)
        self.place_at_grid(sq_c, "C5", scale_factor=0.8)

        self.play(FadeIn(sq_a), FadeIn(sq_b), FadeIn(sq_c))
        self.wait(2)
