#!/usr/bin/env python3
"""Prepare and submit a Redwood City 311 report. Nothing is submitted without --confirm."""

import argparse
import json
import mimetypes
import os
import re
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

CLIENT_ID = "226"
SPACE_ID = "29066"
API = "https://vc0.publicstuff.com"
CITY = "Redwood City"
ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "catalog.json"
ACCOUNT_PATH = Path.home() / ".config" / "myrwc" / "account.json"
PREVIEW_PATH = Path.home() / ".config" / "myrwc" / "preview.json"
STREET_LIGHT_ID = 27267
CORNER_FIELDS = {
    "Please provide street name and Cross Street.",
    "Cross streets/specific address where vehicle is located?",
}

sys.stdout.reconfigure(line_buffering=True)


def die(message, code=1):
    print(message, file=sys.stderr)
    raise SystemExit(code)


def load_catalog():
    catalog = json.loads(CATALOG_PATH.read_text())
    for item in catalog:
        item["name"] = item["name"].strip()
        for field in item["fields"]:
            field["name"] = field["name"].strip()
    return catalog


def name_tokens(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def singular(token):
    if len(token) > 3 and token.endswith("s"):
        return token[:-1]
    return token


def tokens_match(query, name):
    needles = name_tokens(query)
    hay = {singular(token) for token in name_tokens(name)}
    if not needles:
        return False
    return all(singular(needle) in hay for needle in needles)


def find_type(catalog, query):
    query = query.strip()
    if query.isdigit():
        matches = [item for item in catalog if item["id"] == int(query)]
    else:
        needle = query.lower()
        exact = [item for item in catalog if item["name"].strip().lower() == needle]
        matches = exact or [item for item in catalog if tokens_match(query, item["name"])]
    if not matches:
        die(f"No myRWC request type matches {query!r}. Run: myrwc.py list")
    if len(matches) > 1:
        lines = "\n".join(f"{item['id']}\t{item['name'].strip()}" for item in matches)
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
            "User-Agent": "myrwc",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = response.read().decode()
    except urllib.error.HTTPError as error:
        body = error.read().decode()
    if not body.strip():
        die("myRWC returned an empty response.")
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        die("myRWC returned a response that was not JSON.")
    status = payload.get("response", {}).get("status", {})
    if status.get("code") != 200:
        die(status.get("message") or body)
    return payload["response"]


def encode_form(fields, photo):
    if photo is None:
        return urllib.parse.urlencode(fields).encode(), "application/x-www-form-urlencoded"
    boundary = "----myrwc" + uuid.uuid4().hex
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


def fill_location_fields(request_type, values, cross_street, overwrite=False):
    for field in request_type["fields"]:
        if field["type"] == "display":
            continue
        if field["name"] not in CORNER_FIELDS:
            continue
        if not cross_street:
            continue
        key = str(field["id"])
        if overwrite or key not in values or str(values.get(key, "")).strip() == "":
            values[key] = cross_street


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
        if field["required"] and blank_field(raw):
            missing.append(field)
            continue
        if blank_field(raw):
            continue
        if field["type"] == "multiselect":
            raw = multiselect_values(field, raw)
        elif field["type"] == "checkbox":
            raw = checkbox_value(field, raw)
        elif field["options"] and raw not in field["options"]:
            die(f"{field['name'].strip()} must be one of: {', '.join(field['options'])}")
        custom[str(field["id"])] = raw
    return custom, missing


def type_caution(request_type):
    name = request_type["name"].strip()
    description = (request_type.get("description") or "").replace("\r\n", "\n").strip()
    confirmation = (request_type.get("confirmation") or "").replace("\r\n", "\n").strip()
    if name == "Homeless":
        return (
            "This reports encampments and people. "
            "Use it only when the person asked for a homeless report, not because a photo shows a person."
        )
    if name == "Other Street Light Problem":
        return (
            "Use this only when the person asked about a fallen pole or fallen wires. "
            "A downed wire is an emergency call, not only a 311 report."
        )
    if name == "Abandoned Vehicles":
        return (
            "Use this only when the person asked to report an abandoned vehicle. "
            "Do not invent a license plate, make, model, or color."
        )
    if name == "Residential Noise" and confirmation:
        return confirmation
    if name in {"Pothole", "Parking in Red Zone"} and description:
        return description
    return ""


def blank_field(raw):
    if raw is None or raw == []:
        return True
    if isinstance(raw, str):
        return raw.strip() == ""
    return False


def checkbox_value(field, raw):
    text = str(raw).strip().lower()
    if text in {"1", "true", "yes", "y"}:
        return "1"
    if text in {"0", "false", "no", "n"}:
        return "0"
    die(f"{field['name'].strip()} must be Yes or No.")


def multiselect_values(field, raw):
    if isinstance(raw, str):
        chosen = [part.strip() for part in raw.split(",") if part.strip()]
    elif isinstance(raw, list):
        chosen = [str(part).strip() for part in raw if str(part).strip()]
    else:
        chosen = []
    seen = []
    for part in chosen:
        if part not in seen:
            seen.append(part)
    if not seen or any(part not in field["options"] for part in seen):
        die(f"{field['name'].strip()} must be one of: {', '.join(field['options'])}")
    return seen


def command_list(args):
    needle = (args.query or "").strip()
    for item in load_catalog():
        if needle and not tokens_match(needle, item["name"]):
            continue
        print(f"{item['id']}\t{item['name'].strip()}")


def command_show(args):
    item = find_type(load_catalog(), args.query)
    print(json.dumps(item, indent=2))


def command_login(_args):
    email = os.environ.get("MYRWC_EMAIL", "").strip()
    password = os.environ.get("MYRWC_PASSWORD", "")
    name = os.environ.get("MYRWC_NAME", "").strip()
    phone = os.environ.get("MYRWC_PHONE", "").strip()
    if not email or not password or not name or not phone:
        die("Set MYRWC_EMAIL, MYRWC_PASSWORD, MYRWC_NAME, and MYRWC_PHONE.")
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
    lat, lon = photo_location(photo)
    place = reverse_geocode(lat, lon, CITY)
    if args.cross:
        place["cross_street"] = args.cross
    account = load_account()
    values = dict(args.field or [])
    fill_location_fields(request_type, values, place["cross_street"])
    description = args.description
    if description is None and request_type["id"] == STREET_LIGHT_ID:
        description = "Street light is out."
    custom, missing = build_custom_fields(request_type, values, account)
    upload = jpeg_for_upload(photo, PREVIEW_PATH.parent)
    preview = {
        "type_id": request_type["id"],
        "type_name": request_type["name"],
        "type_description": (request_type.get("description") or "").replace("\r\n", "\n").strip(),
        "confirmation": (request_type.get("confirmation") or "").replace("\r\n", "\n").strip(),
        "caution": type_caution(request_type),
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
        die(f"Not signed in. Ask for myRWC email, password, name, and phone, then run login. Account file: {ACCOUNT_PATH}")
    photo = preview.get("photo")
    if photo and not Path(photo).expanduser().is_file():
        die(f"Photo not found: {photo}. Run prepare again.")
    try:
        lat = float(preview["latitude"])
        lon = float(preview["longitude"])
    except (KeyError, TypeError, ValueError):
        die("This preview has no location. Run prepare again.")
    reverse_geocode(lat, lon, CITY)
    request_type = find_type(load_catalog(), str(preview["type_id"]))
    values = dict(preview.get("custom_fields") or {})
    fill_location_fields(request_type, values, preview.get("cross_street") or "", overwrite=True)
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
    print(f"Submitted to myRWC. Request {request_id}.")
    print(request_url)


def parse_field(value):
    if "=" not in value:
        die(f"--field must look like 3346=Broadway & Jefferson Ave, not {value!r}")
    key, raw = value.split("=", 1)
    return key, raw


def main():
    parser = argparse.ArgumentParser(description="Prepare and submit a Redwood City 311 report.")
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
    prepare_parser.add_argument("--type", default="Street Light Outage")
    prepare_parser.add_argument("--description")
    prepare_parser.add_argument("--cross")
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
