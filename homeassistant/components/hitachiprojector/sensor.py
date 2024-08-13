"""Platform for media player integration."""

from __future__ import annotations

from libhitachiprojector.hitachiprojector import HitachiProjectorConnection, ReplyType

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_MAC, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import (
    ConfigEntryError,
    HomeAssistantError,
    InvalidStateError,
)
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceInfo, format_mac
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add switches for passed config_entry in HA."""

    con = config_entry.runtime_data

    # Use config MAC for unique ID for now
    mac = config_entry.data.get(CONF_MAC)
    if not mac:
        raise ConfigEntryError("invalid mac")

    async_add_entities(
        [
            HitachiProjectorFilterTimeSensor(con, mac),
            HitachiProjectorLampTimeSensor(con, mac),
        ]
    )


class HitachiProjectorBaseSensor(SensorEntity):
    """Representation of device sensor."""

    key: str
    mac: str
    name: str

    def __init__(
        self, con: HitachiProjectorConnection, mac: str, key: str, name: str
    ) -> None:
        """Initialize the media player."""
        self._con = con
        self.key = key
        self.mac = format_mac(mac)
        self.name = name

        self._attr_unique_id = f"hitachiprojector_{self.mac}_{self.key}"

        self._attr_translation_key = self.key
        self._attr_has_entity_name = True

    @property
    def device_info(self) -> DeviceInfo:
        """Information about this entity/device."""
        return {
            "connections": {(dr.CONNECTION_NETWORK_MAC, self.mac)},
            "identifiers": {(DOMAIN, self.mac)},
        }


class HitachiProjectorFilterTimeSensor(HitachiProjectorBaseSensor):
    """Representation of device sensor."""

    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.HOURS
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_suggested_display_precision = 0

    def __init__(self, con: HitachiProjectorConnection, mac: str) -> None:
        """Initialize the sensor."""
        super().__init__(con, mac, "filter_time", "Filter time")

    async def async_update(self) -> None:
        """Retrieve latest state of the device."""
        try:
            reply_type, status = await self._con.get_filter_time()
            if reply_type != ReplyType.DATA or status is None:
                raise InvalidStateError("Unexpected reply type")
            self._attr_native_value = status
            self._attr_available = True
        except (RuntimeError, HomeAssistantError):
            self._attr_available = False


class HitachiProjectorLampTimeSensor(HitachiProjectorBaseSensor):
    """Representation of device sensor."""

    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.HOURS
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_suggested_display_precision = 0

    def __init__(self, con: HitachiProjectorConnection, mac: str) -> None:
        """Initialize the sensor."""
        super().__init__(con, mac, "lamp_time", "Lamp time")

    async def async_update(self) -> None:
        """Retrieve latest state of the device."""
        try:
            reply_type, status = await self._con.get_lamp_time()
            if reply_type != ReplyType.DATA or status is None:
                raise InvalidStateError("Unexpected reply type")
            self._attr_native_value = status
            self._attr_available = True
        except (RuntimeError, HomeAssistantError):
            self._attr_available = False
