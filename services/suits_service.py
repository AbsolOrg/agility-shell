import os
import json
import time
import copy
from loguru import logger
from fabric.core.service import Service, Signal, Property
from gi.repository import GLib, Gdk
from user_options import user_options
from utils.sounds import play_sound

SUITS_CONFIG_DIR = os.path.expanduser("~/.config/agility-shell/config")
SUITS_FILE = os.path.join(SUITS_CONFIG_DIR, "suits.json")


class SuitsService(Service):
    _instance: "SuitsService | None" = None

    @staticmethod
    def get_instance() -> "SuitsService":
        if SuitsService._instance is None:
            SuitsService._instance = SuitsService()
        return SuitsService._instance

    @Signal
    def active_changed(self, suite_id: str) -> None: ...

    @Signal
    def suites_changed(self) -> None: ...

    @Signal
    def switching_started(self, from_id: str, to_id: str) -> None: ...

    @Signal
    def switching_finished(self, suite_id: str) -> None: ...

    @Property(str, "read-write", default_value="")
    def active_id(self) -> str:
        return self._active_id

    @active_id.setter
    def active_id(self, value: str):
        self._active_id = value

    @Property(object, "read-write")
    def suites(self) -> list[dict]:
        return self._suites

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._active_id: str = "desktop-1"
        self._suites: list[dict] = []
        self._is_applying: bool = False
        self._is_switching: bool = False

        self._load()

        # Register callback on user_options so runtime adjustments auto-sync to active preset
        user_options.register_save_callback(self.sync_from_current)
        GLib.idle_add(self._setup_wallpaper_listener)

    def _capture_current(self) -> dict:
        """Create a deep-copy snapshot of all customizable visual shell state."""
        return {
            "bars": copy.deepcopy(user_options.bars.configs),
            "desktop_canvas": copy.deepcopy(user_options.desktop_canvas.placements),
            "desktop_applets": copy.deepcopy(user_options.desktop_applets.applets),
            "wallpaper": {
                "path": user_options.wallpaper.path,
                "transition_type": getattr(user_options.wallpaper, "transition_type", "random"),
                "transition_duration": getattr(user_options.wallpaper, "transition_duration", 1.5),
                "transition_speed": getattr(user_options.wallpaper, "transition_speed", "medium"),
                "transition_fps": getattr(user_options.wallpaper, "transition_fps", 60),
                "enabled_transitions": copy.deepcopy(getattr(user_options.wallpaper, "enabled_transitions", [])),
                "custom_transitions": copy.deepcopy(getattr(user_options.wallpaper, "custom_transitions", [])),
                "switcher_style": getattr(user_options.wallpaper, "switcher_style", "dock"),
                "hotkey_animations": getattr(user_options.wallpaper, "hotkey_animations", True),
            },
            "theme": {
                "light_theme": user_options.theme.light_theme,
                "dark_theme": user_options.theme.dark_theme,
                "active_accent": user_options.theme.active_accent,
                "is_dark": user_options.theme.is_dark,
                "scheme_type": user_options.theme.scheme_type,
                "opacity": user_options.theme.opacity,
                "border_style": user_options.theme.border_style,
                "font_monospace_style": user_options.theme.font_monospace_style,
            },
            "settings": {
                "dnd": user_options.settings.dnd,
                "hover_open": user_options.settings.hover_open,
                "hover_delay": user_options.settings.hover_delay,
                "hover_widgets": copy.deepcopy(user_options.settings.hover_widgets),
                "bar_theme": getattr(user_options.settings, "bar_theme", "default"),
                "bar_blur": getattr(user_options.settings, "bar_blur", True),
                "bar_opacity": getattr(user_options.settings, "bar_opacity", 1.0),
                "widget_opacity": getattr(user_options.settings, "widget_opacity", 1.0),
                "desktop_widget_opacity": getattr(user_options.settings, "desktop_widget_opacity", 1.0),
                "dash_blur": getattr(user_options.settings, "dash_blur", True),
                "dash_dim_opacity": getattr(user_options.settings, "dash_dim_opacity", 0.6),
                "dash_card_opacity": getattr(user_options.settings, "dash_card_opacity", 1.0),
                "instant_dash": getattr(user_options.settings, "instant_dash", True),
                "awe_widgets_enabled": getattr(user_options.settings, "awe_widgets_enabled", False),
                "bluetooth_on_startup": getattr(user_options.settings, "bluetooth_on_startup", False),
                "pinned_apps": copy.deepcopy(getattr(user_options.settings, "pinned_apps", [])),
            },
            "dock": {
                "entries": copy.deepcopy(getattr(user_options.dock, "entries", [])),
            },
            "launcher": {
                "grid": getattr(user_options.launcher, "grid", False),
            },
            "templates": {
                "enabled": copy.deepcopy(getattr(user_options.templates, "enabled", [])),
            },
        }

    def _load(self) -> None:
        os.makedirs(SUITS_CONFIG_DIR, exist_ok=True)
        if os.path.isfile(SUITS_FILE):
            try:
                with open(SUITS_FILE, "r") as f:
                    data = json.load(f)
                self._suites = data.get("suites", [])
                self._active_id = data.get("active_id", "")
                if self._suites and not any(s["id"] == self._active_id for s in self._suites):
                    self._active_id = self._suites[0]["id"]
                logger.info(f"[SuitsService] loaded {len(self._suites)} suites from {SUITS_FILE}")
                return
            except Exception as e:
                logger.error(f"[SuitsService] failed to load {SUITS_FILE}: {e}")

        # If file does not exist or failed to load, seed from current user options
        logger.info("[SuitsService] initializing default Desktop 1 preset from current settings")
        initial_suite = {
            "id": "desktop-1",
            "name": "Desktop 1",
            "created_at": time.time(),
            "config": self._capture_current(),
        }
        self._suites = [initial_suite]
        self._active_id = "desktop-1"
        self._save()

    def _save(self) -> None:
        try:
            os.makedirs(SUITS_CONFIG_DIR, exist_ok=True)
            data = {
                "active_id": self._active_id,
                "suites": self._suites,
            }
            tmp = SUITS_FILE + ".tmp"
            with open(tmp, "w") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp, SUITS_FILE)
            logger.info(f"[SuitsService] saved {len(self._suites)} suites to {SUITS_FILE}")
        except Exception as e:
            logger.error(f"[SuitsService] failed to save suites: {e}")

    def _setup_wallpaper_listener(self):
        try:
            from services.wallpaper import WallpaperService
            wp = WallpaperService.get_instance()
            wp.connect("wallpaper-changed", lambda _svc, path: self._on_wallpaper_changed(path))
        except Exception as e:
            logger.debug(f"[SuitsService] deferred wallpaper service connection: {e}")
        return GLib.SOURCE_REMOVE

    def _on_wallpaper_changed(self, path: str):
        if self._is_applying or self._is_switching or not path:
            return
        active_suite = self.get_active_suite()
        if not active_suite:
            return
        active_suite.setdefault("config", {}).setdefault("wallpaper", {})["path"] = path
        self._save()
        self.suites_changed()

    def sync_from_current(self) -> None:
        """Auto-sync active preset with recent user_options changes."""
        if self._is_applying or self._is_switching:
            return
        active_suite = self.get_active_suite()
        if not active_suite:
            return
        try:
            active_suite["config"] = self._capture_current()
            self._save()
            self.suites_changed()
        except Exception as e:
            logger.error(f"[SuitsService] sync_from_current error: {e}")

    def get_active_suite(self) -> dict | None:
        return next((s for s in self._suites if s["id"] == self._active_id), None)

    def get_suite(self, suite_id: str) -> dict | None:
        return next((s for s in self._suites if s["id"] == suite_id), None)

    def _next_desktop_name(self) -> str:
        idx = 1
        existing_names = {s.get("name", "") for s in self._suites}
        while f"Desktop {idx}" in existing_names:
            idx += 1
        return f"Desktop {idx}"

    def create_suite(self, name: str | None = None, clone_active: bool = True) -> dict:
        new_id = f"desktop-{int(time.time() * 1000)}"
        new_name = name.strip() if (name and name.strip()) else self._next_desktop_name()

        if clone_active:
            active = self.get_active_suite()
            config = copy.deepcopy(active["config"]) if active else self._capture_current()
        else:
            config = self._capture_current()

        suite = {
            "id": new_id,
            "name": new_name,
            "created_at": time.time(),
            "config": config,
        }
        self._suites.append(suite)
        self._save()
        self.suites_changed()
        logger.info(f"[SuitsService] created suite '{new_name}' ({new_id})")
        return suite

    def duplicate_suite(self, suite_id: str) -> dict | None:
        source = self.get_suite(suite_id)
        if not source:
            return None
        new_id = f"desktop-{int(time.time() * 1000)}"
        new_name = f"{source.get('name', 'Desktop')} (Copy)"
        suite = {
            "id": new_id,
            "name": new_name,
            "created_at": time.time(),
            "config": copy.deepcopy(source["config"]),
        }
        self._suites.append(suite)
        self._save()
        self.suites_changed()
        logger.info(f"[SuitsService] duplicated suite '{source.get('name', 'Desktop')}' to '{new_name}'")
        return suite

    def rename_suite(self, suite_id: str, new_name: str) -> bool:
        new_name = new_name.strip()
        if not new_name:
            return False
        suite = self.get_suite(suite_id)
        if not suite:
            return False
        suite["name"] = new_name
        self._save()
        self.suites_changed()
        logger.info(f"[SuitsService] renamed suite {suite_id} to '{new_name}'")
        return True

    def delete_suite(self, suite_id: str) -> bool:
        if len(self._suites) <= 1:
            logger.warning("[SuitsService] cannot delete the only existing desktop suite")
            return False
        suite = self.get_suite(suite_id)
        if not suite:
            return False

        # If deleting the currently active suite, switch to another suite first
        if suite_id == self._active_id:
            other = next((s for s in self._suites if s["id"] != suite_id), None)
            if other:
                self.switch_suite(other["id"])

        self._suites = [s for s in self._suites if s["id"] != suite_id]
        self._save()
        self.suites_changed()
        logger.info(f"[SuitsService] deleted suite {suite_id}")
        return True

    def switch_suite(self, suite_id: str) -> bool:
        if self._is_switching:
            logger.warning(f"[SuitsService] switch already in progress, ignoring switch to {suite_id}")
            return False

        if suite_id == self._active_id:
            logger.info(f"[SuitsService] suite {suite_id} is already active")
            return True

        target_suite = self.get_suite(suite_id)
        if not target_suite:
            logger.error(f"[SuitsService] cannot switch to unknown suite {suite_id}")
            return False

        self._is_switching = True

        # First, ensure current active preset has latest state saved
        self.sync_from_current()

        prev_id = self._active_id
        target_name = target_suite.get("name", "Desktop")
        target_cfg = target_suite.get("config", {})

        logger.info(f"[SuitsService] switching from {prev_id} to {suite_id} ('{target_name}')...")
        self.switching_started(prev_id, suite_id)

        from windows.suits_transition import play_doom_melt_transition

        def _do_switch():
            self._is_applying = True
            try:
                # 1. Apply snapshot to user_options in-memory
                self._apply_snapshot_to_user_options(target_cfg)
                user_options.save()

                self._active_id = suite_id
                self._save()

                # 2. Synchronized Execution of Shell Visual Updates
                self._apply_visual_updates(target_cfg, target_name)

            except Exception as e:
                logger.error(f"[SuitsService] error applying suite {suite_id}: {e}")
            finally:
                self._is_applying = False

            self.active_changed(suite_id)
            self.suites_changed()

        def _on_finish():
            self._is_switching = False
            self.switching_finished(suite_id)

        try:
            # Trigger the vertical strip melt animation!
            play_doom_melt_transition(on_switch=_do_switch, on_finish=_on_finish)
        except Exception as e:
            self._is_switching = False
            logger.error(f"[SuitsService] transition failed: {e}")
            _do_switch()
            _on_finish()

        return True

    def _apply_snapshot_to_user_options(self, cfg: dict) -> None:
        if "bars" in cfg:
            user_options.bars.configs = copy.deepcopy(cfg["bars"])
        if "desktop_canvas" in cfg:
            user_options.desktop_canvas.placements = copy.deepcopy(cfg["desktop_canvas"])
        if "desktop_applets" in cfg:
            user_options.desktop_applets.applets = copy.deepcopy(cfg["desktop_applets"])

        if "wallpaper" in cfg:
            for k, v in cfg["wallpaper"].items():
                if hasattr(user_options.wallpaper, k):
                    setattr(user_options.wallpaper, k, copy.deepcopy(v) if isinstance(v, (list, dict)) else v)

        if "theme" in cfg:
            for k, v in cfg["theme"].items():
                if hasattr(user_options.theme, k):
                    setattr(user_options.theme, k, copy.deepcopy(v) if isinstance(v, (list, dict)) else v)

        if "settings" in cfg:
            for k, v in cfg["settings"].items():
                if hasattr(user_options.settings, k):
                    setattr(user_options.settings, k, copy.deepcopy(v) if isinstance(v, (list, dict)) else v)

        if "dock" in cfg:
            user_options.dock.entries = copy.deepcopy(cfg["dock"].get("entries", []))

        if "launcher" in cfg:
            user_options.launcher.grid = cfg["launcher"].get("grid", False)

        if "templates" in cfg:
            user_options.templates.enabled = copy.deepcopy(cfg["templates"].get("enabled", []))

    def _apply_visual_updates(self, cfg: dict, target_name: str) -> None:
        from services.singletons import bar_manager, style_service
        from services.themes import ThemeService
        from windows.dash.themes import write_border_css, write_font_css
        from services.wallpaper import WallpaperService
        from services.desktop_applets import DesktopAppletService

        # A. Apply Wallpaper (instant, under the Doom melt overlay)
        wp_cfg = cfg.get("wallpaper", {})
        wp_path = wp_cfg.get("path") or user_options.wallpaper.path
        if wp_path and os.path.exists(wp_path):
            try:
                wp_service = WallpaperService.get_instance()
                # Use transition_type="none" so awww does NOT run competing animations!
                wp_service.set_wallpaper(wp_path, transition_type="none")
            except Exception as wp_err:
                logger.error(f"[SuitsService] wallpaper transition failed: {wp_err}")

        # B. Theme & Color Transition
        try:
            theme_service = ThemeService.get_instance()
            is_dark = user_options.theme.is_dark
            theme_service.apply_dark(is_dark)

            active_theme = user_options.theme.dark_theme if is_dark else user_options.theme.light_theme
            if is_dark:
                theme_service.apply_dark_theme(active_theme)
            else:
                theme_service.apply_light_theme(active_theme)

            theme_service.apply_accent(user_options.theme.active_accent)
            write_border_css(user_options.theme.border_style)
            write_font_css(user_options.theme.font_monospace_style)
            theme_service.apply()

            if style_service:
                style_service.reload()
        except Exception as th_err:
            logger.error(f"[SuitsService] theme transition failed: {th_err}")

        # C. Desktop Canvas Applets Rebuild
        try:
            applet_service = DesktopAppletService.get_instance()
            for win in list(applet_service._windows.values()):
                win.rebuild()
            applet_service.apply_desktop_widget_opacity(user_options.settings.desktop_widget_opacity)
        except Exception as ap_err:
            logger.error(f"[SuitsService] canvas update failed: {ap_err}")

        # D. Bars Rebuild & Style Application
        try:
            if bar_manager:
                bar_manager.reload_bars()
                bar_manager.apply_bar_theme(user_options.settings.bar_theme)
                bar_manager.apply_blur(user_options.settings.bar_blur)
                bar_manager.apply_bar_opacity(user_options.settings.bar_opacity)
                bar_manager.apply_widget_opacity(user_options.settings.widget_opacity)
        except Exception as bar_err:
            logger.error(f"[SuitsService] bars update failed: {bar_err}")

        # E. OSD Notification
        try:
            if bar_manager and hasattr(bar_manager, "_osds"):
                for osd in bar_manager._osds.values():
                    if hasattr(osd, "show_suits_switch"):
                        osd.show_suits_switch(target_name)
        except Exception as osd_err:
            logger.error(f"[SuitsService] OSD notification failed: {osd_err}")

        # F. Sound feedback
        try:
            play_sound("desktop-switch")
        except Exception:
            pass

    def cycle_next_suite(self) -> None:
        if len(self._suites) <= 1:
            return
        idx = next((i for i, s in enumerate(self._suites) if s["id"] == self._active_id), -1)
        next_idx = (idx + 1) % len(self._suites)
        self.switch_suite(self._suites[next_idx]["id"])

    def cycle_prev_suite(self) -> None:
        if len(self._suites) <= 1:
            return
        idx = next((i for i, s in enumerate(self._suites) if s["id"] == self._active_id), 0)
        prev_idx = (idx - 1) % len(self._suites)
        self.switch_suite(self._suites[prev_idx]["id"])


suits_service = SuitsService.get_instance()
