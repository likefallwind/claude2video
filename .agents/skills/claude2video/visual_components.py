"""
Visual Components Library for TeachingScene-based educational videos.

Provides high-level UI components (info cards, callout boxes, badges,
comparison layouts, etc.) and a subject-based color palette system.
Import these in generated section files alongside teaching_scene.py
and anim_helpers.py.
"""

from manim import *
import numpy as np

# ---------------------------------------------------------------------------
# Color Palette System
# ---------------------------------------------------------------------------

COLOR_PALETTES = {
    "physics": {
        "primary": "#4FC3F7",      # light blue
        "secondary": "#FF6B6B",    # coral red
        "accent": "#FFD700",       # gold
        "highlight": "#81C784",    # soft green
        "text": "#FFFFFF",         # white
        "muted": "#90A4AE",       # blue-grey
        "bg_gradient": ("#1A237E", "#0D47A1"),  # deep blue gradient
    },
    "math": {
        "primary": "#CE93D8",      # lavender
        "secondary": "#4FC3F7",    # sky blue
        "accent": "#FFD54F",       # amber
        "highlight": "#81C784",    # green
        "text": "#FFFFFF",
        "muted": "#B0BEC5",
        "bg_gradient": ("#311B92", "#4A148C"),
    },
    "biology": {
        "primary": "#81C784",      # green
        "secondary": "#4FC3F7",    # blue
        "accent": "#FFB74D",       # orange
        "highlight": "#F06292",    # pink
        "text": "#FFFFFF",
        "muted": "#A5D6A7",
        "bg_gradient": ("#1B5E20", "#2E7D32"),
    },
    "chemistry": {
        "primary": "#FF8A65",      # deep orange
        "secondary": "#4DD0E1",    # cyan
        "accent": "#FFD740",       # amber
        "highlight": "#CE93D8",    # purple
        "text": "#FFFFFF",
        "muted": "#BCAAA4",
        "bg_gradient": ("#BF360C", "#E65100"),
    },
    "default": {
        "primary": "#4FC3F7",
        "secondary": "#FF6B6B",
        "accent": "#FFD700",
        "highlight": "#81C784",
        "text": "#FFFFFF",
        "muted": "#90A4AE",
        "bg_gradient": ("#212121", "#424242"),
    },
}

# ---------------------------------------------------------------------------
# Helper: area dimensions from grid keys
# ---------------------------------------------------------------------------

def _area_rect(scene, tl, br, padding=0.1):
    """Return (center, width, height) for a grid area."""
    p_tl = scene.grid[tl]
    p_br = scene.grid[br]
    w = abs(p_br[0] - p_tl[0]) - 2 * padding
    h = abs(p_tl[1] - p_br[1]) - 2 * padding
    cx = (p_tl[0] + p_br[0]) / 2
    cy = (p_tl[1] + p_br[1]) / 2
    return np.array([cx, cy, 0]), max(w, 0.3), max(h, 0.3)


# ---------------------------------------------------------------------------
# Component 1: Info Card
# ---------------------------------------------------------------------------

def create_info_card(scene, title, body, tl, br, accent_color="#4FC3F7",
                     icon_path=None):
    """Create a rounded-rectangle info card with title, body, and optional icon.

    Parameters
    ----------
    scene : TeachingScene
    title : str
        Card title text.
    body : str
        Card body text (can be multi-line with ``\\n``).
    tl, br : str
        Grid keys for top-left / bottom-right of the card area.
    accent_color : str
        Hex color for the title bar accent.
    icon_path : str or None
        Path to an optional icon image displayed in the top-right corner.

    Returns
    -------
    VGroup
        The complete card group, already positioned in the grid area.
    """
    center, w, h = _area_rect(scene, tl, br)

    # Background rounded rectangle
    bg = RoundedRectangle(
        corner_radius=0.15, width=w, height=h,
        fill_color="#1E1E2E", fill_opacity=0.85,
        stroke_color=accent_color, stroke_width=1.5,
    )

    # Accent bar at top
    bar = Rectangle(
        width=w, height=0.06,
        fill_color=accent_color, fill_opacity=1.0,
        stroke_width=0,
    )
    bar.next_to(bg, UP, buff=0).shift(DOWN * 0.03)

    # Title
    title_mob = Text(title, font_size=20, color=accent_color, weight=BOLD)
    title_mob.scale(min(1.0, (w - 0.3) / max(title_mob.width, 1e-6)))
    title_mob.next_to(bg.get_top(), DOWN, buff=0.2)
    title_mob.align_to(bg, LEFT).shift(RIGHT * 0.2)

    # Body
    body_mob = Text(body, font_size=16, color="#E0E0E0", line_spacing=1.3)
    max_body_w = w - 0.4
    max_body_h = h - 0.8
    if body_mob.width > 0 and body_mob.height > 0:
        body_scale = min(max_body_w / body_mob.width,
                         max_body_h / body_mob.height, 1.0)
        body_mob.scale(body_scale)
    body_mob.next_to(title_mob, DOWN, buff=0.2)
    body_mob.align_to(bg, LEFT).shift(RIGHT * 0.2)

    card = VGroup(bg, bar, title_mob, body_mob)

    # Optional icon
    if icon_path is not None:
        try:
            icon = ImageMobject(icon_path).scale_to_fit_height(0.5)
            icon.next_to(bg.get_corner(UR), DL, buff=0.1)
            card.add(icon)
        except Exception:
            pass  # gracefully skip if image not found

    card.move_to(center)
    return card


