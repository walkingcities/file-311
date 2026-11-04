#!/usr/bin/env python3
"""Prepare and submit a Palo Alto 311 report. Nothing is submitted without --confirm."""

import argparse
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

COMMON = Path(__file__).resolve().parents[2] / "file-311-common"
if str(COMMON) not in sys.path:
    sys.path.insert(0, str(COMMON))
try:
    from geocode import reverse_geocode
    from photo import jpeg_for_upload, photo_location
except ModuleNotFoundError:
    print(
        "Missing file-311-common. Install it beside this skill, or copy skills/file-311-common into the same skills directory.",
        file=sys.stderr,
    )
    raise SystemExit(1)

CLIENT_ID = "406"
SPACE_ID = "26742"
API = "https://vc0.publicstuff.com"
ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "catalog.json"
ACCOUNT_PATH = Path.home() / ".config" / "paloalto311" / "account.json"
PREVIEW_PATH = Path.home() / ".config" / "paloalto311" / "preview.json"
STREET_LIGHT_ID = 32794
ADDRESS_FIELDS = {
    "Light Location Address",
    "Location Address of Lid/Cover",
    "Address or Location for Request",
}
CORNER_FIELDS = {"Cross Street", "Intersection"}

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


def fill_location_fields(request_type, values, address, cross_street, overwrite=False):
    for field in request_type["fields"]:
        if field["type"] == "display":
            continue
        if field["name"] in ADDRESS_FIELDS:
            chosen = address
        elif field["name"] in CORNER_FIELDS:
            chosen = cross_street
        else:
            continue
        if not chosen:
            continue
        key = str(field["id"])
        if overwrite or key not in values or str(values.get(key, "")).strip() == "":
            values[key] = chosen


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
    place = reverse_geocode(lat, lon, "Palo Alto")
    if args.cross:
        place["cross_street"] = args.cross
    account = load_account()
    values = dict(args.field or [])
    fill_location_fields(request_type, values, place["address"], place["cross_street"])
    if request_type["id"] == STREET_LIGHT_ID:
        condition_field = field_by_name(request_type, "Condition of Light")
        damage_field = field_by_name(request_type, "Is there damage to the light?")
        if condition_field:
            values.setdefault(str(condition_field["id"]), args.condition)
        if damage_field:
            values.setdefault(str(damage_field["id"]), args.damage)
    description = args.description
    if description is None and request_type["id"] == STREET_LIGHT_ID:
        description = "Street light is out."
    custom, missing = build_custom_fields(request_type, values, account)
    upload = jpeg_for_upload(photo, PREVIEW_PATH.parent)
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
    values = dict(preview.get("custom_fields") or {})
    fill_location_fields(
        request_type,
        values,
        preview.get("address") or "",
        preview.get("cross_street") or "",
        overwrite=True,
    )
    custom, missing = build_custom_fields(request_type, values, account)
    if missing:
        names = ", ".join(field["name"] for field in missing)
        die(f"Still missing: {names}")
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
