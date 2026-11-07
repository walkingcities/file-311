# Menlo Park 311 catalog

Every request type in [`skills/menlo-park/catalog.json`](../../skills/menlo-park/catalog.json). A checkmark in the Run column links to that photo run in [`runs.md`](runs.md). This file is Menlo Park only. The list of other places is [`../jurisdictions.md`](../jurisdictions.md).

Streetlight is covered offline by [`tests/test_menlo_park_street_light.py`](../../tests/test_menlo_park_street_light.py). That test uses a stand-in photo and does not call the city. The camera-photo run is [Street light out, November 7, 2026](runs.md#street-light-out-november-7-2026).

## Source

`catalog.json` is a trimmed copy of Menlo Park's request types from the SeeClickFix API, read November 5, 2026. The same 20 types, organization `Menlo Park`, came back from `GET /api/v2/issues/new?lat=&lng=` at city hall, downtown, Belle Haven, Sharon Heights, Sand Hill, El Camino Real, Willow Road, Bayfront Expressway, and the south edge. Questions came from `GET /api/v2/request_types/{id}`.

The file keeps `id`, `name`, `organization`, the guest, anonymous, private, and `block_submission` flags, the form note, whether that note is public, and the title, description, and image fields. A note is form guidance. The script does not send it. `list`, `show`, `prepare`, and `submit` read this file. They do not refetch this list.

Every type has guest reporting off, anonymous reporting off, and private visibility off. There are no select lists and no name or phone fields. A report that can be submitted needs a public title. Description and image are optional on the form. This skill still requires the camera photo because that file carries the GPS.

Retired street-light id 15864, used by an older public request, now returns 404. The live id is 94217.

## Request types

20 types, in the order `issues/new` returned them.

| Run | Id | Request type |
| --- | --- | --- |
|  | 94209 | [Downtown Parking Machine](#downtown-parking-machine) |
|  | 94210 | [Dumping (larger waste, debris, bulky items, etc.)](#dumping-larger-waste-debris-bulky-items-etc) |
|  | 94211 | [EV Chargers](#ev-chargers) |
|  | 30942 | [Flooding](#flooding) |
|  | 131037 | [Gas leaf blower/string trimmer use](#gas-leaf-blowerstring-trimmer-use) |
|  | 100710 | [General Code Enforcement Issue](#general-code-enforcement-issue) |
|  | 22023 | [Graffiti](#graffiti) |
|  | 94242 | [Park Restrooms](#park-restrooms) |
|  | 94212 | [Parks and Playgrounds repairs](#parks-and-playgrounds-repairs) |
|  | 94213 | [Potholes](#potholes) |
|  | 94214 | [Public signs](#public-signs) |
|  | 94215 | [Sidewalks](#sidewalks) |
|  | 22033 | [Street Sweeping](#street-sweeping) |
|  | 94216 | [Street and curb striping and painting](#street-and-curb-striping-and-painting) |
| [✅](runs.md#street-light-out-november-7-2026) | 94217 | [Streetlight](#streetlight) |
|  | 22027 | [Traffic Enforcement](#traffic-enforcement) |
|  | 32517 | [Traffic Signal Issue](#traffic-signal-issue) |
|  | 94218 | [Trees](#trees) |
|  | 94219 | [Water System](#water-system) |
|  | 94220 | [Weed control on public land](#weed-control-on-public-land) |

## Types

### Downtown Parking Machine

Parking machine malfunction.

Id 94209. The report is public. Guest and anonymous reporting are off. A title is required. Description and image are optional.

### Dumping (larger waste, debris, bulky items, etc.)

Larger waste items discarded on public streets, alleys, sidewalks, or other public property. Please do not report litter (e.g. waste that could be blown away by wind). For information on free bulky item pick up, contact Recology at 650-595-3900 or visit https://www.recology.com/recology-san-mateo-county/bulky-items/

Id 94210. The report is public. Guest and anonymous reporting are off. A title is required. Description and image are optional.

### EV Chargers

Public EV charger malfunction.

Id 94211. The report is public. Guest and anonymous reporting are off. A title is required. Description and image are optional.

### Flooding

**NOTE**This is for reporting minor localized flooding or ponding. DO NOT report any life threatening conditions through this system. Please contact 911 if this is an emergency.

Id 30942. The report is public. This note is public. Guest and anonymous reporting are off. A title is required. Description and image are optional.

### Gas leaf blower/string trimmer use

If gas-powered leaf blower use is currently in progress, call the non-emergency line at 650-330-6300 for a potential real-time response. For past incidents, please include the date and time of the violation. An informational letter will be sent to the reported property about the zero emission landscaping equipment ordinance.

Id 131037. The report is public. Guest and anonymous reporting are off. A title is required. Description and image are optional. Choose this only when the person asked for it by name.

### General Code Enforcement Issue

For non-permitted construction, noise ordinance violations, weekend construction, etc.

Id 100710. The report is public. Guest and anonymous reporting are off. A title is required. Description and image are optional. Choose this only when the person asked for it by name.

### Graffiti

If graffiti is in progress, please dial the non-emergency number, 650-330-6300. City crews address graffiti on public property. Please provide photos to help with the location and issue. Private property owners and utility companies are responsible for graffiti removal on their property.

Id 22023. The report is public. This note is public. Guest and anonymous reporting are off. A title is required. Description and image are optional.

### Park Restrooms

Clogged toilets, no water coming from sink, no paper products, lights out in restroom. Please call 650-330-6780

Id 94242. SeeClickFix blocks submission. There is no title field. This is a phone call.

### Parks and Playgrounds repairs

Playground repairs, park maintenance, drinking fountains and irrigation issues. Note: Flood Park is maintained by County of San Mateo (650) 363-4100.

Id 94212. The report is public. Guest and anonymous reporting are off. A title is required. Description and image are optional.

### Potholes

Potholes (small bowl-shaped depressions in the street pavement). If it is safe to do so, please include photographs to assist crews with the location. Potholes on Willow Road, Bayshore Rd and/or El Camino Real are repaired by Caltrans. To submit a Caltrans request, please call (916) 654-5266 or visit http://www.dot.ca.gov/hq/maint/msrsubmit.

Id 94213. The report is public. Guest and anonymous reporting are off. A title is required. Description and image are optional. The script refuses a pothole whose address is El Camino Real, Willow, or Bayshore, including Bayshore Freeway.

### Public signs

Damaged existing traffic, parking and other public signs.

Id 94214. The report is public. Guest and anonymous reporting are off. A title is required. Description and image are optional.

### Sidewalks

Sidewalk tripping hazards. City performs temporary repairs on all sidewalks. For hazards not caused by City trees, abutting property owners are responsible for permanent repairs. https://www.menlopark.gov/sidewalks

Id 94215. The report is public. Guest and anonymous reporting are off. A title is required. Description and image are optional.

### Street Sweeping

Missed street sweep. For street sweep schedule, visit: https://www.menlopark.gov/Streetsweeping

Id 22033. The report is public. Guest and anonymous reporting are off. A title is required. Description and image are optional.

### Street and curb striping and painting

Street and curb stripping and painting maintenance.

Id 94216. The report is public. Guest and anonymous reporting are off. A title is required. Description and image are optional.

### Streetlight

Example run recorded. See [Street light out, November 7, 2026](runs.md#street-light-out-november-7-2026).

Existing streetlight issues (broken, outages or on all day). - For streetlights on electric poles please call PG&E 1-877-660-6789

Id 94217. The report is public. Guest and anonymous reporting are off. A title is required. Description and image are optional on the form. The photo is still required here because it carries the GPS. The default title is "Street light is out."

### Traffic Enforcement

For vehicles parked illegally in a red zone or blocking driveway, please call Police dispatch at 650-330-6300 for immediate response.

Id 22027. The report is public. This note is public. Guest and anonymous reporting are off. A title is required. Description and image are optional. Choose this only when the person asked for it by name.

### Traffic Signal Issue

Please call 650-330-6300 for traffic signal outages

Id 32517. SeeClickFix blocks submission. There is no title field. This is a phone call.

### Trees

Tree issues (branch/tree down, visibility of traffic signs/signals, blocking street/sidewalk, dead/unstable, other).

Id 94218. The report is public. Guest and anonymous reporting are off. A title is required. Description and image are optional.

### Water System

Water system issues for Menlo Park Municipal Water customers. For Cal Water, please call 650-561-9709. Water providers look up: https://menlopark.maps.arcgis.com/apps/InformationLookup/index.html?appid=e61f0eed1e7f46119f75a5e2d297a358

Id 94219. The report is public. Guest and anonymous reporting are off. A title is required. Description and image are optional.

### Weed control on public land

Weed control on street medians and City owned land and facilities. For Dumbarton railroad tracks please call SamTrans (650) 508-6200

Id 94220. The report is public. Guest and anonymous reporting are off. A title is required. Description and image are optional.
