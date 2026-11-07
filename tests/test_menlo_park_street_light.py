"""Street-light reports for Menlo Park, exercised without SeeClickFix.

urllib is patched on the city script and on the shared geocoder. A test that
reaches the network fails.
"""

import argparse
import contextlib
import io
import json
import os
import stat
import struct
import sys
import unittest
import urllib.request
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "file-311-common"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "menlo-park" / "scripts"))
import menlopark311
import photo


ADDRESS = "701 Laurel St, Menlo Park, CA 94025"
CORNER = "Laurel St & Ravenswood Ave"
TOKEN = "test-token"


def jpeg_with_gps():
    """A tiny JPEG whose EXIF GPS is 37.4530 N, 122.1820 W, in downtown Menlo Park."""

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
    tiff[120:144] = rational(37) + rational(27) + rational(1080, 100)
    tiff[144:168] = rational(122) + rational(10) + rational(5520, 100)
    app1 = b"Exif\x00\x00" + bytes(tiff)
    return b"\xff\xd8" + b"\xff\xe1" + struct.pack(">H", 2 + len(app1)) + app1 + b"\xff\xd9"


class FakeResponse:
    def __init__(self, body, status=200):
        self.body = body.encode()
        self.status = status

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


class MenloParkStreetLightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.account_path = root / "account.json"
        self.preview_path = root / "preview.json"
        self.photo = root / "light.jpg"
        self.photo.write_bytes(jpeg_with_gps())
        for patcher in (
            patch.object(menlopark311, "ACCOUNT_PATH", self.account_path),
            patch.object(menlopark311, "PREVIEW_PATH", self.preview_path),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)
        network = patch("urllib.request.urlopen")
        self.network = network.start()
        self.addCleanup(network.stop)
        self.network.side_effect = self.forbid_network
        self.address = ADDRESS
        self.submitted = None

    def forbid_network(self, url, *args, **kwargs):
        target = getattr(url, "full_url", url)
        raise AssertionError(f"test tried to reach the network: {target}")

    def geocode_body(self, street):
        return {
            "address": {
                "City": "Menlo Park",
                "Address": street,
                "RegionAbbr": "CA",
                "Postal": "94025",
            }
        }

    def geocode_only(self, url, *args, **kwargs):
        target = getattr(url, "full_url", url)
        if "seeclickfix.com" in target:
            raise AssertionError(f"prepare contacted SeeClickFix: {target}")
        if "geocode.arcgis.com" not in target:
            raise AssertionError(f"unexpected geocoder call: {target}")
        if "StreetInt" in target:
            body = {"address": {"ShortLabel": CORNER, "City": "Menlo Park"}}
        else:
            body = self.geocode_body(self.address.split(",")[0])
        return FakeResponse(json.dumps(body))

    def seeclickfix(self, url, *args, **kwargs):
        target = getattr(url, "full_url", url)
        if "geocode.arcgis.com" in target:
            return self.geocode_only(url, *args, **kwargs)
        self.assertIsInstance(url, urllib.request.Request)
        if "seeclickfix.com" not in target:
            raise AssertionError(f"unexpected call: {target}")
        if url.get_method() == "GET" and "/issues/new" in target:
            body = {
                "request_types": [
                    {
                        "organization": "Menlo Park",
                        "title": "Streetlight",
                        "url": "https://seeclickfix.com/api/v2/request_types/94217",
                    }
                ]
            }
            return FakeResponse(json.dumps(body))
        if url.get_method() == "POST" and target.endswith("/api/v2/issues"):
            self.submitted = url
            body = {"id": 2001, "html_url": "https://seeclickfix.com/issues/2001", "summary": "Street light is out."}
            return FakeResponse(json.dumps(body), status=201)
        raise AssertionError(target)

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
            type=kwargs.get("type", "Streetlight"),
            title=kwargs.get("title"),
            description=kwargs.get("description"),
            cross=kwargs.get("cross"),
        )
        with contextlib.redirect_stdout(io.StringIO()):
            menlopark311.command_prepare(args)
        return json.loads(self.preview_path.read_text())

    def sign_in(self):
        menlopark311.save_account({"token": TOKEN, "id": 42, "name": "Ada Resident"})

    def test_jpeg_gps_is_in_menlo_park(self):
        lat, lon = photo.jpeg_gps(str(self.photo))
        self.assertAlmostEqual(lat, 37.4530, places=4)
        self.assertAlmostEqual(lon, -122.1820, places=4)

    def test_prepare_street_light_asks_only_the_geocoder(self):
        self.network.side_effect = self.geocode_only
        preview = self.prepare()
        self.assertEqual(preview["type_id"], 94217)
        self.assertEqual(preview["type_name"], "Streetlight")
        self.assertEqual(preview["title"], "Street light is out.")
        self.assertEqual(preview["description"], "")
        self.assertEqual(preview["address"], ADDRESS)
        self.assertEqual(preview["cross_street"], CORNER)
        self.assertIn("1-877-660-6789", preview["note"])
        self.assertEqual(preview["caution"], "")
        self.assertEqual(preview["missing_fields"], [])
        self.assertTrue(preview["public"])
        self.assertEqual(stat.S_IMODE(self.preview_path.stat().st_mode), 0o600)
        for call in self.network.call_args_list:
            target = getattr(call.args[0], "full_url", call.args[0])
            self.assertIn("geocode.arcgis.com", target)
            self.assertNotIn("seeclickfix.com", target)

    def test_prepare_refuses_a_photo_outside_menlo_park(self):
        def elsewhere(url, *args, **kwargs):
            target = getattr(url, "full_url", url)
            if "seeclickfix.com" in target:
                raise AssertionError(target)
            return FakeResponse(json.dumps({"address": {"City": "Palo Alto", "Address": "450 Alma St"}}))

        self.network.side_effect = elsewhere
        message = self.exit_message(self.prepare)
        self.assertIn("This photo is in Palo Alto.", message)

    def test_prepare_refuses_a_blocked_traffic_signal(self):
        message = self.exit_message(lambda: self.prepare(type="Traffic Signal Issue"))
        self.assertIn("650-330-6300", message)
        self.network.assert_not_called()

    def test_submit_without_confirm_does_not_call_the_city(self):
        self.network.side_effect = self.geocode_only
        self.prepare()
        self.sign_in()
        self.network.reset_mock()
        self.network.side_effect = self.seeclickfix
        message = self.exit_message(
            lambda: menlopark311.command_submit(argparse.Namespace(preview=None, confirm=False))
        )
        self.assertIn("Refusing to submit.", message)
        self.network.assert_not_called()

    def test_submit_street_light_posts_the_prepared_report(self):
        self.network.side_effect = self.geocode_only
        self.prepare(description="The street light at this corner is dark.")
        self.sign_in()
        self.network.reset_mock()
        self.network.side_effect = self.seeclickfix
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            menlopark311.command_submit(argparse.Namespace(preview=None, confirm=True))
        city_calls = [
            call
            for call in self.network.call_args_list
            if "seeclickfix.com" in getattr(call.args[0], "full_url", "")
        ]
        self.assertEqual(len(city_calls), 2)
        request = self.submitted
        self.assertEqual(request.full_url, "https://seeclickfix.com/api/v2/issues")
        self.assertEqual(request.get_header("Authorization"), f"Bearer {TOKEN}")
        self.assertNotIn("--real", request.get_header("Authorization"))
        values = form_values(request)
        self.assertEqual(values["request_type_id"], "94217")
        self.assertEqual(values["answers[summary]"], "Street light is out.")
        self.assertEqual(values["answers[description]"], "The street light at this corner is dark.")
        self.assertEqual(values["address"], ADDRESS)
        self.assertEqual(values["answers[issue_image]"], self.photo.read_bytes())
        self.assertNotIn("anonymize_reporter", values)
        text = output.getvalue()
        self.assertIn("Request 2001.", text)
        self.assertIn("https://seeclickfix.com/issues/2001", text)

    def test_submit_refuses_caltrans_potholes(self):
        streets = ("800 El Camino Real", "100 Willow Rd", "E Bayshore Rd")
        for street in streets:
            with self.subTest(street=street):
                self.address = f"{street}, Menlo Park, CA 94025"
                self.network.side_effect = self.geocode_only
                preview = self.prepare(type="Potholes", title="Pothole in the lane.")
                self.assertIn("(916) 654-5266", preview["caution"])
                self.sign_in()
                self.network.reset_mock()
                self.network.side_effect = self.geocode_only
                message = self.exit_message(
                    lambda: menlopark311.command_submit(argparse.Namespace(preview=None, confirm=True))
                )
                self.assertIn("(916) 654-5266", message)
                for call in self.network.call_args_list:
                    target = getattr(call.args[0], "full_url", call.args[0])
                    self.assertNotIn("seeclickfix.com", target)

    def test_submit_refuses_a_pothole_without_a_title(self):
        self.network.side_effect = self.geocode_only
        preview = self.prepare(type="Potholes")
        self.assertEqual(preview["title"], "")
        self.assertEqual(preview["missing_fields"][0]["name"], "Issue Title")
        self.sign_in()
        self.network.reset_mock()
        self.network.side_effect = self.geocode_only
        message = self.exit_message(
            lambda: menlopark311.command_submit(argparse.Namespace(preview=None, confirm=True))
        )
        self.assertIn("Still missing: Issue Title", message)

    def test_login_rejects_a_token_that_does_not_start_with_dashes(self):
        with patch.dict(os.environ, {"MENLOPARK311_TOKEN": ""}, clear=False):
            os.environ.pop("MENLOPARK311_TOKEN", None)
            message = self.exit_message(lambda: menlopark311.command_login(argparse.Namespace()))
        self.assertIn("MENLOPARK311_TOKEN", message)
        with patch.dict(os.environ, {"MENLOPARK311_TOKEN": "name-and-date-secret"}):
            message = self.exit_message(lambda: menlopark311.command_login(argparse.Namespace()))
        self.assertIn("starts with --", message)
        self.network.assert_not_called()
        self.assertFalse(self.account_path.exists())
