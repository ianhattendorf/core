"""Platform for media player integration."""

from __future__ import annotations

from libhitachiprojector.hitachiprojector import (
    Command,
    HitachiProjectorConnection,
    InputSource,
    ReplyType,
    commands,
)

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import InvalidStateError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, POWER_STATUS_TO_MEDIA_PLAYER_STATE, SOURCE_TO_SET_COMMAND


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add media player for passed config_entry in HA."""

    con = config_entry.runtime_data

    async_add_entities([HitachiProjectorMediaPlayer(con, config_entry.entry_id)])


class HitachiProjectorMediaPlayer(MediaPlayerEntity):
    """Representation of a media player."""

    entry_id: str

    supported_features = (
        MediaPlayerEntityFeature.TURN_ON
        | MediaPlayerEntityFeature.TURN_OFF
        | MediaPlayerEntityFeature.SELECT_SOURCE
    )

    def __init__(self, con: HitachiProjectorConnection, entry_id: str) -> None:
        """Initialize the media player."""
        self.entry_id = entry_id
        self._con = con

        self._attr_unique_id = f"hitachiprojector_{self.entry_id}_media_player"

        self._attr_has_entity_name = True
        self._attr_name = None

        self._attr_device_class = MediaPlayerDeviceClass.TV

        self._attr_source_list = [e.name for e in InputSource]

    async def async_added_to_hass(self) -> None:
        """Run when this Entity has been added to HA."""

    async def async_will_remove_from_hass(self) -> None:
        """Entity being removed from hass."""

    @property
    def device_info(self) -> DeviceInfo:
        """Information about this entity/device."""
        return {
            "configuration_url": f"http://{self._con.host}",
            "identifiers": {(DOMAIN, self.entry_id)},
            "manufacturer": "Hitachi",
            "name": "Hitachi Projector",
        }

    @property
    def icon(self) -> str | None:
        """Return the icon to use in the frontend, if any."""
        if self.state == MediaPlayerState.ON:
            return "mdi:projector"

        return "mdi:projector-off"

    async def async_update(self) -> None:
        """Retrieve latest state of the device."""
        try:
            reply_type, status = await self._con.get_power_status()
            if reply_type != ReplyType.DATA or status is None:
                raise InvalidStateError("Unexpected reply type")
            self._attr_state = POWER_STATUS_TO_MEDIA_PLAYER_STATE[status]
            self._attr_available = True
        except RuntimeError:
            self._attr_available = False

        reply_type, status = await self._con.get_input_source()
        if reply_type == ReplyType.DATA and status is not None:
            self._attr_source = status.name

    async def async_turn_on(self) -> None:
        """Turn the device on."""
        reply_type, _ = await self._con.async_send_cmd(commands[Command.PowerTurnOn])
        if reply_type != ReplyType.ACK:
            raise InvalidStateError("Unexpected reply type")

    async def async_turn_off(self) -> None:
        """Turn the device off."""
        reply_type, _ = await self._con.async_send_cmd(commands[Command.PowerTurnOff])
        if reply_type != ReplyType.ACK:
            raise InvalidStateError("Unexpected reply type")

    async def async_select_source(self, source: str) -> None:
        """Select input source."""
        command = SOURCE_TO_SET_COMMAND[source]
        reply_type, _ = await self._con.async_send_cmd(commands[command])
        if reply_type != ReplyType.ACK:
            raise InvalidStateError("Unexpected reply type")
