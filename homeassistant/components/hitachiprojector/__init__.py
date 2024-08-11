"""The Hitachi Projector integration."""

from __future__ import annotations

from libhitachiprojector.hitachiprojector import (
    Command,
    HitachiProjectorConnection,
    ReplyType,
    commands,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

PLATFORMS: list[Platform] = [Platform.MEDIA_PLAYER]

# TODO Create ConfigEntry type alias with API object
# TODO Rename type alias and update all entry annotations
# type New_NameConfigEntry = ConfigEntry[MyApi]  # noqa: F821
type New_NameConfigEntry = ConfigEntry  # noqa: F821


# TODO Update entry annotation
async def async_setup_entry(hass: HomeAssistant, entry: New_NameConfigEntry) -> bool:
    """Set up Hitachi Projector from a config entry."""

    # TODO async
    con = HitachiProjectorConnection(host=entry.data[CONF_HOST])
    reply_type, _ = con.send_cmd(commands[Command.PowerGet])
    if reply_type != ReplyType.DATA:
        raise ConfigEntryNotReady(f"Unable to connect to {entry.data[CONF_HOST]}")

    entry.runtime_data = con

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


# TODO Update entry annotation
async def async_unload_entry(hass: HomeAssistant, entry: New_NameConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
