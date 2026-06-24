"""Support pour les interrupteurs (Switch) Helio France."""
import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HelioFranceBoostSwitch(coordinator, entry)])


class HelioFranceBoostSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self.entry = entry
        self._attr_name = f"Helio Marche Forcée {entry.title}"
        self._attr_icon = "mdi:lightning-bolt"
        self._attr_unique_id = f"{coordinator.device_uuid}_boost_forced_switch"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.device_uuid)},
            "name": f"Helio France {self.entry.title}",
            "manufacturer": "Helio France",
            "model": "e-HELIO",
        }

    @property
    def is_on(self) -> bool:
        if self.coordinator.data is None:
            return False
        return bool(self.coordinator.data.get("relay_boost", False))

    async def async_turn_on(self, **kwargs):
        await self.coordinator.async_set_boost_mode(True)

    async def async_turn_off(self, **kwargs):
        await self.coordinator.async_set_boost_mode(False)