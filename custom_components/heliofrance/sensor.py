"""Support pour les capteurs numériques Helio France."""
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENSORS_TYPES

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    for sensor_key, config in SENSORS_TYPES.items():
        entities.append(HelioFranceSensor(coordinator, entry, sensor_key, config))
        
    entities.append(HelioFranceTimerSensor(coordinator, entry))
        
    async_add_entities(entities)


class HelioFranceSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry, sensor_key, config):
        super().__init__(coordinator)
        self.entry = entry
        self.sensor_key = sensor_key
        self._attr_name = f"Helio {config[0]} {entry.title}"
        self._attr_native_unit_of_measurement = config[1]
        self._attr_icon = config[2]
        self._attr_unique_id = f"{coordinator.device_uuid}_{sensor_key}"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.device_uuid)},
            "name": f"Helio France {self.entry.title}",
            "manufacturer": "Helio France",
            "model": "e-HELIO",
        }

    @property
    def native_value(self):
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self.sensor_key)


class HelioFranceTimerSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self.entry = entry
        self._attr_name = f"Helio Prochaine Requête {entry.title}"
        self._attr_icon = "mdi:timer-sand"
        self._attr_unique_id = f"{coordinator.device_uuid}_api_timer"
        self._attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.device_uuid)},
            "name": f"Helio France {self.entry.title}",
            "manufacturer": "Helio France",
            "model": "e-HELIO",
        }

    @property
    def native_value(self):
        if hasattr(self.coordinator, 'next_update'):
            return self.coordinator.next_update
        return None