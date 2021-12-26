from typing import Final

from homeassistant.const import Platform

DOMAIN = "ha-pse-grid-stat"

BASE_API_URL = "https://www.pse.pl/transmissionMapService"
LINK_COUNTRIES = {"SE", "DE", "CZ", "SK", "UA", "LT"}

DEFAULT_NAME: Final = "PSE Grid Statistics"
DEFAULT_SCAN_INTERVAL: Final = 60

PSE_GRID_SERVICE: Final = "PSEGridService"

ATTRIBUTION: Final = "Statistic retrieved from PSE state page"

PLATFORMS: Final = [Platform.SENSOR]
