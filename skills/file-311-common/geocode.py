"""Turn a photo location into a street address. No city 311 API."""

import json
import sys
import urllib.error
import urllib.request

GEOCODE = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/reverseGeocode"


def die(message, code=1):
    print(message, file=sys.stderr)
    raise SystemExit(code)


def reverse_geocode(lat, lon, city):
    url = f"{GEOCODE}?f=json&location={lon},{lat}"
    with urllib.request.urlopen(url, timeout=30) as response:
        payload = json.loads(response.read().decode())
    address = payload.get("address") or {}
    found = address.get("City") or ""
    if not found:
        die("Could not find that place. Check that the machine is online and try the photo again.")
    if found != city:
        die(f"This photo is in {found}. {city} 311 reports are only for inside the city.")
    street = address.get("Address") or ""
    state = address.get("RegionAbbr") or "CA"
    postal = address.get("Postal") or ""
    formatted = ", ".join(part for part in [street, found, f"{state} {postal}".strip()] if part)
    cross = ""
    cross_url = f"{GEOCODE}?f=json&featureTypes=StreetInt&location={lon},{lat}"
    try:
        with urllib.request.urlopen(cross_url, timeout=30) as response:
            cross_payload = json.loads(response.read().decode())
        cross = (cross_payload.get("address") or {}).get("ShortLabel") or ""
    except urllib.error.URLError:
        cross = ""
    return {"address": formatted, "city": found, "zipcode": postal, "cross_street": cross}