# ---------------------------------------------------------------------------
# Component 2: Callout Box
# ---------------------------------------------------------------------------

_CALLOUT_STYLES = {
    "key":     {"bar": "#FFD700", "bg": "#3E2723", "icon": "!"},
    "formula": {"bar": "#CE93D8", "bg": "#1A1A2E", "icon": "f"},
    "note":    {"bar": "#4FC3F7", "bg": "#0D1B2A", "icon": "i"},
    "warning": {"bar": "#FFB74D", "bg": "#3E2723", "icon": "!"},
}


def create_callout_box(scene, text, tl, br, style="note", color=None):
    """Create a callout box with a colored left bar and translucent background.

    Parameters
    ----------
    scene : TeachingScene
    text : str
        The callout text content.
    tl, br : str
        Grid keys for the bounding area.
    style : str
        One of ``"key"``, ``"formula"``, ``"note"``, ``"warning"``.
    color : str or None
        Override bar color.

    Returns
    -------
    VGroup
        The callout group, positioned in the grid area.
    """
    center, w, h = _area_rect(scene, tl, br)
    s = _CALLOUT_STYLES.get(style, _CALLOUT_STYLES["note"])
    bar_color = color or s["bar"]

    # Background
    bg = Rectangle(
        width=w, height=h,
        fill_color=s["bg"], fill_opacity=0.7,
        stroke_width=0,
    )

    # Left accent bar
    bar = Rectangle(
        width=0.06, height=h,
        fill_color=bar_color, fill_opacity=1.0,
        stroke_width=0,
    )
    bar.align_to(bg, LEFT)

    # Text content
    txt = Text(text, font_size=18, color="#FFFFFF", line_spacing=1.2)
    max_txt_w = w - 0.4
    max_txt_h = h - 0.2
    if txt.width > 0 and txt.height > 0:
        txt_scale = min(max_txt_w / txt.width, max_txt_h / txt.height, 1.0)
        txt.scale(txt_scale)
    txt.next_to(bar, RIGHT, buff=0.15)
    txt.align_to(bg, UP).shift(DOWN * 0.1)

    callout = VGroup(bg, bar, txt)
    callout.move_to(center)
    return callout


# ---------------------------------------------------------------------------
# Component 3: Gradient Rectangle
# ---------------------------------------------------------------------------

def create_gradient_rect(width, height, color_top, color_bottom, opacity=0.3):
    """Create a vertical gradient rectangle using layered thin strips.

    Parameters
    ----------
    width, height : float
        Dimensions in scene units.
    color_top, color_bottom : str
        Hex colors for top and bottom.
    opacity : float
        Overall fill opacity.

    Returns
    -------
    VGroup
        A group of thin rectangles forming the gradient.
    """
    n_strips = 20
    strip_h = height / n_strips
    strips = VGroup()
    for i in range(n_strips):
        alpha = i / max(n_strips - 1, 1)
        c = interpolate_color(ManimColor(color_top), ManimColor(color_bottom), alpha)
        strip = Rectangle(
            width=width, height=strip_h + 0.005,  # slight overlap to avoid gaps
            fill_color=c, fill_opacity=opacity,
            stroke_width=0,
        )
        y_offset = height / 2 - strip_h * (i + 0.5)
        strip.shift(UP * y_offset)
        strips.add(strip)
    return strips


# ---------------------------------------------------------------------------
# Component 4: Number Badge
# ---------------------------------------------------------------------------

