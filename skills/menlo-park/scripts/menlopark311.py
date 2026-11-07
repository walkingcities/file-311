#!/usr/bin/env python3
"""Prepare and submit an ACT Menlo Park report. Nothing is submitted without --confirm."""

import argparse
import json
import mimetypes
import os
import re
import sys
import urllib.error
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

API = "https://seeclickfix.com"
CITY = "Menlo Park"
ORGANIZATION = "Menlo Park"
ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "catalog.json"
ACCOUNT_PATH = Path.home() / ".config" / "menlopark311" / "account.json"
PREVIEW_PATH = Path.home() / ".config" / "menlopark311" / "preview.json"
STREET_LIGHT_ID = 94217
POTHOLE_ID = 94213
CALTRANS = (
    "Potholes on Willow Road, Bayshore Road, and El Camino Real are repaired by Caltrans. "
    "Call (916) 654-5266 or visit http://www.dot.ca.gov/hq/maint/msrsubmit."
)
NAMED_ONLY = {
    "Traffic Enforcement": (
        "Use this only when the person asked for traffic enforcement. "
        "A car in a red zone or blocking a driveway is a call to police dispatch at 650-330-6300."
    ),
    "General Code Enforcement Issue": "Use this only when the person asked for code enforcement.",
    "Gas leaf blower/string trimmer use": (
        "Use this only when the person asked to report a gas leaf blower or string trimmer. "
        "If the blower is in use now, call 650-330-6300."
    ),
}

sys.stdout.reconfigure(line_buffering=True)


def die(message, code=1):
    print(message, file=sys.stderr)
    raise SystemExit(code)


def load_catalog():
    catalog = json.loads(CATALOG_PATH.read_text())
    for item in catalog:
        item["name"] = item["name"].strip()
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
        die(f"No Menlo Park request type matches {query!r}. Run: menlopark311.py list")
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


def api_call(path, token=None, fields=None, photo=None):
    headers = {"Accept": "application/json", "User-Agent": "menlopark-311"}
    data = None
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if fields is not None:
        data, content_type = encode_multipart(fields, photo)
        headers["Content-Type"] = content_type
    request = urllib.request.Request(API + path, data=data, headers=headers, method="POST" if fields is not None else "GET")
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            status = response.status
            body = response.read().decode()
    except urllib.error.HTTPError as error:
        status = error.code
        body = error.read().decode()
    except urllib.error.URLError as error:
        die(f"Could not reach SeeClickFix. Check that the machine is online and try again. {error}")
    if not body.strip():
        die("SeeClickFix returned an empty response.")
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        die("SeeClickFix returned a response that was not JSON.")
    if status >= 400:
        die(error_text(payload) or f"SeeClickFix returned {status}.")
    return status, payload


def error_text(payload):
    errors = payload.get("errors") if isinstance(payload, dict) else None
    if isinstance(errors, dict):
        parts = []
        for key, messages in errors.items():
            if isinstance(messages, list):
                parts.append(f"{key}: {'; '.join(str(item) for item in messages)}")
            else:
                parts.append(f"{key}: {messages}")
        return " ".join(parts)
    if isinstance(errors, str):
        return errors
    return ""


def encode_multipart(fields, photo):
    boundary = "----menlopark311" + uuid.uuid4().hex
    chunks = []
    for key, value in fields.items():
        chunks.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{key}\"\r\n\r\n{value}\r\n".encode()
        )
    if photo:
        filename = Path(photo).name
        mime = mimetypes.guess_type(filename)[0] or "image/jpeg"
        file_bytes = Path(photo).read_bytes()
        chunks.append(
            (
                f"--{boundary}\r\nContent-Disposition: form-data; name=\"answers[issue_image]\"; filename=\"{filename}\"\r\n"
                f"Content-Type: {mime}\r\n\r\n"
            ).encode()
            + file_bytes
            + b"\r\n"
        )
    chunks.append(f"--{boundary}--\r\n".encode())
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


def caltrans_street(address):
    text = (address or "").casefold()
    if "el camino real" in text or "bayshore" in text:
        return True
    return bool(re.search(r"\bwillow\b", text))


def type_caution(request_type, address):
    parts = []
    named = NAMED_ONLY.get(request_type["name"])
    if named:
        parts.append(named)
    if request_type["id"] == POTHOLE_ID and caltrans_street(address):
        parts.append(CALTRANS)
    note = (request_type.get("note") or "").strip()
    if "911" in note and note not in parts:
        parts.append(note)
    return "\n".join(parts)


def issue_title(request_type, title):
    chosen = (title or "").strip()
    if chosen:
        return chosen
    if request_type["id"] == STREET_LIGHT_ID:
        return "Street light is out."
    return ""


def menlo_park_offers(payload, type_id):
    for item in payload.get("request_types") or []:
        url = (item.get("url") or "").rstrip("/")
        if item.get("organization") == ORGANIZATION and url.endswith(f"/{type_id}"):
            return True
    return False


def organization_names(payload):
    names = []
    for item in payload.get("request_types") or []:
        name = item.get("organization") or "none"
        if name not in names:
            names.append(name)
    return names


