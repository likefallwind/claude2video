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
