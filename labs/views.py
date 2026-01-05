import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.http import Http404
from decouple import config

RANCHER_URL = config("RANCHER_URL")
RANCHER_TOKEN = config("RANCHER_TOKEN")
RANCHER_PROJECT = config("RANCHER_PROJECT")
RANCHER_NAMESPACE = config("RANCHER_NAMESPACE")

HEADERS = {
    "Authorization": f"Bearer {RANCHER_TOKEN}"
}

PODS_URL = f"{RANCHER_URL}/v3/project/{RANCHER_PROJECT}/pods"


def get_matching_pod_ip(name_substring, use_node_ip=False):
    try:
        resp = requests.get(PODS_URL, headers=HEADERS, params={"namespaceId": RANCHER_NAMESPACE}, verify=False)
        print(f"[DEBUG] Status: {resp.status_code}")
        pods = resp.json().get("data", [])
        matching_pods = [pod for pod in pods if name_substring in pod.get("name", "")]

        if not matching_pods:
            print(f"[DEBUG] No matching pod for: {name_substring}")
            return "Unavailable"

        matching_pods.sort(key=lambda p: p.get("createdTS", 0), reverse=True)
        pod = matching_pods[0]

        if use_node_ip:
            return pod.get("status", {}).get("nodeIp", "Unavailable")
        else:
            return pod.get("status", {}).get("podIp", "Unavailable")

    except Exception as e:
        print(f"[ERROR] {e}")
        return "Unavailable"


@login_required
def dashboard(request):
    pods = [
        {
            "name": "kali-host",
            "box_type": "Kali",
            "ip": get_matching_pod_ip("kali-host", use_node_ip=True),
            "ssh_username": "root",
            "ssh_password": "password",
            "ssh_port": 30022
        },
        {
            "name": "ftp-vuln",
            "box_type": "FTP",
            "ip": get_matching_pod_ip("ftp-vuln"),
            "ssh_username": "-",
            "ssh_password": "-",
            "ssh_port": "-"
        },
        {
            "name": "mysql-vuln",
            "box_type": "MySQL",
            "ip": get_matching_pod_ip("mysql-vuln"),
            "ssh_username": "-",
            "ssh_password": "-",
            "ssh_port": "-"
        }
    ]
    return render(request, 'labs/dashboard.html', {'pods': pods})


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def walkthrough(request, box_type):
    if box_type == "ftp":
        return render(request, "labs/walkthrough_ftp.html")
    elif box_type == "mysql":
        return render(request, "labs/walkthrough_mysql.html")
    else:
        raise Http404("Walkthrough not found.")
