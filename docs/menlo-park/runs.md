# Menlo Park 311 runs

Camera-photo runs for Menlo Park. This file does not cover other jurisdictions. [`catalog.md`](catalog.md) links here from the Run column.

The agent follows [`skills/menlo-park/SKILL.md`](../../skills/menlo-park/SKILL.md). `list` and `show` only read `catalog.json`. `prepare` calls the Esri geocoder and writes `~/.config/menlopark311/preview.json`. `submit --confirm` is the only command that files the report. It checks the pin, checks that SeeClickFix still offers the type for Menlo Park, then POSTs to `https://seeclickfix.com/api/v2/issues`. `login` is a separate call, and only when that account file is missing. It sends the personal access token and does not send a password.

No camera-photo run is recorded yet. Streetlight is covered offline by [`tests/test_menlo_park_street_light.py`](../../tests/test_menlo_park_street_light.py). That test uses a stand-in photo and does not call the city.
