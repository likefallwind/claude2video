"""
Animation helper utilities for TeachingScene-based educational videos.

Provides high-level functions that wrap common Manim patterns to avoid
boilerplate and ensure objects fit within the 6×6 Visual Anchor Grid.
Import these in generated section files alongside teaching_scene.py.
"""

from manim import *
import numpy as np


def fit_and_place(scene, obj, top_left, bottom_right, padding=0.15):
    """Scale *obj* to fit inside the grid area defined by *top_left*–*bottom_right*,
    then center it in that area.  Unlike ``place_in_area`` this guarantees the
    object will not overflow the region.

    Parameters
    ----------
    scene : TeachingScene
        The scene whose ``.grid`` dict provides anchor positions.
    obj : Mobject
        The object to scale and place.
    top_left, bottom_right : str
        Grid keys such as ``"A1"`` and ``"C4"``.
    padding : float
        Inset from the area boundary on each side (in scene units).

    Returns
    -------
    Mobject
        The same *obj*, scaled and moved in-place.
    """
    tl = scene.grid[top_left]
    br = scene.grid[bottom_right]

    area_w = abs(br[0] - tl[0]) - 2 * padding
    area_h = abs(tl[1] - br[1]) - 2 * padding

    if area_w <= 0 or area_h <= 0:
        # Fallback: just center without scaling
        center = (tl + br) / 2
        obj.move_to(center)
        return obj

    obj_w = obj.width if obj.width > 0 else 1e-6
    obj_h = obj.height if obj.height > 0 else 1e-6

    scale = min(area_w / obj_w, area_h / obj_h, 1.0)
    obj.scale(scale)

    center = np.array([(tl[0] + br[0]) / 2, (tl[1] + br[1]) / 2, 0])
    obj.move_to(center)
    return obj


def create_fitted_axes(scene, top_left, bottom_right, x_range, y_range,
                       padding=0.15, **axes_kwargs):
    """Create a Manim ``Axes`` object that fits exactly inside a grid area.

    Parameters
    ----------
    scene : TeachingScene
        The scene whose ``.grid`` dict provides anchor positions.
    top_left, bottom_right : str
        Grid keys defining the bounding area.
    x_range, y_range : list
        ``[min, max, step]`` passed to ``Axes``.
    padding : float
        Inset from the area boundary.
    **axes_kwargs
        Extra keyword arguments forwarded to ``Axes`` (e.g. ``axis_config``).

    Returns
    -------
    Axes
        A properly sized and positioned ``Axes`` instance.
    """
    tl = scene.grid[top_left]
    br = scene.grid[bottom_right]

    area_w = abs(br[0] - tl[0]) - 2 * padding
    area_h = abs(tl[1] - br[1]) - 2 * padding

    defaults = dict(
        x_length=max(area_w, 0.5),
        y_length=max(area_h, 0.5),
        tips=True,
        axis_config={"include_numbers": True, "font_size": 18},
    )
    defaults.update(axes_kwargs)

    axes = Axes(x_range=x_range, y_range=y_range, **defaults)

    center = np.array([(tl[0] + br[0]) / 2, (tl[1] + br[1]) / 2, 0])
    axes.move_to(center)
    return axes


def animate_along_curve(scene, obj, func, axes, t_range, run_time=3.0,
                        trace=True, trace_color=YELLOW):
    """Animate *obj* along a parametric curve plotted on *axes*.

    Uses a ``ValueTracker`` so the motion is smooth and physics-accurate.

    Parameters
    ----------
    scene : TeachingScene
        The active scene (needed for ``scene.play``).
    obj : Mobject
        The object to move (e.g. a ``Dot``).
    func : callable
        ``func(t) -> (x, y)`` in *data* coordinates matching *axes*.
    axes : Axes
        The coordinate system used for mapping.
    t_range : list
        ``[t_start, t_end]``.
    run_time : float
        Duration of the animation in seconds.
    trace : bool
        Whether to draw a ``TracedPath`` behind the object.
    trace_color
        Color for the traced path.

    Returns
    -------
    tuple
        ``(tracker, traced_path_or_None)`` so the caller can remove them later.
    """
    t0, t1 = t_range[0], t_range[1]
    tracker = ValueTracker(t0)

    def _updater(m):
        t = tracker.get_value()
        x, y = func(t)
        m.move_to(axes.c2p(x, y))

    obj.add_updater(_updater)
    # Set initial position
    _updater(obj)

    traced = None
    if trace:
        traced = TracedPath(obj.get_center, stroke_color=trace_color,
                            stroke_width=2)
        scene.add(traced)

    scene.play(tracker.animate.set_value(t1), run_time=run_time,
               rate_func=linear)
    obj.remove_updater(_updater)
    return tracker, traced


