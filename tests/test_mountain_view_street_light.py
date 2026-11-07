"""Street-light reports for Mountain View, exercised without Ask Mountain View.

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
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "mountain-view" / "scripts"))
import mountainview311
import photo


ADDRESS = "500 Castro St, Mountain View, CA 94041"
CORNER = "Castro St & California St"
SESSION = ["PHPSESSID=abc123; path=/", "THE_GOVT=128; path=/"]
SESSION_HEADER = "PHPSESSID=abc123; THE_GOVT=128"
CONFIRMATION = "<html><body><p>Thank you. Your request has been submitted. Request ID: 445566.</p></body></html>"
FORM_PAGE = '<html><form name="mainform"><input id="sendrequestbutton" type="submit"></form></html>'


def jpeg_with_gps():
    """A tiny JPEG whose EXIF GPS is 37.3900 N, 122.0800 W, in downtown Mountain View."""

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
    tiff[120:144] = rational(37) + rational(23) + rational(24)
    tiff[144:168] = rational(122) + rational(4) + rational(48)
    app1 = b"Exif\x00\x00" + bytes(tiff)
    return b"\xff\xd8" + b"\xff\xe1" + struct.pack(">H", 2 + len(app1)) + app1 + b"\xff\xd9"


class FakeResponse:
    def __init__(self, body, status=200, headers=None):
        self.body = body.encode() if isinstance(body, str) else body
        self.status = status
        self.headers = headers or {}

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


class MountainViewStreetLightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.preview_path = root / "preview.json"
        self.photo = root / "light.jpg"
        self.photo.write_bytes(jpeg_with_gps())
        patcher = patch.object(mountainview311, "PREVIEW_PATH", self.preview_path)
        patcher.start()
        self.addCleanup(patcher.stop)
        network = patch("urllib.request.urlopen")
        self.network = network.start()
        self.addCleanup(network.stop)
        self.network.side_effect = self.forbid_network
        self.address = ADDRESS
        self.submitted = None
        self.confirmation = CONFIRMATION
        self.session = SESSION

    def forbid_network(self, url, *args, **kwargs):
        target = getattr(url, "full_url", url)
        raise AssertionError(f"test tried to reach the network: {target}")

    def geocode_body(self, street):
        return {
            "address": {
                "City": "Mountain View",
                "Address": street,
                "RegionAbbr": "CA",
                "Postal": "94041",
            }
        }

    def geocode_only(self, url, *args, **kwargs):
        target = getattr(url, "full_url", url)
        if "comcate.com" in target:
            raise AssertionError(f"prepare contacted Ask Mountain View: {target}")
        if "geocode.arcgis.com" not in target:
            raise AssertionError(f"unexpected geocoder call: {target}")
        if "StreetInt" in target:
            body = {"address": {"ShortLabel": CORNER, "City": "Mountain View"}}
        else:
            body = self.geocode_body(self.address.split(",")[0])
        return FakeResponse(json.dumps(body))

    def ask_mountain_view(self, url, *args, **kwargs):
        target = getattr(url, "full_url", url)
        if "geocode.arcgis.com" in target:
            return self.geocode_only(url, *args, **kwargs)
        self.assertIsInstance(url, urllib.request.Request)
        if "clients.comcate.com" not in target:
            raise AssertionError(f"unexpected call: {target}")
        if url.get_method() == "GET" and "newrequest.php" in target:
            return FakeResponse("<html>Ask Mountain View</html>", headers={"Set-Cookie": self.session})
        if url.get_method() == "POST" and target.rstrip("/").endswith("/newrequest.php"):
            self.submitted = url
            return FakeResponse(self.confirmation)
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
            type=kwargs.get("type", "Street Lights"),
            description=kwargs.get("description"),
            cross=kwargs.get("cross"),
        )
        with contextlib.redirect_stdout(io.StringIO()):
            mountainview311.command_prepare(args)
        return json.loads(self.preview_path.read_text())

    def test_jpeg_gps_is_in_mountain_view(self):
        lat, lon = photo.jpeg_gps(str(self.photo))
        self.assertAlmostEqual(lat, 37.3900, places=4)
        self.assertAlmostEqual(lon, -122.0800, places=4)

    def test_prepare_street_light_asks_only_the_geocoder(self):
        self.network.side_effect = self.geocode_only
        preview = self.prepare()
        self.assertEqual(preview["type_id"], 10878)
        self.assertEqual(preview["topic_id"], 2643)
        self.assertEqual(preview["type_name"], "Street Lights")
        self.assertEqual(preview["description"], f"Street light is out at {ADDRESS}.")
        self.assertEqual(preview["address"], ADDRESS)
        self.assertEqual(preview["cross_street"], CORNER)
        self.assertIn("(650) 903-6329", preview["note"])
        self.assertTrue(preview["public"])
        self.assertTrue(preview["anonymous"])
        self.assertEqual(stat.S_IMODE(self.preview_path.stat().st_mode), 0o600)
        for call in self.network.call_args_list:
            target = getattr(call.args[0], "full_url", call.args[0])
            self.assertIn("geocode.arcgis.com", target)
            self.assertNotIn("comcate.com", target)

    def test_prepare_keeps_a_rewritten_description_and_the_address(self):
        self.network.side_effect = self.geocode_only
        preview = self.prepare(description="The street light at this corner is dark.")
        self.assertEqual(
            preview["description"],
            f"The street light at this corner is dark. Location: {ADDRESS}.",
        )

    def test_prepare_refuses_a_photo_outside_mountain_view(self):
        def elsewhere(url, *args, **kwargs):
            target = getattr(url, "full_url", url)
            if "comcate.com" in target:
                raise AssertionError(target)
            return FakeResponse(json.dumps({"address": {"City": "Palo Alto", "Address": "450 Alma St"}}))

        self.network.side_effect = elsewhere
        message = self.exit_message(self.prepare)
        self.assertIn("This photo is in Palo Alto.", message)

    def test_prepare_refuses_any_other_type(self):
        message = self.exit_message(lambda: self.prepare(type="Potholes"))
        self.assertIn("Street Lights only", message)
        self.network.assert_not_called()

    def test_submit_without_confirm_does_not_call_the_city(self):
        self.network.side_effect = self.geocode_only
        self.prepare()
        self.network.reset_mock()
        self.network.side_effect = self.ask_mountain_view
        message = self.exit_message(
            lambda: mountainview311.command_submit(argparse.Namespace(preview=None, confirm=False))
        )
        self.assertIn("Refusing to submit.", message)
        self.network.assert_not_called()

    def test_submit_street_light_posts_the_prepared_report(self):
        self.network.side_effect = self.geocode_only
        self.prepare(description="The street light at this corner is dark.")
        self.network.reset_mock()
        self.network.side_effect = self.ask_mountain_view
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            mountainview311.command_submit(argparse.Namespace(preview=None, confirm=True))
        city_calls = [
            call
            for call in self.network.call_args_list
            if "comcate.com" in getattr(call.args[0], "full_url", "")
        ]
        self.assertEqual(len(city_calls), 2)
        self.assertEqual(city_calls[0].args[0].get_method(), "GET")
        request = self.submitted
        self.assertEqual(request.full_url, "https://clients.comcate.com/newrequest.php")
        self.assertEqual(request.get_header("Cookie"), SESSION_HEADER)
        values = form_values(request)
        self.assertEqual(values["fbreason"], "2643")
        self.assertEqual(values["fbsubreason"], "10878")
        self.assertEqual(values["fbtype"], "1")
        self.assertEqual(values["mailsent"], f"The street light at this corner is dark. Location: {ADDRESS}.")
        self.assertEqual(values["autogen"], "1")
        self.assertEqual(values["requestsubmit"], "1")
        self.assertEqual(values["newuser"], "0")
        self.assertEqual(values["incfields"], "0")
        self.assertEqual(values["baseAddrType"], "1")
        self.assertEqual(values["attachmentCnt"], "1")
        self.assertEqual(values["title1"], "Street light")
        self.assertEqual(values["val"], "")
        self.assertEqual(values["file1"], self.photo.read_bytes())
        for name in ("username", "password", "email", "fname", "lname"):
            self.assertNotIn(name, values)
        text = output.getvalue()
        self.assertIn("Submitted to Ask Mountain View.", text)
        self.assertIn("Request 445566.", text)
        self.assertIn("Thank you.", text)

    def test_submit_refuses_a_form_that_comes_back(self):
        self.network.side_effect = self.geocode_only
        self.prepare()
        self.network.reset_mock()
        self.confirmation = FORM_PAGE
        self.network.side_effect = self.ask_mountain_view
        message = self.exit_message(
            lambda: mountainview311.command_submit(argparse.Namespace(preview=None, confirm=True))
        )
        self.assertIn("returned the request form", message)
        self.assertIn("No account was created.", message)

    def test_submit_refuses_a_session_without_the_agency_cookie(self):
        self.network.side_effect = self.geocode_only
        self.prepare()
        self.network.reset_mock()
        self.session = ["PHPSESSID=abc123; path=/"]
        self.network.side_effect = self.ask_mountain_view
        message = self.exit_message(
            lambda: mountainview311.command_submit(argparse.Namespace(preview=None, confirm=True))
        )
        self.assertIn("did not start a session", message)
        self.assertIsNone(self.submitted)
