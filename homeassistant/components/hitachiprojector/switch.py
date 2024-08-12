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
from homeassistant.const import CONF_MAC
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError, InvalidStateError
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
            HitachiProjectorBlankModeSwitch(con, mac),
            HitachiProjectorEcoModeSwitch(con, mac),
            HitachiProjectorAutoEcoModeSwitch(con, mac),
        ]
    )


class HitachiProjectorBaseSwitch(SwitchEntity):
    """Representation of device switch."""

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


class HitachiProjectorBlankModeSwitch(HitachiProjectorBaseSwitch):
    """Representation of device switch."""

    def __init__(self, con: HitachiProjectorConnection, mac: str) -> None:
        """Initialize the switch."""
        super().__init__(con, mac, "blank_mode", "Blank mode")

    async def async_update(self) -> None:
        """Retrieve latest state of the device."""
        try:
            reply_type, status = await self._con.get_blank_status()
            if reply_type != ReplyType.DATA or status is None:
                raise InvalidStateError("Unexpected reply type")
            self._attr_is_on = status == BlankStatus.On
            self._attr_available = True
        except RuntimeError:
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

    def __init__(self, con: HitachiProjectorConnection, mac: str) -> None:
        """Initialize the switch."""
        super().__init__(con, mac, "eco_mode", "Eco mode")

    async def async_update(self) -> None:
        """Retrieve latest state of the device."""
        try:
            reply_type, status = await self._con.get_eco_mode_status()
            if reply_type != ReplyType.DATA or status is None:
                raise InvalidStateError("Unexpected reply type")
            self._attr_is_on = status == EcoModeStatus.Eco
            self._attr_available = True
        except RuntimeError:
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

    def __init__(self, con: HitachiProjectorConnection, mac: str) -> None:
        """Initialize the switch."""
        super().__init__(con, mac, "auto_eco_mode", "Auto eco mode")

    async def async_update(self) -> None:
        """Retrieve latest state of the device."""
        try:
            reply_type, status = await self._con.get_auto_eco_mode_status()
            if reply_type != ReplyType.DATA or status is None:
                raise InvalidStateError("Unexpected reply type")
            self._attr_is_on = status == AutoEcoModeStatus.On
            self._attr_available = True
        except RuntimeError:
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
