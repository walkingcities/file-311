"""Street-light reports for Redwood City, exercised without the myRWC server.

urllib is patched on the city script and on the shared geocoder. A test that
reaches the network fails.
"""

import argparse
import contextlib
import io
import json
import stat
import struct
import sys
import unittest
import urllib.request
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "file-311-common"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "redwood-city" / "scripts"))
import myrwc
import photo


ADDRESS = "1017 Middlefield Rd, Redwood City, CA 94063"
CORNER = "Middlefield Rd & Jefferson Ave"
CITY_URL = "https://vc0.publicstuff.com/api/2.0/request_submit"


def jpeg_with_gps():
    """A tiny JPEG whose EXIF GPS is 37.4855 N, 122.2282 W, in Redwood City."""

    def rational(numerator, denominator=1):
        return struct.pack("<II", numerator, denominator)

    tiff = bytearray(168)
    tiff[0:2] = b"II"
    tiff[2:4] = struct.pack("<H", 42)
    tiff[4:8] = struct.pack("<I", 8)
    tiff[8:10] = struct.pack("<H", 1)
    tiff[10:12] = struct.pack("<H", 0x8825)
    tiff[12:14] = struct.pack("<H", 4)
    tiff[14:18] = struct.pack("<I", 1)
    tiff[18:22] = struct.pack("<I", 26)
    tiff[26:28] = struct.pack("<H", 4)

    def entry(base, tag, typ, count, value):
        tiff[base : base + 2] = struct.pack("<H", tag)
        tiff[base + 2 : base + 4] = struct.pack("<H", typ)
        tiff[base + 4 : base + 8] = struct.pack("<I", count)
        tiff[base + 8 : base + 12] = value if isinstance(value, bytes) else struct.pack("<I", value)

    base = 28
    entry(base, 1, 2, 2, b"N\x00\x00")
    entry(base + 12, 2, 5, 3, 120)
    entry(base + 24, 3, 2, 2, b"W\x00\x00")
    entry(base + 36, 4, 5, 3, 144)
    tiff[120:144] = rational(37) + rational(29) + rational(780, 100)
    tiff[144:168] = rational(122) + rational(13) + rational(4152, 100)
    app1 = b"Exif\x00\x00" + bytes(tiff)
    return b"\xff\xd8" + b"\xff\xe1" + struct.pack(">H", 2 + len(app1)) + app1 + b"\xff\xd9"


class FakeResponse:
    def __init__(self, body):
        self.body = body.encode()

    def read(self):
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        return False


def form_values(request):
    boundary = request.get_header("Content-type").split("boundary=", 1)[1].encode()
    values = {}
    for part in request.data.split(b"--" + boundary):
        if b'name="' not in part:
            continue
        header, content = part.split(b"\r\n\r\n", 1)
        name = header.split(b'name="', 1)[1].split(b'"', 1)[0].decode()
        if content.endswith(b"\r\n"):
            content = content[:-2]
        values[name] = content if b'filename="' in header else content.decode()
    return values


class RedwoodCityStreetLightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.account_path = root / "account.json"
        self.preview_path = root / "preview.json"
        self.photo = root / "light.jpg"
        self.photo.write_bytes(jpeg_with_gps())
        for patcher in (
            patch.object(myrwc, "ACCOUNT_PATH", self.account_path),
            patch.object(myrwc, "PREVIEW_PATH", self.preview_path),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)
        network = patch("urllib.request.urlopen")
        self.network = network.start()
        self.addCleanup(network.stop)
        self.network.side_effect = self.forbid_network

    def forbid_network(self, url, *args, **kwargs):
        target = getattr(url, "full_url", url)
        raise AssertionError(f"test tried to reach the network: {target}")

    def geocode_only(self, url, *args, **kwargs):
        target = getattr(url, "full_url", url)
        if "publicstuff.com" in target:
            raise AssertionError(f"prepare contacted the city API: {target}")
        if "geocode.arcgis.com" not in target:
            raise AssertionError(f"unexpected geocoder call: {target}")
        if "StreetInt" in target:
            body = {"address": {"ShortLabel": CORNER, "City": "Redwood City"}}
        else:
            body = {
                "address": {
                    "City": "Redwood City",
                    "Address": "1017 Middlefield Rd",
                    "RegionAbbr": "CA",
                    "Postal": "94063",
                }
            }
        return FakeResponse(json.dumps(body))

    def city_api(self, url, *args, **kwargs):
        target = getattr(url, "full_url", url)
        if "geocode.arcgis.com" in target:
            return self.geocode_only(url, *args, **kwargs)
        self.assertIsInstance(url, urllib.request.Request)
        if "publicstuff.com" not in target:
            raise AssertionError(f"unexpected call: {url.full_url}")
        self.submitted = url
        payload = {
            "response": {
                "status": {"code": 200},
                "request_id": 1001,
                "request_url": "https://iframe.publicstuff.com/#?client_id=226&request_id=1001",
            }
        }
        return FakeResponse(json.dumps(payload))

    def exit_message(self, func):
        errors = io.StringIO()
        with self.assertRaises(SystemExit) as caught:
            with contextlib.redirect_stderr(errors):
                func()
        self.assertEqual(caught.exception.code, 1)
        return errors.getvalue()

    def prepare(self, **kwargs):
        args = argparse.Namespace(
            photo=kwargs.get("photo", str(self.photo)),
            type=kwargs.get("type", "Street Light Outage"),
            description=kwargs.get("description"),
            cross=kwargs.get("cross"),
            field=kwargs.get("field"),
        )
        with contextlib.redirect_stdout(io.StringIO()):
            myrwc.command_prepare(args)
        return json.loads(self.preview_path.read_text())

    def sign_in(self):
        myrwc.save_account(
            {
                "api_key": "test-api-key",
                "email": "resident@example.com",
                "name": "Ada Resident",
                "phone": "650-555-0100",
            }
        )

    def test_jpeg_gps_is_in_redwood_city(self):
        lat, lon = photo.jpeg_gps(str(self.photo))
        self.assertAlmostEqual(lat, 37.4855, places=4)
        self.assertAlmostEqual(lon, -122.2282, places=4)

    def test_prepare_street_light_asks_only_the_geocoder(self):
        self.network.side_effect = self.geocode_only
        preview = self.prepare()
        self.assertEqual(preview["type_id"], 27267)
        self.assertEqual(preview["type_name"], "Street Light Outage")
        self.assertEqual(preview["description"], "Street light is out.")
        self.assertEqual(preview["address"], ADDRESS)
        self.assertEqual(preview["cross_street"], CORNER)
        self.assertEqual(preview["custom_fields"]["3346"], CORNER)
        self.assertEqual(preview["missing_fields"], [])
        self.assertIn("3 business days", preview["confirmation"])
        self.assertEqual(preview["caution"], "")
        self.assertFalse(preview["public"])
        self.assertEqual(stat.S_IMODE(self.preview_path.stat().st_mode), 0o600)
        for call in self.network.call_args_list:
            target = getattr(call.args[0], "full_url", call.args[0])
            self.assertIn("geocode.arcgis.com", target)
            self.assertNotIn("publicstuff.com", target)

    def test_prepare_refuses_a_photo_outside_redwood_city(self):
        def elsewhere(url, *args, **kwargs):
            target = getattr(url, "full_url", url)
            if "publicstuff.com" in target:
                raise AssertionError(target)
            return FakeResponse(json.dumps({"address": {"City": "Palo Alto", "Address": "450 Alma St"}}))

        self.network.side_effect = elsewhere
        message = self.exit_message(self.prepare)
        self.assertIn("This photo is in Palo Alto.", message)

    def test_submit_without_confirm_does_not_call_the_city(self):
        self.network.side_effect = self.geocode_only
        self.prepare()
        self.sign_in()
        self.network.reset_mock()
        self.network.side_effect = self.city_api
        message = self.exit_message(
            lambda: myrwc.command_submit(argparse.Namespace(preview=None, confirm=False))
        )
        self.assertIn("Refusing to submit.", message)
        self.network.assert_not_called()

    def test_submit_street_light_posts_the_prepared_report(self):
        self.network.side_effect = self.geocode_only
        self.prepare()
        self.sign_in()
        self.network.reset_mock()
        self.network.side_effect = self.city_api
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            myrwc.command_submit(argparse.Namespace(preview=None, confirm=True))
        city_calls = [
            call
            for call in self.network.call_args_list
            if "publicstuff.com" in getattr(call.args[0], "full_url", call.args[0])
        ]
        self.assertEqual(len(city_calls), 1)
        request = self.submitted
        self.assertEqual(request.full_url, CITY_URL)
        values = form_values(request)
        self.assertEqual(values["client_id"], "226")
        self.assertEqual(values["space_id"], "29066")
        self.assertEqual(values["request_type_id"], "27267")
        self.assertEqual(values["description"], "Street light is out.")
        self.assertEqual(values["address"], ADDRESS)
        self.assertEqual(values["api_key"], "test-api-key")
        self.assertEqual(json.loads(values["custom_field_3346"]), CORNER)
        self.assertNotIn("is_private", values)
        self.assertEqual(values["uploadedfile"], self.photo.read_bytes())
        text = output.getvalue()
        self.assertIn("Request 1001.", text)
        self.assertIn("https://iframe.publicstuff.com/#?client_id=226&request_id=1001", text)

    def test_submit_refuses_when_the_cross_street_is_missing(self):
        def no_corner(url, *args, **kwargs):
            target = getattr(url, "full_url", url)
            if "publicstuff.com" in target:
                raise AssertionError(target)
            if "StreetInt" in target:
                body = {"address": {"ShortLabel": "", "City": "Redwood City"}}
            else:
                body = {
                    "address": {
                        "City": "Redwood City",
                        "Address": "1017 Middlefield Rd",
                        "RegionAbbr": "CA",
                        "Postal": "94063",
                    }
                }
            return FakeResponse(json.dumps(body))

        self.network.side_effect = no_corner
        preview = self.prepare()
        self.assertEqual(preview["cross_street"], "")
        self.assertEqual(preview["custom_fields"], {})
        self.assertIn("Please provide street name and Cross Street.", [field["name"] for field in preview["missing_fields"]])
        self.sign_in()
        self.network.reset_mock()
        self.network.side_effect = no_corner
        message = self.exit_message(
            lambda: myrwc.command_submit(argparse.Namespace(preview=None, confirm=True))
        )
        self.assertIn("Still missing: Please provide street name and Cross Street.", message)

    def test_checkbox_yes_is_sent_as_one(self):
        self.network.side_effect = self.geocode_only
        preview = self.prepare(type="Other Street Light Problem", description="The pole is down.", field=[("3331", "Yes")])
        self.assertEqual(preview["custom_fields"]["3331"], "1")
        self.assertIn("downed wire", preview["caution"])

    def test_homeless_caution_names_a_person(self):
        self.network.side_effect = self.geocode_only
        preview = self.prepare(type="Homeless", description="A camp is beside the sidewalk.")
        self.assertIn("person", preview["caution"])
        self.assertFalse(preview["public"])
