import requests
import json
import urllib3

# Désactivation des alertes SSL pour le réseau de l'école
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

def lister_et_choisir_appareil(token):
    """Liste les appareils disponibles et demande à l'utilisateur d'en choisir un."""
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    url_devices = f"{BASE_URL}/devices/"
    
    try:
        response = requests.get(url_devices, headers=headers, timeout=10, verify=False)
        if response.status_code != 200:
            print(f"❌ Erreur lors de la récupération des appareils : {response.status_code}")
            return None

        devices = response.json()
        if not devices:
            print("❌ Aucun appareil trouvé sur ce compte.")
            return None

        print(f"\n===========================================")
        print(f"📱 {len(devices)} APPAREIL(S) TROUVÉ(S) SUR VOTRE COMPTE :")
        print(f"===========================================")
        for index, device in enumerate(devices):
            device_name = device.get("custom_name") or device.get("name") or "Sans nom"
            print(f" [{index}] - {device_name} (UUID: {device.get('uuid')})")
        print(f"===========================================\n")

        # Demande de choix à l'utilisateur
        while True:
            choix = input("👉 Entrez le numéro de l'appareil à afficher (ex: 0 ou 1) : ")
            if choix.isdigit() and 0 <= int(choix) < len(devices):
                return devices[int(choix)]
            print("⚠️ Choix invalide. Veuillez entrer un nombre valide de la liste.")

    except Exception as e:
        print(f"❌ Erreur lors de la récupération de la liste : {e}")
        return None

def afficher_telemetrie(device):
    """Affiche proprement les données de télémétrie de l'appareil sélectionné."""
    device_name = device.get("custom_name") or device.get("name")
    telemetry = device.get("last_telemetry", {})

    print(f"\n===========================================")
    print(f"📡 APPAREIL SÉLECTIONNÉ : {device_name}")
    print(f"🆔 ID : {device.get('id')} | UUID: {device.get('uuid')}")
    print(f"📅 Date des données     : {telemetry.get('date')}")
    print(f"===========================================")
    print(f"☀️ Capteur Solaire (Panneau)  : {telemetry.get('solar_panel')} °C")
    print(f"🧪 Température Ballon Haut    : {telemetry.get('tank_high')} °C")
    print(f"🧪 Température Ballon Bas     : {telemetry.get('tank_low')} °C")
    print(f"💧 Température Entrée Eau     : {telemetry.get('tank_input')} °C")
    print(f"🔄 Circulateur (Pompe)        : {'Allumé' if telemetry.get('relay_pump') else 'Éteint'}")
    print(f"⚡ Résistance d'Appoint (Boost): {'Allumée' if telemetry.get('relay_boost') else 'Éteinte'}")
    print(f"🎈 Pression du Système        : {telemetry.get('pressure')} bar")
    print(f"===========================================\n")

if __name__ == "__main__":
    token_auth = obtenir_token()
    if token_auth:
        appareil_choisi = lister_et_choisir_appareil(token_auth)
        if appareil_choisi:
            afficher_telemetrie(appareil_choisi)