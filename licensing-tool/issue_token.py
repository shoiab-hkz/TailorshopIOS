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
  {"id": 6, "label": "CLIENT-006", "name": "خیاطی شماره ۶"},
  {"id": 7, "label": "CLIENT-007", "name": "خیاطی شماره ۷"},
  {"id": 8, "label": "CLIENT-008", "name": "خیاطی شماره ۸"},
  {"id": 9, "label": "CLIENT-009", "name": "خیاطی شماره ۹"},
  {"id": 10, "label": "CLIENT-010", "name": "خیاطی شماره ۱۰"},
  {"id": 11, "label": "CLIENT-011", "name": "خیاطی شماره ۱۱"},
  {"id": 12, "label": "CLIENT-012", "name": "خیاطی شماره ۱۲"},
  {"id": 13, "label": "CLIENT-013", "name": "خیاطی شماره ۱۳"},
  {"id": 14, "label": "CLIENT-014", "name": "خیاطی شماره ۱۴"},
  {"id": 15, "label": "CLIENT-015", "name": "خیاطی شماره ۱۵"},
  {"id": 16, "label": "CLIENT-016", "name": "خیاطی شماره ۱۶"},
  {"id": 17, "label": "CLIENT-017", "name": "خیاطی شماره ۱۷"},
  {"id": 18, "label": "CLIENT-018", "name": "خیاطی شماره ۱۸"},
  {"id": 19, "label": "CLIENT-019", "name": "خیاطی شماره ۱۹"},
  {"id": 20, "label": "CLIENT-020", "name": "خیاطی شماره ۲۰"},
  {"id": 21, "label": "CLIENT-021", "name": "خیاطی شماره ۲۱"},
  {"id": 22, "label": "CLIENT-022", "name": "خیاطی شماره ۲۲"},
  {"id": 23, "label": "CLIENT-023", "name": "خیاطی شماره ۲۳"},
  {"id": 24, "label": "CLIENT-024", "name": "خیاطی شماره ۲۴"},
  {"id": 25, "label": "CLIENT-025", "name": "خیاطی شماره ۲۵"},
  {"id": 26, "label": "CLIENT-026", "name": "خیاطی شماره ۲۶"},
  {"id": 27, "label": "CLIENT-027", "name": "خیاطی شماره ۲۷"},
  {"id": 28, "label": "CLIENT-028", "name": "خیاطی شماره ۲۸"},
  {"id": 29, "label": "CLIENT-029", "name": "خیاطی شماره ۲۹"},
  {"id": 30, "label": "CLIENT-030", "name": "خیاطی شماره ۳۰"},
  {"id": 31, "label": "CLIENT-031", "name": "خیاطی شماره ۳۱"},
  {"id": 32, "label": "CLIENT-032", "name": "خیاطی شماره ۳۲"},
  {"id": 33, "label": "CLIENT-033", "name": "خیاطی شماره ۳۳"},
  {"id": 34, "label": "CLIENT-034", "name": "خیاطی شماره ۳۴"},
  {"id": 35, "label": "CLIENT-035", "name": "خیاطی شماره ۳۵"},
  {"id": 36, "label": "CLIENT-036", "name": "خیاطی شماره ۳۶"},
  {"id": 37, "label": "CLIENT-037", "name": "خیاطی شماره ۳۷"},
  {"id": 38, "label": "CLIENT-038", "name": "خیاطی شماره ۳۸"},
  {"id": 39, "label": "CLIENT-039", "name": "خیاطی شماره ۳۹"},
  {"id": 40, "label": "CLIENT-040", "name": "خیاطی شماره ۴۰"},
  {"id": 41, "label": "CLIENT-041", "name": "خیاطی شماره ۴۱"},
  {"id": 42, "label": "CLIENT-042", "name": "خیاطی شماره ۴۲"},
  {"id": 43, "label": "CLIENT-043", "name": "خیاطی شماره ۴۳"},
  {"id": 44, "label": "CLIENT-044", "name": "خیاطی شماره ۴۴"},
  {"id": 45, "label": "CLIENT-045", "name": "خیاطی شماره ۴۵"},
  {"id": 46, "label": "CLIENT-046", "name": "خیاطی شماره ۴۶"},
  {"id": 47, "label": "CLIENT-047", "name": "خیاطی شماره ۴۷"},
  {"id": 48, "label": "CLIENT-048", "name": "خیاطی شماره ۴۸"},
  {"id": 49, "label": "CLIENT-049", "name": "خیاطی شماره ۴۹"},
  {"id": 50, "label": "CLIENT-050", "name": "خیاطی شماره ۵۰"},
  {"id": 51, "label": "CLIENT-051", "name": "خیاطی شماره ۵۱"},
  {"id": 52, "label": "CLIENT-052", "name": "خیاطی شماره ۵۲"},
  {"id": 53, "label": "CLIENT-053", "name": "خیاطی شماره ۵۳"},
  {"id": 54, "label": "CLIENT-054", "name": "خیاطی شماره ۵۴"},
  {"id": 55, "label": "CLIENT-055", "name": "خیاطی شماره ۵۵"},
  {"id": 56, "label": "CLIENT-056", "name": "خیاطی شماره ۵۶"},
  {"id": 57, "label": "CLIENT-057", "name": "خیاطی شماره ۵۷"},
  {"id": 58, "label": "CLIENT-058", "name": "خیاطی شماره ۵۸"},
  {"id": 59, "label": "CLIENT-059", "name": "خیاطی شماره ۵۹"},
  {"id": 60, "label": "CLIENT-060", "name": "خیاطی شماره ۶۰"},
  {"id": 61, "label": "CLIENT-061", "name": "خیاطی شماره ۶۱"},
  {"id": 62, "label": "CLIENT-062", "name": "خیاطی شماره ۶۲"},
  {"id": 63, "label": "CLIENT-063", "name": "خیاطی شماره ۶۳"},
  {"id": 64, "label": "CLIENT-064", "name": "خیاطی شماره ۶۴"},
  {"id": 65, "label": "CLIENT-065", "name": "خیاطی شماره ۶۵"},
  {"id": 66, "label": "CLIENT-066", "name": "خیاطی شماره ۶۶"},
  {"id": 67, "label": "CLIENT-067", "name": "خیاطی شماره ۶۷"},
  {"id": 68, "label": "CLIENT-068", "name": "خیاطی شماره ۶۸"},
  {"id": 69, "label": "CLIENT-069", "name": "خیاطی شماره ۶۹"},
  {"id": 70, "label": "CLIENT-070", "name": "خیاطی شماره ۷۰"},
  {"id": 71, "label": "CLIENT-071", "name": "خیاطی شماره ۷۱"},
  {"id": 72, "label": "CLIENT-072", "name": "خیاطی شماره ۷۲"},
  {"id": 73, "label": "CLIENT-073", "name": "خیاطی شماره ۷۳"},
  {"id": 74, "label": "CLIENT-074", "name": "خیاطی شماره ۷۴"},
  {"id": 75, "label": "CLIENT-075", "name": "خیاطی شماره ۷۵"},
  {"id": 76, "label": "CLIENT-076", "name": "خیاطی شماره ۷۶"},
  {"id": 77, "label": "CLIENT-077", "name": "خیاطی شماره ۷۷"},
  {"id": 78, "label": "CLIENT-078", "name": "خیاطی شماره ۷۸"},
  {"id": 79, "label": "CLIENT-079", "name": "خیاطی شماره ۷۹"},
  {"id": 80, "label": "CLIENT-080", "name": "خیاطی شماره ۸۰"},
  {"id": 81, "label": "CLIENT-081", "name": "خیاطی شماره ۸۱"},
  {"id": 82, "label": "CLIENT-082", "name": "خیاطی شماره ۸۲"},
  {"id": 83, "label": "CLIENT-083", "name": "خیاطی شماره ۸۳"},
  {"id": 84, "label": "CLIENT-084", "name": "خیاطی شماره ۸۴"},
  {"id": 85, "label": "CLIENT-085", "name": "خیاطی شماره ۸۵"},
  {"id": 86, "label": "CLIENT-086", "name": "خیاطی شماره ۸۶"},
  {"id": 87, "label": "CLIENT-087", "name": "خیاطی شماره ۸۷"},
  {"id": 88, "label": "CLIENT-088", "name": "خیاطی شماره ۸۸"},
  {"id": 89, "label": "CLIENT-089", "name": "خیاطی شماره ۸۹"},
  {"id": 90, "label": "CLIENT-090", "name": "خیاطی شماره ۹۰"},
  {"id": 91, "label": "CLIENT-091", "name": "خیاطی شماره ۹۱"},
  {"id": 92, "label": "CLIENT-092", "name": "خیاطی شماره ۹۲"},
  {"id": 93, "label": "CLIENT-093", "name": "خیاطی شماره ۹۳"},
  {"id": 94, "label": "CLIENT-094", "name": "خیاطی شماره ۹۴"},
  {"id": 95, "label": "CLIENT-095", "name": "خیاطی شماره ۹۵"},
  {"id": 96, "label": "CLIENT-096", "name": "خیاطی شماره ۹۶"},
  {"id": 97, "label": "CLIENT-097", "name": "خیاطی شماره ۹۷"},
  {"id": 98, "label": "CLIENT-098", "name": "خیاطی شماره ۹۸"},
  {"id": 99, "label": "CLIENT-099", "name": "خیاطی شماره ۹۹"},
  {"id": 100, "label": "CLIENT-100", "name": "خیاطی شماره ۱۰۰"}
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
