import requests
import json
import urllib3

# Désactivation des alertes SSL pour le réseau de l'école
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#USERNAME = "adrien.lavergne@2027.icam.fr"
#PASSWORD = "Tcpl#mdpte2021."
USERNAME = "victor.grebet@2027.icam.fr"
PASSWORD = "Azerty12345"
BASE_URL = "https://heliofrance-data.fr"

def obtenir_token():
    """S'authentifie auprès du serveur pour obtenir le Token."""
    url = f"{BASE_URL}/api-token-auth/"
    payload = {"username": USERNAME, "password": PASSWORD}
    
    print("Demande de token d'authentification...")
    try:
        response = requests.post(url, json=payload, timeout=10, verify=False)
        if response.status_code == 200:
            print("✅ Authentification réussie !")
            return response.json().get("token")
        else:
            print(f"❌ Échec d'authentification ({response.status_code})")
            return None
    except Exception as e:
        print(f"❌ Erreur connexion : {e}")
        return None

def recuperer_telemetrie(token):
    """Récupère les appareils et affiche les données de télémétrie."""
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    url_devices = f"{BASE_URL}/devices/"
    
    try:
        response = requests.get(url_devices, headers=headers, timeout=10, verify=False)
        if response.status_code != 200:
            print(f"❌ Erreur serveur lors de la récupération : {response.status_code}")
            return

        devices = response.json()
        if not devices:
            print("❌ Aucun appareil trouvé sur ce compte.")
            return

        # On sélectionne le premier appareil trouvé (ID: 1284 - Test R&D)
        device = devices[0]
        device_name = device.get("custom_name") or device.get("name")
        telemetry = device.get("last_telemetry", {})

        print(f"\n===========================================")
        print(f"📡 APPAREIL : {device_name} (UUID: {device.get('uuid')})")
        print(f"📅 Date des données : {telemetry.get('date')}")
        print(f"===========================================")
        print(f"☀️ Capteur Solaire (Panneau)  : {telemetry.get('solar_panel')} °C")
        print(f"🧪 Température Ballon Haut    : {telemetry.get('tank_high')} °C")
        print(f"🧪 Température Ballon Bas     : {telemetry.get('tank_low')} °C")
        print(f"💧 Température Entrée Eau     : {telemetry.get('tank_input')} °C")
        print(f"🔄 Circulateur (Pompe)        : {'Allumé' if telemetry.get('relay_pump') else 'Éteint'}")
        print(f"⚡ Résistance d'Appoint (Boost): {'Allumée' if telemetry.get('relay_boost') else 'Éteinte'}")
        print(f"🎈 Pression du Système        : {telemetry.get('pressure')} bar")
        print(f"===========================================\n")

    except Exception as e:
        print(f"❌ Erreur lors de l'extraction des données : {e}")

if __name__ == "__main__":
    token_auth = obtenir_token()
    if token_auth:
        recuperer_telemetrie(token_auth)