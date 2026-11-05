# Other cities

Palo Alto is the only city this repo files. A photo outside Palo Alto is refused. Another city is a new folder under `skills/`, using the same photo, GPS, and preview-before-send flow. Nothing below is built.

Checked November 3, 2026, from each city's public site and, where one exists, its public API. A SeeClickFix place page is not evidence that a city runs 311 there. Palo Alto has one and uses PublicStuff.

Effort is the work to add a city skill like Palo Alto. Photo GPS, JPEG conversion, and reverse geocoding already live in `file-311-common`. The city client, catalog, account file, and boundary check do not carry over.

| City | System | How a resident files | Programmatic access | Account | Photo and location | Effort |
| --- | --- | --- | --- | --- | --- | --- |
| Palo Alto | Accela PublicStuff. Client `406`, API `https://vc0.publicstuff.com`. | PaloAlto311 site and app. | JSON API. Catalog is already in `skills/palo-alto/catalog.json`. | PaloAlto311 login. Password is not saved. | Photo GPS becomes the address. This is the working client. | Done |
| Menlo Park | SeeClickFix, branded ACT Menlo Park. Place id `76196`. | [ACT Menlo Park](https://www.menlopark.gov/Services/ACT-Menlo-Park) and the ACT Menlo Park app. The city says the software is SeeClickFix. | Public API v2. Request types come from `GET /api/v2/issues/new?lat=&lng=`. Create is `POST /api/v2/issues` and requires an authenticated user. Docs: [dev.seeclickfix.com](https://dev.seeclickfix.com/v2/issues/reporting/). | Required. Streetlight, potholes, and sidewalks set `permit_guest_reporting` and `permit_anonymous_reporting` to false. | Latitude, longitude, and a written address are required. Image is an optional file field. | Low |
| Mountain View | Comcate CRM, branded Ask Mountain View. Government id `128`. | [Ask Mountain View](https://clients.comcate.com/newrequest.php?id=128) and the Ask Mountain View app (`com.comcate.mountainviewapp`). | No public API found. The topic tree is embedded in the page: 43 topics and 283 subtopics. Submit is an HTML form. Custom fields load from `POST ajax_customfields.php`; that call returned an empty body without a session. | Optional. The form offers new user, existing user, or anonymous. The city says the letter is a public record. | The form has file inputs (`file1` and more). The page's location flag is on for potholes and sidewalks, and off for street lights and traffic signals. | Medium |
| Sunnyvale | MySunnyvale. Salesforce Public Sector Solutions, implemented by Catalyst Consulting Group (council file 25-0827). Chatbot name is Sunny. | Web portal and the MySunnyvale CA app. The city says it replaced Access Sunnyvale on June 22, 2026. | No public citizen API. A Salesforce connected app would have to come from the city. The city's MySunnyvale page returned HTTP 403 to this check, so the live form was not read. | Not confirmed on the new portal. | Not confirmed on the new portal. | High |

## What to build, in order

### 1. Menlo Park

This is the only neighbor with the same shape as Palo Alto: a catalog endpoint, a create endpoint, a photo, and a lat/lng.

On November 3, 2026, a point inside the city (`37.4530, -122.1817`) returned 20 Menlo Park request types:

- Downtown Parking Machine
- Dumping (larger waste, debris, bulky items, etc.)
- EV Chargers
- Flooding
- Gas leaf blower/string trimmer use
- General Code Enforcement Issue
- Graffiti
- Park Restrooms
- Parks and Playgrounds repairs
- Potholes (`94213`)
- Public signs
- Sidewalks (`94215`)
- Street Sweeping
- Street and curb striping and painting
- Streetlight (`94217`)
- Traffic Enforcement
- Traffic Signal Issue
- Trees
- Water System
- Weed control on public land

Streetlight questions are a required title, an optional description, a note, and an optional image. The note tells the resident to call PG&E at 1-877-660-6789 for streetlights on electric poles. Potholes on Willow Road, Bayshore Road, and El Camino Real are Caltrans, not the city. The same-day issue list included Streetlight, Trees, Street Sweeping, and Flooding, all acknowledged.

Before a skill exists:

- Register a SeeClickFix user and confirm `POST /api/v2/issues` accepts a photo as multipart, the way the docs describe.
- Record which answers are public. Streetlight title, description, and image are not marked private. The PG&E note is.
- Decide the boundary. A photo in Palo Alto must stay on PublicStuff. A photo in Menlo Park must not be sent to Palo Alto.
- Keep the preview. Nothing is sent until the user agrees.

### 2. Mountain View

Ask Mountain View can take a street report. The Streets topic (`2643`) includes:

| Subtopic | Id | Location widget in the page |
| --- | --- | --- |
| Street Lights | 10878 | Off |
| Potholes & Pavement Issues | 11266 | On |
| Sidewalk | 18005 | On |
| Street condition/Sidewalk condition | 18054 | On |
| Traffic Signals | 10855 | Off |
| Power Outages | 10870 | Off |
| Street Sweeping | 10879 | Not checked |
| Street Signs | 10854 | Not checked |

Graffiti is its own topic. Illegal dumping on streets and sidewalks is subtopic `16487`, and its location widget is on. Tree issues sit under Parks, Trees and Trails.

The location flag is a JavaScript variable on the form (`jsTopicLocation_<subtopic>`). Off does not mean the request has no place. It means this page does not show the map widget for that subtopic. Street lights may be a typed address. That has to be read from the custom-field HTML after a real session, which this check did not get.

A skill here would post the same form a browser posts. Comcate can change field names without a versioned API. Capture the submitted field names once, from a session, before writing a client. Do not send a request while doing that.

### 3. Sunnyvale

Do not build against Access Sunnyvale. The city replaced it with MySunnyvale on June 22, 2026, and said open tickets would move. Old Dynamics 365 portal pages are still indexed, including a street form with pole number, pole type, and outage, dim, flickering, or on during the day. Those are the retired form.

The new system is Salesforce Public Sector Solutions in Government Cloud, with a mobile app and Bucher-Suter telephony, under a contract awarded to Catalyst Consulting Group (file 25-0827, September 30, 2025). The name MySunnyvale and the chatbot name Sunny were set in file 26-0130.

Next check, once the portal can be opened:

- The public URL, and whether a guest can file without a Salesforce account.
- Whether a photo and coordinates are fields, or only a typed address.
- The street-light category, and whether pole number survived the move.

Until then, the phone line for street lights, potholes, sweeping, and debris is (408) 730-7415. That is a fallback, not an integration.

## Shared work, after a second city exists

The Palo Alto script refuses a photo outside the city. A later change can read the photo's city and pick the skill. That router is not useful until Menlo Park or Mountain View can submit.

PublicStuff is not the shared client. None of these three cities use it. SeeClickFix would be a second client, used by Menlo Park only until another SeeClickFix city is confirmed.