def create_number_badge(scene, number, label, grid_pos, color="#4FC3F7"):
    """Create a circular number badge with a text label below.

    Parameters
    ----------
    scene : TeachingScene
    number : int or str
        The number to display inside the circle.
    label : str
        Short label text below the badge.
    grid_pos : str
        Grid key for center placement.
    color : str
        Badge circle fill color.

    Returns
    -------
    VGroup
        Badge + label group, positioned at the grid point.
    """
    circle = Circle(radius=0.25, fill_color=color, fill_opacity=0.9,
                    stroke_color=WHITE, stroke_width=1.5)
    num_text = Text(str(number), font_size=22, color=WHITE, weight=BOLD)
    num_text.move_to(circle.get_center())

    lbl = Text(label, font_size=14, color="#E0E0E0")
    lbl.next_to(circle, DOWN, buff=0.1)
    lbl_scale = min(1.0, 0.7 / max(lbl.width, 1e-6))
    lbl.scale(lbl_scale)

    badge = VGroup(circle, num_text, lbl)
    badge.move_to(scene.grid[grid_pos])
    return badge


# ---------------------------------------------------------------------------
# Component 5: Comparison Layout
# ---------------------------------------------------------------------------

def create_comparison_layout(scene, left_items, right_items, tl, br,
                             left_color="#4FC3F7", right_color="#FF6B6B"):
    """Create a two-column comparison layout with colored header bars.

    Parameters
    ----------
    scene : TeachingScene
    left_items : list[str]
        Bullet texts for the left column.
    right_items : list[str]
        Bullet texts for the right column.
    tl, br : str
        Grid keys bounding the entire comparison area.
    left_color, right_color : str
        Header bar colors for left/right columns.

    Returns
    -------
    VGroup
        The complete comparison layout, positioned in the grid area.
    """
    center, w, h = _area_rect(scene, tl, br)
    col_w = (w - 0.15) / 2  # gap between columns

    # Left column
    left_header = Rectangle(
        width=col_w, height=0.3,
        fill_color=left_color, fill_opacity=0.8, stroke_width=0,
    )
    left_bg = Rectangle(
        width=col_w, height=h - 0.35,
        fill_color="#1E1E2E", fill_opacity=0.6, stroke_width=0,
    )
    left_bg.next_to(left_header, DOWN, buff=0.05)

    left_texts = VGroup()
    for item in left_items:
        t = Text(f"  {item}", font_size=14, color="#E0E0E0")
        t.scale(min(1.0, (col_w - 0.2) / max(t.width, 1e-6)))
        left_texts.add(t)
    left_texts.arrange(DOWN, aligned_edge=LEFT, buff=0.12)
    left_texts.next_to(left_bg.get_top(), DOWN, buff=0.1)

    left_col = VGroup(left_header, left_bg, left_texts)

    # Right column
    right_header = Rectangle(
        width=col_w, height=0.3,
        fill_color=right_color, fill_opacity=0.8, stroke_width=0,
    )
    right_bg = Rectangle(
        width=col_w, height=h - 0.35,
        fill_color="#1E1E2E", fill_opacity=0.6, stroke_width=0,
    )
    right_bg.next_to(right_header, DOWN, buff=0.05)

    right_texts = VGroup()
    for item in right_items:
        t = Text(f"  {item}", font_size=14, color="#E0E0E0")
        t.scale(min(1.0, (col_w - 0.2) / max(t.width, 1e-6)))
        right_texts.add(t)
    right_texts.arrange(DOWN, aligned_edge=LEFT, buff=0.12)
    right_texts.next_to(right_bg.get_top(), DOWN, buff=0.1)

    right_col = VGroup(right_header, right_bg, right_texts)

    # Position columns side by side
    left_col.shift(LEFT * (col_w / 2 + 0.075))
    right_col.shift(RIGHT * (col_w / 2 + 0.075))

    layout = VGroup(left_col, right_col)
    layout.move_to(center)
    return layout


# ---------------------------------------------------------------------------
# Component 6: Separator
# ---------------------------------------------------------------------------

def create_separator(scene, tl, br, style="line", color="#90A4AE"):
    """Create a decorative separator line between grid positions.

    Parameters
    ----------
    scene : TeachingScene
    tl, br : str
        Grid keys — separator runs horizontally from tl to br.
    style : str
        ``"line"``, ``"dots"``, or ``"gradient"``.
    color : str
        Separator color.

    Returns
    -------
    Mobject
        The separator object.
    """
    p_tl = scene.grid[tl]
    p_br = scene.grid[br]
    mid_y = (p_tl[1] + p_br[1]) / 2
    start = np.array([p_tl[0], mid_y, 0])
    end = np.array([p_br[0], mid_y, 0])

    if style == "dots":
        n_dots = 12
        dots = VGroup()
        for i in range(n_dots):
            alpha = i / max(n_dots - 1, 1)
            pos = start + alpha * (end - start)
            dot = Dot(pos, radius=0.025, color=color)
            dots.add(dot)
        return dots

    elif style == "gradient":
        line = Line(start, end, stroke_width=1.5, color=color)
        line.set_stroke(opacity=[0, 1, 1, 0])  # fade at edges
        return line

    else:  # "line"
        return Line(start, end, stroke_width=1.0, color=color)
