"""Constants for ha_aftership."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

# Integration metadata
DOMAIN = "ha_aftership"
ATTRIBUTION = "Data provided by aftership.com"
CONF_NAME = "name"
CONF_API_KEY = "api_key"

# Platform parallel updates - applied to all platforms
PARALLEL_UPDATES = 1

# Default configuration values
DEFAULT_UPDATE_INTERVAL_HOURS = 1
DEFAULT_ENABLE_DEBUGGING = False
