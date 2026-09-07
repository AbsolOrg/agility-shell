from __future__ import annotations
import os
import math
import cairo
from fabric.widgets.box import Box
from fabric.widgets.button import Button
from fabric.widgets.label import Label
from fabric.widgets.entry import Entry
from fabric.widgets.grid import Grid
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib
from snippets import Icon, ClippingScrolledWindow
from services.suits_service import suits_service
from windows.suits import get_wallpaper_pixbuf
from utils.sounds import play_sound
from user_options import user_options


class DashSuiteCard(Box):
    def __init__(self, suite: dict, is_active: bool, on_switch, on_duplicate, on_delete, on_rename):
        self.suite = suite
        self.suite_id = suite.get("id", "")
        self.is_active = is_active
        self._on_switch = on_switch
        self._on_duplicate = on_duplicate
        self._on_delete = on_delete
        self._on_rename = on_rename

        self._editing_name = False

        cfg = suite.get("config", {})
        wp_cfg = cfg.get("wallpaper", {})
        wp_path = wp_cfg.get("path", "")
        theme_cfg = cfg.get("theme", {})
        bars_cfg = cfg.get("bars", [])
        canvas_cfg = cfg.get("desktop_canvas", {})
        qs_cfg = cfg.get("quickshell_widgets", {})

        # Count widgets
        total_bar_widgets = 0
        for m in bars_cfg:
            for b in m.get("bars", []):
                total_bar_widgets += len(b.get("left", [])) + len(b.get("center", [])) + len(b.get("right", []))
        total_canvas = sum(len(items) for items in canvas_cfg.values()) if isinstance(canvas_cfg, dict) else 0

        qs_enabled = qs_cfg.get("enabled", False)
        qs_settings = qs_cfg.get("settings", {})
        qs_vis = qs_settings.get("manager", {}).get("visibility", {})
        active_qs_count = sum(1 for v in qs_vis.values() if v) if (qs_enabled and isinstance(qs_vis, dict)) else 0
        qs_badge_str = f"{active_qs_count} widgets" if qs_enabled else "Widgets Off"

        theme_name = (theme_cfg.get("dark_theme") if theme_cfg.get("is_dark", True) else theme_cfg.get("light_theme")) or "Default"
        is_dark = theme_cfg.get("is_dark", True)
        mode_str = "Dark" if is_dark else "Light"

        # --- 1. Header (Title/Subtitle + 3-dots Menu) ---
        name_str = suite.get("name", "Desktop")

        self._name_label = Label(
            label=name_str,
            style="font-size: 14.5px; font-weight: 700;",
            h_align="start",
        )
        self._name_entry = Entry(
            text=name_str,
            style="font-size: 13.5px; min-width: 140px; padding: 2px 6px; border-radius: 6px;",
            visible=False,
        )
        self._name_entry.connect("activate", self._commit_rename)
        self._name_entry.connect("focus-out-event", lambda *_: self._commit_rename())

        self._desc_label = Label(
            label=f"{theme_name} • {mode_str} Mode",
            style="font-size: 11px; opacity: 0.65;",
            h_align="start",
        )

        titles_box = Box(
            orientation="v",
            spacing=1,
            h_align="start",
            h_expand=True,
            children=[self._name_label, self._name_entry, self._desc_label],
        )

        menu_btn = Button(
            style_classes=["dash-suite-icon-btn"],
            child=Icon(icon_name="dots-three-vertical-duotone", icon_size=17),
            tooltip_text="More options",
            on_clicked=lambda _btn: self._show_menu(_btn),
        )

        header_row = Box(
            orientation="h",
            spacing=10,
            h_align="fill",
            v_align="center",
            style="padding: 12px 14px 8px 14px;",
            children=[titles_box, menu_btn],
        )

        # --- 2. Wallpaper Preview Banner with Rounded Mask & Badges ---
        pixbuf = get_wallpaper_pixbuf(wp_path, 320, 160)
        if pixbuf:
            img = Gtk.Image.new_from_pixbuf(pixbuf)
        else:
            img = Box(
                style="min-width: 310px; min-height: 150px; background-color: var(--surface_container_high);",
                v_align="center",
                h_align="center",
                children=[Icon(icon_name="image-duotone", icon_size=36)],
            )

        # Mini widget silhouette canvas
        widgets_to_draw = []
        if qs_enabled and isinstance(qs_settings, dict):
            for w_key, w_val in qs_settings.items():
                if w_key == "manager" or not isinstance(w_val, dict):
                    continue
                if qs_vis.get(w_key, True) and "x" in w_val and "y" in w_val:
                    widgets_to_draw.append({
                        "x": float(w_val.get("x", 0)),
                        "y": float(w_val.get("y", 0)),
                        "scale": float(w_val.get("scale", 1.0)),
                    })

        mini_canvas = Gtk.DrawingArea()
        mini_canvas.set_size_request(310, 150)

        def _draw_silhouettes(_da, cr):
            sx = 310.0 / 1920.0
            sy = 150.0 / 1080.0
            for w_info in widgets_to_draw:
                mx = max(6.0, min(270.0, w_info["x"] * sx))
                my = max(6.0, min(120.0, w_info["y"] * sy))
                mw = max(18.0, min(65.0, 180.0 * w_info["scale"] * sx))
                mh = max(12.0, min(42.0, 120.0 * w_info["scale"] * sy))

                cr.save()
                r = 3.0
                cr.new_sub_path()
                cr.arc(mx + mw - r, my + r, r, -math.pi / 2, 0)
                cr.arc(mx + mw - r, my + mh - r, r, 0, math.pi / 2)
                cr.arc(mx + r, my + mh - r, r, math.pi / 2, math.pi)
                cr.arc(mx + r, my + r, r, math.pi, 3 * math.pi / 2)
                cr.close_path()

                cr.set_source_rgba(0.08, 0.12, 0.18, 0.60)
                cr.fill_preserve()
                cr.set_source_rgba(0.48, 0.82, 1.0, 0.75)
                cr.set_line_width(1.0)
                cr.stroke()
                cr.restore()

        mini_canvas.connect("draw", _draw_silhouettes)

        thumb_overlay = Gtk.Overlay()
        thumb_overlay.add(img)
        thumb_overlay.add_overlay(mini_canvas)

        img_container = Box(
            style_classes=["dash-suite-thumb"],
            style="min-width: 310px; min-height: 150px; border-radius: 10px;",
            children=[thumb_overlay],
        )

        top_badges_left = Box(
            orientation="h",
            spacing=6,
            h_align="start",
            v_align="start",
            style="margin: 8px;",
            children=[
                Label(
                    label=f"{total_bar_widgets} bar • {total_canvas} canvas • {qs_badge_str}",
                    style="font-size: 10px; font-weight: 600; padding: 3px 8px; border-radius: 6px; background-color: rgba(0,0,0,0.68); color: #ffffff;",
                )
            ],
        )

        top_badges_right = Box(
            orientation="h",
            spacing=6,
            h_align="end",
            v_align="start",
            style="margin: 8px;",
        )
        if is_active:
            top_badges_right.add(
                Label(
                    label="ACTIVE",
                    style="font-size: 10px; font-weight: 800; padding: 4px 10px; border-radius: 8px; background-color: var(--primary); color: var(--on_primary); letter-spacing: 0.5px;",
                )
            )

        overlay_header = Box(
            orientation="h",
            h_align="fill",
            h_expand=True,
            children=[top_badges_left, Box(h_expand=True), top_badges_right],
        )

        banner_box = Box(
            orientation="v",
            h_align="fill",
            h_expand=True,
            style="padding: 0 12px;",
            children=[overlay_header, img_container],
        )

        # --- 3. Footer Row with Apply / Active Button ---
        footer_info = Label(
            label="Preset Layout",
            style="font-size: 11px; opacity: 0.55; font-weight: 500;",
            h_align="start",
            v_align="center",
        )

        if is_active:
            main_action = Button(
                style_classes=["dash-suite-apply-btn", "active"],
                child=Box(
                    orientation="h",
                    spacing=6,
                    children=[
                        Icon(icon_name="check-circle-duotone", icon_size=15),
                        Label(label="Active", style="font-size: 12px; font-weight: 600;"),
                    ],
                ),
            )
            main_action.set_sensitive(False)
        else:
            main_action = Button(
                style_classes=["dash-suite-apply-btn"],
                child=Box(
                    orientation="h",
                    spacing=6,
                    children=[
                        Icon(icon_name="sparkle-duotone", icon_size=15),
                        Label(label="Apply", style="font-size: 12px; font-weight: 600;"),
                    ],
                ),
                tooltip_text=f"Switch to {name_str}",
                on_clicked=lambda *_: self._on_switch(self.suite_id),
            )

        footer_row = Box(
            orientation="h",
            spacing=8,
            h_align="fill",
            v_align="center",
            style="padding: 10px 14px 14px 14px;",
            children=[footer_info, Box(h_expand=True), main_action],
        )

        classes = ["dash-suite-card"]
        if is_active:
            classes.append("active")

        super().__init__(
            orientation="v",
            spacing=4,
            style_classes=classes,
            style="min-width: 320px; border-radius: 16px; background-color: alpha(var(--surface_container_lowest), 0.88);",
            children=[
                header_row,
                banner_box,
                footer_row,
            ],
        )

    def _show_menu(self, btn):
        menu = Gtk.Menu()
        menu.set_reserve_toggle_size(False)

        rename_item = Gtk.MenuItem()
        rename_box = Box(orientation="h", spacing=8)
        rename_box.add(Icon(icon_name="pencil-simple-duotone", icon_size=15))
        rename_box.add(Label(label="Rename Desktop"))
        rename_item.add(rename_box)
        rename_item.connect("activate", lambda *_: self._start_rename())
        menu.append(rename_item)

        dup_item = Gtk.MenuItem()
        dup_box = Box(orientation="h", spacing=8)
        dup_box.add(Icon(icon_name="copy-duotone", icon_size=15))
        dup_box.add(Label(label="Duplicate Desktop"))
        dup_item.add(dup_box)
        dup_item.connect("activate", lambda *_: self._on_duplicate(self.suite_id))
        menu.append(dup_item)

        export_item = Gtk.MenuItem()
        export_box = Box(orientation="h", spacing=8)
        export_box.add(Icon(icon_name="arrow-square-out-duotone", icon_size=15))
        export_box.add(Label(label="Export Preset"))
        export_item.add(export_box)
        export_item.connect("activate", lambda *_: self._export_desktop())
        menu.append(export_item)

        sep = Gtk.SeparatorMenuItem()
        menu.append(sep)

        del_item = Gtk.MenuItem()
        del_box = Box(orientation="h", spacing=8)
        del_box.add(Icon(icon_name="trash-duotone", icon_size=15))
        del_box.add(Label(label="Delete Desktop"))
        del_item.add(del_box)
        if len(suits_service.suites) <= 1:
            del_item.set_sensitive(False)
        else:
            del_item.connect("activate", lambda *_: self._on_delete(self.suite_id))
        menu.append(del_item)

        menu.show_all()
        try:
            menu.popup_at_widget(btn, Gdk.Gravity.SOUTH_END, Gdk.Gravity.NORTH_END, None)
        except Exception:
            menu.popup(None, None, None, None, 0, Gtk.get_current_event_time())

    def _export_desktop(self):
        dialog = Gtk.FileChooserDialog(
            title="Export Desktop Preset",
            parent=None,
            action=Gtk.FileChooserAction.SAVE,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE, Gtk.ResponseType.OK,
        )
        clean_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in self.suite.get("name", "desktop")).lower()
        dialog.set_current_name(f"{clean_name}.suit.json")
        dialog.set_do_overwrite_confirmation(True)

        res = dialog.run()
        if res == Gtk.ResponseType.OK:
            dest = dialog.get_filename()
            dialog.destroy()
            if dest:
                if not dest.endswith(".json"):
                    dest += ".json"
                if suits_service.export_suite(self.suite_id, dest):
                    play_sound("widget-placed")
        else:
            dialog.destroy()

    def _start_rename(self):
        self._editing_name = True
        self._name_label.set_visible(False)
        self._desc_label.set_visible(False)
        self._name_entry.set_text(self.suite.get("name", "Desktop"))
        self._name_entry.set_visible(True)
        self._name_entry.grab_focus()

    def _commit_rename(self, *_):
        if not self._editing_name:
            return
        self._editing_name = False
        new_text = self._name_entry.get_text().strip()
        if new_text and new_text != self.suite.get("name"):
            self._on_rename(self.suite_id, new_text)
            self._name_label.set_label(new_text)
        self._name_entry.set_visible(False)
        self._name_label.set_visible(True)
        self._desc_label.set_visible(True)