def command_list(args):
    needle = (args.query or "").strip()
    for item in load_catalog():
        if needle and not tokens_match(needle, item["name"]):
            continue
        print(f"{item['id']}\t{item['name'].strip()}")


def command_show(args):
    print(json.dumps(find_type(load_catalog(), args.query), indent=2))


def command_login(_args):
    token = os.environ.get("MENLOPARK311_TOKEN", "").strip()
    if not token:
        die("Set MENLOPARK311_TOKEN to the CivicPlus personal access token.")
    if not token.startswith("--"):
        die("Copy only the token value that starts with --. Leave off the name and date shown before it.")
    _status, profile = api_call("/api/v2/profile", token=token)
    user_id = profile.get("id") if isinstance(profile, dict) else None
    if not user_id:
        die("That token did not sign in. Create a new personal access token and try again.")
    name = (profile.get("name") or "").strip()
    save_account({"token": token, "id": user_id, "name": name})
    who = name or f"user {user_id}"
    print(f"Signed in as {who}. The token was saved. Account file: {ACCOUNT_PATH}")


def command_prepare(args):
    request_type = find_type(load_catalog(), args.type)
    if request_type.get("block_submission"):
        note = (request_type.get("note") or "").strip()
        die(note or f"{request_type['name']} cannot be submitted here.")
    photo = str(Path(args.photo).expanduser().resolve())
    if not Path(photo).is_file():
        die(f"Photo not found: {photo}")
    lat, lon = photo_location(photo)
    place = reverse_geocode(lat, lon, CITY)
    if args.cross:
        place["cross_street"] = args.cross
    title = issue_title(request_type, args.title)
    description = args.description if args.description is not None else ""
    account = load_account()
    upload = jpeg_for_upload(photo, PREVIEW_PATH.parent)
    missing = []
    if not title:
        missing.append({"id": "summary", "name": "Issue Title"})
    preview = {
        "type_id": request_type["id"],
        "type_name": request_type["name"],
        "note": (request_type.get("note") or "").strip(),
        "note_public": bool(request_type.get("note_public")),
        "caution": type_caution(request_type, place["address"]),
        "title": title,
        "description": description,
        "latitude": lat,
        "longitude": lon,
        "address": place["address"],
        "cross_street": place["cross_street"],
        "zipcode": place["zipcode"],
        "photo": upload,
        "original_photo": photo,
        "missing_fields": missing,
        "public": not request_type.get("private_visibility"),
        "reporter_name": (account or {}).get("name") or "",
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
    if not account or not account.get("token"):
        die(f"Not signed in. Ask for the ACT Menlo Park token, then run login. Account file: {ACCOUNT_PATH}")
    photo = preview.get("photo")
    if not photo or not Path(photo).expanduser().is_file():
        die(f"Photo not found: {photo}. Run prepare again.")
    try:
        lat = float(preview["latitude"])
        lon = float(preview["longitude"])
    except (KeyError, TypeError, ValueError):
        die("This preview has no location. Run prepare again.")
    place = reverse_geocode(lat, lon, CITY)
    request_type = find_type(load_catalog(), str(preview["type_id"]))
    if request_type.get("block_submission"):
        note = (request_type.get("note") or "").strip()
        die(note or f"{request_type['name']} cannot be submitted here.")
    address = place["address"]
    if request_type["id"] == POTHOLE_ID and caltrans_street(address):
        die(CALTRANS)
    title = (preview.get("title") or "").strip()
    if not title:
        die("Still missing: Issue Title")
    _status, offered = api_call(f"/api/v2/issues/new?lat={lat}&lng={lon}")
    if not menlo_park_offers(offered, request_type["id"]):
        found = ", ".join(organization_names(offered)) or "none"
        die(f"SeeClickFix does not offer that Menlo Park request at this pin. Organizations: {found}.")
    fields = {
        "lat": str(lat),
        "lng": str(lon),
        "address": address,
        "request_type_id": str(request_type["id"]),
        "answers[summary]": title,
    }
    description = preview.get("description") or ""
    if description:
        fields["answers[description]"] = description
    status, payload = api_call("/api/v2/issues", token=account["token"], fields=fields, photo=str(Path(photo).expanduser()))
    if status == 202:
        print("SeeClickFix accepted the report and is holding it for review.")
        return
    request_id = payload.get("id")
    if not request_id:
        die("SeeClickFix did not return a request id.")
    request_url = payload.get("html_url") or f"https://seeclickfix.com/issues/{request_id}"
    print(f"Submitted to ACT Menlo Park. Request {request_id}.")
    print(request_url)


def main():
    parser = argparse.ArgumentParser(description="Prepare and submit an ACT Menlo Park report.")
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
    prepare_parser.add_argument("--type", default="Streetlight")
    prepare_parser.add_argument("--title")
    prepare_parser.add_argument("--description")
    prepare_parser.add_argument("--cross")
    prepare_parser.set_defaults(func=command_prepare)

    submit_parser = sub.add_parser("submit")
    submit_parser.add_argument("--preview")
    submit_parser.add_argument("--confirm", action="store_true")
    submit_parser.set_defaults(func=command_submit)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
