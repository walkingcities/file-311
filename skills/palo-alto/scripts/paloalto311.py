#!/usr/bin/env python3
"""Prepare and submit a Palo Alto 311 report. Nothing is submitted without --confirm."""

import argparse
import json
import mimetypes
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

CLIENT_ID = "406"
SPACE_ID = "26742"
API = "https://vc0.publicstuff.com"
GEOCODE = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/reverseGeocode"
ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "catalog.json"
ACCOUNT_PATH = Path.home() / ".config" / "paloalto311" / "account.json"
PREVIEW_PATH = Path.home() / ".config" / "paloalto311" / "preview.json"
SWIFT_GPS = Path(__file__).resolve().parent / "photo-gps.swift"
STREET_LIGHT_ID = 32794

sys.stdout.reconfigure(line_buffering=True)


def die(message, code=1):
    print(message, file=sys.stderr)
    raise SystemExit(code)


def load_catalog():
    return json.loads(CATALOG_PATH.read_text())


def find_type(catalog, query):
    query = query.strip()
    if query.isdigit():
        matches = [item for item in catalog if item["id"] == int(query)]
    else:
        needle = query.lower()
        exact = [item for item in catalog if item["name"].lower() == needle]
        matches = exact or [item for item in catalog if needle in item["name"].lower()]
    if not matches:
        die(f"No Palo Alto 311 request type matches {query!r}. Run: paloalto311.py list")
    if len(matches) > 1:
        lines = "\n".join(f"{item['id']}\t{item['name']}" for item in matches)
        die(f"More than one request type matches {query!r}:\n{lines}")
    return matches[0]


def load_account():
    if not ACCOUNT_PATH.exists():
        return None
    return json.loads(ACCOUNT_PATH.read_text())


def save_account(account):
    ACCOUNT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ACCOUNT_PATH.write_text(json.dumps(account, indent=2) + "\n")
    os.chmod(ACCOUNT_PATH, 0o600)


