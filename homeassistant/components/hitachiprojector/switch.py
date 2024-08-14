"""Platform for media player integration."""

from __future__ import annotations

from typing import Any

from libhitachiprojector.hitachiprojector import (
    AutoEcoModeStatus,
    BlankStatus,
    Command,
    EcoModeStatus,
    HitachiProjectorConnection,
    ReplyType,
    commands,
)

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, InvalidStateError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add switches for passed config_entry in HA."""

    con = config_entry.runtime_data

    async_add_entities(
        [
            HitachiProjectorBlankModeSwitch(con, config_entry.entry_id),
            HitachiProjectorEcoModeSwitch(con, config_entry.entry_id),
            HitachiProjectorAutoEcoModeSwitch(con, config_entry.entry_id),
        ]
    )


class HitachiProjectorBaseSwitch(SwitchEntity):
    """Representation of device switch."""

    key: str
    entry_id: str

    def __init__(
        self, con: HitachiProjectorConnection, entry_id: str, key: str
    ) -> None:
        """Initialize the media player."""
        self._con = con
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


class HitachiProjectorBlankModeSwitch(HitachiProjectorBaseSwitch):
    """Representation of device switch."""

    def __init__(self, con: HitachiProjectorConnection, entry_id: str) -> None:
        """Initialize the switch."""
        super().__init__(con, entry_id, "blank_mode")

    async def async_update(self) -> None:
        """Retrieve latest state of the device."""
        try:
            reply_type, status = await self._con.get_blank_status()
            if reply_type != ReplyType.DATA or status is None:
                raise InvalidStateError("Unexpected reply type")
            self._attr_is_on = status == BlankStatus.On
            self._attr_available = True
        except (RuntimeError, HomeAssistantError):
            self._attr_available = False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn switch on."""
        reply_type, _ = await self._con.async_send_cmd(commands[Command.BlankOn])
        if reply_type != ReplyType.ACK:
            raise InvalidStateError("Unexpected reply type")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn switch off."""
        reply_type, _ = await self._con.async_send_cmd(commands[Command.BlankOff])
        if reply_type != ReplyType.ACK:
            raise InvalidStateError("Unexpected reply type")


class HitachiProjectorEcoModeSwitch(HitachiProjectorBaseSwitch):
    """Representation of device switch."""

    def __init__(self, con: HitachiProjectorConnection, entry_id: str) -> None:
        """Initialize the switch."""
        super().__init__(con, entry_id, "eco_mode")

    async def async_update(self) -> None:
        """Retrieve latest state of the device."""
        try:
            reply_type, status = await self._con.get_eco_mode_status()
            if reply_type != ReplyType.DATA or status is None:
                raise InvalidStateError("Unexpected reply type")
            self._attr_is_on = status == EcoModeStatus.Eco
            self._attr_available = True
        except (RuntimeError, HomeAssistantError):
            self._attr_available = False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn switch on."""
        reply_type, _ = await self._con.async_send_cmd(commands[Command.EcoModeEco])
        if reply_type != ReplyType.ACK:
            raise InvalidStateError("Unexpected reply type")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn switch off."""
        reply_type, _ = await self._con.async_send_cmd(commands[Command.EcoModeNormal])
        if reply_type != ReplyType.ACK:
            raise InvalidStateError("Unexpected reply type")


class HitachiProjectorAutoEcoModeSwitch(HitachiProjectorBaseSwitch):
    """Representation of device switch."""

    def __init__(self, con: HitachiProjectorConnection, entry_id: str) -> None:
        """Initialize the switch."""
        super().__init__(con, entry_id, "auto_eco_mode")

    async def async_update(self) -> None:
        """Retrieve latest state of the device."""
        try:
            reply_type, status = await self._con.get_auto_eco_mode_status()
            if reply_type != ReplyType.DATA or status is None:
                raise InvalidStateError("Unexpected reply type")
            self._attr_is_on = status == AutoEcoModeStatus.On
            self._attr_available = True
        except (RuntimeError, HomeAssistantError):
            self._attr_available = False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn switch on."""
        reply_type, _ = await self._con.async_send_cmd(commands[Command.AutoEcoModeOn])
        if reply_type != ReplyType.ACK:
            raise InvalidStateError("Unexpected reply type")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn switch off."""
        reply_type, _ = await self._con.async_send_cmd(commands[Command.AutoEcoModeOff])
        if reply_type != ReplyType.ACK:
            raise InvalidStateError("Unexpected reply type")
