from typing import Callable, Final
from dataclasses import dataclass
from homeassistant.components.sensor import SensorEntityDescription, SensorStateClass

from homeassistant.const import Platform

DOMAIN = "ha_pse_grid_stat"

BASE_API_URL = "https://www.pse.pl/transmissionMapService"

DEFAULT_NAME: Final = "PSE Grid Statistics"
DEFAULT_SCAN_INTERVAL: Final = 60

PSE_GRID_SERVICE: Final = "PSEGridService"

ATTRIBUTION: Final = "Statistic retrieved from PSE state page"

PLATFORMS: Final = [Platform.SENSOR]


@dataclass
class PSESensorEntityDescription(SensorEntityDescription):
    """Class describing PSE sensor entities."""

    value: Callable = round


SENSOR_TYPES: Final[tuple[PSESensorEntityDescription, ...]] = (
    PSESensorEntityDescription(
        key="pse-link-se",
        name="PSE Grid Link with SE",
        native_unit_of_measurement="MW",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower",
        value=lambda coordinator: coordinator.countries_link["SE"]["wartosc"],
    ),
    PSESensorEntityDescription(
        key="pse-link-de",
        name="PSE Grid Link with DE",
        native_unit_of_measurement="MW",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower",
        value=lambda coordinator: coordinator.countries_link["DE"]["wartosc"],
    ),
    PSESensorEntityDescription(
        key="pse-link-cz",
        name="PSE Grid Link with CZ",
        native_unit_of_measurement="MW",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower",
        value=lambda coordinator: coordinator.countries_link["CZ"]["wartosc"],
    ),
    PSESensorEntityDescription(
        key="pse-link-sk",
        name="PSE Grid Link with SK",
        native_unit_of_measurement="MW",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower",
        value=lambda coordinator: coordinator.countries_link["SK"]["wartosc"],
    ),
    PSESensorEntityDescription(
        key="pse-link-ua",
        name="PSE Grid Link with UA",
        native_unit_of_measurement="MW",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower",
        value=lambda coordinator: coordinator.countries_link["UA"]["wartosc"],
    ),
    PSESensorEntityDescription(
        key="pse-link-lt",
        name="PSE Grid Link with LT",
        native_unit_of_measurement="MW",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower",
        value=lambda coordinator: coordinator.countries_link["LT"]["wartosc"],
    ),
    PSESensorEntityDescription(
        key="pse-required-power",
        name="PSE Grid Poland Power Consumption",
        native_unit_of_measurement="MW",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower-import",
        value=lambda coordinator: coordinator.json_output["data"]["podsumowanie"][
            "zapotrzebowanie"
        ],
    ),
    PSESensorEntityDescription(
        key="pse-generated-power",
        name="PSE Grid Poland Power Generation",
        native_unit_of_measurement="MW",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower-export",
        value=lambda coordinator: coordinator.json_output["data"]["podsumowanie"][
            "generacja"
        ],
    ),
    PSESensorEntityDescription(
        key="pse-power-difference",
        name="PSE Grid Power Demand/Required Difference",
        native_unit_of_measurement="MW",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower",
        value=lambda coordinator: str(
            int(coordinator.json_output["data"]["podsumowanie"]["generacja"])
            - int(coordinator.json_output["data"]["podsumowanie"]["zapotrzebowanie"])
        ),
    ),
    PSESensorEntityDescription(
        key="pse-power-production-water",
        name="PSE Grid Power Power production by Water",
        native_unit_of_measurement="MW",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:hydro-power",
        value=lambda coordinator: coordinator.json_output["data"]["podsumowanie"][
            "wodne"
        ],
    ),
    PSESensorEntityDescription(
        key="pse-power-production-wind",
        name="PSE Grid Power Power production by Wind",
        native_unit_of_measurement="MW",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:wind-turbine",
        value=lambda coordinator: coordinator.json_output["data"]["podsumowanie"][
            "wiatrowe"
        ],
    ),
    PSESensorEntityDescription(
        key="pse-power-production-pv",
        name="PSE Grid Power Power production by Solar panels",
        native_unit_of_measurement="MW",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-power",
        value=lambda coordinator: coordinator.json_output["data"]["podsumowanie"]["PV"],
    ),
    PSESensorEntityDescription(
        key="pse-power-production-coal",
        name="PSE Grid Power Power production by Coal",
        native_unit_of_measurement="MW",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower-export",
        value=lambda coordinator: coordinator.json_output["data"]["podsumowanie"][
            "cieplne"
        ],
    ),
    PSESensorEntityDescription(
        key="pse-power-production-other",
        name="PSE Grid Power Power production by Other sources",
        native_unit_of_measurement="MW",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower-export",
        value=lambda coordinator: coordinator.json_output["data"]["podsumowanie"][
            "inne"
        ],
    ),
)
