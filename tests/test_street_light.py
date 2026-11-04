"""Street-light reports, exercised without the PaloAlto311 server.

urllib is patched on the city script and on the shared geocoder. A test that
reaches the network fails.
"""

import argparse
import contextlib
import io
import json
import stat
import struct
import subprocess
import sys
import unittest
import urllib.request
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "file-311-common"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "palo-alto" / "scripts"))
import geocode
import paloalto311
import photo


PASSWORD = "secret-password"
ADDRESS = "450 Alma St, Palo Alto, CA 94301"
CORNER = "Alma St & Lytton Ave"
CITY_URL = "https://vc0.publicstuff.com/api/2.0/request_submit"


def jpeg_with_gps():
    """A tiny JPEG whose EXIF GPS is 37.4419 N, 122.1430 W."""

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
    tiff[120:144] = rational(37) + rational(26) + rational(3084, 100)
    tiff[144:168] = rational(122) + rational(8) + rational(3480, 100)
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


class StreetLightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.account_path = root / "account.json"
        self.preview_path = root / "preview.json"
        self.photo = root / "light.jpg"
        self.photo.write_bytes(jpeg_with_gps())
        for patcher in (
            patch.object(paloalto311, "ACCOUNT_PATH", self.account_path),
            patch.object(paloalto311, "PREVIEW_PATH", self.preview_path),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)
        network = patch("urllib.request.urlopen")
        self.network = network.start()
        self.addCleanup(network.stop)
        self.network.side_effect = self.forbid_network
        self.geocode_network = self.network

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
            body = {"address": {"ShortLabel": CORNER, "City": "Palo Alto"}}
        else:
            body = {
                "address": {
                    "City": "Palo Alto",
                    "Address": "450 Alma St",
                    "RegionAbbr": "CA",
                    "Postal": "94301",
                }
            }
        return FakeResponse(json.dumps(body))

    def city_api(self, url, *args, **kwargs):
        self.assertIsInstance(url, urllib.request.Request)
        if "geocode.arcgis.com" in url.full_url or "publicstuff.com" not in url.full_url:
            raise AssertionError(f"unexpected call: {url.full_url}")
        self.submitted = url
        if url.full_url.endswith("/api/2.1/user_login"):
            payload = {"response": {"status": {"code": 200}, "api_key": "test-api-key"}}
        else:
            payload = {
                "response": {
                    "status": {"code": 200},
                    "request_id": 1001,
                    "request_url": "https://iframe.publicstuff.com/#?client_id=406&request_id=1001",
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
            type=kwargs.get("type", "Street Light Out"),
            description=kwargs.get("description"),
            cross=kwargs.get("cross"),
            condition=kwargs.get("condition", "Out"),
            damage=kwargs.get("damage", "No"),
            lat=kwargs.get("lat"),
            lon=kwargs.get("lon"),
            field=kwargs.get("field"),
        )
        with contextlib.redirect_stdout(io.StringIO()):
            paloalto311.command_prepare(args)
        return json.loads(self.preview_path.read_text())

    def sign_in(self, name="Ada Resident", phone="650-555-0100"):
        paloalto311.save_account(
            {"api_key": "test-api-key", "email": "resident@example.com", "name": name, "phone": phone}
        )

    def test_jpeg_gps_matches_the_camera_location(self):
        self.assertEqual(photo.jpeg_gps(str(self.photo)), (37.4419, -122.143))

    def test_photo_without_gps_stops_before_any_network_call(self):
        empty = Path(self.tmp.name) / "empty.jpg"
        empty.write_bytes(b"\xff\xd8\xff\xd9")
        message = self.exit_message(lambda: self.prepare(photo=str(empty)))
        self.assertIn("This photo has no location.", message)
        self.geocode_network.assert_not_called()
        self.network.assert_not_called()

    def test_prepare_street_light_asks_only_the_geocoder(self):
        self.geocode_network.side_effect = self.geocode_only
        preview = self.prepare()
        self.assertEqual(preview["type_name"], "Street Light Out")
        self.assertEqual(preview["description"], "Street light is out.")
        self.assertEqual(preview["address"], ADDRESS)
        self.assertEqual(preview["cross_street"], CORNER)
        self.assertEqual(preview["custom_fields"]["3258"], ADDRESS)
        self.assertEqual(preview["custom_fields"]["3259"], CORNER)
        self.assertEqual(preview["custom_fields"]["3257"], "Out")
        self.assertEqual(preview["custom_fields"]["3263"], "No")
        self.assertEqual([field["name"] for field in preview["missing_fields"]], ["Name", "Phone Number"])
        self.assertTrue(preview["public"])
        self.assertEqual(stat.S_IMODE(self.preview_path.stat().st_mode), 0o600)
        for call in self.geocode_network.call_args_list:
            target = getattr(call.args[0], "full_url", call.args[0])
            self.assertIn("geocode.arcgis.com", target)
            self.assertNotIn("publicstuff.com", target)

    def test_prepare_refuses_a_photo_outside_palo_alto(self):
        def elsewhere(url, *args, **kwargs):
            target = getattr(url, "full_url", url)
            if "publicstuff.com" in target:
                raise AssertionError(target)
            return FakeResponse(json.dumps({"address": {"City": "Menlo Park", "Address": "1 El Camino Real"}}))

        self.geocode_network.side_effect = elsewhere
        message = self.exit_message(self.prepare)
        self.assertIn("This photo is in Menlo Park.", message)

    def test_submit_without_confirm_does_not_call_the_city(self):
        self.geocode_network.side_effect = self.geocode_only
        self.prepare()
        self.sign_in()
        self.network.reset_mock()
        self.network.side_effect = self.city_api
        message = self.exit_message(
            lambda: paloalto311.command_submit(argparse.Namespace(preview=None, confirm=False))
        )
        self.assertIn("Refusing to submit.", message)
        self.network.assert_not_called()

    def test_submit_street_light_posts_the_prepared_report(self):
        self.geocode_network.side_effect = self.geocode_only
        self.prepare()
        self.sign_in()
        self.network.reset_mock()
        self.network.side_effect = self.city_api
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            paloalto311.command_submit(argparse.Namespace(preview=None, confirm=True))
        self.network.assert_called_once()
        request = self.submitted
        self.assertEqual(request.full_url, CITY_URL)
        values = form_values(request)
        self.assertEqual(values["request_type_id"], "32794")
        self.assertEqual(values["description"], "Street light is out.")
        self.assertEqual(values["address"], ADDRESS)
        self.assertEqual(values["api_key"], "test-api-key")
        self.assertEqual(values["has_image"], "1")
        self.assertEqual(json.loads(values["custom_field_3257"]), "Out")
        self.assertEqual(json.loads(values["custom_field_3263"]), "No")
        self.assertEqual(json.loads(values["custom_field_3258"]), ADDRESS)
        self.assertEqual(json.loads(values["custom_field_3259"]), CORNER)
        self.assertEqual(json.loads(values["custom_field_3266"]), "Ada Resident")
        self.assertEqual(json.loads(values["custom_field_3260"]), "650-555-0100")
        self.assertEqual(values["uploadedfile"], self.photo.read_bytes())
        self.assertNotIn(PASSWORD.encode(), request.data)
        text = output.getvalue()
        self.assertIn("Request 1001.", text)
        self.assertIn("https://iframe.publicstuff.com/#?client_id=406&request_id=1001", text)

    def test_submit_uses_a_corner_edited_in_the_preview(self):
        self.geocode_network.side_effect = self.geocode_only
        preview = self.prepare()
        preview["cross_street"] = "Bryant St & University Ave"
        self.preview_path.write_text(json.dumps(preview))
        self.sign_in()
        self.network.reset_mock()
        self.network.side_effect = self.city_api
        with contextlib.redirect_stdout(io.StringIO()):
            paloalto311.command_submit(argparse.Namespace(preview=None, confirm=True))
        values = form_values(self.submitted)
        self.assertEqual(json.loads(values["custom_field_3259"]), "Bryant St & University Ave")

    def test_submit_refuses_while_name_and_phone_are_missing(self):
        self.geocode_network.side_effect = self.geocode_only
        self.prepare()
        paloalto311.save_account({"api_key": "test-api-key", "email": "resident@example.com"})
        self.network.reset_mock()
        self.network.side_effect = self.city_api
        message = self.exit_message(
            lambda: paloalto311.command_submit(argparse.Namespace(preview=None, confirm=True))
        )
        self.assertIn("Still missing: Name, Phone Number", message)
        self.network.assert_not_called()

    def test_login_does_not_save_the_password(self):
        self.network.side_effect = self.city_api
        env = {
            "PALOALTO311_EMAIL": "resident@example.com",
            "PALOALTO311_PASSWORD": PASSWORD,
            "PALOALTO311_NAME": "Ada Resident",
            "PALOALTO311_PHONE": "650-555-0100",
        }
        with patch.dict("os.environ", env, clear=False):
            with contextlib.redirect_stdout(io.StringIO()):
                paloalto311.command_login(argparse.Namespace())
        saved = self.account_path.read_text()
        self.assertNotIn(PASSWORD, saved)
        self.assertEqual(json.loads(saved)["api_key"], "test-api-key")
        self.assertEqual(stat.S_IMODE(self.account_path.stat().st_mode), 0o600)
        request = self.submitted
        self.assertTrue(request.full_url.endswith("/api/2.1/user_login"))
        self.assertIn(PASSWORD, request.data.decode())

    def test_pothole_intersection_comes_from_the_geocoder(self):
        self.geocode_network.side_effect = self.geocode_only
        preview = self.prepare(type="Pothole", description="Pothole in the lane.")
        self.assertEqual(preview["custom_fields"]["5128"], CORNER)
        self.assertEqual(preview["missing_fields"], [])

    def test_heic_photos_are_converted_to_separate_files(self):
        def fake_sips(cmd, check, capture_output):
            Path(cmd[cmd.index("--out") + 1]).write_bytes(b"jpeg")

        with patch("photo.subprocess.run", fake_sips):
            first = photo.jpeg_for_upload(str(Path(self.tmp.name) / "one.heic"), self.tmp.name)
            second = photo.jpeg_for_upload(str(Path(self.tmp.name) / "two.heic"), self.tmp.name)
        self.assertNotEqual(Path(first).name, Path(second).name)
        self.assertNotEqual(Path(first).name, "street-light.jpg")
        self.assertTrue(Path(first).is_file())

    def test_heic_without_sips_asks_for_a_jpeg(self):
        for error in (FileNotFoundError(), subprocess.CalledProcessError(1, "sips")):
            with self.subTest(error=type(error).__name__):
                with patch("photo.subprocess.run", side_effect=error):
                    message = self.exit_message(
                        lambda: photo.jpeg_for_upload(str(Path(self.tmp.name) / "one.heic"), self.tmp.name)
                    )
                self.assertIn("Export it as a JPEG", message)


if __name__ == "__main__":
    unittest.main()
