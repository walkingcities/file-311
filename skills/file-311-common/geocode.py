"""Turn a photo location into a street address. No city 311 API."""

import json
import sys
import urllib.error
import urllib.request

GEOCODE = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/reverseGeocode"


def die(message, code=1):
    print(message, file=sys.stderr)
    raise SystemExit(code)


def fetch_geocode(url):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "paloalto-311", "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode()
    return json.loads(body)


def same_city(found, city):
    return found.strip().casefold() == city.strip().casefold()


def reverse_geocode(lat, lon, city):
    try:
        payload = fetch_geocode(f"{GEOCODE}?f=json&location={lon},{lat}")
    except urllib.error.URLError as error:
        die(f"Could not find that place. Check that the machine is online and try the photo again. {error}")
    except json.JSONDecodeError:
        die("Could not find that place. Check that the machine is online and try the photo again.")
    address = payload.get("address") or {}
    found = (address.get("City") or "").strip()
    if not found:
        die("Could not find that place. Check that the machine is online and try the photo again.")
    if not same_city(found, city):
        die(f"This photo is in {found}. {city} 311 reports are only for inside the city.")
    street = address.get("Address") or ""
    state = address.get("RegionAbbr") or "CA"
    postal = address.get("Postal") or ""
    formatted = ", ".join(part for part in [street, found, f"{state} {postal}".strip()] if part)
    cross = ""
    try:
        cross_payload = fetch_geocode(f"{GEOCODE}?f=json&featureTypes=StreetInt&location={lon},{lat}")
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        cross_payload = {}
    cross_address = cross_payload.get("address") or {}
    cross_city = (cross_address.get("City") or "").strip()
    if not cross_city or same_city(cross_city, city):
        cross = cross_address.get("ShortLabel") or ""
    return {"address": formatted, "city": found, "zipcode": postal, "cross_street": cross}