def api_request(path, fields, photo=None):
    data, content_type = encode_form(fields, photo)
    request = urllib.request.Request(
        API + path,
        data=data,
        headers={
            "PublicStuff-Client": CLIENT_ID,
            "Content-Type": content_type,
            "Accept": "application/json",
            "User-Agent": "paloalto-311",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = response.read().decode()
    except urllib.error.HTTPError as error:
        body = error.read().decode()
    if not body.strip():
        die("PaloAlto311 returned an empty response.")
    payload = json.loads(body)
    status = payload.get("response", {}).get("status", {})
    if status.get("code") != 200:
        die(status.get("message") or body)
    return payload["response"]


def encode_form(fields, photo):
    if photo is None:
        return urllib.parse.urlencode(fields).encode(), "application/x-www-form-urlencoded"
    boundary = "----paloalto311" + uuid.uuid4().hex
    chunks = []
    for key, value in fields.items():
        chunks.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{key}\"\r\n\r\n{value}\r\n".encode()
        )
    filename = Path(photo).name
    mime = mimetypes.guess_type(filename)[0] or "image/jpeg"
    file_bytes = Path(photo).read_bytes()
    chunks.append(
        (
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"uploadedfile\"; filename=\"{filename}\"\r\n"
            f"Content-Type: {mime}\r\n\r\n"
        ).encode()
        + file_bytes
        + b"\r\n"
    )
    chunks.append(f"--{boundary}--\r\n".encode())
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


def photo_location(path):
    suffix = Path(path).suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        return jpeg_gps(path)
    if suffix in {".heic", ".heif"}:
        return swift_gps(path)
    die("This photo has no location.")


def jpeg_gps(path):
    tiff = exif_tiff(Path(path).read_bytes())
    coords = tiff_gps(tiff) if tiff else None
    if coords is None:
        die("This photo has no location.")
    return coords


def swift_gps(path):
    swift = shutil.which("swift")
    if not swift or not SWIFT_GPS.is_file():
        die("This HEIC photo needs Swift to read its location. Export it as a JPEG, or install the Swift tools.")
    result = subprocess.run([swift, str(SWIFT_GPS), path], text=True, capture_output=True)
    if result.returncode != 0:
        die(result.stderr.strip() or "This photo has no location.")
    try:
        lat, lon = result.stdout.split()
        return float(lat), float(lon)
    except ValueError:
        die(result.stderr.strip() or "This photo has no location.")


def exif_tiff(data):
    if len(data) < 4 or data[:2] != b"\xff\xd8":
        return None
    offset = 2
    while offset + 4 <= len(data):
        if data[offset] != 0xFF:
            return None
        marker = data[offset + 1]
        if marker == 0xDA:
            return None
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            offset += 2
            continue
        length = int.from_bytes(data[offset + 2 : offset + 4], "big")
        if length < 2 or offset + 2 + length > len(data):
            return None
        if marker == 0xE1:
            payload = data[offset + 4 : offset + 2 + length]
            if payload.startswith(b"Exif\x00\x00"):
                return payload[6:]
        offset += 2 + length
    return None


def tiff_gps(tiff):
    if len(tiff) < 8 or tiff[:2] not in (b"II", b"MM"):
        return None
    endian = "little" if tiff[:2] == b"II" else "big"

    def u16(off):
        return int.from_bytes(tiff[off : off + 2], endian)

    def u32(off):
        return int.from_bytes(tiff[off : off + 4], endian)

    if u16(2) != 42:
        return None
    entries = ifd_entries(tiff, u32(4), u16)
    gps_entry = entries.get(0x8825)
    if not gps_entry or gps_entry[0] != 4 or gps_entry[1] != 1:
        return None
    gps = ifd_entries(tiff, u32(gps_entry[2]), u16)
    lat = gps_degrees(tiff, gps.get(2), gps.get(1), endian)
    lon = gps_degrees(tiff, gps.get(4), gps.get(3), endian)
    if lat is None or lon is None:
        return None
    return lat, lon


def ifd_entries(tiff, offset, u16):
    if offset < 0 or offset + 2 > len(tiff):
        return {}
    count = u16(offset)
    entries = {}
    for index in range(count):
        base = offset + 2 + index * 12
        if base + 12 > len(tiff):
            break
        tag = u16(base)
        typ = u16(base + 2)
        number = int.from_bytes(tiff[base + 4 : base + 8], "little" if tiff[:2] == b"II" else "big")
        entries[tag] = (typ, number, base + 8)
    return entries


def component_size(typ):
    return {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 7: 1, 9: 4, 10: 8}.get(typ, 0)


def entry_offset(tiff, entry, endian):
    typ, count, value_at = entry
    size = component_size(typ) * count
    if size <= 4:
        return value_at
    return int.from_bytes(tiff[value_at : value_at + 4], endian)


def gps_degrees(tiff, rationals, ref, endian):
    if not rationals or rationals[0] != 5 or rationals[1] < 3:
        return None
    start = entry_offset(tiff, rationals, endian)
    if start < 0 or start + 24 > len(tiff):
        return None
    parts = []
    for index in range(3):
        base = start + index * 8
        num = int.from_bytes(tiff[base : base + 4], endian)
        den = int.from_bytes(tiff[base + 4 : base + 8], endian)
        parts.append(num / den if den else 0)
    degrees = parts[0] + parts[1] / 60 + parts[2] / 3600
    if ref:
        letter = tiff[entry_offset(tiff, ref, endian) : entry_offset(tiff, ref, endian) + 1]
        if letter in (b"S", b"W"):
            degrees = -degrees
    return degrees


def geocode(lat, lon):
    url = f"{GEOCODE}?f=json&location={lon},{lat}"
    with urllib.request.urlopen(url, timeout=30) as response:
        payload = json.loads(response.read().decode())
    address = payload.get("address") or {}
    city = address.get("City") or ""
    if not city:
        die("Could not find that place. Check that the machine is online and try the photo again.")
    if city != "Palo Alto":
        die(f"This photo is in {city}. Palo Alto 311 reports are only for inside the city.")
    street = address.get("Address") or ""
    state = address.get("RegionAbbr") or "CA"
    postal = address.get("Postal") or ""
    formatted = ", ".join(part for part in [street, city, f"{state} {postal}".strip()] if part)
    cross = ""
    cross_url = f"{GEOCODE}?f=json&featureTypes=StreetInt&location={lon},{lat}"
    try:
        with urllib.request.urlopen(cross_url, timeout=30) as response:
            cross_payload = json.loads(response.read().decode())
        cross = (cross_payload.get("address") or {}).get("ShortLabel") or ""
    except urllib.error.URLError:
        cross = ""
    return {"address": formatted, "city": city, "zipcode": postal, "cross_street": cross}


def jpeg_for_upload(path):
    suffix = Path(path).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".gif", ".tif", ".tiff", ".bmp", ".webp"}:
        return path
    if suffix not in {".heic", ".heif"}:
        die(f"PaloAlto311 does not accept {suffix or 'that'} photos. Use a JPEG or HEIC photo.")
    destination = PREVIEW_PATH.parent / "street-light.jpg"
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["sips", "-s", "format", "jpeg", path, "--out", str(destination)],
        check=True,
        capture_output=True,
    )
    return str(destination)


