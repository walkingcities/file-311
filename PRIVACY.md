# Privacy policy

Walking Cities publishes File 311. This policy describes what the Palo Alto, Redwood City, and Menlo Park skills do with personal data on your computer. They run there. Walking Cities does not receive or store that data.

Effective November 5, 2026.

## Data collected

You choose the photo. The skill reads the GPS coordinates stored in that camera file. It does not ask the operating system for your location.

It sends those coordinates to Esri ArcGIS at `geocode.arcgis.com` and receives a street address, city, ZIP code, and cross street.

When you sign in, you provide the email, password, name, and phone number on your PaloAlto311 or myRWC account. The password is used for that sign-in and is not written to disk. The skill saves the email, name, phone number, and the API key returned by the city service. Palo Alto and Redwood City use separate account files.

When you sign in to Menlo Park, you provide a SeeClickFix personal access token. The skill saves that token, your user id, and your display name. It does not ask for a Menlo Park password.

A confirmed Palo Alto or Redwood City report can include the photo, the GPS coordinates, the address, the description you gave, the request type, and the name, email, and phone number from the account file. A confirmed Menlo Park report can include the photo, the GPS coordinates, the address, the title, the description, and the display name from the account file. That display name is public.

## Purposes

The skill uses this data to prepare a city 311 report and, after you agree, to file that report. The printed preview is how the chat app shows you the request before anything is sent.

## Recipients

Esri receives the photo's coordinates when the skill looks up an address.

The City of Palo Alto 311 service, at `vc0.publicstuff.com`, receives the Palo Alto sign-in and, after you agree, the Palo Alto report. A public link to a filed Palo Alto report is on `iframe.publicstuff.com`.

The City of Redwood City myRWC service, at `vc0.publicstuff.com`, receives the Redwood City sign-in and, after you agree, the Redwood City report. The myRWC catalog marks those requests private.

SeeClickFix, at `seeclickfix.com`, receives the Menlo Park token check and, after you agree, the Menlo Park report. The title, description, photo, and map pin are public.

The chat app you are using, such as Cursor, Claude, or Codex, sees the preview because the skill prints it in the conversation.

Walking Cities is not a recipient. Nothing is sent to Walking Cities.

## Retention

`~/.config/paloalto311/account.json` and `~/.config/myrwc/account.json` keep the email, name, phone number, and API key until you delete that file. `~/.config/paloalto311/preview.json` and `~/.config/myrwc/preview.json` keep the draft until you delete it. These files are mode `600`.

`~/.config/menlopark311/account.json` keeps the SeeClickFix token, user id, and display name until you delete that file. `~/.config/menlopark311/preview.json` keeps the Menlo Park draft until you delete it. These files are mode `600`. The Menlo Park token is kept. A Menlo Park password is not.

The password is not kept.

Walking Cities keeps none of this data. The city keeps a submitted report under the city's own policy.

## Your controls

Nothing is sent to the city until you agree.

Delete the account file for that city to sign out. Delete the preview file to drop a draft. Omit the photo and the skill stops.

Questions go to [GitHub Issues](https://github.com/walkingcities/file-311/issues).
