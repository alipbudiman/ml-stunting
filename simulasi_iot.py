"""Simulasi sederhana perangkat IOT.
Meniru perilaku IOT.cpp tanpa WiFi / hardware.
Sekali jalan:
1. (Opsional) reset data device -> POST /reset/{did}
2. Kirim data berat & tinggi acak -> POST /recive

Jalankan:
    python simulasi_iot.py --host 4.145.112.100 --port 5000 --did IOT_001
Atau ke localhost:
    python simulasi_iot.py --host localhost --port 5000
"""
from __future__ import annotations
import argparse
import json
import random
import sys
import time
from urllib import request, error

DEFAULT_HOST = "4.145.112.100"  # Sama seperti di IOT.cpp
DEFAULT_PORT = 5000
DEFAULT_DID = "IOT_001"  # Device ID default tanpa timestamp

RESET_PATH = "/reset/{did}"
SEND_PATH = "/recive"


def build_url(host: str, port: int, path: str) -> str:
    # Jika host sudah mengandung http/https jangan tambah lagi
    if host.startswith("http://") or host.startswith("https://"):
        base = host.rstrip('/')
    else:
        base = f"http://{host}:{port}"  # Backend saat ini hanya HTTP
    if not path.startswith('/'):
        path = '/' + path
    return base + path


def http_post(url: str, data: dict | None = None, timeout: float = 10.0):
    payload = None
    headers = {"User-Agent": "IoT-Sim/1.0"}
    if data is not None:
        payload = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
        headers["Content-Length"] = str(len(payload))
    req = request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, body
    except error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")
    except Exception as e:
        return None, f"ERROR: {e}" 


def send_reset(host: str, port: int, did: str):
    url = build_url(host, port, RESET_PATH.format(did=did))
    print(f"[RESET] POST {url}")
    status, body = http_post(url)
    print(f"[RESET] Status: {status}\n[RESET] Body  : {body[:300]}")
    return status == 200


def send_measurement(host: str, port: int, did: str, berat: float, tinggi: float):
    url = build_url(host, port, SEND_PATH)
    data = {"bb": round(berat, 2), "tb": round(tinggi, 1), "did": did}
    print(f"[SEND ] POST {url}\n        Data: {data}")
    status, body = http_post(url, data)
    print(f"[SEND ] Status: {status}\n[SEND ] Body  : {body[:300]}")
    return status == 200


def generate_random_measurement():
    # Asumsi anak 0-5 th -> berat 4.5 - 5.0 kg, tinggi 60 - 70 cm
    berat = random.uniform(4.5, 5.0)
    tinggi = random.uniform(60.0, 70.0)
    return berat, tinggi


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Simulasi kirim data IOT sekali jalan")
    p.add_argument("--host", default=DEFAULT_HOST, help="Host/IP server (bisa 'localhost')")
    p.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port server")
    p.add_argument("--did", default=None, help=f"Device ID (default: {DEFAULT_DID})")
    p.add_argument("--no-reset", action="store_true", help="Lewatkan panggilan reset")
    p.add_argument("--seed", type=int, default=None, help="Random seed (opsional)")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if args.seed is not None:
        random.seed(args.seed)
    did = args.did or DEFAULT_DID  # Tanpa suffix timestamp

    print("=== SIMULASI IOT (sekali run) ===")
    print(f"Server : {args.host}:{args.port}")
    print(f"Device : {did}")

    if not args.no_reset:
        ok = send_reset(args.host, args.port, did)
        if not ok:
            print("[WARN] Reset gagal (lanjut kirim data)")
    else:
        print("[INFO] Melewati reset")

    berat, tinggi = generate_random_measurement()
    print(f"Generated measurement -> Berat: {berat:.2f} kg | Tinggi: {tinggi:.1f} cm")

    ok = send_measurement(args.host, args.port, did, berat, tinggi)
    if ok:
        print("[DONE] Data terkirim sukses")
        return 0
    else:
        print("[FAIL] Gagal kirim data")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
