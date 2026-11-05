# Redwood City 311 runs

Camera-photo runs for Redwood City. This file does not cover other jurisdictions. [`catalog.md`](catalog.md) links here from the Run column.

The agent follows [`skills/redwood-city/SKILL.md`](../../skills/redwood-city/SKILL.md). `list` and `show` only read `catalog.json`. `prepare` calls the Esri geocoder and writes `~/.config/myrwc/preview.json`. `submit --confirm` is the only command that files the report. It POSTs to myRWC. `login` is a separate POST, and only when that account file is missing.

No camera-photo run is recorded yet. Street Light Outage is covered offline by [`tests/test_redwood_city_street_light.py`](../../tests/test_redwood_city_street_light.py). That test uses a stand-in photo and does not call the city.
