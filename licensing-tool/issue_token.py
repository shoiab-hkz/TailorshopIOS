"""
Atelye PWA — License Token Issuer

Replaces the USB-writer tool. When a client installs the PWA on their
phone, the activation screen shows a "device code" (32 hex chars). They
send that code to you (SMS/WhatsApp/etc). You run this script, paste the
code, choose the client label, and you get a signed token back to send
them. They paste it into the app and it activates.

Run:   python licensing-tool/issue_token.py
"""

import base64
import hashlib
import hmac
import json
import re
import sys

# MUST match the MASTER_SECRET in index.html License module
MASTER_SECRET = 'atelye@khayat#2024$secret!key|v2'
PRODUCT = 'atelye'
VERSION = 'pwa-1'

CLIENTS = [
    {"id": 1, "label": "CLIENT-001", "name": "خیاطی شماره ۱"},
    {"id": 2, "label": "CLIENT-002", "name": "خیاطی شماره ۲"},
    {"id": 3, "label": "CLIENT-003", "name": "خیاطی شماره ۳"},
    {"id": 4, "label": "CLIENT-004", "name": "خیاطی شماره ۴"},
    {"id": 5, "label": "CLIENT-005", "name": "خیاطی شماره ۵"},
]

def sign(label, device_id):
    payload = {
        'label':     label,
        'device_id': device_id,
        'product':   PRODUCT,
        'version':   VERSION,
    }
    msg = f"{label}:{device_id}".encode('utf-8')
    sig = hmac.new(MASTER_SECRET.encode('utf-8'), msg, hashlib.sha256).hexdigest()
    payload['sig'] = sig
    raw = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    return base64.b64encode(raw).decode('ascii')

def main():
    print()
    print('═' * 56)
    print('  Atelye PWA — License Token Issuer')
    print('═' * 56)
    print()

    device_id = input('Paste client device code (32 hex chars): ').strip().lower()
    if not re.fullmatch(r'[0-9a-f]{32}', device_id):
        print('ERROR: invalid device code — must be 32 hex characters.')
        sys.exit(1)

    print()
    print('Select client:')
    for c in CLIENTS:
        print(f"  {c['id']}. {c['label']} — {c['name']}")
    print(f"  {len(CLIENTS)+1}. [Custom label]")
    print()

    choice = input('Choice: ').strip()
    try:
        n = int(choice)
    except ValueError:
        print('ERROR: invalid choice.'); sys.exit(1)

    if 1 <= n <= len(CLIENTS):
        label = CLIENTS[n-1]['label']
    elif n == len(CLIENTS) + 1:
        label = input('Custom label (e.g. CLIENT-006): ').strip()
        if not label:
            print('ERROR: empty label.'); sys.exit(1)
    else:
        print('ERROR: out of range.'); sys.exit(1)

    token = sign(label, device_id)

    print()
    print('═' * 56)
    print(f'  Client:    {label}')
    print(f'  Device:    {device_id}')
    print('═' * 56)
    print()
    print('TOKEN (send this to the client):')
    print()
    print(token)
    print()
    print('(Client pastes it into the activation screen.)')
    print()

if __name__ == '__main__':
    main()
