"""PSE Grid sensor platform."""
from datetime import timedelta
from homeassistant import config_entries, core
from homeassistant.helpers.device_registry import DeviceEntryType
from . import PseGridNetDataUpdater
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.helpers.entity import DeviceInfo

try:
    from homeassistant.components.binary_sensor import BinarySensorEntity
except ImportError:
    from homeassistant.components.binary_sensor import (
        BinarySensorDevice as BinarySensorEntity,
    )

from .const import DOMAIN, SENSOR_TYPES, PSESensorEntityDescription


SCAN_INTERVAL = timedelta(minutes=1)

DEFAULT_SCAN_INTERVAL = timedelta(minutes=5)


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Setup sensors from a config entry created in the integrations UI."""
    coordinator = hass.data[DOMAIN]
    async_add_entities(
        BaseSensorPSEEntity(coordinator, description) for description in SENSOR_TYPES
    )
    sensors = [
        PowerStatePSEEntityDescr(coordinator),
        PowerStatePSEBinaryEntity(coordinator),
    ]
    async_add_entities(sensors)


class BaseSensorPSEEntity(CoordinatorEntity, SensorEntity):
    """Representation of a RequiredPowerPSEEntity."""

    coordinator: PseGridNetDataUpdater

    def __init__(
        self,
        coordinator: PseGridNetDataUpdater,
        entity_description: PSESensorEntityDescription,
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
            configuration_url="https://www.pse.pl/transmissionMapService",
        )
        self._name = entity_description.name
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
        return self.entity_description.value(self.coordinator)

    async def async_update(self):
        await self.coordinator.async_update()


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
            icon="mdi:transmission-tower-export",
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
    def available(self) -> bool:
        """Return True if entity is available."""
        self._available = self.coordinator.data_available
        return self._available

    @property
    def state(self):
        difference = int(self.coordinator.json_output["data"]["podsumowanie"]["zapotrzebowanie"])
        for direction in self.coordinator.json_output["data"]["przesyly"]:
            difference = difference - int(direction["wartosc"])
        self._attr_state = "Exporting" if difference < 0 else "Importing"
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
            icon="mdi:transmission-tower-export",
        )
        self._attr_name = self.entity_description.name
        self._attr_unique_id = self.entity_description.key
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            name="PSE Grid",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://www.pse.pl/transmissionMapService",
        )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        self._available = self.coordinator.data_available
        return self._available

    @property
    def is_on(self):
        difference = int(
            self.coordinator.json_output["data"]["podsumowanie"]["generacja"]
        ) - int(self.coordinator.json_output["data"]["podsumowanie"]["zapotrzebowanie"])
        return difference > 0

    async def async_update(self):
        await self.coordinator.async_update()
