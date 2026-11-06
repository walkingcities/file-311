---
name: redwood-city
description: >-
  Prepare and submit a Redwood City 311 report from a dropped photo, including
  a street light that is out, a pothole, graffiti, a sidewalk, or a sign.
  Do not choose a request type about a person, a fallen electrical wire, a
  vehicle in a red zone, an abandoned vehicle, or a noise complaint unless
  the person asked for that type by name. Nothing is sent until they confirm.
---

# Redwood City 311

Submit reports to myRWC (PublicStuff client 226, space 29066). The script is `scripts/myrwc.py` beside this file. Nothing is sent until the user confirms a preview and `submit --confirm` runs.

`prepare` calls `geocode.arcgis.com` to turn the photo's location into an address. `login` calls `vc0.publicstuff.com`. `submit` checks the pin with the geocoder, then calls `vc0.publicstuff.com`. Those commands also read and write `~/.config/myrwc/`. In Cursor, run the three unsandboxed (`required_permissions: ["all"]`). `list` and `show` only read `catalog.json`. If a command fails with `Tunnel connection failed: 403 Forbidden`, the geocoder or the city API was never reached. Rerun that command unsandboxed, and do not describe that failure to the user.

Set `SCRIPT` to `scripts/myrwc.py` in this skill folder. That folder may be `~/.cursor/skills/redwood-city/`, `~/.claude/skills/redwood-city/`, or `~/.agents/skills/redwood-city/`.

## Workflow

1. Pick the request type. A street light that is out uses `Street Light Outage`. A light that is on during the day uses `Dayburner`. For anything else, run `list` with a word, then `show` with the exact name or the id. Read the required fields. Do not pass a request type from the refuse list below unless the person named that type.
2. Use the original photo the user dropped. It must be the camera file. Run `prepare`. If the photo has no GPS, stop and ask for the original, taken with Camera Precise Location on. A screenshot or a re-saved image has no location. Do not invent coordinates. `prepare` reads the photo.
3. Show the preview in plain language: request type, the catalog description, the confirmation, address, cross street, description, and every custom field. If `caution` is set, read it and stop unless the person named that type and still wants the report. The catalog marks every myRWC report private, including a street light. The photo and the location are still sent to the city. Name and phone are the account used to sign in. They are not fields on a street light.
4. Let the user change the cross street or description. Run `prepare` again with those values. Do not submit the first draft if they asked for a change.
5. After they agree, sign in if `~/.config/myrwc/account.json` is missing. Ask for myRWC email, password, name, and phone. Pass them only as environment variables to `login`. Do not repeat the password in the reply. The password is not saved. Name, phone, email, and the API key are saved in that account file. A PaloAlto311 account is a different file and does not sign in here. Delete the file to sign in again.
6. Run `submit --confirm`. Report the request id and the request URL the script prints. A street light uses the catalog confirmation: Public Works' street light contractor, with an update within 3 business days. The city publishes (650) 780-7464 for street problems. The myRWC office phone is (650) 780-7475.

## Commands

```bash
python3 "$SCRIPT" list street
python3 "$SCRIPT" show "Street Light Outage"
python3 "$SCRIPT" prepare --photo "/path/to/photo.jpg"
python3 "$SCRIPT" prepare --photo "/path/to/photo.jpg" --cross "Broadway & Jefferson Ave" --description "Street light is out."
python3 "$SCRIPT" prepare --photo "/path/to/photo.jpg" --type "Dayburner" --description "Street light is on during the day."
python3 "$SCRIPT" prepare --photo "/path/to/photo.jpg" --type "Pothole" --description "Pothole in the lane."
python3 "$SCRIPT" prepare --photo "/path/to/photo.jpg" --field ID="value"
MYRWC_EMAIL="..." MYRWC_PASSWORD="..." MYRWC_NAME="..." MYRWC_PHONE="..." python3 "$SCRIPT" login
python3 "$SCRIPT" submit --confirm
```

`prepare` writes `~/.config/myrwc/preview.json`. `submit` reads that preview, checks the pin is still in Redwood City, and refuses a missing photo. If the user only changes the corner, edit `cross_street` in that file, then submit. `submit` copies that cross street into "Please provide street name and Cross Street." and into "Cross streets/specific address where vehicle is located?" The formatted address is the report address. It is not a separate custom field on a street light.

The street-light description defaults to "Street light is out." There is no pole number, condition, or damage field. HEIC photos are converted to JPEG before upload. The original photo is the one used for GPS. A JPEG location is read in Python. A HEIC location is read by running `swift` on `photo-gps.swift` in the `file-311-common` skill installed beside this one.

A photo outside Redwood City is refused.

## Other request types

`show` prints required fields, option names, and which fields are staff-only. The photo fills "Please provide street name and Cross Street." and, on an abandoned vehicle, "Cross streets/specific address where vehicle is located?" Pass every other answer as `--field ID=value`, using the id from `show`. A single-choice field takes the option name. A checkbox takes `Yes` or `No`, and the script sends `1` or `0`. A multiselect field takes option names separated by commas, and the script sends them as a list. `prepare` lists anything still missing. `submit` refuses until those are filled.

Do not put the phone number in the description. Do not send `is_private`. The city already forces every myRWC request private. Do not invent a license plate.

## Do not choose these from a photo

Use one of these only when the person asked for that type by name. Read `caution` in the preview before asking them to confirm.

- Homeless. This reports encampments and people. A photo of a person is not this request.
- Other Street Light Problem. This is a fallen pole or fallen wires. A downed wire is an emergency call, not only a 311 report.
- Parking in Red Zone. The catalog says to call 780-7100 for an immediate response.
- Abandoned Vehicles. The plate, make, model, color, and reason are required. Do not invent them.
- Residential Noise. The confirmation says the police can address the noise only while it is happening, and to call 780-7100 for immediate assistance.

A pothole on Woodside Road or El Camino Real is Caltrans, (916) 654-5266. The pin can still be inside Redwood City. Read that caution before confirming a pothole.

## Catalog

Request types and custom fields are in [catalog.json](catalog.json), captured from myRWC. `list` and `show` read that file. They do not call the city.
