---
name: palo-alto
description: >-
  Prepare and submit a Palo Alto 311 report from a dropped photo, including a
  street light that is out or a pothole. Use when the user mentions Palo Alto
  311, PaloAlto311, a street light, a pothole, or drops a photo of a city
  issue such as graffiti, a sidewalk, or a storm drain.
---

# Palo Alto 311

Submit reports to PaloAlto311 (PublicStuff client 406). The script is `scripts/paloalto311.py` beside this file. Nothing is sent until the user confirms a preview and `submit --confirm` runs.

`prepare` calls `geocode.arcgis.com` to turn the photo's location into an address. `login` and `submit` call `vc0.publicstuff.com`. Those commands also read and write `~/.config/paloalto311/`. In Cursor, run the three unsandboxed (`required_permissions: ["all"]`). `list` and `show` only read `catalog.json`. If a command fails with `Tunnel connection failed: 403 Forbidden`, the geocoder or the city API was never reached. Rerun that command unsandboxed, and do not describe that failure to the user.

Set `SCRIPT` to `scripts/paloalto311.py` in this skill folder. That folder may be `~/.cursor/skills/palo-alto/`, `~/.claude/skills/palo-alto/`, or `~/.agents/skills/palo-alto/`.

## Workflow

1. Pick the request type. Street light outages use `Street Light Out`. For anything else, run `list` or `show` and read the required fields.
2. Use the original photo the user dropped. It must be the camera file. Run `prepare`. If the photo has no GPS, stop and ask for the original, taken with Camera Precise Location on. A screenshot or a re-saved image has no location.
3. Show the preview in plain language: request type, address, cross street, description, and every custom field. Say which fields are staff-only. For a street light, the photo and the location are public. Name and phone are staff-only.
4. Let the user change the cross street, description, condition, or damage. Run `prepare` again with those values. Do not submit the first draft if they asked for a change.
5. After they agree, sign in if `~/.config/paloalto311/account.json` is missing. Ask for PaloAlto311 email, password, name, and phone. Pass them only as environment variables to `login`. Do not repeat the password in the reply. The password is not saved. Name, phone, email, and the API key are saved in that account file. Delete the file to sign in again.
6. Run `submit --confirm`. Report the request id and the request URL the script prints. That URL opens the report in PaloAlto311. A street light report asks the city for up to 5 business days. The street-light desk is (650) 496-6916 on workdays. A power outage is a different report and a different phone line, (650) 496-6914.

## Commands

```bash
python3 "$SCRIPT" list street
python3 "$SCRIPT" show "Street Light Out"
python3 "$SCRIPT" prepare --photo "/path/to/photo.jpg"
python3 "$SCRIPT" prepare --photo "/path/to/photo.jpg" --cross "Matadero Ave & Park Blvd" --description "Street light is out." --condition Out --damage No
python3 "$SCRIPT" prepare --photo "/path/to/photo.jpg" --type "Pothole" --description "Pothole in the lane."
python3 "$SCRIPT" prepare --photo "/path/to/photo.jpg" --field ID="value"
PALOALTO311_EMAIL="..." PALOALTO311_PASSWORD="..." PALOALTO311_NAME="..." PALOALTO311_PHONE="..." python3 "$SCRIPT" login
python3 "$SCRIPT" submit --confirm
```

`prepare` writes `~/.config/paloalto311/preview.json`. `submit` reads that preview. If the user only changes the corner, edit `cross_street` in that file, then submit. `submit` copies that cross street into Cross Street and Intersection fields, and the formatted address into the location-address fields. Name and phone can be missing from the preview until `login`. `submit` fills them from the account file.

Street light defaults are condition `Out` and damage `No`. Pole number stays blank. HEIC photos are converted to JPEG before upload. The original photo is the one used for GPS. A JPEG location is read in Python. A HEIC location is read by running `swift` on `photo-gps.swift` in the `file-311-common` skill installed beside this one.

A photo outside Palo Alto is refused.

## Other request types

`show` prints required fields, option names, and which fields are staff-only. The photo fills Cross Street, Intersection, Light Location Address, Location Address of Lid/Cover, and Address or Location for Request. Pass every other answer as `--field ID=value`, using the id from `show`. A single-choice field takes the option name, such as `Out` or `No`. A multiselect field takes those names separated by commas, such as `Leak, Irrigation Runoff`, and the script sends them as a list. `prepare` lists anything still missing. `submit` refuses until those are filled. Name and phone are filled from the account file when the field is named `Name`, `Contact Name`, or `Phone Number`.

Do not put the phone number in the public description. Do not send `is_private`. Residents cannot mark a Palo Alto request private. Do not invent a pole number.

## Catalog

Request types and custom fields are in [catalog.json](catalog.json), captured from PaloAlto311. `list` and `show` read that file. They do not call the city.
