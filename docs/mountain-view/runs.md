# Mountain View 311 runs

Camera-photo runs for Mountain View. This file does not cover other jurisdictions. [`catalog.md`](catalog.md) links here from the Run column.

The agent follows [`skills/mountain-view/SKILL.md`](../../skills/mountain-view/SKILL.md). `list` and `show` only read `catalog.json`. `prepare` calls the Esri geocoder and writes `~/.config/mountainview311/preview.json`. `submit --confirm` is the only command that files the report. It loads the Ask Mountain View form, then posts that form. There is no account.

No camera-photo run is recorded yet. Street Lights is covered offline by [`tests/test_mountain_view_street_light.py`](../../tests/test_mountain_view_street_light.py). That test uses a stand-in photo and does not call the city.