def strobe_effect(scene, path_func, axes, n, t_range, dot_radius=0.06,
                  dot_color=WHITE, stagger=0.15, run_time=None):
    """Create a stroboscopic (multi-exposure) animation along a path.

    Dots appear one-by-one at equal time intervals along the trajectory,
    producing realistic strobe spacing that reflects the actual velocity.

    Parameters
    ----------
    scene : TeachingScene
        The active scene.
    path_func : callable
        ``path_func(t) -> (x, y)`` in data coordinates.
    axes : Axes
        Coordinate system for mapping.
    n : int
        Number of strobe dots.
    t_range : list
        ``[t_start, t_end]``.
    dot_radius : float
        Radius of each strobe dot.
    dot_color
        Color for strobe dots.
    stagger : float
        Delay between successive dot appearances.
    run_time : float or None
        Total run_time for the LaggedStart.  Defaults to ``n * stagger``.

    Returns
    -------
    VGroup
        The group of strobe dots (already on screen).
    """
    t0, t1 = t_range[0], t_range[1]
    times = np.linspace(t0, t1, n)
    dots = VGroup()
    for t in times:
        x, y = path_func(t)
        dot = Dot(axes.c2p(x, y), radius=dot_radius, color=dot_color)
        dots.add(dot)

    if run_time is None:
        run_time = n * stagger

    scene.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in dots],
                            lag_ratio=stagger / run_time),
               run_time=run_time)
    return dots


# ---------------------------------------------------------------------------
# Enhanced animation helpers
# ---------------------------------------------------------------------------

def highlight_region(scene, tl, br, color="#FFD700", opacity=0.15, run_time=0.5):
    """Fade in a semi-transparent rectangle to highlight a grid region.

    Parameters
    ----------
    scene : TeachingScene
        The active scene.
    tl, br : str
        Grid keys for the region corners.
    color : str
        Highlight color.
    opacity : float
        Fill opacity (keep low for a subtle effect).
    run_time : float
        Animation duration.

    Returns
    -------
    Rectangle
        The highlight rectangle (already on screen).
    """
    p_tl = scene.grid[tl]
    p_br = scene.grid[br]
    w = abs(p_br[0] - p_tl[0])
    h = abs(p_tl[1] - p_br[1])
    center = np.array([(p_tl[0] + p_br[0]) / 2, (p_tl[1] + p_br[1]) / 2, 0])

    rect = Rectangle(
        width=w, height=h,
        fill_color=color, fill_opacity=opacity,
        stroke_width=0,
    )
    rect.move_to(center)
    scene.play(FadeIn(rect), run_time=run_time)
    return rect


def pulse_glow(scene, obj, color="#FFD700", n_pulses=2, run_time=1.0):
    """Create a pulsing glow effect around an object.

    A surrounding circle scales up and fades out repeatedly.

    Parameters
    ----------
    scene : TeachingScene
        The active scene.
    obj : Mobject
        The object to pulse around.
    color : str
        Glow color.
    n_pulses : int
        Number of pulse repetitions.
    run_time : float
        Total animation duration.

    Returns
    -------
    None
    """
    pulse_time = run_time / max(n_pulses, 1)
    for _ in range(n_pulses):
        glow = Circle(
            radius=max(obj.width, obj.height) / 2 + 0.1,
            stroke_color=color, stroke_width=3, fill_opacity=0,
        )
        glow.move_to(obj.get_center())
        scene.play(
            glow.animate.scale(1.5).set_stroke(opacity=0),
            run_time=pulse_time,
        )
        scene.remove(glow)


def animated_arrow_chain(scene, points, color="#4FC3F7", run_time=1.5):
    """Draw an arrow chain connecting a list of points, segment by segment.

    Parameters
    ----------
    scene : TeachingScene
        The active scene.
    points : list[np.ndarray | str]
        Sequence of positions. If a string is given, it is looked up in
        ``scene.grid``.
    color : str
        Arrow color.
    run_time : float
        Total animation duration for all segments.

    Returns
    -------
    VGroup
        The group of arrow segments (already on screen).
    """
    resolved = []
    for p in points:
        if isinstance(p, str):
            resolved.append(scene.grid[p])
        else:
            resolved.append(np.array(p))

    arrows = VGroup()
    seg_time = run_time / max(len(resolved) - 1, 1)
    for i in range(len(resolved) - 1):
        arrow = Arrow(
            resolved[i], resolved[i + 1],
            color=color, buff=0.05,
            stroke_width=2.5, max_tip_length_to_length_ratio=0.2,
        )
        arrows.add(arrow)
        scene.play(GrowArrow(arrow), run_time=seg_time)

    return arrows
