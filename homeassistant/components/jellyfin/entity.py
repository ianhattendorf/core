"""Base Entity for Jellyfin."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_NAME, DOMAIN
from .coordinator import JellyfinDataT, JellyfinDataUpdateCoordinator


class JellyfinEntity(CoordinatorEntity[JellyfinDataUpdateCoordinator[JellyfinDataT]]):
    """Defines a base Jellyfin entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: JellyfinDataUpdateCoordinator[JellyfinDataT],
        description: EntityDescription,
    ) -> None:
        """Initialize the Jellyfin entity."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.server_id}-{description.key}"
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, self.coordinator.server_id)},
            manufacturer=DEFAULT_NAME,
            name=self.coordinator.server_name,
            sw_version=self.coordinator.server_version,
        )


class JellyfinClientEntity(JellyfinEntity):
    """Defines a base client Jellyfin entity."""

    session_data: dict[str, Any] | None
    session_id: str

    def __init__(
        self,
        coordinator: JellyfinDataUpdateCoordinator[JellyfinDataT],
        description: EntityDescription,
        session_id: str,
        session_data: dict[str, Any],
    ) -> None:
        """Initialize the Jellyfin entity."""
        super().__init__(coordinator, description)

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
