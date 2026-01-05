import requests
from decouple import config

RANCHER_URL = config("RANCHER_URL")
RANCHER_TOKEN = config("RANCHER_TOKEN")
RANCHER_PROJECT = config("RANCHER_PROJECT")
NAMESPACE = config("RANCHER_NAMESPACE")

HEADERS = {
    "Authorization": f"Bearer {RANCHER_TOKEN}"
}
VERIFY_SSL = False

BASE_PODS_URL = f"{RANCHER_URL}/v3/project/{RANCHER_PROJECT}/pods"

def get_pod_ip(name_prefix):
    response = requests.get(BASE_PODS_URL, headers=HEADERS, verify=VERIFY_SSL)
    print("[DEBUG] Status:", response.status_code)

    if response.status_code == 200:
        pods = response.json().get("data", [])
        print(f"[DEBUG] Found {len(pods)} pods")
        for pod in pods:
            print(f"[DEBUG] Pod Name: {pod['name']}, IP: {pod.get('status', {}).get('podIp')}")
            if pod["name"].startswith(name_prefix):
                return pod.get("status", {}).get("podIp", "Pending")
    else:
        print("[ERROR] Rancher API failed:", response.text)
    
    return "Unavailable"

