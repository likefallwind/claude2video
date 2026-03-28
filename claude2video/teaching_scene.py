"""
TeachingScene — Base class for all Code2Video section scenes.

This class implements the 6x6 Visual Anchor Grid system from the Code2Video
framework. Every generated section scene MUST inherit from TeachingScene and
use its positioning methods. DO NOT MODIFY this file.
"""

from manim import *
import numpy as np


class TeachingScene(Scene):
    def setup_layout(self, title_text, lecture_lines):
        # BASE
        self.camera.background_color = "#000000"
        self.title = Text(title_text, font_size=28, color=WHITE).to_edge(UP)
        self.add(self.title)

        # Left-side lecture content — width-constrained to avoid overlap
        MAX_LECTURE_WIDTH = 5.0  # scene units; keeps text in the left ~35%
        lecture_texts = [Text(line, font_size=22, color=WHITE) for line in
                         lecture_lines]
        self.lecture = VGroup(*lecture_texts).arrange(DOWN, aligned_edge=LEFT).scale(
            0.8)
        # Shrink further if any line exceeds the maximum width
        if self.lecture.width > MAX_LECTURE_WIDTH:
            self.lecture.scale(MAX_LECTURE_WIDTH / self.lecture.width)
        self.lecture.to_edge(LEFT, buff=0.2)
        self.add(self.lecture)

        # Define fine-grained animation grid (6x6 grid on right side)
        # Grid starts at x=1.8 so it never overlaps with lecture text.
        self.grid = {}
        rows = ["A", "B", "C", "D", "E", "F"]  # Top to bottom
        cols = ["1", "2", "3", "4", "5", "6"]  # Left to right

        for i, row in enumerate(rows):
            for j, col in enumerate(cols):
                x = 1.8 + j * 0.95
                y = 2.2 - i * 0.95
                self.grid[f"{row}{col}"] = np.array([x, y, 0])

    def place_at_grid(self, mobject, grid_pos, scale_factor=1.0):
        mobject.scale(scale_factor)
        mobject.move_to(self.grid[grid_pos])
        return mobject

    def place_in_area(self, mobject, top_left, bottom_right, scale_factor=1.0):
        tl_pos = self.grid[top_left]
        br_pos = self.grid[bottom_right]

        # Calculate center of the area
        center_x = (tl_pos[0] + br_pos[0]) / 2
        center_y = (tl_pos[1] + br_pos[1]) / 2
        center = np.array([center_x, center_y, 0])

        mobject.scale(scale_factor)
        mobject.move_to(center)
        return mobject
