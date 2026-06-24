"""Support pour les capteurs binaires (On/Off) Helio France."""
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, BINARY_SENSORS_TYPES

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Configuration des capteurs binaires."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    for sensor_key, config in BINARY_SENSORS_TYPES.items():
        entities.append(HelioFranceBinarySensor(coordinator, entry, sensor_key, config))
        
    async_add_entities(entities)


class HelioFranceBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Représentation d'un capteur binaire Helio France."""

    def __init__(self, coordinator, entry, sensor_key, config):
        """Initialisation."""
        super().__init__(coordinator)
        self.entry = entry
        self.sensor_key = sensor_key
        self._attr_name = f"Helio {config[0]} {entry.title}"
        self._attr_icon = config[1]
        # ID unique lié à l'UUID matériel de l'appareil
        self._attr_unique_id = f"{coordinator.device_uuid}_{sensor_key}"

    @property
    def device_info(self):
        """Rattachement strict au même appareil matériel."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.device_uuid)},
            "name": f"Helio France {self.entry.title}",
            "manufacturer": "Helio France",
            "model": "e-HELIO",
        }

    @property
    def is_on(self) -> bool:
        """Retourne vrai si le relais est actif."""
        if self.coordinator.data is None:
            return False
        return bool(self.coordinator.data.get(self.sensor_key, False))