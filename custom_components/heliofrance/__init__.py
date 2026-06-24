"""Initialisation de l'intégration Helio France e-HELIO."""
import logging
from datetime import timedelta
import aiohttp
import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import DOMAIN, BASE_URL, SCAN_INTERVAL_MINUTES

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "binary_sensor", "switch"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configuration de l'intégration Helio France."""
    hass.data.setdefault(DOMAIN, {})

    # Utilisation des clés exactes stockées par ton config_flow
    username = entry.data.get("email")
    password = entry.data.get("password")

    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))

    coordinator = HelioFranceDataUpdateCoordinator(hass, session, username, password, entry.data.get("uuid"))
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

class HelioFranceDataUpdateCoordinator(DataUpdateCoordinator):
    """Gère la récupération périodique des données."""

    def __init__(self, hass, session, username, password, target_uuid):
        self.session = session
        self.username = username
        self.password = password
        self.device_uuid = target_uuid  # UUID fixé ici
        self.token = None
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=SCAN_INTERVAL_MINUTES),
        )

    async def _async_get_token(self):
        url = f"{BASE_URL}/api-token-auth/"
        payload = {"username": self.username, "password": self.password}
        
        async with async_timeout.timeout(10):
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    self.token = data.get("token")
                else:
                    raise UpdateFailed(f"Erreur Auth {response.status}")

    async def _async_update_data(self):
        if not self.token:
            await self._async_get_token()

        headers = {"Authorization": f"Token {self.token}", "Content-Type": "application/json"}

        try:
            async with async_timeout.timeout(15):
                # Requête directe via l'UUID récupéré du config_flow
                async with self.session.get(f"{BASE_URL}/devices/{self.device_uuid}/", headers=headers) as response:
                    if response.status == 401:
                        await self._async_get_token()
                        headers["Authorization"] = f"Token {self.token}"
                        async with self.session.get(f"{BASE_URL}/devices/{self.device_uuid}/", headers=headers) as retry_response:
                            data = await retry_response.json()
                    else:
                        data = await response.json()
                
                return data.get("last_telemetry", {})

        except Exception as err:
            raise UpdateFailed(f"Erreur de communication : {err}")

    async def async_set_boost_mode(self, state: bool):
        if not self.token or not self.device_uuid:
            return False
            
        url = f"{BASE_URL}/devices/{self.device_uuid}/config/"
        headers = {"Authorization": f"Token {self.token}", "Content-Type": "application/json"}
        
        try:
            async with self.session.put(url, json={"boost_forced": state}, headers=headers) as response:
                if response.status in (200, 204):
                    await self.async_request_refresh()
                    return True
                return False
        except Exception:
            return False