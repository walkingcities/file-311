#!/usr/bin/env python3
"""Prepare and submit an Ask Mountain View street-light report. Nothing is submitted without --confirm."""

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

FORM = "https://clients.comcate.com/newrequest.php"
GOVT_ID = "128"
CITY = "Mountain View"
ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "catalog.json"
PREVIEW_PATH = Path.home() / ".config" / "mountainview311" / "preview.json"
STREET_LIGHT_ID = 10878
TOPIC_ID = 2643
CONCERN = "1"
USER_AGENT = "mountainview-311"

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
        die(f"No Mountain View request type matches {query!r}. This skill files Street Lights only.")
    if len(matches) > 1:
        lines = "\n".join(f"{item['id']}\t{item['name'].strip()}" for item in matches)
        die(f"More than one request type matches {query!r}:\n{lines}")
    return matches[0]


def cookie_header(response):
    headers = getattr(response, "headers", None)
    raw = []
    if headers is None:
        return ""
    if hasattr(headers, "get_all"):
        raw = headers.get_all("Set-Cookie") or []
    elif isinstance(headers, dict):
        value = headers.get("Set-Cookie")
        if isinstance(value, list):
            raw = value
        elif value:
            raw = [value]
    pairs = []
    for item in raw:
        pair = str(item).split(";", 1)[0].strip()
        if pair:
            pairs.append(pair)
    return "; ".join(pairs)


def fetch(request):
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return getattr(response, "status", 200), response.read(), cookie_header(response)
    except urllib.error.HTTPError as error:
        return error.code, error.read(), cookie_header(error)
    except urllib.error.URLError as error:
        die(f"Could not reach Ask Mountain View. Check that the machine is online and try again. {error}")


def encode_multipart(fields, photo):
    boundary = "----mountainview311" + uuid.uuid4().hex
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
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"file1\"; filename=\"{filename}\"\r\n"
            f"Content-Type: {mime}\r\n\r\n"
        ).encode()
        + file_bytes
        + b"\r\n"
    )
    chunks.append(f"--{boundary}--\r\n".encode())
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


def request_text(description, address):
    chosen = (description or "").strip()
    if not chosen:
        return f"Street light is out at {address}."
    if address.casefold() in chosen.casefold():
        return chosen
    return f"{chosen} Location: {address}."


def confirmation_text(html):
    text = re.sub(r"(?is)<script\b.*?>.*?</script>", " ", html)
    text = re.sub(r"(?is)<style\b.*?>.*?</style>", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def parse_confirmation(body):
    html = body.decode("utf-8", errors="replace")
    lowered = html.lower()
    text = confirmation_text(html)
    if "sendrequestbutton" in lowered or 'name="mainform"' in lowered:
        die(
            "Ask Mountain View returned the request form instead of a confirmation. "
            "The anonymous street-light report was not accepted. No account was created."
        )
    match = re.search(
        r"(?:request|case|reference|tracking)\s*(?:id|number|#)?\s*[:#]?\s*(\d{3,})",
        text,
        re.I,
    )
    request_id = match.group(1) if match else ""
    if not request_id and not re.search(r"thank you|submitted|received", text, re.I):
        snippet = text[:400] or "The page was empty."
        die(f"Ask Mountain View did not confirm the report. {snippet}")
    return request_id, text


def command_list(args):
    needle = (args.query or "").strip()
    for item in load_catalog():
        if needle and not tokens_match(needle, item["name"]):
            continue
        print(f"{item['id']}\t{item['name'].strip()}")


def command_show(args):
    print(json.dumps(find_type(load_catalog(), args.query), indent=2))


def command_prepare(args):
    request_type = find_type(load_catalog(), args.type)
    if request_type["id"] != STREET_LIGHT_ID:
        die("This skill files Street Lights only.")
    photo = str(Path(args.photo).expanduser().resolve())
    if not Path(photo).is_file():
        die(f"Photo not found: {photo}")
    lat, lon = photo_location(photo)
    place = reverse_geocode(lat, lon, CITY)
    if args.cross:
        place["cross_street"] = args.cross
    description = request_text(args.description, place["address"])
    upload = jpeg_for_upload(photo, PREVIEW_PATH.parent)
    preview = {
        "type_id": request_type["id"],
        "topic_id": request_type["topic_id"],
        "type_name": request_type["name"],
        "topic": request_type["topic"],
        "request_type": request_type["request_type"],
        "note": (request_type.get("note") or "").strip(),
        "description": description,
        "latitude": lat,
        "longitude": lon,
        "address": place["address"],
        "cross_street": place["cross_street"],
        "zipcode": place["zipcode"],
        "photo": upload,
        "original_photo": photo,
        "public": True,
        "anonymous": True,
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
    if preview.get("type_id") != STREET_LIGHT_ID or preview.get("topic_id") != TOPIC_ID:
        die("This skill files Street Lights only.")
    photo = preview.get("photo")
    if not photo or not Path(photo).expanduser().is_file():
        die(f"Photo not found: {photo}. Run prepare again.")
    try:
        lat = float(preview["latitude"])
        lon = float(preview["longitude"])
    except (KeyError, TypeError, ValueError):
        die("This preview has no location. Run prepare again.")
    place = reverse_geocode(lat, lon, CITY)
    description = request_text(preview.get("description"), place["address"])
    status, _body, cookie = fetch(
        urllib.request.Request(
            f"{FORM}?id={GOVT_ID}",
            headers={"User-Agent": USER_AGENT, "Accept": "text/html"},
        )
    )
    if status >= 400:
        die(f"Ask Mountain View returned {status} for the request form.")
    if "PHPSESSID=" not in cookie or f"THE_GOVT={GOVT_ID}" not in cookie:
        die("Ask Mountain View did not start a session. No report was sent.")
    fields = {
        "fbreason": str(TOPIC_ID),
        "fbsubreason": str(STREET_LIGHT_ID),
        "fbtype": CONCERN,
        "mailsent": description,
        "autogen": "1",
        "requestsubmit": "1",
        "newuser": "0",
        "incfields": "0",
        "baseAddrType": "1",
        "attachmentCnt": "1",
        "title1": "Street light",
        "val": "",
    }
    data, content_type = encode_multipart(fields, str(Path(photo).expanduser()))
    status, body, _cookie = fetch(
        urllib.request.Request(
            FORM,
            data=data,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html",
                "Content-Type": content_type,
                "Cookie": cookie,
            },
            method="POST",
        )
    )
    if status >= 400:
        die(f"Ask Mountain View returned {status}. The report was not confirmed.")
    request_id, text = parse_confirmation(body)
    print("Submitted to Ask Mountain View.")
    if request_id:
        print(f"Request {request_id}.")
    else:
        print("The confirmation page did not include a request id.")
    print(text)


def main():
    parser = argparse.ArgumentParser(description="Prepare and submit an Ask Mountain View street-light report.")
    sub = parser.add_subparsers(dest="command", required=True)

    list_parser = sub.add_parser("list")
    list_parser.add_argument("query", nargs="?")
    list_parser.set_defaults(func=command_list)

    show_parser = sub.add_parser("show")
    show_parser.add_argument("query")
    show_parser.set_defaults(func=command_show)

    prepare_parser = sub.add_parser("prepare")
    prepare_parser.add_argument("--photo", required=True)
    prepare_parser.add_argument("--type", default="Street Lights")
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
