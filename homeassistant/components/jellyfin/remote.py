"""Support for Jellyfin remote commands."""

from __future__ import annotations

from collections.abc import Iterable
import time
from typing import Any

from homeassistant.components.remote import (
    ATTR_DELAY_SECS,
    ATTR_NUM_REPEATS,
    DEFAULT_DELAY_SECS,
    DEFAULT_NUM_REPEATS,
    RemoteEntity,
    RemoteEntityDescription,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import JellyfinConfigEntry
from .const import (
    SERVICE_COMMAND_DISPLAY_MESSAGE,
    SERVICE_COMMAND_SEND_STRING,
    SERVICE_SCHEMA_COMMAND_DISPLAY_MESSAGE,
    SERVICE_SCHEMA_COMMAND_SEND_STRING,
)
from .coordinator import JellyfinDataUpdateCoordinator
from .entity import JellyfinClientEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: JellyfinConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Jellyfin remote from a config entry."""
    jellyfin_data = entry.runtime_data
    coordinator = jellyfin_data.coordinators["sessions"]

    @callback
    def handle_coordinator_update() -> None:
        """Add remote per session."""
        entities: list[RemoteEntity] = []
        for session_id, session_data in coordinator.data.items():
            if (
                session_id not in coordinator.remote_session_ids
                and session_data["SupportsRemoteControl"]
            ):
                entity: RemoteEntity = JellyfinRemote(
                    coordinator, session_id, session_data
                )
                coordinator.remote_session_ids.add(session_id)
                entities.append(entity)
        async_add_entities(entities)

    handle_coordinator_update()

    entry.async_on_unload(coordinator.async_add_listener(handle_coordinator_update))

    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        SERVICE_COMMAND_DISPLAY_MESSAGE,
        SERVICE_SCHEMA_COMMAND_DISPLAY_MESSAGE,
        "command_display_message",
    )

    platform.async_register_entity_service(
        SERVICE_COMMAND_SEND_STRING,
        SERVICE_SCHEMA_COMMAND_SEND_STRING,
        "command_send_string",
    )


class JellyfinRemote(JellyfinClientEntity, RemoteEntity):
    """Defines a Jellyfin remote entity."""

    def __init__(
        self,
        coordinator: JellyfinDataUpdateCoordinator,
        session_id: str,
        session_data: dict[str, Any],
    ) -> None:
        """Initialize the Jellyfin Remote entity."""
        super().__init__(
            coordinator,
            RemoteEntityDescription(
                key=session_id,
            ),
            session_id,
            session_data,
        )

    @property
    def is_on(self) -> bool:
        """Return if the client is on."""
        return self.session_data["IsActive"] if self.session_data else False

    def send_command(self, command: Iterable[str], **kwargs: Any) -> None:
        """Send a command to the client."""
        num_repeats = kwargs.get(ATTR_NUM_REPEATS, DEFAULT_NUM_REPEATS)
        delay = kwargs.get(ATTR_DELAY_SECS, DEFAULT_DELAY_SECS)

        for _ in range(num_repeats):
            for single_command in command:
                self.coordinator.api_client.jellyfin.command(
                    self.session_id, single_command
                )
                time.sleep(delay)

    def command_display_message(self, header: str, text: str, **kwargs: Any) -> None:
        """Send a command to display a message on a client."""
        timeout_ms = kwargs.get("timeout_ms")

        arguments = {"Header": header, "Text": text}
        if timeout_ms is not None:
            arguments["timeout_ms"] = timeout_ms

        self.coordinator.api_client.jellyfin.command(
            self.session_id, "DisplayMessage", None, arguments
        )

    def command_send_string(self, string: str) -> None:
        """Send a command to enter a string to a client."""
        arguments = {"String": string}

        self.coordinator.api_client.jellyfin.command(
            self.session_id, "SendString", None, arguments
        )
