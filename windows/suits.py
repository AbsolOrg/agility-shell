from __future__ import annotations
import os
import hashlib
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from fabric.widgets.scrolledwindow import ScrolledWindow
from fabric.widgets.image import Image
from snippets import Icon, Applet, AppletPage
from services.suits_service import suits_service
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib
from utils.sounds import play_sound

THUMBS_DIR = os.path.expanduser("~/.cache/agility-shell/suits_thumbs")
os.makedirs(THUMBS_DIR, exist_ok=True)


def get_wallpaper_pixbuf(path: str, width: int = 76, height: int = 48) -> GdkPixbuf.Pixbuf | None:
    if not path or not os.path.isfile(path):
        return None
    try:
        return GdkPixbuf.Pixbuf.new_from_file_at_scale(path, width, height, False)
    except Exception:
        return None


class SuitsPopupCard(Button):
    def __init__(self, suite: dict, is_active: bool, on_select):
        self.suite = suite
        self.suite_id = suite.get("id", "")
        self._on_select = on_select

        cfg = suite.get("config", {})
        wp_cfg = cfg.get("wallpaper", {})
        wp_path = wp_cfg.get("path", "")
        theme_cfg = cfg.get("theme", {})
        bars_cfg = cfg.get("bars", [])
        canvas_cfg = cfg.get("desktop_canvas", {})

        # 1. Wallpaper Thumbnail Widget
        pixbuf = get_wallpaper_pixbuf(wp_path, 80, 48)
        if pixbuf:
            gtk_img = Gtk.Image.new_from_pixbuf(pixbuf)
            thumb_box = Box(
                style_classes=["suits-popup-thumb"],
                style="min-width: 80px; min-height: 48px; border-radius: 6px;",
                children=[gtk_img],
            )
        else:
            thumb_box = Box(
                style_classes=["suits-popup-thumb", "fallback"],
                style="min-width: 80px; min-height: 48px; border-radius: 6px; background-color: var(--surface_container_high);",
                v_align="center",
                h_align="center",
                children=[Icon(icon_name="image-duotone", icon_size=20)],
            )

        # 2. Text Info Column
        name_label = Label(
            label=suite.get("name", "Desktop"),
            style="font-size: 13px; font-weight: 600;",
            h_align="start",
        )

        theme_name = (theme_cfg.get("dark_theme") if theme_cfg.get("is_dark", True) else theme_cfg.get("light_theme")) or "Default"
        accent_name = theme_cfg.get("active_accent", "")
        
        # Count widgets
        total_bar_widgets = 0
        for m in bars_cfg:
            for b in m.get("bars", []):
                total_bar_widgets += len(b.get("left", [])) + len(b.get("center", [])) + len(b.get("right", []))
        total_canvas = sum(len(items) for items in canvas_cfg.values()) if isinstance(canvas_cfg, dict) else 0

        subtitle = f"{theme_name} • {total_bar_widgets} bar • {total_canvas} desktop"
        sub_label = Label(
            label=subtitle,
            style="font-size: 10.5px; opacity: 0.65;",
            h_align="start",
        )

        text_col = Box(
            orientation="v",
            spacing=3,
            h_align="start",
            v_align="center",
            h_expand=True,
            children=[name_label, sub_label],
        )

        # 3. Status Badge
        badge_box = Box(v_align="center", h_align="end")
        if is_active:
            active_badge = Label(
                label="Active",
                style="font-size: 11px; font-weight: 600; padding: 3px 8px; border-radius: 6px; background-color: var(--primary); color: var(--on_primary);",
            )
            badge_box.add(active_badge)
        else:
            switch_icon = Icon(icon_name="caret-right-duotone", icon_size=16)
            badge_box.add(switch_icon)

        row = Box(
            orientation="h",
            spacing=12,
            h_align="fill",
            v_align="center",
            children=[thumb_box, text_col, badge_box],
        )

        classes = ["suits-popup-card", "menu-device-item"]
        if is_active:
            classes.append("active")

        super().__init__(
            child=row,
            style_classes=classes,
            on_clicked=lambda *_: self._clicked(),
        )

    def _clicked(self):
        self._on_select(self.suite_id)


class SuitsApplet(Applet):
    def __init__(self, parent=None, **kwargs):
        self._parent = parent

        # Header action buttons
        self._add_btn = Button(
            style_classes=["applet-misc-button"],
            child=Icon(icon_name="plus", icon_size=16),
            tooltip_text="Create New Desktop",
            on_clicked=lambda *_: self._on_add_clicked(),
        )

        self._dash_btn = Button(
            style_classes=["applet-misc-button"],
            child=Icon(icon_name="diamonds-four-duotone", icon_size=16),
            tooltip_text="Open in Dash",
            on_clicked=lambda *_: self._open_dash(),
        )

        self._cards_box = Box(
            orientation="v",
            spacing=6,
            h_expand=True,
            style="padding: 4px 0;",
        )

        self._scroll = ScrolledWindow(
            min_content_height=220,
            max_content_height=360,
            h_expand=True,
            v_expand=True,
            child=self._cards_box,
        )

        content = Box(
            orientation="v",
            spacing=8,
            children=[self._scroll],
        )

        header_actions = Box(
            orientation="h",
            spacing=4,
            children=[self._add_btn, self._dash_btn],
        )

        page = AppletPage(
            first=True,
            title="Desktop Suits",
            header_right_children=header_actions,
            child=content,
        )

        super().__init__(main_menu=page, **kwargs)

        self._refresh()

        suits_service.connect("active-changed", lambda *_: self._refresh())
        suits_service.connect("suites-changed", lambda *_: self._refresh())

    def _refresh(self):
        for child in self._cards_box.get_children():
            self._cards_box.remove(child)

        active_id = suits_service.active_id
        for suite in suits_service.suites:
            is_active = (suite.get("id") == active_id)
            card = SuitsPopupCard(suite, is_active, on_select=self._on_suite_selected)
            self._cards_box.add(card)

        self._cards_box.show_all()

    def _on_suite_selected(self, suite_id: str):
        if self._parent and hasattr(self._parent, "toggle"):
            self._parent.toggle()
        def _do_switch():
            suits_service.switch_suite(suite_id)
            return GLib.SOURCE_REMOVE
        GLib.timeout_add(120, _do_switch)

    def _on_add_clicked(self):
        new_suite = suits_service.create_suite(clone_active=True)
        if self._parent and hasattr(self._parent, "toggle"):
            self._parent.toggle()
        def _do_switch():
            suits_service.switch_suite(new_suite["id"])
            return GLib.SOURCE_REMOVE
        GLib.timeout_add(120, _do_switch)

    def _open_dash(self):
        if self._parent and hasattr(self._parent, "toggle"):
            self._parent.toggle()
        import services.singletons as singletons
        if singletons.bar_manager and singletons.bar_manager._dash:
            singletons.bar_manager._dash.toggle_suits(None)