class DashSuitsPage(Box):
    def __init__(self, dash_instance=None, **kwargs):
        self._dash = dash_instance

        # --- Top Header & Action Bar ---
        title_box = Box(
            orientation="v",
            spacing=2,
            h_align="start",
            children=[
                Label(
                    label="Desktop Suites & Presets",
                    style="font-size: 16px; font-weight: 700;",
                    h_align="start",
                ),
                Label(
                    label="Complete desktop environments: switch wallpapers, themes, bar layouts & desktop widgets instantly.",
                    style="font-size: 11.5px; opacity: 0.65;",
                    h_align="start",
                ),
            ],
        )

        self._count_badge = Label(
            label="0 Desktops",
            style="font-size: 11px; font-weight: 600; padding: 4px 10px; border-radius: 12px; background-color: var(--surface_container_high);",
        )

        self._bar_pin_icon = Icon(icon_name="plus-circle-duotone", icon_size=16)
        self._bar_pin_label = Label(label="Add Suits to Bar", style="font-size: 12.5px; font-weight: 600;")
        self._bar_pin_btn = Button(
            style_classes=["dash-suite-pin-btn"],
            child=Box(
                orientation="h",
                spacing=8,
                children=[
                    self._bar_pin_icon,
                    self._bar_pin_label,
                ],
            ),
            tooltip_text="Pin Suits preset switcher to your bar",
            on_clicked=lambda *_: self._toggle_bar_pin(),
        )

        new_suite_btn = Button(
            style_classes=["dash-suite-new-btn"],
            child=Box(
                orientation="h",
                spacing=8,
                children=[
                    Icon(icon_name="plus", icon_size=16),
                    Label(label="New Desktop", style="font-size: 12.5px; font-weight: 600;"),
                ],
            ),
            tooltip_text="Create a new desktop preset based on current configuration",
            on_clicked=lambda *_: self._create_new_desktop(),
        )

        import_suite_btn = Button(
            style_classes=["dash-suite-pin-btn"],
            child=Box(
                orientation="h",
                spacing=8,
                children=[
                    Icon(icon_name="arrow-square-in-duotone", icon_size=16),
                    Label(label="Import", style="font-size: 12.5px; font-weight: 600;"),
                ],
            ),
            tooltip_text="Import a shared desktop preset (.json)",
            on_clicked=lambda *_: self._import_desktop(),
        )

        header_bar = Box(
            orientation="h",
            spacing=12,
            h_align="fill",
            v_align="center",
            style="padding: 0 16px 12px 16px; min-width: 1080px;",
            children=[
                title_box,
                Box(h_expand=True),
                self._count_badge,
                import_suite_btn,
                self._bar_pin_btn,
                new_suite_btn,
            ],
        )

        # --- Grid Container ---
        self._grid = Grid(
            column_homogeneous=True,
            row_homogeneous=False,
            column_spacing=16,
            row_spacing=16,
            h_expand=True,
        )

        self._scroll = ClippingScrolledWindow(
            h_expand=False,
            h_align="center",
            style_classes=["dash-grid"],
            child=self._grid,
            max_content_size=(1104, 520),
            fade_distance=40,
            overlay_scroll=True,
            kinetic_scroll=True,
            h_scrollbar_policy="never",
            v_scrollbar_policy="automatic",
        )
        self._scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self._scroll.set_size_request(1104, 520)

        main_box = Box(
            orientation="v",
            spacing=12,
            h_align="center",
            v_align="center",
            children=[header_bar, self._scroll],
        )

        super().__init__(
            orientation="v",
            v_align="center",
            h_align="center",
            spacing=16,
            children=[main_box],
            **kwargs,
        )

        suits_service.connect("active-changed", lambda *_: self._refresh())
        suits_service.connect("suites-changed", lambda *_: self._refresh())
        self.connect("map", lambda *_: self._update_pin_button())

        self._refresh()

    def _is_in_bar(self) -> bool:
        for monitor_cfg in user_options.bars.configs:
            for bar_cfg in monitor_cfg.get("bars", []):
                for sec in ("left", "center", "right"):
                    for item in bar_cfg.get(sec, []):
                        if isinstance(item, str) and item == "Suits":
                            return True
                        elif isinstance(item, dict) and item.get("widget") == "Suits":
                            return True
        return False

    def _update_pin_button(self):
        in_bar = self._is_in_bar()
        ctx = self._bar_pin_btn.get_style_context()
        if in_bar:
            self._bar_pin_icon.set_property("icon-name", "check-circle-duotone")
            self._bar_pin_label.set_label("Suits in Bar")
            ctx.remove_class("dash-suite-pin-btn")
            ctx.add_class("dash-suite-pinned-btn")
            self._bar_pin_btn.set_tooltip_text("Suits is pinned to your bar. Click to unpin/remove.")
        else:
            self._bar_pin_icon.set_property("icon-name", "plus-circle-duotone")
            self._bar_pin_label.set_label("Add Suits to Bar")
            ctx.remove_class("dash-suite-pinned-btn")
            ctx.add_class("dash-suite-pin-btn")
            self._bar_pin_btn.set_tooltip_text("Pin Suits desktop preset switcher to your bar")

    def _toggle_bar_pin(self):
        in_bar = self._is_in_bar()
        if in_bar:
            for monitor_cfg in user_options.bars.configs:
                for bar_cfg in monitor_cfg.get("bars", []):
                    for sec in ("left", "center", "right"):
                        bar_cfg[sec] = [
                            w for w in bar_cfg.get(sec, [])
                            if (w if isinstance(w, str) else w.get("widget")) != "Suits"
                        ]
            user_options.save()
            play_sound("widget-removed")
        else:
            if user_options.bars.configs and user_options.bars.configs[0].get("bars"):
                bar_cfg = user_options.bars.configs[0]["bars"][0]
                right_sec = bar_cfg.setdefault("right", [])
                insert_idx = len(right_sec)
                for idx, w in enumerate(right_sec):
                    w_name = w if isinstance(w, str) else w.get("widget")
                    if w_name in ("Settings", "Session"):
                        insert_idx = idx
                        break
                right_sec.insert(insert_idx, "Suits")
                user_options.save()
                play_sound("widget-placed")

        import services.singletons as singletons
        if singletons.bar_manager and hasattr(singletons.bar_manager, "reload_bars"):
            singletons.bar_manager.reload_bars()
        self._update_pin_button()

    def _refresh(self):
        for child in self._grid.get_children():
            self._grid.remove(child)

        self._update_pin_button()

        suites = suits_service.suites
        unit = "Desktop" if len(suites) == 1 else "Desktops"
        self._count_badge.set_label(f"{len(suites)} {unit}")

        active_id = suits_service.active_id

        # Render 3 columns in grid
        cols = 3
        for idx, suite in enumerate(suites):
            is_active = (suite.get("id") == active_id)
            card = DashSuiteCard(
                suite,
                is_active=is_active,
                on_switch=self._switch_suite,
                on_duplicate=self._duplicate_suite,
                on_delete=self._delete_suite,
                on_rename=self._rename_suite,
            )
            col = idx % cols
            row = idx // cols
            self._grid.attach(card, col, row, 1, 1)

        self._grid.show_all()

    def _create_new_desktop(self):
        new_suite = suits_service.create_suite(clone_active=True)
        play_sound("desktop-switch")
        self._refresh()

    def _import_desktop(self):
        dialog = Gtk.FileChooserDialog(
            title="Import Desktop Preset",
            parent=None,
            action=Gtk.FileChooserAction.OPEN,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK,
        )
        filter_json = Gtk.FileFilter()
        filter_json.set_name("Suit JSON Files (*.json)")
        filter_json.add_pattern("*.json")
        dialog.add_filter(filter_json)

        filter_all = Gtk.FileFilter()
        filter_all.set_name("All Files")
        filter_all.add_pattern("*")
        dialog.add_filter(filter_all)

        res = dialog.run()
        if res == Gtk.ResponseType.OK:
            src = dialog.get_filename()
            dialog.destroy()
            if src:
                imported = suits_service.import_suite(src)
                if imported:
                    play_sound("widget-placed")
                    self._refresh()
        else:
            dialog.destroy()

    def _switch_suite(self, suite_id: str):
        if self._dash and hasattr(self._dash, "toggle"):
            self._dash.toggle()
        def _do_switch():
            suits_service.switch_suite(suite_id)
            return GLib.SOURCE_REMOVE
        GLib.timeout_add(160, _do_switch)

    def _duplicate_suite(self, suite_id: str):
        suits_service.duplicate_suite(suite_id)
        self._refresh()

    def _delete_suite(self, suite_id: str):
        suits_service.delete_suite(suite_id)
        self._refresh()

    def _rename_suite(self, suite_id: str, new_name: str):
        suits_service.rename_suite(suite_id, new_name)
