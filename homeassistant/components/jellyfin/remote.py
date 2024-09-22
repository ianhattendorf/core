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
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import JellyfinConfigEntry
from .const import DOMAIN
from .coordinator import JellyfinDataUpdateCoordinator
from .entity import JellyfinEntity


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


class JellyfinRemote(JellyfinEntity, RemoteEntity):
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
        )

        self.session_id = session_id
        self.session_data: dict[str, Any] = session_data
        self.device_id: str = session_data["DeviceId"]
        self.device_name: str = session_data["DeviceName"]
        self.client_name: str = session_data["Client"]
        self.app_version: str = session_data["ApplicationVersion"]

        self.capabilities: dict[str, Any] = session_data["Capabilities"]

        if self.capabilities.get("SupportsPersistentIdentifier", False):
            self._attr_device_info = DeviceInfo(
                identifiers={(DOMAIN, self.device_id)},
                manufacturer="Jellyfin",
                model=self.client_name,
                name=self.device_name,
                sw_version=self.app_version,
                via_device=(DOMAIN, coordinator.server_id),
            )
            self._attr_name = None
        else:
            self._attr_device_info = None
            self._attr_has_entity_name = False
            self._attr_name = self.device_name

    @property
    def is_on(self) -> bool:
        """Return if the client is on."""
        is_active: bool = self.session_data["IsActive"]
        return is_active

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
