import requests

# Remplace ici par tes vrais identifiants de l'application Heliofrance
USERNAME = "TON_EMAIL_OU_UTILISATEUR"
PASSWORD = "TON_MOT_DE_PASSE"

BASE_URL = "https://heliofrance-data.fr"

def obtenir_token():
    """Étape 1: S'authentifier auprès du serveur pour obtenir le Token."""
    url = f"{BASE_URL}/api-token-auth/"
    payload = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    print("Demande de token d'authentification...")
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            token = response.json().get("token")
            print("✅ Authentification réussie !")
            return token
        else:
            print(f"Échec d'authentification ({response.status_code}) : {response.text}")
            return None
    except Exception as e:
        print(f"Erreur lors de la connexion au serveur : {e}")
        return None

def recuperer_telemetrie(token):
    """Étape 2: Récupérer la liste des appareils puis les données des capteurs."""
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    # 1. On récupère d'abord l'ID de l'appareil
    url_devices = f"{BASE_URL}/devices/"
    try:
        response_devices = requests.get(url_devices, headers=headers, timeout=10)
        if response_devices.status_code != 200 or not response_devices.json():
            print("Impossible de récupérer la liste des appareils.")
            return
        
        # On prend le premier appareil de la liste
        device = response_devices.json()[0]
        device_id = device.get("id")
        device_name = device.get("custom_name") or device.get("name")
        print(f"Appareil trouvé : {device_name} (ID: {device_id})")
        
        # 2. On interroge la télémétrie de cet appareil
        # Note: on utilise généralement le dernier échantillon enregistré
        url_telemetry = f"{BASE_URL}/devices/{device_id}/telemetry/"
        response_telemetry = requests.get(url_telemetry, headers=headers, timeout=10)
        
        if response_telemetry.status_code == 200:
            # Selon la structure, c'est souvent une liste des dernières mesures
            data_list = response_telemetry.json()
            if isinstance(data_list, list) and len(data_list) > 0:
                donnees = data_list[0] # Le plus récent
            else:
                donnees = data_list
            
            print("\n===DONNÉES CAPTEURS (CLOUD) ===")
            print(f"Capteur Solaire (Panneau) : {donnees.get('solar_panel')} °C")
            print(f"Ballon Temp Haut           : {donnees.get('tank_high')} °C")
            print(f"Ballon Temp Bas            : {donnees.get('tank_low')} °C")
            print(f"Pression du système        : {donnees.get('pressure')} bar")
            print(f"Circulateur Solaire (Pompe): {'Allumé' if donnees.get('relay_pump') else 'Éteint'}")
            print("===================================\n")
        else:
            print(f"Erreur lors de la récupération des capteurs : {response_telemetry.status_code}")
            
    except Exception as e:
        print(f"Erreur lors de la récupération des données : {e}")

if __name__ == "__main__":
    token_auth = obtenir_token()
    if token_auth:
        recuperer_telemetrie(token_auth)