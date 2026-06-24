"""Constantes pour l'intégration Helio France e-HELIO."""

DOMAIN = "heliofrance"
BASE_URL = "https://heliofrance-data.fr"
SCAN_INTERVAL_MINUTES = 1

SENSORS_TYPES = {
    "tank_high": ["Température Haut Ballon", "°C", "mdi:thermometer"],
    "tank_low": ["Température Bas Ballon", "°C", "mdi:thermometer"],
    "tank_input": ["Température Entrée Eau", "°C", "mdi:thermometer-water"],
    "solar_panel": ["Température Panneau", "°C", "mdi:solar-panel"],
    "tank_1_level": ["Niveau Ballon", "%", "mdi:water-percent"],
    "pump_power": ["Puissance Pompe", "%", "mdi:pump"],
    "pressure": ["Pression", "bar", "mdi:gauge"],
    "flow": ["Débit", "L/min", "mdi:water-pump"]
}

BINARY_SENSORS_TYPES = {
    "relay_pump": ["Relais Pompe", "mdi:pump"],
    "relay_valve_1": ["Relais Vanne 1", "mdi:valve"],
    "relay_valve_2": ["Relais Vanne 2", "mdi:valve"]
}