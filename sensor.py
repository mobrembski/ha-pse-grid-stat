"""GitHub sensor platform."""
import datetime
import logging
import re
from datetime import date, datetime, timedelta, timezone
from typing import Any, Callable, Dict, Optional
from urllib import parse
import urllib.request, json
from homeassistant import config_entries, core
from homeassistant.helpers.device_registry import DeviceEntryType
from . import PseGridNetDataUpdater
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import Throttle

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
    StateType,
)

try:
    from homeassistant.components.binary_sensor import BinarySensorEntity
except ImportError:
    from homeassistant.components.binary_sensor import (
        BinarySensorDevice as BinarySensorEntity,
    )

from .const import DOMAIN, LINK_COUNTRIES


SCAN_INTERVAL = timedelta(minutes=1)

DEFAULT_SCAN_INTERVAL = timedelta(minutes=5)


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Setup sensors from a config entry created in the integrations UI."""
    # config = hass.data[DOMAIN][config_entry.entry_id]
    # # Update our config to include new repos and remove those that have been removed.
    # if config_entry.options:
    #     config.update(config_entry.options)
    coordinator = hass.data[DOMAIN]
    sensors = [
        RequiredPowerPSEEntity(coordinator),
        GeneratedPowerPSEEntity(coordinator),
        PowerStatePSEEntity(coordinator),
        PowerStatePSEEntityDescr(coordinator),
        PowerStatePSEBinaryEntity(coordinator),
        PowerWaterProductionPSEEntity(coordinator),
        PowerWindProductionPSEEntity(coordinator),
        PowerPVProductionPSEEntity(coordinator),
        PowerCoalProductionPSEEntity(coordinator),
        PowerOtherProductionPSEEntity(coordinator),
    ]
    for country in LINK_COUNTRIES:
        sensors.append(CountryLinkPSEEntity(coordinator, country))
    async_add_entities(sensors, update_before_add=True)


class BaseSensorPSEEntity(CoordinatorEntity, SensorEntity):
    """Representation of a RequiredPowerPSEEntity."""

    coordinator: PseGridNetDataUpdater

    def __init__(
        self, coordinator: PseGridNetDataUpdater, entity_description, name
    ) -> None:
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.entity_description = entity_description
        self._attr_name = entity_description.name
        self._attr_unique_id = entity_description.key
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            name="PSE Grid",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://www.speedtest.net/",
        )
        self._name = name
        self._state = None
        self._available = False

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        self._available = self.coordinator.data_available
        return self._available

    @property
    def native_value(self):
        return self.coordinator.json_output["data"]["podsumowanie"]["zapotrzebowanie"]

    async def async_update(self):
        await self.coordinator.async_update()


class CountryLinkPSEEntity(BaseSensorPSEEntity):
    """Representation of a RequiredPowerPSEEntity."""

    def __init__(self, updater, country):
        super().__init__(
            updater,
            SensorEntityDescription(
                key="pse-link-" + country,
                name="PSE Grid Link with " + country,
                native_unit_of_measurement="MW",
                state_class=SensorStateClass.MEASUREMENT,
            ),
            "PSE Grid Link with " + country,
        )
        self.country = country
        self.attrs: Dict[str, Any] = {
            "parallel": "",
            "plan": "",
            "value": "",
        }

    @property
    def icon(self):
        return "mdi:transmission-tower"

    @property
    def native_value(self):
        self.attrs = {
            "parallel": self.coordinator.countries_link[self.country]["rownolegly"],
            "plan": self.coordinator.countries_link[self.country]["wartosc_plan"],
            "value": self.coordinator.countries_link[self.country]["wartosc"],
        }
        return self.coordinator.countries_link[self.country]["wartosc"]


class RequiredPowerPSEEntity(BaseSensorPSEEntity):
    """Representation of a RequiredPowerPSEEntity."""

    def __init__(self, updater):
        super().__init__(
            updater,
            SensorEntityDescription(
                key="pse-required-power",
                name="PSE Grid Poland Power Consumption",
                native_unit_of_measurement="MW",
                state_class=SensorStateClass.MEASUREMENT,
            ),
            "PSE Grid Poland Power Required",
        )

    @property
    def icon(self):
        return "mdi:transmission-tower-import"

    @property
    def native_value(self):
        return self.coordinator.json_output["data"]["podsumowanie"]["zapotrzebowanie"]


class GeneratedPowerPSEEntity(BaseSensorPSEEntity):
    """Representation of a GeneratedPowerPSEEntity."""

    def __init__(self, updater):
        super().__init__(
            updater,
            SensorEntityDescription(
                key="pse-generated-power",
                name="PSE Grid Poland Power Generation",
                native_unit_of_measurement="MW",
                state_class=SensorStateClass.MEASUREMENT,
            ),
            "PSE Grid Poland Power Generation",
        )

    @property
    def icon(self):
        return "mdi:transmission-tower-export"

    @property
    def native_value(self):
        return self.coordinator.json_output["data"]["podsumowanie"]["generacja"]


class PowerStatePSEEntity(BaseSensorPSEEntity):
    """Representation of a PowerStatePSEEntity."""

    def __init__(self, updater):
        super().__init__(
            updater,
            SensorEntityDescription(
                key="pse-power-difference",
                name="PSE Grid Power Demand/Required Difference",
                native_unit_of_measurement="MW",
                state_class=SensorStateClass.MEASUREMENT,
            ),
            "PSE Grid Power Demand/Required Difference",
        )

    @property
    def icon(self):
        return "mdi:transmission-tower"

    @property
    def native_value(self):
        difference = int(
            self.coordinator.json_output["data"]["podsumowanie"]["generacja"]
        ) - int(self.coordinator.json_output["data"]["podsumowanie"]["zapotrzebowanie"])
        return str(difference)


class PowerWaterProductionPSEEntity(BaseSensorPSEEntity):
    """Representation of a PowerWaterProductionPSEEntity."""

    def __init__(self, updater):
        super().__init__(
            updater,
            SensorEntityDescription(
                key="pse-power-production-water",
                name="PSE Grid Power Power production by Water",
                native_unit_of_measurement="MW",
                state_class=SensorStateClass.MEASUREMENT,
            ),
            "PSE Grid Power Power production by Water",
        )

    @property
    def icon(self):
        return "mdi:hydro-power"

    @property
    def native_value(self):
        return self.coordinator.json_output["data"]["podsumowanie"]["wodne"]


class PowerWindProductionPSEEntity(BaseSensorPSEEntity):
    """Representation of a PowerWindProductionPSEEntity."""

    def __init__(self, updater):
        super().__init__(
            updater,
            SensorEntityDescription(
                key="pse-power-production-wind",
                name="PSE Grid Power Power production by Wind",
                native_unit_of_measurement="MW",
                state_class=SensorStateClass.MEASUREMENT,
            ),
            "PSE Grid Power Power production by Wind",
        )

    @property
    def icon(self):
        return "mdi:wind-turbine"

    @property
    def native_value(self):
        return self.coordinator.json_output["data"]["podsumowanie"]["wiatrowe"]


class PowerPVProductionPSEEntity(BaseSensorPSEEntity):
    """Representation of a PowerPVProductionPSEEntity."""

    def __init__(self, updater):
        super().__init__(
            updater,
            SensorEntityDescription(
                key="pse-power-production-pv",
                name="PSE Grid Power Power production by Solar panels",
                native_unit_of_measurement="MW",
                state_class=SensorStateClass.MEASUREMENT,
            ),
            "PSE Grid Power Power production by Solar panels",
        )

    @property
    def icon(self):
        return "mdi:solar-power"

    @property
    def native_value(self):
        return self.coordinator.json_output["data"]["podsumowanie"]["PV"]


class PowerCoalProductionPSEEntity(BaseSensorPSEEntity):
    """Representation of a PowerCoalProductionPSEEntity."""

    def __init__(self, updater):
        super().__init__(
            updater,
            SensorEntityDescription(
                key="pse-power-production-coal",
                name="PSE Grid Power Power production by Coal",
                native_unit_of_measurement="MW",
                state_class=SensorStateClass.MEASUREMENT,
            ),
            "PSE Grid Power Power production by Coal",
        )

    @property
    def icon(self):
        return "mdi:transmission-tower-export"

    @property
    def native_value(self):
        return self.coordinator.json_output["data"]["podsumowanie"]["cieplne"]


class PowerOtherProductionPSEEntity(BaseSensorPSEEntity):
    """Representation of a PowerCoalProductionPSEEntity."""

    def __init__(self, updater):
        super().__init__(
            updater,
            SensorEntityDescription(
                key="pse-power-production-other",
                name="PSE Grid Power Power production by Other sources",
                native_unit_of_measurement="MW",
                state_class=SensorStateClass.MEASUREMENT,
            ),
            "PSE Grid Power Power production by Other sources",
        )

    @property
    def icon(self):
        return "mdi:transmission-tower-export"

    @property
    def native_value(self):
        return self.coordinator.json_output["data"]["podsumowanie"]["inne"]


class PowerStatePSEEntityDescr(CoordinatorEntity, BinarySensorEntity):
    """Representation of a PowerStatePSEEntityDescr."""

    def __init__(self, coordinator: PseGridNetDataUpdater) -> None:
        super().__init__(coordinator)
        self._name = "PSE Grid Power Exporting State Value"
        self._state = None
        self._available = False
        self.entity_description = SensorEntityDescription(
            key="pse-power-state-description",
            name="PSE Grid Power State Description",
            state_class=SensorStateClass.MEASUREMENT,
        )
        self._attr_name = self.entity_description.name
        self._attr_unique_id = self.entity_description.key
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            name="PSE Grid",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://www.speedtest.net/",
        )

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        self._available = self.coordinator.data_available
        return self._available

    @property
    def icon(self):
        return "mdi:transmission-tower-export"

    @property
    def state(self):
        difference = int(
            self.coordinator.json_output["data"]["podsumowanie"]["generacja"]
        ) - int(self.coordinator.json_output["data"]["podsumowanie"]["zapotrzebowanie"])
        self._attr_state = "Exporting" if difference > 0 else "Importing"
        return self._attr_state

    async def async_update(self):
        await self.coordinator.async_update()


class PowerStatePSEBinaryEntity(CoordinatorEntity, BinarySensorEntity):
    """Representation of a PowerStatePSEBinaryEntity."""

    def __init__(self, coordinator: PseGridNetDataUpdater) -> None:
        super().__init__(coordinator)
        self._name = "PSE Grid Power Exporting State"
        self._state = None
        self._available = False
        self.entity_description = SensorEntityDescription(
            key="pse-power-state-binary",
            name="PSE Grid Power State Binary sensor",
            state_class=SensorStateClass.MEASUREMENT,
        )
        self._attr_name = self.entity_description.name
        self._attr_unique_id = self.entity_description.key
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            name="PSE Grid",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://www.speedtest.net/",
        )

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        self._available = self.coordinator.data_available
        return self._available

    @property
    def icon(self):
        return "mdi:transmission-tower-export"

    @property
    def is_on(self):
        difference = int(
            self.coordinator.json_output["data"]["podsumowanie"]["generacja"]
        ) - int(self.coordinator.json_output["data"]["podsumowanie"]["zapotrzebowanie"])
        return difference > 0

    async def async_update(self):
        await self.coordinator.async_update()
