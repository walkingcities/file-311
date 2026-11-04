"""Read a photo's location and convert HEIC into a JPEG. No city API."""

import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

SWIFT_GPS = Path(__file__).resolve().parent / "photo-gps.swift"


def die(message, code=1):
    print(message, file=sys.stderr)
    raise SystemExit(code)


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


def jpeg_for_upload(path, directory):
    suffix = Path(path).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".gif", ".tif", ".tiff", ".bmp", ".webp"}:
        return path
    if suffix not in {".heic", ".heif"}:
        die(f"This report does not accept {suffix or 'that'} photos. Use a JPEG or HEIC photo.")
    digest = hashlib.sha256(str(Path(path).resolve()).encode()).hexdigest()[:16]
    destination = Path(directory) / f"upload-{digest}.jpg"
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            ["sips", "-s", "format", "jpeg", path, "--out", str(destination)],
            check=True,
            capture_output=True,
        )
    except FileNotFoundError:
        die("This HEIC photo needs the macOS sips tool to become a JPEG. Export it as a JPEG and use that file.")
    except subprocess.CalledProcessError:
        die("Could not convert this HEIC photo to JPEG. Export it as a JPEG and use that file.")
    return str(destination)
