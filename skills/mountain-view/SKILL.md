---
name: mountain-view
description: >-
  Prepare and submit a Mountain View street-light report from a dropped photo.
  The light is out, broken, or on all day. This skill files Street Lights
  only. Nothing is sent until the person confirms.
---

# Mountain View 311

Submit a street-light report to Ask Mountain View (Comcate). The script is `scripts/mountainview311.py` beside this file. Nothing is sent until the user confirms a preview and `submit --confirm` runs.

`prepare` calls `geocode.arcgis.com` to turn the photo's location into an address. `submit` loads the Ask Mountain View form, then posts that form. Those commands also read and write `~/.config/mountainview311/`. In Cursor, run them unsandboxed (`required_permissions: ["all"]`). `list` and `show` only read `catalog.json`. If a command fails with `Tunnel connection failed: 403 Forbidden`, the geocoder or Ask Mountain View was never reached. Rerun that command unsandboxed, and do not describe that failure to the user.

Set `SCRIPT` to `scripts/mountainview311.py` in this skill folder. That folder may be `~/.cursor/skills/mountain-view/`, `~/.claude/skills/mountain-view/`, or `~/.agents/skills/mountain-view/`.

## Workflow

1. A street light that is out, broken, or on all day uses `Street Lights`. Run `show` and read the note. This skill files that one type. A pothole, sidewalk, sign, or anything else is not this report.
2. Use the original photo the user dropped. It must be the camera file. Run `prepare`. If the photo has no GPS, stop and ask for the original, taken with Camera Precise Location on. A screenshot or a re-saved image has no location. Do not invent coordinates. `prepare` reads the photo.
3. Show the preview in plain language: Street Lights, the catalog note, address, cross street, and description. The letter and the photo are public records. The report is anonymous. Ask Mountain View does not email a status. Urgent street light outages are a call to Public Services, (650) 903-6329. An emergency is 911.
4. Let the user change the description or the cross street. Run `prepare` again with those values. Do not submit the first draft if they asked for a change. The cross street is shown in the preview. The form has no cross-street field. The address is written into the request text.
5. After they agree, run `submit --confirm`. There is no account and no login. Report the request id when the script prints one, and read the confirmation text it prints. The city tracks non-urgent reports during normal business hours. Ask Mountain View is not for emergencies.

## Commands

```bash
python3 "$SCRIPT" list street
python3 "$SCRIPT" show "Street Lights"
python3 "$SCRIPT" prepare --photo "/path/to/photo.jpg"
python3 "$SCRIPT" prepare --photo "/path/to/photo.jpg" --description "The street light at this corner is dark."
python3 "$SCRIPT" submit --confirm
```

`prepare` writes `~/.config/mountainview311/preview.json`. It does not call Ask Mountain View. `submit` reads that preview, checks the pin is still in Mountain View, and refuses a missing photo. The description defaults to `Street light is out at {address}.` The photo is required because it carries the GPS.

HEIC photos are converted to JPEG before upload. The original photo is the one used for GPS. A JPEG location is read in Python. A HEIC location is read by running `swift` on `photo-gps.swift` in the `file-311-common` skill installed beside this one.

A photo outside Mountain View is refused.

## Catalog

Street Lights is the only request type, in [catalog.json](catalog.json), captured from the Ask Mountain View form on November 7, 2026. The topic is Streets, `2643`. The subtopic is Street Lights, `10878`. `list` and `show` read that file. They do not call the city.