def field_by_name(request_type, name):
    for field in request_type["fields"]:
        if field["name"] == name:
            return field
    return None


def build_custom_fields(request_type, values, account):
    custom = {}
    missing = []
    for field in request_type["fields"]:
        if field["type"] == "display":
            continue
        raw = values.get(str(field["id"]))
        if raw is None and field["name"] in {"Name", "Contact Name"} and account:
            raw = account.get("name")
        if raw is None and field["name"] == "Phone Number" and account:
            raw = account.get("phone")
        if field["required"] and (raw is None or str(raw).strip() == ""):
            missing.append(field)
            continue
        if raw is None or str(raw).strip() == "":
            continue
        if field["options"] and raw not in field["options"]:
            die(f"{field['name']} must be one of: {', '.join(field['options'])}")
        custom[str(field["id"])] = raw
    return custom, missing


def command_list(args):
    needle = (args.query or "").lower()
    for item in load_catalog():
        if needle and needle not in item["name"].lower():
            continue
        print(f"{item['id']}\t{item['name']}")


def command_show(args):
    item = find_type(load_catalog(), args.query)
    print(json.dumps(item, indent=2))


def command_login(_args):
    email = os.environ.get("PALOALTO311_EMAIL", "").strip()
    password = os.environ.get("PALOALTO311_PASSWORD", "")
    name = os.environ.get("PALOALTO311_NAME", "").strip()
    phone = os.environ.get("PALOALTO311_PHONE", "").strip()
    if not email or not password or not name or not phone:
        die("Set PALOALTO311_EMAIL, PALOALTO311_PASSWORD, PALOALTO311_NAME, and PALOALTO311_PHONE.")
    response = api_request(
        "/api/2.1/user_login",
        {"email": email, "password": password, "device": "iframe", "client_id": CLIENT_ID},
    )
    save_account({"api_key": response["api_key"], "email": email, "name": name, "phone": phone})
    print(f"Signed in as {email}. The password was not saved. Account file: {ACCOUNT_PATH}")


def command_prepare(args):
    catalog = load_catalog()
    request_type = find_type(catalog, args.type)
    photo = str(Path(args.photo).expanduser().resolve())
    if not Path(photo).is_file():
        die(f"Photo not found: {photo}")
    if args.lat is not None and args.lon is not None:
        lat, lon = args.lat, args.lon
    else:
        lat, lon = photo_location(photo)
    place = geocode(lat, lon)
    if args.cross:
        place["cross_street"] = args.cross
    account = load_account()
    values = dict(args.field or [])
    if request_type["id"] == STREET_LIGHT_ID:
        address_field = field_by_name(request_type, "Light Location Address")
        cross_field = field_by_name(request_type, "Cross Street")
        condition_field = field_by_name(request_type, "Condition of Light")
        damage_field = field_by_name(request_type, "Is there damage to the light?")
        if address_field:
            values.setdefault(str(address_field["id"]), place["address"])
        if cross_field and place["cross_street"]:
            values.setdefault(str(cross_field["id"]), place["cross_street"])
        if condition_field:
            values.setdefault(str(condition_field["id"]), args.condition)
        if damage_field:
            values.setdefault(str(damage_field["id"]), args.damage)
    description = args.description
    if description is None and request_type["id"] == STREET_LIGHT_ID:
        description = "Street light is out."
    custom, missing = build_custom_fields(request_type, values, account)
    upload = jpeg_for_upload(photo)
    preview = {
        "type_id": request_type["id"],
        "type_name": request_type["name"],
        "title": request_type["name"],
        "description": description or "",
        "latitude": lat,
        "longitude": lon,
        "address": place["address"],
        "cross_street": place["cross_street"],
        "zipcode": place["zipcode"],
        "photo": upload,
        "original_photo": photo,
        "custom_fields": custom,
        "missing_fields": [
            {"id": field["id"], "name": field["name"], "options": field["options"], "staff_only": field["staff_only"]}
            for field in missing
        ],
        "staff_only_fields": [field["name"] for field in request_type["fields"] if field["staff_only"] and field["type"] != "display"],
        "public": not request_type["force_private"],
    }
    PREVIEW_PATH.parent.mkdir(parents=True, exist_ok=True)
    PREVIEW_PATH.write_text(json.dumps(preview, indent=2) + "\n")
    os.chmod(PREVIEW_PATH, 0o600)
    print(json.dumps(preview, indent=2))


