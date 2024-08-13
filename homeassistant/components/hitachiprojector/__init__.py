"""The Hitachi Projector integration."""

from __future__ import annotations

from libhitachiprojector.hitachiprojector import HitachiProjectorConnection, ReplyType

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

PLATFORMS: list[Platform] = [Platform.MEDIA_PLAYER, Platform.SENSOR, Platform.SWITCH]

type HitachiProjectorConfigEntry = ConfigEntry[HitachiProjectorConnection]


async def async_setup_entry(
    hass: HomeAssistant, entry: HitachiProjectorConfigEntry
) -> bool:
    """Set up Hitachi Projector from a config entry."""

    password = entry.data[CONF_PASSWORD]
    con = HitachiProjectorConnection(host=entry.data[CONF_HOST], password=password)
    reply_type, _ = await con.get_power_status()
    if reply_type != ReplyType.DATA:
        raise ConfigEntryNotReady(f"Unable to connect to {entry.data[CONF_HOST]}")

    entry.runtime_data = con

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: HitachiProjectorConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
