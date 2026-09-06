import os
import time
import random
import subprocess
import cairo
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
gi.require_version("GtkLayerShell", "0.1")

from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, GtkLayerShell
from loguru import logger
from user_options import user_options


class DoomMeltOverlay(Gtk.Window):
    """
    Full-screen Wayland overlay that performs the iconic vertical strip melt transition.
    Vertical columns of the previous desktop melt away from top to bottom in staggered waves,
    revealing the new desktop underneath.
    """

    def __init__(self, monitor: Gdk.Monitor, pixbuf: GdkPixbuf.Pixbuf, duration: float = 0.72, num_columns: int = 60):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self._pixbuf = pixbuf
        self._duration = duration
        self._num_cols = num_columns
        self._start_time = None
        self._progress = 0.0
        self._timer_id = None
        self._on_done = None

        # Setup Layer Shell
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.NONE)
        GtkLayerShell.set_exclusive_zone(self, -1)
        GtkLayerShell.set_monitor(self, monitor)

        for edge in (
            GtkLayerShell.Edge.TOP,
            GtkLayerShell.Edge.BOTTOM,
            GtkLayerShell.Edge.LEFT,
            GtkLayerShell.Edge.RIGHT,
        ):
            GtkLayerShell.set_anchor(self, edge, True)
            GtkLayerShell.set_margin(self, edge, 0)

        # Set transparent RGBA visual and app-paintable
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)
        self.set_app_paintable(True)

        # Force transparent window background via CSS provider
        css = Gtk.CssProvider()
        css.load_from_data(b"window { background-color: transparent; }")
        self.get_style_context().add_provider(css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # Correlated random-walk column delays (ragged dripping melt wave)
        self._delays = []
        curr = random.uniform(0.0, 0.07)
        for _ in range(self._num_cols):
            curr = max(0.0, min(0.36, curr + random.uniform(-0.05, 0.05)))
            self._delays.append(curr)

        self.connect("draw", self._on_draw)

    def start(self, on_done=None):
        self._on_done = on_done
        self._start_time = time.time()
        self._timer_id = GLib.timeout_add(16, self._on_tick)

    def _on_tick(self):
        if self._start_time is None:
            return GLib.SOURCE_CONTINUE

        elapsed = time.time() - self._start_time
        self._progress = min(1.0, elapsed / self._duration)
        self.queue_draw()

        if self._progress >= 1.0:
            self._timer_id = None
            if callable(self._on_done):
                try:
                    self._on_done()
                except Exception as e:
                    logger.error(f"[DoomMelt] on_done callback error: {e}")
            self.destroy()
            return GLib.SOURCE_REMOVE

        return GLib.SOURCE_CONTINUE

    def _on_draw(self, widget, cr: cairo.Context):
        W = widget.get_allocated_width()
        H = widget.get_allocated_height()

        if W <= 0 or H <= 0 or not self._pixbuf:
            return False

        # Clear entire overlay surface completely transparent
        cr.set_operator(cairo.OPERATOR_CLEAR)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)

        col_w = W / self._num_cols
        progress = self._progress

        for i in range(self._num_cols):
            d = self._delays[i]
            if progress < d:
                t = 0.0
            else:
                t = min(1.0, (progress - d) / (1.0 - d))

            # Accelerating quadratic gravity drop
            y_cut = int(t * t * (H + 24))

            if y_cut < H:
                col_x = int(i * col_w)
                col_width = int((i + 1) * col_w) - col_x + 1

                cr.save()
                # Clip remaining old desktop in this column (from y_cut to bottom H)
                cr.rectangle(col_x, y_cut, col_width, H - y_cut)
                cr.clip()

                # Draw previous screen snapshot stationary at (0, 0)
                Gdk.cairo_set_source_pixbuf(cr, self._pixbuf, 0, 0)
                cr.paint()

                # Drip edge shadow on the falling cut boundary
                cr.set_source_rgba(0, 0, 0, 0.45)
                cr.rectangle(col_x, y_cut, col_width, 4)
                cr.fill()

                cr.restore()

        return True


def capture_desktop_pixbuf(monitor: Gdk.Monitor) -> GdkPixbuf.Pixbuf | None:
    """Capture snapshot of current desktop or fallback to current wallpaper."""
    geom = monitor.get_geometry()
    W, H = geom.width, geom.height
    tmp_path = f"/tmp/agility_melt_{os.getpid()}_{monitor.get_geometry().x}.ppm"

    # Attempt instant grim capture
    try:
        res = subprocess.run(
            ["grim", "-t", "ppm", tmp_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=0.25,
        )
        if res.returncode == 0 and os.path.isfile(tmp_path):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(tmp_path, W, H, False)
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
            return pixbuf
    except Exception:
        pass

    # Fallback to current wallpaper
    wp_path = getattr(user_options.wallpaper, "path", None)
    if wp_path and os.path.isfile(wp_path):
        try:
            return GdkPixbuf.Pixbuf.new_from_file_at_scale(wp_path, W, H, False)
        except Exception:
            pass

    return None


def play_doom_melt_transition(on_switch=None, on_finish=None):
    """
    Play the full-screen Doom Vertical Melt transition on active monitors.
    `on_switch`: Callback to apply preset changes underneath while overlay covers screen.
    `on_finish`: Callback when melt animation completes.
    """
    display = Gdk.Display.get_default()
    if not display:
        if on_switch:
            on_switch()
        if on_finish:
            on_finish()
        return

    n_monitors = display.get_n_monitors()
    overlays = []

    for i in range(n_monitors):
        mon = display.get_monitor(i)
        pixbuf = capture_desktop_pixbuf(mon)
        if pixbuf:
            overlay = DoomMeltOverlay(mon, pixbuf, duration=0.72)
            overlays.append(overlay)

    # If no overlays could be created, execute switch immediately
    if not overlays:
        if on_switch:
            on_switch()
        if on_finish:
            on_finish()
        return

    finished_count = [0]
    total_overlays = len(overlays)

    def _done_one():
        finished_count[0] += 1
        if finished_count[0] >= total_overlays and on_finish:
            on_finish()

    # 1. Map and present overlays with the frozen current screen
    for overlay in overlays:
        overlay.show_all()

    # 2. After overlay is displayed on screen, apply the new preset underneath and start melting
    def _start_melt_and_switch():
        if on_switch:
            on_switch()

        for overlay in overlays:
            overlay.start(on_done=_done_one)

        return GLib.SOURCE_REMOVE

    # 35ms gives the Wayland compositor 2 frame cycles to reliably present the overlay
    GLib.timeout_add(35, _start_melt_and_switch)
