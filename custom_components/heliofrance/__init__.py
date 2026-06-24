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
    """Configuration de l'intégration Helio France depuis une entrée."""
    hass.data.setdefault(DOMAIN, {})

    # Récupération sécurisée depuis la configuration utilisateur (UI)
    username = entry.data.get("email")
    password = entry.data.get("password")
    device_uuid = entry.data.get("uuid")

    if not username or not password:
        _LOGGER.error("Identifiants manquants dans la configuration.")
        return False

    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
    coordinator = HelioFranceDataUpdateCoordinator(hass, session, username, password, entry.title, device_uuid)
    
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

class HelioFranceDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, session, username, password, entry_title, device_uuid):
        self.session = session
        self.username = username
        self.password = password
        self.entry_title = entry_title
        self.device_uuid = device_uuid
        self.token = None
        super().__init__(
            hass, _LOGGER, name=DOMAIN,
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
                    raise UpdateFailed(f"Erreur authentification {response.status}")

    async def _async_update_data(self):
        if not self.token:
            await self._async_get_token()
        headers = {"Authorization": f"Token {self.token}", "Content-Type": "application/json"}
        try:
            async with async_timeout.timeout(15):
                async with self.session.get(f"{BASE_URL}/devices/{self.device_uuid}/", headers=headers) as response:
                    if response.status == 401:
                        await self._async_get_token()
                        headers["Authorization"] = f"Token {self.token}"
                        async with self.session.get(f"{BASE_URL}/devices/{self.device_uuid}/", headers=headers) as r:
                            data = await r.json()
                    else:
                        data = await response.json()
                self.next_update = dt_util.utcnow() + timedelta(minutes=SCAN_INTERVAL_MINUTES)
                return data.get("last_telemetry", {})
        except Exception as err:
            raise UpdateFailed(f"Erreur de communication : {err}")

    async def async_set_boost_mode(self, state: bool):
        url = f"{BASE_URL}/devices/{self.device_uuid}/config/"
        headers = {"Authorization": f"Token {self.token}", "Content-Type": "application/json"}
        payload = {"boost_forced": state} 
        async with self.session.put(url, json=payload, headers=headers) as response:
            if response.status in (200, 204):
                await self.async_request_refresh()
                return True
            return False