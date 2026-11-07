---
name: file-311-common
description: >-
  Shared photo and geocoding code for file-311 city skills. Do not use this
  skill to file a report or when someone drops a photo. Use the city skill,
  such as palo-alto, redwood-city, menlo-park, or mountain-view.
---

# file-311 common

This folder is a library. City skills import `photo.py` and `geocode.py` from here. It does not file a report.

`photo.py` reads a JPEG location and, on a Mac, a HEIC location through `photo-gps.swift`. `geocode.py` turns that location into an address for a named city.
