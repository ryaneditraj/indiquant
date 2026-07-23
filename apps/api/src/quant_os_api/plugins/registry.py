"""Data / broker provider registry driven by config.yaml."""

from __future__ import annotations

from typing import Any

from quant_os_api.config import Settings, get_settings
from quant_os_api.plugins.loader import instantiate_plugin


class ProviderRegistry:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def _section(self, key: str) -> dict[str, Any]:
        raw = self.settings.yaml_config.get(key, {})
        return raw if isinstance(raw, dict) else {}

    def list_data_providers(self) -> list[dict[str, Any]]:
        section = self._section("data_providers")
        providers = section.get("providers", {})
        default = section.get("default")
        out: list[dict[str, Any]] = []
        if not isinstance(providers, dict):
            return out
        for name, cfg in providers.items():
            if not isinstance(cfg, dict):
                continue
            out.append(
                {
                    "name": name,
                    "enabled": bool(cfg.get("enabled", False)),
                    "module": cfg.get("module"),
                    "default": name == default,
                    "health": self._safe_health("data_providers", name),
                }
            )
        return out

    def get_data_provider(self, name: str | None = None) -> Any:
        section = self._section("data_providers")
        providers = section.get("providers", {})
        chosen = name or section.get("default")
        if not chosen or not isinstance(providers, dict) or chosen not in providers:
            raise KeyError(f"Unknown data provider: {chosen}")
        cfg = providers[chosen]
        if not cfg.get("enabled", False):
            raise RuntimeError(f"Data provider disabled: {chosen}")
        module = cfg.get("module")
        if not module:
            raise RuntimeError(f"No module configured for data provider: {chosen}")
        # Module path points at class: package.module.ClassName
        return instantiate_plugin(str(module))

    def _safe_health(self, section_key: str, name: str) -> dict[str, Any]:
        try:
            if section_key == "data_providers":
                provider = self.get_data_provider(name)
            else:
                return {"status": "unknown"}
            return provider.health()
        except Exception as exc:  # noqa: BLE001 — surface plugin errors to UI
            return {"status": "error", "error": str(exc)}


def get_registry() -> ProviderRegistry:
    return ProviderRegistry()
