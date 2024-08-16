"""Platform for media player integration."""

from __future__ import annotations

from libhitachiprojector.hitachiprojector import ReplyType

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, InvalidStateError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import HitachiProvider
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add switches for passed config_entry in HA."""

    provider = config_entry.runtime_data

    async_add_entities(
        [
            HitachiProjectorFilterTimeSensor(provider, config_entry.entry_id),
            HitachiProjectorLampTimeSensor(provider, config_entry.entry_id),
        ]
    )


class HitachiProjectorBaseSensor(SensorEntity):
    """Representation of device sensor."""

    key: str
    entry_id: str

    def __init__(self, provider: HitachiProvider, entry_id: str, key: str) -> None:
        """Initialize the media player."""
        self.provider = provider
        self.key = key
        self.entry_id = entry_id

        self._attr_unique_id = f"hitachiprojector_{self.entry_id}_{self.key}"

        self._attr_translation_key = self.key
        self._attr_has_entity_name = True

    @property
    def device_info(self) -> DeviceInfo:
        """Information about this entity/device."""
        return {
            "identifiers": {(DOMAIN, self.entry_id)},
        }


class HitachiProjectorFilterTimeSensor(HitachiProjectorBaseSensor):
    """Representation of device sensor."""

    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.HOURS
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_suggested_display_precision = 0

    def __init__(self, provider: HitachiProvider, entry_id: str) -> None:
        """Initialize the sensor."""
        super().__init__(provider, entry_id, "filter_time")

    async def async_update(self) -> None:
        """Retrieve latest state of the device."""
        try:
            (
                reply_type,
                status,
            ) = await self.provider.hitachi_connection.get_filter_time()
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

    def __init__(self, provider: HitachiProvider, entry_id: str) -> None:
        """Initialize the sensor."""
        super().__init__(provider, entry_id, "lamp_time")

    async def async_update(self) -> None:
        """Retrieve latest state of the device."""
        try:
            reply_type, status = await self.provider.hitachi_connection.get_lamp_time()
            if reply_type != ReplyType.DATA or status is None:
                raise InvalidStateError("Unexpected reply type")
            self._attr_native_value = status
            self._attr_available = True
        except (RuntimeError, HomeAssistantError):
            self._attr_available = False
