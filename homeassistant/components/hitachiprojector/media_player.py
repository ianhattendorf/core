"""Platform for media player integration."""

from __future__ import annotations

from libhitachiprojector.hitachiprojector import (
    Command,
    HitachiProjectorConnection,
    PowerStatus,
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
from homeassistant.const import CONF_MAC, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError, InvalidStateError
from homeassistant.helpers.device_registry import DeviceInfo, format_mac
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add media player for passed config_entry in HA."""

    con = config_entry.runtime_data

    name = config_entry.data.get(CONF_NAME)
    if not name:
        name = "UNKNOWN NAME"

    # Use config MAC for unique ID for now
    mac = config_entry.data.get(CONF_MAC)
    if not mac:
        raise ConfigEntryError("invalid mac")

    async_add_entities([HitachiProjectorMediaPlayer(con, name, mac)])


class HitachiProjectorMediaPlayer(MediaPlayerEntity):
    """Representation of a media player."""

    mac: str
    name: str

    supported_features = (
        MediaPlayerEntityFeature.TURN_ON | MediaPlayerEntityFeature.TURN_OFF
    )

    # TODO need to confirm _attr_unique_id, _attr_name, device_info.identifiers requirements
    def __init__(self, con: HitachiProjectorConnection, name: str, mac: str) -> None:
        """Initialize the media player."""
        # Usual setup is done here. Callbacks are added in async_added_to_hass.
        self.name = name
        self.mac = format_mac(mac)
        self._con = con

        # A unique_id for this entity with in this domain. This means for example if you
        # have a sensor on this cover, you must ensure the value returned is unique,
        # which is done here by appending "_cover". For more information, see:
        # https://developers.home-assistant.io/docs/entity_registry_index/#unique-id-requirements
        # Note: This is NOT used to generate the user visible Entity ID used in automations.
        self._attr_unique_id = f"hitachiprojector_{self.mac}_media_player"

        # This is the name for this *entity*, the "name" attribute from "device_info"
        # is used as the device name for device screens in the UI. This name is used on
        # entity screens, and used to build the Entity ID that's used is automations etc.
        self._attr_name = f"hitachiprojector_{self.mac}"

        self._attr_device_class = MediaPlayerDeviceClass.TV

    async def async_added_to_hass(self) -> None:
        """Run when this Entity has been added to HA."""

    async def async_will_remove_from_hass(self) -> None:
        """Entity being removed from hass."""

    # TODO make this unique
    @property
    def device_info(self) -> DeviceInfo:
        """Information about this entity/device."""
        return {
            "identifiers": {(DOMAIN, self.mac)},
            # If desired, the name for the device could be different to the entity
            "name": self.name,
            "manufacturer": "Hitachi",
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
            reply_type, data = self._con.send_cmd(commands[Command.PowerGet])
            if reply_type != ReplyType.DATA or data is None:
                raise InvalidStateError("Unexpected reply type")
            status = PowerStatus(int.from_bytes(data, byteorder="little"))
            match status:
                case PowerStatus.On:
                    self._attr_state = MediaPlayerState.ON
                case PowerStatus.Off:
                    self._attr_state = MediaPlayerState.OFF
                case PowerStatus.CoolDown:
                    self._attr_state = MediaPlayerState.OFF
            self._attr_available = True
        except RuntimeError:
            self._attr_available = False

    # TODO all async
    async def async_turn_on(self) -> None:
        """Turn the device on."""
        reply_type, _ = self._con.send_cmd(commands[Command.PowerTurnOn])
        if reply_type != ReplyType.ACK:
            raise InvalidStateError("Unexpected reply type")

    async def async_turn_off(self) -> None:
        """Turn the device off."""
        reply_type, _ = self._con.send_cmd(commands[Command.PowerTurnOff])
        if reply_type != ReplyType.ACK:
            raise InvalidStateError("Unexpected reply type")
