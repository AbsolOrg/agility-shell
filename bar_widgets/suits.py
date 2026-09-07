from .base import BaseButton, VARIANT_ICON, VARIANT_ICON_LABEL, VARIANT_LABEL
from snippets import Icon
from services.suits_service import suits_service


class SuitsButton(BaseButton):
    VARIANTS = [VARIANT_ICON, VARIANT_ICON_LABEL, VARIANT_LABEL]

    def __init__(self, monitor_id, vertical, variant=None, **kwargs):
        self._icon_widget = Icon(icon_name="suits-duotone", icon_size=16)
        active_suite = suits_service.get_active_suite()
        initial_label = active_suite.get("name", "Desktop") if active_suite else "Desktop"

        super().__init__(
            icon=self._icon_widget,
            label=initial_label,
            variant=variant or VARIANT_ICON,
            **kwargs,
        )

        self.add_style_class("suits-bar-button")
        self._sync()

        suits_service.connect("active-changed", lambda *_: self._sync())
        suits_service.connect("suites-changed", lambda *_: self._sync())

    def _sync(self, *_):
        active_suite = suits_service.get_active_suite()
        name = active_suite.get("name", "Desktop") if active_suite else "Desktop"
        self._update_label(name)
        self.set_tooltip_text(f"Desktop Preset: {name}")
