# Privacy policy

Walking Cities publishes File 311. This policy describes what the Palo Alto skill does with personal data on your computer. It runs there. Walking Cities does not receive or store that data.

Effective November 5, 2026.

## Data collected

You choose the photo. The skill reads the GPS coordinates stored in that camera file. It does not ask the operating system for your location.

It sends those coordinates to Esri ArcGIS at `geocode.arcgis.com` and receives a street address, city, ZIP code, and cross street.

When you sign in, you provide the email, password, name, and phone number on your PaloAlto311 account. The password is used for that sign-in and is not written to disk. The skill saves the email, name, phone number, and the API key returned by the city service.

A confirmed report can include the photo, the GPS coordinates, the address, the description you gave, the request type, and the name, email, and phone number from the account file.

## Purposes

The skill uses this data to prepare a Palo Alto 311 report and, after you agree, to file that report. The printed preview is how the chat app shows you the request before anything is sent.

## Recipients

Esri receives the photo's coordinates when the skill looks up an address.

The City of Palo Alto 311 service, at `vc0.publicstuff.com`, receives the sign-in and, after you agree, the report. A public link to a filed report is on `iframe.publicstuff.com`.

The chat app you are using, such as Cursor, Claude, or Codex, sees the preview because the skill prints it in the conversation.

Walking Cities is not a recipient. Nothing is sent to Walking Cities.

## Retention

`~/.config/paloalto311/account.json` keeps the email, name, phone number, and API key until you delete that file. `~/.config/paloalto311/preview.json` keeps the draft until you delete it. Both files are mode `600`.

The password is not kept.

Walking Cities keeps none of this data. The city keeps a submitted report under the city's own policy.

## Your controls

Nothing is sent to the city until you agree.

Delete `~/.config/paloalto311/account.json` to sign out. Delete `~/.config/paloalto311/preview.json` to drop a draft. Omit the photo and the skill stops.

Questions go to [GitHub Issues](https://github.com/walkingcities/file-311/issues).
