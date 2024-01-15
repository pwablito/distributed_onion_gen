import tempfile
import requests
import zipfile
import pathlib
import base64
import time
import subprocess
import shutil
import os

server_host = os.getenv("MASTER_ONION")
print(f"Server host: {server_host}")
server_port = 80

session = requests.session()
session.proxies = {
    'http': 'socks5h://127.0.0.1:9050'
}

def upload_onion(path):
    with tempfile.TemporaryDirectory() as d:
        with zipfile.ZipFile(f"{d}/onion.zip", "w") as zf:
            for f in pathlib.Path(path).iterdir():
                zf.write(f, arcname=f.name)
        with open(f"{d}/onion.zip", "rb") as f:
            body = {
                "zipfile": base64.b64encode(f.read()).decode()
            }
    for _ in range(5):
        try:
            session.post(f"http://{server_host}:{server_port}/found", json=body)
            return
        except requests.exceptions.ConnectionError:
            time.sleep(10)
            print("Failed to connect to master, trying again shortly...")
    exit("Failed to connect too many times. Exiting now.")


def get_filters():
    for _ in range(5):
        try:
            res = session.get(f"http://{server_host}:{server_port}/filters")
            return res.json()["filters"]
        except requests.exceptions.ConnectionError:
            time.sleep(10)
            print("Failed to connect to master, trying again shortly...")
    exit("Failed to connect too many times. Exiting now.")


def generate_onion(filters, timeout=60):
    try:
        print(f"Searching for up to {timeout} seconds with filter \"{','.join(filters)}\"")
        p = subprocess.run(
            ["mkp224o", "-z", "-s", "-n", "1", *filters],
            timeout=timeout,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        onion_name = p.stdout.decode().strip()
        return onion_name
    except subprocess.TimeoutExpired:
        print("Timed out.")
        return None


def main():
    while True:
        filters = get_filters()
        if not filters:
            time.sleep(10)
            continue
        found_onion = generate_onion(filters)
        if found_onion:
            print(f"Successfully found onion, uploading... ({found_onion})")
            upload_onion(found_onion)
            shutil.rmtree(found_onion)


if __name__ == "__main__":
    main()