def command_submit(args):
    if not args.confirm:
        die("Refusing to submit. Show the preview to the user, then run again with --confirm.")
    preview_path = Path(args.preview).expanduser() if args.preview else PREVIEW_PATH
    if not preview_path.exists():
        die(f"No preview at {preview_path}. Run prepare first.")
    preview = json.loads(preview_path.read_text())
    account = load_account()
    if not account or not account.get("api_key"):
        die(f"Not signed in. Ask for PaloAlto311 email, password, name, and phone, then run login. Account file: {ACCOUNT_PATH}")
    request_type = find_type(load_catalog(), str(preview["type_id"]))
    custom, missing = build_custom_fields(request_type, preview.get("custom_fields") or {}, account)
    if missing:
        names = ", ".join(field["name"] for field in missing)
        die(f"Still missing: {names}")
    if request_type["id"] == STREET_LIGHT_ID and preview.get("cross_street"):
        cross_field = field_by_name(request_type, "Cross Street")
        address_field = field_by_name(request_type, "Light Location Address")
        if cross_field:
            custom[str(cross_field["id"])] = preview["cross_street"]
        if address_field:
            custom[str(address_field["id"])] = preview["address"]
    fields = {
        "title": preview.get("title") or request_type["name"],
        "description": preview.get("description") or "",
        "request_type_id": str(preview["type_id"]),
        "latitude": str(preview["latitude"]),
        "longitude": str(preview["longitude"]),
        "address": preview["address"],
        "user_address": preview["address"],
        "long_address": preview["address"],
        "zipcode": preview.get("zipcode") or "",
        "space_id": SPACE_ID,
        "client_id": CLIENT_ID,
        "device": "iframe",
        "api_key": account["api_key"],
    }
    for field_id, value in custom.items():
        fields[f"custom_field_{field_id}"] = json.dumps(value)
    photo = preview.get("photo")
    if photo:
        fields["has_image"] = "1"
    response = api_request("/api/2.0/request_submit", fields, photo)
    request_id = response.get("request_id")
    request_url = response.get("request_url") or (
        f"https://iframe.publicstuff.com/#?client_id={CLIENT_ID}&request_id={request_id}"
    )
    print(f"Submitted to PaloAlto311. Request {request_id}.")
    print(request_url)


def parse_field(value):
    if "=" not in value:
        die(f"--field must look like 3259=Matadero Ave & Park Blvd, not {value!r}")
    key, raw = value.split("=", 1)
    return key, raw


def main():
    parser = argparse.ArgumentParser(description="Prepare and submit a Palo Alto 311 report.")
    sub = parser.add_subparsers(dest="command", required=True)

    list_parser = sub.add_parser("list")
    list_parser.add_argument("query", nargs="?")
    list_parser.set_defaults(func=command_list)

    show_parser = sub.add_parser("show")
    show_parser.add_argument("query")
    show_parser.set_defaults(func=command_show)

    login_parser = sub.add_parser("login")
    login_parser.set_defaults(func=command_login)

    prepare_parser = sub.add_parser("prepare")
    prepare_parser.add_argument("--photo", required=True)
    prepare_parser.add_argument("--type", default="Street Light Out")
    prepare_parser.add_argument("--description")
    prepare_parser.add_argument("--cross")
    prepare_parser.add_argument("--condition", default="Out")
    prepare_parser.add_argument("--damage", default="No")
    prepare_parser.add_argument("--lat", type=float)
    prepare_parser.add_argument("--lon", type=float)
    prepare_parser.add_argument("--field", action="append", type=parse_field)
    prepare_parser.set_defaults(func=command_prepare)

    submit_parser = sub.add_parser("submit")
    submit_parser.add_argument("--preview")
    submit_parser.add_argument("--confirm", action="store_true")
    submit_parser.set_defaults(func=command_submit)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
