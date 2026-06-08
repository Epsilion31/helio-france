"""Constantes pour l'intégration Helio France e-HELIO."""

DOMAIN = "heliofrance"
BASE_URL = "https://heliofrance-data.fr"

# Intervalle de rafraîchissement des données (1 minute pour éviter l'erreur 429)
SCAN_INTERVAL_MINUTES = 1

# Configuration des capteurs (Key API: [Nom HA, Unité, Icône])
SENSORS_TYPES = {
    "solar_panel": ["Température Panneau Solaire", "°C", "mdi:solar-power"],
    "tank_high": ["Température Ballon Haut", "°C", "mdi:thermometer-high"],
    "tank_low": ["Température Ballon Bas", "°C", "mdi:thermometer-low"],
    "tank_input": ["Température Entrée Eau", "°C", "mdi:water-thermometer"],
    "pressure": ["Pression du Système", "bar", "mdi:gauge"],
    "pump_power": ["Puissance Pompe", "%", "mdi:speedometer"],
}

# Configuration des entités binaires (Clé API: [Nom HA, Icône])
BINARY_SENSORS_TYPES = {
    "relay_pump": ["Circulateur (Pompe)", "mdi:pump"],
    "relay_boost": ["Résistance d'Appoint (Boost)", "mdi:lightning-bolt"],
}