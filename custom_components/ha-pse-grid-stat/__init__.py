"""The PSE Grid Stat integration."""
from __future__ import annotations
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import CoreState, HomeAssistant

from .const import (
    BASE_API_URL,
    DOMAIN,
    PSE_GRID_SERVICE,
    DEFAULT_SCAN_INTERVAL,
    PLATFORMS,
)

from homeassistant.const import CONF_SCAN_INTERVAL, EVENT_HOMEASSISTANT_STARTED
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
import urllib.request
import json

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up the PSE Grid Stat component."""
    coordinator = PseGridNetDataUpdater(hass, config_entry)
    await coordinator.async_setup()

    async def _enable_scheduled_pse_download(*_):
        """Activate the data update coordinator."""
        coordinator.update_interval = timedelta(
            minutes=config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        )
        await coordinator.async_refresh()

    if hass.state == CoreState.running:
        await _enable_scheduled_pse_download()
    else:
        hass.bus.async_listen_once(
            EVENT_HOMEASSISTANT_STARTED, _enable_scheduled_pse_download
        )

    hass.data[DOMAIN] = coordinator

    hass.config_entries.async_setup_platforms(config_entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload PSE Grid Stat Entry from config_entry."""
    hass.services.async_remove(DOMAIN, PSE_GRID_SERVICE)

    unload_ok = await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    )
    if unload_ok:
        hass.data.pop(DOMAIN)
    return unload_ok


class PseGridNetDataUpdater(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        self._hass = hass
        self.data_available = False
        self.json_output = None
        self.countries_link = {"": ""}
        self.config_entry: ConfigEntry = config_entry
        super().__init__(
            self._hass,
            _LOGGER,
            name=DOMAIN,
            update_method=self.async_update,
        )

    def _update_data(self):
        with urllib.request.urlopen(BASE_API_URL) as url:
            self.json_output = json.loads(url.read().decode())
            countries = self.json_output["data"]["przesyly"]
            for country in countries:
                self.countries_link[country["id"]] = country
            self.data_available = True

    async def async_update(self) -> dict[str, str]:
        """Update PSE Grid Stats data."""
        return await self._hass.async_add_executor_job(self._update_data)

    async def async_setup(self) -> None:
        await self._hass.async_add_executor_job(self._update_data)

        async def request_update(call):
            """Request update."""
            await self.async_request_refresh()

        self.hass.services.async_register(DOMAIN, PSE_GRID_SERVICE, request_update)

        self.config_entry.async_on_unload(
            self.config_entry.add_update_listener(options_updated_listener)
        )


async def options_updated_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""

    hass.data[DOMAIN].update_interval = timedelta(
        minutes=entry.options[CONF_SCAN_INTERVAL]
    )
    await hass.data[DOMAIN].async_request_refresh()
