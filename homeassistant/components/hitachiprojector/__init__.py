"""The Hitachi Projector integration."""

from __future__ import annotations

from libhitachiprojector.hitachiprojector import HitachiProjectorConnection, ReplyType
from pypjlink import Projector
from pypjlink.projector import ProjectorError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.device_registry import DeviceInfo

PLATFORMS: list[Platform] = [Platform.MEDIA_PLAYER, Platform.SENSOR, Platform.SWITCH]
ERR_PROJECTOR_UNAVAILABLE = "projector unavailable"

type HitachiProjectorConfigEntry = ConfigEntry[HitachiProvider]


class PJLinkProvider:
    """Provider for PJLink protocol."""

    host: str
    password: str
    port: int

    def __init__(self, host: str, password: str) -> None:
        """Initialize PJLinkProvider."""
        self.host = host
        self.password = password
        self.port = 4352

    def projector(self):
        """Create PJLink Projector instance."""

        try:
            projector = Projector.from_address(self.host, self.port)
            projector.authenticate(self.password)
        except (TimeoutError, OSError) as err:
            raise ProjectorError(ERR_PROJECTOR_UNAVAILABLE) from err

        return projector


class HitachiProvider:
    """Hitachi Projector provider. Includes PJLink and proprietary Hitachi protocol connections."""

    pjlink_provider: PJLinkProvider
    hitachi_connection: HitachiProjectorConnection
    device_info: DeviceInfo

    def __init__(
        self,
        hitachi_connection: HitachiProjectorConnection,
        pjlink_provider: PJLinkProvider,
        device_info: DeviceInfo,
    ) -> None:
        """Initialize HitachiProvider."""
        self.hitachi_connection = hitachi_connection
        self.pjlink_provider = pjlink_provider
        self.device_info = device_info


async def async_setup_entry(
    hass: HomeAssistant, entry: HitachiProjectorConfigEntry
) -> bool:
    """Set up Hitachi Projector from a config entry."""

    host = entry.data[CONF_HOST]
    password = entry.data[CONF_PASSWORD]

    hitachi_connection = HitachiProjectorConnection(host=host, password=password)
    reply_type, _ = await hitachi_connection.get_power_status()
    if reply_type != ReplyType.DATA:
        raise ConfigEntryNotReady(f"Unable to connect to {entry.data[CONF_HOST]}")

    pjlink_provider = PJLinkProvider(host, password)
    device_info = DeviceInfo()
    try:
        with pjlink_provider.projector() as projector:
            device_info["name"] = projector.get_name()
            device_info["manufacturer"] = projector.get_manufacturer()
            device_info["model"] = projector.get_product_name()
    except ProjectorError as err:
        raise ConfigEntryNotReady(
            f"Unable to connect to {entry.data[CONF_HOST]}"
        ) from err

    entry.runtime_data = HitachiProvider(
        hitachi_connection, pjlink_provider, device_info
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: HitachiProjectorConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
