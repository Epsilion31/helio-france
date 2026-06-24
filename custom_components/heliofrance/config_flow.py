"""Config flow for Helio France integration."""
import logging
import voluptuous as vol
import requests
import urllib3
from homeassistant import config_entries
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
BASE_URL = "https://heliofrance-data.fr"

# Désactivation des alertes SSL comme dans ton script de test
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class HelioFranceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Helio France."""
    VERSION = 1

    def __init__(self):
        """Initialize."""
        self.email = None
        self.password = None
        self.token = None
        self.devices = []

    def _fetch_token_and_devices(self):
        """Requête synchrone identique au script de test."""
        try:
            # 1. Demande de Token
            res_token = requests.post(
                f"{BASE_URL}/api-token-auth/",
                json={"username": self.email, "password": self.password},
                timeout=10,
                verify=False
            )
            if res_token.status_code != 200:
                return "invalid_auth"
            self.token = res_token.json().get("token")

            # 2. Demande des Appareils
            headers = {"Authorization": f"Token {self.token}"}
            res_devices = requests.get(
                f"{BASE_URL}/devices/",
                headers=headers,
                timeout=10,
                verify=False
            )
            if res_devices.status_code == 200:
                self.devices = res_devices.json()
                return "success"
            return "cannot_connect"
        except Exception:
            return "cannot_connect"

    async def async_step_user(self, user_input=None):
        """First step: ask for credentials."""
        errors = {}
        if user_input is not None:
            self.email = user_input["email"]
            self.password = user_input["password"]

            # Exécution de la requête via l'exécuteur de Home Assistant pour ne pas bloquer le système
            result = await self.hass.async_add_executor_job(self._fetch_token_and_devices)

            if result != "success":
                errors["base"] = result
            elif not self.devices:
                errors["base"] = "no_devices"
            else:
                # Si on a des appareils, on va TOUJOURS à l'étape de sélection (pratique s'il y en a 2 !)
                return await self.async_step_select_device()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("email"): str,
                vol.Required("password"): str,
            }),
            errors=errors
        )

    async def async_step_select_device(self, user_input=None):
        """Étape de sélection avec liste déroulante intégrée à l'UI."""
        if user_input is not None:
            selected_uuid = user_input["device"]
            selected_device = next(d for d in self.devices if d["uuid"] == selected_uuid)
            device_name = selected_device.get("custom_name") or selected_device.get("name") or "e-HELIO"
            
            return self.async_create_entry(
                title=device_name,
                data={
                    "email": self.email,
                    "password": self.password,
                    "uuid": selected_uuid
                }
            )

        # Construction du dictionnaire pour la liste déroulante coulissante
        device_options = {
            d["uuid"]: f"{d.get('custom_name') or d.get('name') or 'Sans nom'} ({d.get('uuid')[:8]})"
            for d in self.devices
        }

        return self.async_show_form(
            step_id="select_device",
            data_schema=vol.Schema({
                vol.Required("device", default=list(device_options.keys())[0]): vol.In(device_options)
            })
        )