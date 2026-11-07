# Mountain View 311 catalog

The request type in [`skills/mountain-view/catalog.json`](../../skills/mountain-view/catalog.json). A checkmark in the Run column links to that photo run in [`runs.md`](runs.md). This file is Mountain View only. The list of other places is [`../jurisdictions.md`](../jurisdictions.md).

Street Lights is covered offline by [`tests/test_mountain_view_street_light.py`](../../tests/test_mountain_view_street_light.py). That test uses a stand-in photo and does not call the city. There is no camera-photo run yet.

## Source

`catalog.json` is the Street Lights row from the Ask Mountain View form, read November 7, 2026. The form is `https://clients.comcate.com/newrequest.php?id=128`. Streets is topic `2643`. Street Lights is subtopic `10878`. The page script sets `jsTopicLocation_10878` to `0`, so the address is written into the request text. `POST ajax_customfields.php` for that subtopic returned an empty table. The file keeps the topic, the subtopic, the Concern request type, and the note. `list`, `show`, `prepare`, and `submit` read this file. They do not refetch it.

This skill files Street Lights only. Potholes, sidewalks, and the other subtopics on the form are not in the catalog.

## Request types

| Run | Id | Request type |
| --- | --- | --- |
|  | 10878 | [Street Lights](#street-lights) |

## Street Lights

Streets, subtopic `10878`. The request type sent to the form is Concern.

Non-urgent street lights go through Ask Mountain View. Urgent street light outages are a call to Public Services at (650) 903-6329. An emergency is 911. The letter and the photo are public records. This report is anonymous, and the city does not email a status.

The description defaults to `Street light is out at {address}.` The photo is required because it carries the GPS.
