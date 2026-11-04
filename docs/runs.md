# Palo Alto 311 runs

Each camera-photo run of the Palo Alto skill. [`catalog.md`](catalog.md) links here from the Run column.

The agent follows [`skills/palo-alto/SKILL.md`](../skills/palo-alto/SKILL.md). `list` and `show` only read `catalog.json`. `prepare` calls the Esri geocoder and writes `~/.config/paloalto311/preview.json`. `submit --confirm` is the only command that files the report. It POSTs to PaloAlto311. `login` is a separate POST, and only when that account file is missing.

## Fallen sign, November 3, 2026

Submitted. PaloAlto311 request [18864090](https://iframe.publicstuff.com/#?client_id=406&request_id=18864090).

Catalog type: [Traffic Signs Damaged or Obstructed](catalog.md#traffic-signs-damaged-or-obstructed), id 15503.

The photo is a green bike-lane wayfinding sign lying on the dirt shoulder, post down, beside a road with a railroad crossing and a 10 mph curve sign. The original camera file is `992FBCAD-1F89-4139-83A4-A89A9630121B_1_105_c-4832a9e1-6c3c-4b5d-a20f-bd006fd58e33.jpg`.

### Chat

**Christopher:** Dry run; do not submit. Report this sign to Palo Alto 311 that fell down. See attached photo.

**Assistant:** Dry run only. Nothing was submitted.

- Request type: Traffic Signs Damaged or Obstructed
- Address: 67 Palo Alto Ave, Palo Alto, CA 94301
- Cross street: Alma St & Palo Alto Ave
- Description: A green bike-lane wayfinding sign has fallen and is lying on the dirt shoulder beside the road. The post is down.
- Intersection (staff-only): Alma St & Palo Alto Ave

The photo and the location are public. This request type has no name or phone field. The intersection is the only staff-only field.

**Christopher:** Can you actually submit the 311 request, and if successful, update the example runs section?

**Assistant:** Submitted to PaloAlto311. Request 18864090. https://iframe.publicstuff.com/#?client_id=406&request_id=18864090

### What the skill did

1. The skill says to pick a request type from `catalog.json` before calling the city. A search for "sign" matched Traffic Signs Damaged or Obstructed (id 15503): "Report missing, bent and unreadable traffic signs." `show` would print one required field, Intersection (id 5128), and mark it staff-only. That lookup is local. It does not call PaloAlto311.

2. `prepare` used the original JPEG. The command was:

```bash
python3 skills/palo-alto/scripts/paloalto311.py prepare \
  --photo "/path/to/992FBCAD-1F89-4139-83A4-A89A9630121B_1_105_c-4832a9e1-6c3c-4b5d-a20f-bd006fd58e33.jpg" \
  --type "Traffic Signs Damaged or Obstructed" \
  --description "A green bike-lane wayfinding sign has fallen and is lying on the dirt shoulder beside the road. The post is down."
```

`prepare` read the GPS from the JPEG in Python: 37.44673888888889, -122.17004444444444. It then called Esri's public reverse geocoder twice:

```
GET https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/reverseGeocode?f=json&location=-122.17004444444444,37.44673888888889
GET https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/reverseGeocode?f=json&featureTypes=StreetInt&location=-122.17004444444444,37.44673888888889
```

The first response had to be inside Palo Alto. It returned 67 Palo Alto Ave, Palo Alto, CA 94301. The second, limited to street intersections, returned Alma St & Palo Alto Ave. The skill copied that corner into Intersection, field 5128, and wrote the preview to `~/.config/paloalto311/preview.json` with mode 600. `prepare` does not send the report.

3. `~/.config/paloalto311/account.json` was already present, so this run did not log in. A first report would set `PALOALTO311_EMAIL`, `PALOALTO311_PASSWORD`, `PALOALTO311_NAME`, and `PALOALTO311_PHONE` and run `login`, which POSTs `https://vc0.publicstuff.com/api/2.1/user_login` with `client_id` 406. The password is not saved. The saved file holds the email, name, phone, and API key.

4. After the preview was confirmed, `submit --confirm` read that preview and POSTed the report:

```
POST https://vc0.publicstuff.com/api/2.0/request_submit
PublicStuff-Client: 406
Content-Type: multipart/form-data
```

The form included `title`, `description`, `request_type_id` 15503, the photo latitude and longitude, the formatted address in `address`, `user_address`, and `long_address`, `zipcode` 94301, `space_id` 26742, `client_id` 406, `device` iframe, the saved API key, `has_image` 1, and the photo as `uploadedfile`. Intersection went out as `custom_field_5128`, with the corner JSON-encoded. The script treats the call as successful when `response.status.code` is 200. PaloAlto311 returned request 18864090 and this URL:

https://iframe.publicstuff.com/#?client_id=406&request_id=18864090
