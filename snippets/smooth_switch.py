import cairo
from gi.repository import Gtk, Gdk
from .animator import Animator

class SmoothSwitch(Gtk.DrawingArea):
    """
    Cairo-drawn switch with animated thumb, drop-in replacement for Switch.
    Emits 'user-toggled' (bool) only on actual user clicks.
    """

    def __init__(
        self,
        active: bool = False,
        width: int = 44,
        height: int = 24,
        on_user_toggle=None,
        style_classes: list | None = None,
        v_align=None,
        v_expand: bool = False,
        h_expand: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._active = bool(active)
        self._width = width
        self._height = height
        self._on_user_toggle = on_user_toggle

        self.set_size_request(width, height)
        self.set_hexpand(h_expand)
        self.set_vexpand(v_expand)
        if v_align is not None:
            if isinstance(v_align, str):
                v_align = {
                    "fill": Gtk.Align.FILL,
                    "start": Gtk.Align.START,
                    "end": Gtk.Align.END,
                    "center": Gtk.Align.CENTER,
                    "baseline": Gtk.Align.BASELINE,
                }[v_align]
            self.set_valign(v_align)

        ctx = self.get_style_context()
        ctx.add_class("smooth-switch")
        if style_classes:
            for cls in style_classes:
                ctx.add_class(cls)

        if self._active:
            ctx.add_class("checked")

        init_val = 1.0 if self._active else 0.0
        self._animator = Animator(
            bezier_curve=(0.2, 0.6, 0.8, 1.0),
            duration=0.2,
            min_value=init_val,
            max_value=init_val,
            tick_widget=self,
        )
        self._animator.value = init_val
        self._animator.connect("notify::value", lambda *_: self.queue_draw())

        self.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.ENTER_NOTIFY_MASK |
            Gdk.EventMask.LEAVE_NOTIFY_MASK
        )
        self.connect("button-press-event", self._on_click)
        self.connect("draw", self._on_draw)
        self.connect("enter-notify-event", self._on_enter)
        self.connect("leave-notify-event", self._on_leave)
        self.show_all()

    def _on_enter(self, *_):
        window = self.get_window()
        if window:
            cursor = Gdk.Cursor.new_from_name(window.get_display(), "pointer")
            window.set_cursor(cursor)
        self.queue_draw()

    def _on_leave(self, *_):
        window = self.get_window()
        if window:
            window.set_cursor(None)
        self.queue_draw()

    def get_active(self) -> bool:
        return self._active

    def set_active(self, value: bool):
        """Programmatic set — does NOT emit user-toggled."""
        value = bool(value)
        target = 1.0 if value else 0.0
        if value == self._active:
            if self._animator.value != target:
                self._animator.value = target
                self._animator.min_value = target
                self._animator.max_value = target
                self.queue_draw()
            return
        self._active = value
        if not self.get_mapped():
            self._animator.value = target
            self._animator.min_value = target
            self._animator.max_value = target
            self.queue_draw()
            return
        self._animate_to(target)

    def _on_click(self, _, event):
        if event.button != 1:
            return False
        self._active = not self._active
        self._animate_to(1.0 if self._active else 0.0)
        if self._on_user_toggle:
            self._on_user_toggle(self._active)
        return True

    def _animate_to(self, target: float):
        self._animator.pause()
        self._animator.min_value = self._animator.value
        self._animator.max_value = target
        self._animator.value = self._animator.min_value
        self._animator.play()

    def _on_draw(self, _, cr: cairo.Context):
        alloc = self.get_allocation()
        w = alloc.width if alloc.width > 0 else self._width
        h = alloc.height if alloc.height > 0 else self._height
        r = h / 2.0
        margin = 2.5
        t = max(0.0, min(1.0, float(self._animator.value)))

        style = self.get_style_context()

        # Query OFF state colors
        had_checked = style.has_class("checked")
        if had_checked:
            style.remove_class("checked")
        off_bg = style.get_background_color(Gtk.StateFlags.NORMAL)
        off_fg = style.get_color(Gtk.StateFlags.NORMAL)

        # Query ON state colors
        style.add_class("checked")
        on_bg = style.get_background_color(Gtk.StateFlags.NORMAL)
        on_fg = style.get_color(Gtk.StateFlags.NORMAL)

        # Restore style class state
        if not self._active and t <= 0.0:
            style.remove_class("checked")

        # Robust fallbacks if CSS returned transparent / unstyled
        if off_bg.alpha < 0.05:
            off_bg = Gdk.RGBA(0.18, 0.19, 0.23, 1.0)
        if on_bg.alpha < 0.05:
            on_bg = Gdk.RGBA(0.55, 0.34, 0.75, 1.0)
        if off_fg.alpha < 0.05:
            off_fg = Gdk.RGBA(0.75, 0.77, 0.82, 1.0)
        if on_fg.alpha < 0.05:
            on_fg = Gdk.RGBA(1.0, 1.0, 1.0, 1.0)

        track_r = off_bg.red   + (on_bg.red   - off_bg.red)   * t
        track_g = off_bg.green + (on_bg.green - off_bg.green) * t
        track_b = off_bg.blue  + (on_bg.blue  - off_bg.blue)  * t
        track_a = off_bg.alpha + (on_bg.alpha - off_bg.alpha) * t

        # Draw switch track capsule
        cr.new_sub_path()
        cr.arc(r,     r, r, 0.5 * 3.14159, 1.5 * 3.14159)
        cr.arc(w - r, r, r, -0.5 * 3.14159, 0.5 * 3.14159)
        cr.close_path()
        cr.set_source_rgba(track_r, track_g, track_b, track_a)
        cr.fill_preserve()

        # Track border outline for contrast (especially when off)
        outline_alpha = 0.20 * (1.0 - t) + 0.10 * t
        cr.set_source_rgba(1.0, 1.0, 1.0, outline_alpha)
        cr.set_line_width(1.0)
        cr.stroke()

        # Thumb metrics
        thumb_r = r - margin
        travel  = w - 2.0 * r
        thumb_x = r + travel * t
        thumb_y = r

        # Thumb drop shadow
        cr.save()
        cr.arc(thumb_x, thumb_y + 1.0, thumb_r, 0, 2 * 3.14159)
        cr.set_source_rgba(0.0, 0.0, 0.0, 0.28)
        cr.fill()
        cr.restore()

        # Thumb body
        thumb_r_c = off_fg.red   + (on_fg.red   - off_fg.red)   * t
        thumb_g_c = off_fg.green + (on_fg.green - off_fg.green) * t
        thumb_b_c = off_fg.blue  + (on_fg.blue  - off_fg.blue)  * t
        thumb_a_c = off_fg.alpha + (on_fg.alpha - off_fg.alpha) * t

        cr.arc(thumb_x, thumb_y, thumb_r, 0, 2 * 3.14159)
        cr.set_source_rgba(thumb_r_c, thumb_g_c, thumb_b_c, thumb_a_c)
        cr.fill()

        return False