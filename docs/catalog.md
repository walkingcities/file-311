# Palo Alto 311 catalog

Every request type in [`skills/palo-alto/catalog.json`](../skills/palo-alto/catalog.json). A checkmark means a camera photo was prepared or submitted in chat, and the transcript is under [Example runs](#example-runs).

Street Light Out is also covered offline by [`tests/test_street_light.py`](../tests/test_street_light.py). That test uses a stand-in photo and does not call the city, so its row stays open until a camera-photo run is recorded here.

## Source

`catalog.json` is a trimmed copy of Palo Alto's request types from the PaloAlto311 PublicStuff API, client 406:

```
https://vc0.publicstuff.com/api/2.0/requesttypes_list?client_id=406&device=iframe&return_type=json
```

The response lists `response.request_types[].request_type`. The file keeps `id`, `name`, `description`, `require_address`, `force_private`, and each custom field's `id`, `name`, `type`, `required`, `staff_only` (`is_public` is 0), and option names. It was captured when the Palo Alto skill was added and is read locally by `list`, `show`, `prepare`, and `submit`. Those commands do not refetch this list.

## Request types

72 types, in catalog order.

| Run | Id | Request type |
| --- | --- | --- |
|  | 1017001 | [Zoning & Land Use](#zoning-land-use) |
|  | 1020061 | [Substandard Housing](#substandard-housing) |
|  | 15505 | [Broken Sidewalk](#broken-sidewalk) |
|  | 1020062 | [Construction Activity (Private Property)](#construction-activity-private-property) |
|  | 15497 | [Tree Care Request](#tree-care-request) |
|  | 1002812 | [Broken or Missing Utility Lid or Manhole Cover](#broken-or-missing-utility-lid-or-manhole-cover) |
|  | 1003189 | [Traffic Safety Concern](#traffic-safety-concern) |
|  | 32342 | [Drinking Fountains](#drinking-fountains) |
|  | 1006533 | [Debris in Bike Lanes](#debris-in-bike-lanes) |
|  | 15496 | [Tree or Limb Down](#tree-or-limb-down) |
|  | 1017000 | [Vehicle Violation (Private Property)](#vehicle-violation-private-property) |
|  | 32713 | [New curb paint or a new parking signs](#new-curb-paint-or-a-new-parking-signs) |
|  | 15887 | [Shopping Cart, Abandoned](#shopping-cart-abandoned) |
|  | 27686 | [Debris in Parking Garages](#debris-in-parking-garages) |
|  | 25018 | [Debris in Roadway](#debris-in-roadway) |
|  | 15506 | [Flooding](#flooding) |
|  | 1019168 | [Other Park Maintenance](#other-park-maintenance) |
| [✅](#fallen-sign-november-3-2026) | 15503 | [Traffic Signs Damaged or Obstructed](#traffic-signs-damaged-or-obstructed) |
|  | 15510 | [Street Resurfacing](#street-resurfacing) |
|  | 1016998 | [Signs (Private Property)](#signs-private-property) |
|  | 32778 | [New traffic signs and/or pavement markings](#new-traffic-signs-andor-pavement-markings) |
|  | 33020 | [Unsafe driving behavior or speeding (non emergency)](#unsafe-driving-behavior-or-speeding-non-emergency) |
|  | 15892 | [Building Maintenance](#building-maintenance) |
|  | 1010806 | [Traffic Signal/Detection/Pedestrian Button Not Working](#traffic-signaldetectionpedestrian-button-not-working) |
|  | 1016997 | [Gas-Powered Leaf Blowers](#gas-powered-leaf-blowers) |
|  | 1016995 | [Fences and Walls](#fences-and-walls) |
|  | 32343 | [Irrigation](#irrigation) |
|  | 32344 | [Tennis Courts - Indicate Court #](#tennis-courts-indicate-court) |
|  | 1013714 | [Pickleball Courts - Indicate Court #](#pickleball-courts-indicate-court) |
|  | 1020084 | [Basketball Courts](#basketball-courts) |
|  | 1020085 | [Picnic Tables, Benches, BBQ Grills](#picnic-tables-benches-bbq-grills) |
|  | 1020087 | [Athletic Field Lighting](#athletic-field-lighting) |
|  | 1020088 | [Field Reservation Issue](#field-reservation-issue) |
|  | 1020089 | [Field Maintenance - Indicate Field #](#field-maintenance-indicate-field) |
|  | 1020090 | [Park Fencing](#park-fencing) |
|  | 1020091 | [Park Landscaping](#park-landscaping) |
|  | 1020092 | [Park Pathways](#park-pathways) |
|  | 1020093 | [Park Lighting](#park-lighting) |
|  | 1020094 | [Park Improvement Requests](#park-improvement-requests) |
|  | 32794 | [Street Light Out](#street-light-out) |
|  | 1006534 | [Potholes in Bike Lanes and/or Roadways](#potholes-in-bike-lanes-andor-roadways) |
|  | 15507 | [Clog/Debris on Storm Drain Grate](#clogdebris-on-storm-drain-grate) |
|  | 1012063 | [Electric Vehicle Charging Station(s)](#electric-vehicle-charging-stations) |
|  | 1017052 | [Playgrounds](#playgrounds) |
|  | 1003188 | [New bicycle rack or bicycle parking in the public ROW](#new-bicycle-rack-or-bicycle-parking-in-the-public-row) |
|  | 23012 | [Abandoned Bike or Scooter](#abandoned-bike-or-scooter) |
|  | 1020228 | [Illegal Dumping - Public Right of Way (P)](#illegal-dumping-public-right-of-way-p) |
|  | 1020108 | [Inquiries on Existing/Planned Transportation Projects](#inquiries-on-existingplanned-transportation-projects) |
|  | 1020060 | [Overgrown Vegetation in Public Right of Way](#overgrown-vegetation-in-public-right-of-way) |
|  | 1016992 | [Property Maintenance (Private Property)](#property-maintenance-private-property) |
|  | 1015852 | [American Disabilities Act (ADA) Request](#american-disabilities-act-ada-request) |
|  | 1013748 | [Parklets, Tables, and Chairs in Public Right of Way](#parklets-tables-and-chairs-in-public-right-of-way) |
|  | 1001404 | [Traffic Signal Timing Issue](#traffic-signal-timing-issue) |
|  | 15605 | [Other Request](#other-request) |
|  | 1002814 | [Damaged/Missing Electric/St Light/Traffic Signal/CPA Comm Cover](#damagedmissing-electricst-lighttraffic-signalcpa-comm-cover) |
|  | 14058 | [Graffiti Removal](#graffiti-removal) |
|  | 1020099 | [Unhoused Outreach-Connection to services](#unhoused-outreach-connection-to-services) |
|  | 4655 | [Pothole](#pothole) |
|  | 1020086 | [Other Park Amenities or Signage](#other-park-amenities-or-signage) |
|  | 1020101 | [AED Concern at City Facility](#aed-concern-at-city-facility) |
|  | 1020110 | [Public Transit Issue/Concern](#public-transit-issueconcern) |
|  | 1020100 | [Fire Code Violations](#fire-code-violations) |
|  | 1020109 | [Suggestions for Pedestrian/Bicycle Access to Destinations](#suggestions-for-pedestrianbicycle-access-to-destinations) |
|  | 1003184 | [Large amount of non-local traffic on a local street](#large-amount-of-non-local-traffic-on-a-local-street) |
|  | 1020098 | [E-bike/Scooter Riding Concern](#e-bikescooter-riding-concern) |
|  | 1001495 | [Drought/Water Waste](#droughtwater-waste) |
|  | 1008122 | [Hazardous Materials](#hazardous-materials) |
|  | 1016999 | [Illegal Signs on Public Property/Right of Way](#illegal-signs-on-public-propertyright-of-way) |
|  | 1016993 | [Noise Violations](#noise-violations) |
|  | 1020059 | [Vehicle Parking Violation - In the Roadway/Sidewalk](#vehicle-parking-violation-in-the-roadwaysidewalk) |
|  | 15499 | [Missed Street Sweeping Route](#missed-street-sweeping-route) |
|  | 1016994 | [Public Right of Way Obstructions/Encroachment](#public-right-of-way-obstructionsencroachment) |

## Example runs

### Fallen sign, November 3, 2026

Prepared on November 3, 2026. Not submitted. The transcript below is the dry-run chat.

The photo is a green bike-lane wayfinding sign lying on the dirt shoulder, post down, beside a road with a railroad crossing and a 10 mph curve sign. The original camera file is `992FBCAD-1F89-4139-83A4-A89A9630121B_1_105_c-4832a9e1-6c3c-4b5d-a20f-bd006fd58e33.jpg`.

**Christopher:** Dry run; do not submit. Report this sign to Palo Alto 311 that fell down. See attached photo.

**Assistant:** Dry run only. Nothing was submitted.

- Request type: Traffic Signs Damaged or Obstructed
- Address: 67 Palo Alto Ave, Palo Alto, CA 94301
- Cross street: Alma St & Palo Alto Ave
- Description: A green bike-lane wayfinding sign has fallen and is lying on the dirt shoulder beside the road. The post is down.
- Intersection (staff-only): Alma St & Palo Alto Ave

The photo and the location would be public. This request type has no name or phone field. The intersection is the only staff-only field.

## Types

### Zoning & Land Use

Complaints may include unpermitted short-term rentals, home-based businesses operating without required approvals, or commercial activity in zones where it is not permitted. NOTE: Do not include personal info in the Description field.

Id 1017001. The city forces this report private. An address is required.

- Contact Name (3608, text, required, staff-only).
- Preferred Method of First Contact (3910, singleselect, required, staff-only). Options: Email (registered user email); Phone (please provide phone number).
- Phone Number (3611, text, optional, staff-only).
- Additional Location Description for Request (3656, text, required, staff-only).

### Substandard Housing

Complaints may include inadequate heating, plumbing, or electrical conditions; the presence of mold, lead, or asbestos; pest infestations; structural hazards (such as failing floors or stairways); or landlords failing to make required repairs in occupied units. NOTE: Do not include personal info in the Description field.

Id 1020061. The city forces this report private. An address is required.

- Contact Name (3608, text, required, staff-only).
- Preferred Method of First Contact (3910, singleselect, required, staff-only). Options: Email (registered user email); Phone (please provide phone number).
- Phone Number (3611, text, optional, staff-only).
- Additional Location Description for Request (3656, text, required, staff-only).

### Broken Sidewalk

Report sidewalks with lifting, a hazardous condition or other concerns.

Id 15505. This report is public. An address is required.

- Intersection (5128, text, required, staff-only).

### Construction Activity (Private Property)

Complaints may include unpermitted construction or demolition, work exceeding an approved permit scope, construction outside of allowed hours (8 AM–6 PM Monday–Friday, 9 AM–6 PM Saturday; no work permitted on Sundays or holidays), or unsafe/exposed hazards. NOTE: Do not include personal info in the Description field.

For after-hours complaints, contact the non-emergency police line at (650) ...

Id 1020062. The city forces this report private. An address is required.

- Contact Name (3608, text, required, staff-only).
- Preferred Method of First Contact (3910, singleselect, required, staff-only). Options: Email (registered user email); Phone (please provide phone number).
- Phone Number (3611, text, optional, staff-only).
- Additional Location Description for Request (3656, text, required, staff-only).

### Tree Care Request

Report tree concerns or questions regarding tree health for trees not on private property.

Id 15497. This report is public. An address is required.

- Intersection (5128, text, required, staff-only).

### Broken or Missing Utility Lid or Manhole Cover

Broken or Missing Utility Lid or Manhole Cover

Id 1002812. This report is public. An address is required.

No custom fields.

### Traffic Safety Concern

Report general traffic congestion or traffic safety concern (non-emergency)

Id 1003189. This report is public. An address is required.

- Contact Name (3608, text, required, staff-only).
- Preferred Method of First Contact (3910, singleselect, required, staff-only). Options: Email (registered user email); Phone (please provide phone number).
- Phone Number (3611, text, optional, staff-only).
- Describe your request (3612, text, required, staff-only).
- Additional Location Description for Request (3656, text, required, staff-only).

### Drinking Fountains

Issues with drinking fountains.

Id 32342. This report is public. An address is not required.

- Park/Site Name for drinking fountain problems (3244, singleselect, required, staff-only). Options: Arastradero Preserve; Baylands Athletic Center; Baylands Nature Preserve; Bol Park; Boulware Park; Bowden Park; Bowling Green Park; Briones Park; Cameron Park; Cogswell Plaza; El Camino Park; Eleanor Pardee Park; Foothills Park; Greer Park; Heritage Park; Hoover Park; Hopkins Tennis Courts; Johnson Park; Lytton Plaza; Mitchell Park; Monroe Park; Peers Park; Ramos Park; Rinconada Park; Robles Park; Scott Park; Seale Park; Stanford/Palo Alto Playing Fields; Terman Park; Timothy Hopkins Creekside Park; Weisshaar Park; Werry Park.

### Debris in Bike Lanes

To report glass, dirt or gravel spills in the Bike Lanes and/or Roadways.

Id 1006533. This report is public. An address is required.

- Intersection (5128, text, required, staff-only).

### Tree or Limb Down

Report a tree or limb that has fallen and obstructing the right of way.

Id 15496. This report is public. An address is required.

- Intersection (5128, text, required, staff-only).

### Vehicle Violation (Private Property)

Report different types of vehicle, trailer, RV issues on private property (e.g., inoperable vehicle storage, extended trailer/RV parking, etc.) NOTE: Do not include personal info in the Description field.

Id 1017000. The city forces this report private. An address is required.

- Contact Name (3608, text, required, staff-only).
- Preferred Method of First Contact (3910, singleselect, required, staff-only). Options: Email (registered user email); Phone (please provide phone number).
- Phone Number (3611, text, optional, staff-only).
- Additional Location Description for Request (3656, text, required, staff-only).

### New curb paint or a new parking signs

Suggest new curb paint or a new parking signs

Id 32713. This report is public. An address is required.

- Contact Name (3608, text, required, staff-only).
- Preferred Method of First Contact (3910, singleselect, required, staff-only). Options: Email (registered user email); Phone (please provide phone number).
- Phone Number (3611, text, optional, staff-only).
- Describe your request (3612, text, required, staff-only).
- Additional Location Description for Request (3656, text, required, staff-only).

### Shopping Cart, Abandoned

Report abandoned shopping carts.

Id 15887. This report is public. An address is required.

- Intersection (5128, text, required, staff-only).

### Debris in Parking Garages

Id 27686. This report is public. An address is required.

- Intersection (5129, text, required, staff-only).

### Debris in Roadway

To report glass, dirt or gravel spills in the roadway.

Id 25018. This report is public. An address is required.

- Intersection (5128, text, required, staff-only).

### Flooding

Report flooding.

Id 15506. This report is public. An address is required.

- Intersection (5128, text, required, staff-only).

### Other Park Maintenance

Report issues with park maintenance not listed above.

Id 1019168. This report is public. An address is required.

- Park Name (3246, singleselect, required, staff-only). Options: Baylands Athletic Center; Baylands Nature Preserve; Bol Park; Boulware Park; Bowden Park; Bowling Green Park; Briones Park; Byxbee Park; Cameron Park; Cogswell Park; El Camino Park; El Palo Alto Park; Eleanor Pardee Park; Esther Clark Park; Foothills Nature Preserve; Greer Park; Heritage Park; Hoover Park; Hopkins Creekside Park; Johnson Park; Lytton Plaza; Mayfield Park; Mayfield Soccer Complex; Mitchell Park; Monroe Park; Pearson-Arastradero Preserve; Peers Park; Ramos Park; Rinconada Park; Robles Park; Sarah Wallis Park; Scott Park; Seale Park; Terman Park; Weisshaar Park; Werry Park.

### Traffic Signs Damaged or Obstructed

Example run recorded. See [Fallen sign, November 3, 2026](#fallen-sign-november-3-2026).

Report missing, bent and unreadable traffic signs.

Id 15503. This report is public. An address is required.

- Intersection (5128, text, required, staff-only).

### Street Resurfacing

Contact us if you have questions about your street or street resurfacing.

Id 15510. This report is public. An address is required.

No custom fields.

### Signs (Private Property)

Complaints may include unpermitted signs, abandoned signs from closed businesses, or illegal temporary or banner signage. NOTE: Do not include personal info in the Description field.

Id 1016998. The city forces this report private. An address is required.

- Contact Name (3608, text, required, staff-only).
- Preferred Method of First Contact (3910, singleselect, required, staff-only). Options: Email (registered user email); Phone (please provide phone number).
- Phone Number (3611, text, optional, staff-only).
- Additional Location Description for Request (3656, text, required, staff-only).

### New traffic signs and/or pavement markings

Suggest new traffic signs and/or pavement markings  (crosswalks, sharrows, etc.)

Id 32778. This report is public. An address is required.

- Contact Name (3608, text, required, staff-only).
- Preferred Method of First Contact (3910, singleselect, required, staff-only). Options: Email (registered user email); Phone (please provide phone number).
- Phone Number (3611, text, optional, staff-only).
- Describe your request (3612, text, required, staff-only).
- Additional Location Description for Request (3656, text, required, staff-only).

### Unsafe driving behavior or speeding (non emergency)

Please report URGENT unsafe driving conditions requiring a prompt response to the Police Department @ (650) 329-2413 or call 911.

Id 33020. This report is public. An address is required.

- Contact Name (3608, text, required, staff-only).
- Preferred Method of First Contact (3910, singleselect, required, staff-only). Options: Email (registered user email); Phone (please provide phone number).
- Phone Number (3611, text, optional, staff-only).
- Describe your request (3612, text, required, staff-only).
- Additional Location Description for Request (3656, text, required, staff-only).

### Building Maintenance

Report a maintenance issue with a City building.

Id 15892. This report is public. An address is required.

No custom fields.

### Traffic Signal/Detection/Pedestrian Button Not Working

Id 1010806. This report is public. An address is not required.

- Contact Name (3608, text, required, staff-only).
- Phone Number (3260, text, required, staff-only).
- Describe your request (3612, text, required, staff-only).
- Additional Location Description for Request (3656, text, required, staff-only).

### Gas-Powered Leaf Blowers

Complaints may include the use of gas-powered leaf blowers on residential property by owners, occupants, or landscaping crews. The City does not currently regulate gas-powered leaf blower use on non-residential properties.

Please be sure to include the specific location, time of occurrence, and day of the week in your report. 

NOTE: Do not include personal info in the Description field.

Id 1016997. The city forces this report private. An address is required.

- Contact Name (3608, text, required, staff-only).
- Preferred Method of First Contact (3910, singleselect, required, staff-only). Options: Email (registered user email); Phone (please provide phone number).
- Phone Number (3611, text, optional, staff-only).
- Additional Location Description for Request (3656, text, required, staff-only).
- Observed Date/Time (39746, text, required, staff-only).
- Please confirm that the address above is correct.  (39747, singleselect, required, staff-only). Options: Yes.

### Fences and Walls

Complaints may include fences or walls that obstruct visibility or are in disrepair. Some situations may be civil matters, and property owners may need to work directly with each other to resolve the issue. NOTE: Do not include personal info in the Description field.

Id 1016995. The city forces this report private. An address is required.

- Contact Name (3608, text, required, staff-only).
- Preferred Method of First Contact (3910, singleselect, required, staff-only). Options: Email (registered user email); Phone (please provide phone number).
- Phone Number (3611, text, optional, staff-only).
- Additional Location Description for Request (3656, text, required, staff-only).

### Irrigation

Issues with sprinklers or drainage.

Id 32343. This report is public. An address is required.

- Park/Site Name for irrigation problems (public) (3247, singleselect, optional, staff-only). Options: Alma Tower; Arastradero Preserve; Baylands Athletic Center; Baylands Nature Preserve; Bol Park; Boulware Park; Bowden Park; Briones Park; Cameron Park; Cogswell Plaza; El Camino Park; Foothills Park; Greer Park; Heritage Park; Homer Tunnel; Hoover Park; Johnson Park; Lawn Bowling Green; Lytton Plaza; Mitchell Park; Pardee Park; Pearson Arastradero Preserve; Peers Park; Ramos Park; Rinconada Park; Robles Park; Scott Street Park; Seale Park; Stanford Palo Alto Playing Fields; Terman Park; Timothy Hopkins at Cowper; Timothy Hopkins at Middlefield; Timothy Hopkins at Webster; Weisshaar Park; Werry Park.

### Tennis Courts - Indicate Court #

Report issues with tennis courts. Please indicate the court # if known. Court numbers are typically labeled on the backstop or fence.

Id 32344. This report is public. An address is not required.

- Park/Site Name for tennis court issues (3248, singleselect, required, staff-only). Options: Cubberley Community Center; Hoover Park; Mitchell Park; Peers Park; Rinconada Park; Terman Park; Weisshaar Park.

### Pickleball Courts - Indicate Court #

Report issues with pickleball courts. Please indicate the court # if known. Court numbers are typically labeled on the backstop or fence.

Id 1013714. This report is public. An address is not required.

- Park Name/Location (42400, text, required, staff-only).

### Basketball Courts

Report issues with a basketball court.

Id 1020084. This report is public. An address is not required.

- Park Name/Location (42400, text, required, staff-only).

### Picnic Tables, Benches, BBQ Grills

Report issues with picnic tables, benches, BBQ grills.

Id 1020085. This report is public. An address is not required.

- Park Name/Location (42400, text, required, staff-only).

### Athletic Field Lighting

Report issues with athletic field lighting.

Id 1020087. This report is public. An address is not required.

- Park Name/Location (42400, text, required, staff-only).

### Field Reservation Issue

Report issues with field reservations.

Id 1020088. This report is public. An address is not required.

- Park Name/Location (42400, text, required, staff-only).

### Field Maintenance - Indicate Field #

Report issues with field maintenance. Please indicate the field # if known. Field numbers are typically labeled on the backstop or fence.

Id 1020089. This report is public. An address is not required.

- Park Name/Location (42400, text, required, staff-only).

### Park Fencing

Report issues with park fencing.

Id 1020090. This report is public. An address is not required.

- Park Name/Location (42400, text, required, staff-only).

### Park Landscaping

Report issues with park landscaping.

Id 1020091. This report is public. An address is not required.

- Park Name/Location (42400, text, required, staff-only).

### Park Pathways

Report issues with park pathways.

Id 1020092. This report is public. An address is not required.

- Park Name/Location (42400, text, required, staff-only).

### Park Lighting

Report issues with park lighting.

Id 1020093. This report is public. An address is not required.

- Park Name/Location (42400, text, required, staff-only).

### Park Improvement Requests

Suggest new park improvements and facilities here.

Id 1020094. This report is public. An address is not required.

- Park Name/Location (42400, text, required, staff-only).

### Street Light Out

Please allow 5 business days for us to make repairs.

Id 32794. This report is public. An address is required.

- Name (3266, text, required, staff-only).
- Phone Number (3260, text, required, staff-only).
- Pole Number (3256, text, optional, staff-only).
- Light Location Address (3258, text, required, staff-only).
- Cross Street (3259, text, required, staff-only).
- Additional Address Info (3262, text, optional, staff-only).
- Condition of Light (3257, singleselect, required, staff-only). Options: Flickering; Out; Stays On.
- Is there damage to the light? (3263, singleselect, required, staff-only). Options: No; Yes.
- If yes, please describe (3264, text, optional, staff-only).
- Additional information or comments (3265, text, optional, staff-only).

### Potholes in Bike Lanes and/or Roadways

Report potholes in bike lanes and roadways.

Id 1006534. This report is public. An address is required.

- Intersection (5128, text, required, staff-only).

### Clog/Debris on Storm Drain Grate

Debris on storm drain grate creating blockage and water ponding in the gutter. 
Call 650.329.2413 to report any active spill of any substance into a storm drain.

Id 15507. This report is public. An address is required.

- Intersection (5128, text, required, staff-only).

### Electric Vehicle Charging Station(s)

Please submit a service request or report an issue with a City of Palo Alto public electric vehicle charging station.

Id 1012063. This report is public. An address is required.

No custom fields.

### Playgrounds

Playground maintenance requests.

Id 1017052. This report is public. An address is required.

- Park Name (3245, singleselect, required, staff-only). Options: Baylands Athletic Center; Baylands Nature Preserve; Bol Park; Boulware Park; Bowden Park; Briones Park; Cameron Park; Cogswell Plaza; El Camino Park; Foothills Park; Greer Park; Heritage Park; Hoover Park; Johnson Park; Lawn Bowling Green; Mitchell Park; Pardee Park; Pearson Arastradero Preserve; Peers Park; Ramos Park; Rinconada Park; Robles Park; Scott Street Park; Seale Park; Stanford Palo Alto Playing Fields; Terman Park; Timothy Hopkins @ Cowper; Timothy Hopkins @ Middlefield; Weisshaar Park; Timothy Hopkins @ Webster; Werry Park.

### New bicycle rack or bicycle parking in the public ROW

New bicycle rack or bicycle parking in the public right-of-way (ROW)

Id 1003188. This report is public. An address is required.

- Contact Name (3608, text, required, staff-only).
- Preferred Method of First Contact (3910, singleselect, required, staff-only). Options: Email (registered user email); Phone (please provide phone number).
- Phone Number (3611, text, optional, staff-only).
- Describe your request (3612, text, required, staff-only).
- Additional Location Description for Request (3656, text, required, staff-only).

### Abandoned Bike or Scooter

Report abandoned bicycles or scooters.

Id 23012. This report is public. An address is required.

- Intersection (5128, text, required, staff-only).

### Illegal Dumping - Public Right of Way (P)

Illegal dumping of leaves, debris, furniture or other items on public streets and sidewalks.

Id 1020228. The city forces this report private. An address is required.

- Intersection (5128, text, required, staff-only).

### Inquiries on Existing/Planned Transportation Projects

Have a question about an existing or future transportation project? Ask here.

Id 1020108. This report is public. An address is not required.

No custom fields.

### Overgrown Vegetation in Public Right of Way

Report overgrown vegetation/weeds in the public right-of-way obstructing sidewalks or visibility.

Id 1020060. The city forces this report private. An address is required.

- Describe your request (3612, text, required, staff-only).
- Contact Name (3608, text, required, staff-only).
- Preferred Method of First Contact (3910, singleselect, required, staff-only). Options: Email (registered user email); Phone (please provide phone number).
- Phone Number (3611, text, optional, staff-only).
- Additional Location Description for Request (3656, text, required, staff-only).

### Property Maintenance (Private Property)

Complaints may include abandoned or vacant buildings, overgrown vegetation, visibly deteriorated structures, or accumulation of trash and debris. NOTE: Do not include personal info in the Description field.

Id 1016992. The city forces this report private. An address is required.

- Contact Name (3608, text, required, staff-only).
- Preferred Method of First Contact (3910, singleselect, required, staff-only). Options: Email (registered user email); Phone (please provide phone number).
- Phone Number (3611, text, optional, staff-only).
- Additional Location Description for Request (3656, text, required, staff-only).

### American Disabilities Act (ADA) Request

Report a concern that a City facility, program, policies, services, or activity is not accessible to persons with disabilities.  If you have numerous concerns, please create a separate service request per concern.

Id 1015852. The city forces this report private. An address is required.

No custom fields.

### Parklets, Tables, and Chairs in Public Right of Way

Use this request ONLY to report table and chairs in the public right-of-way that may be a permitting issue. This request will be routed to Public Works Engineering Services staff, who are responsible for reviewing work in the public right-of-way. NOTE: Do not include personal info in the Description field.

Id 1013748. The city forces this report private. An address is required.

No custom fields.

### Traffic Signal Timing Issue

Suggest New Traffic Signal (New Left Turn Light, New Intersection Traffic Light, etc)

Id 1001404. This report is public. An address is required.

- Contact Name (3608, text, required, staff-only).
- Preferred Method of First Contact (3910, singleselect, required, staff-only). Options: Email (registered user email); Phone (please provide phone number).
- Phone Number (3611, text, optional, staff-only).
- Describe your request (3612, text, required, staff-only).
- Additional Location Description for Request (3656, text, required, staff-only).

### Other Request

For other community inquiries, please share specific details about what you are reporting including a short description of the issue, location, and contact information should we have follow-up questions. Otherwise, please email the City at  City at CityMgr@paloalto.gov or call us at 650-329-2100. Thank you.

Id 15605. This report is public. An address is not required.

- Contact Name (3608, text, required, staff-only).
- Preferred Method of First Contact (3910, singleselect, required, staff-only). Options: Email (registered user email); Phone (please provide phone number).
- Describe your request (3610, text, required, staff-only).

### Damaged/Missing Electric/St Light/Traffic Signal/CPA Comm Cover

City of Palo Alto will send their utility first repsonders out to investigate the request.
*ATTN  for all other utilities, contact as follows:
AT&T:  1-800-288-2020 
Comcast: 1-800-934-6489
CalTrans:  (415) 330-6500

Id 1002814. This report is public. An address is required.

- Name (3266, text, required, staff-only).
- Phone Number (3254, text, required, staff-only).
- Location Address of Lid/Cover (13715, text, required, staff-only).
- Cross Street (3259, text, required, staff-only).
- Additional Address Info and/or Lid# (13854, text, optional, staff-only).
- Condition of Lid/Cover (13716, singleselect, required, staff-only). Options: Broken/Damaged; Missing.

### Graffiti Removal

Report graffiti and vandalism for removal.

Id 14058. This report is public. An address is required.

- Intersection (5128, text, required, staff-only).

### Unhoused Outreach-Connection to services

Share details about an unhoused individual  to help connect them to support services.

Id 1020099. This report is public. An address is not required.

No custom fields.

### Pothole

Report potholes.

Id 4655. This report is public. An address is required.

- Intersection (5128, text, required, staff-only).

### Other Park Amenities or Signage

Report issues with park signs or amenities not listed above.

Id 1020086. This report is public. An address is not required.

- Park Name/Location (42400, text, required, staff-only).

### AED Concern at City Facility

Report concerns that an AED located at City facility or park may need to be addressed.

Id 1020101. This report is public. An address is required.

No custom fields.

### Public Transit Issue/Concern

Inquiries about Palo Alto Link, PATMA transit passes, or other available transit services.

Id 1020110. This report is public. An address is not required.

No custom fields.

### Fire Code Violations

Report fire code violations such as:
-Blocked building entrances/exits
-Blocked emergency access
-Faulty building sprinkler or alarm systems

Id 1020100. This report is public. An address is required.

No custom fields.

### Suggestions for Pedestrian/Bicycle Access to Destinations

Submit suggestions to improve pedestrian or bicycle access to common destinations such as transit stations, schools, parks, shopping, etc. This request is NOT for American Disabilities Act (ADA) improvements.

Id 1020109. This report is public. An address is not required.

No custom fields.

### Large amount of non-local traffic on a local street

Report large amount of non-local traffic on a local street

Id 1003184. This report is public. An address is required.

- Contact Name (3608, text, required, staff-only).
- Preferred Method of First Contact (3910, singleselect, required, staff-only). Options: Email (registered user email); Phone (please provide phone number).
- Phone Number (3611, text, optional, staff-only).
- Describe your request (3612, text, required, staff-only).
- Additional Location Description for Request (3656, text, required, staff-only).

### E-bike/Scooter Riding Concern

Please report URGENT unsafe driving conditions requiring a prompt response to the Police Department @ (650) 329-2413 or call 911.

Id 1020098. This report is public. An address is not required.

No custom fields.

### Drought/Water Waste

Report Water Waste

Id 1001495. The city forces this report private. An address is not required.

- Address Type (3238, singleselect, required, staff-only). Options: Commercial; Other; Residential.
- Violation Type (3720, multiselect, required, staff-only). Options: Days of Week; General Water Waste; Irrigation Runoff; Leak; Time of Day.
- Address or Location for Request (3609, text, required, staff-only).
- Cross Street (3259, text, required, staff-only).

### Hazardous Materials

Report hazardous materials/waste illegal dumping, spills, or storage. 

If you feel that this is an emergency situation, please call 911.

Id 1008122. This report is public. An address is required.

No custom fields.

### Illegal Signs on Public Property/Right of Way

Report different types of Illegal signs on public property or public right of way (A Frame signs on sidewalk, signs on street medians, street light poles, utility poles, etc.) NOTE: Do not include personal info in the Description field.

Id 1016999. The city forces this report private. An address is required.

- Contact Name (3608, text, required, staff-only).
- Preferred Method of First Contact (3910, singleselect, required, staff-only). Options: Email (registered user email); Phone (please provide phone number).
- Phone Number (3611, text, optional, staff-only).
- Additional Location Description for Request (3656, text, required, staff-only).

### Noise Violations

Complaints may include excessive noise from HVAC units, pool or spa equipment, or water features on private property. NOTE: Do not include personal info in the Description field.

Id 1016993. The city forces this report private. An address is required.

- Contact Name (3608, text, required, staff-only).
- Preferred Method of First Contact (3910, singleselect, required, staff-only). Options: Email (registered user email); Phone (please provide phone number).
- Phone Number (3611, text, optional, staff-only).
- Additional Location Description for Request (3656, text, required, staff-only).

### Vehicle Parking Violation - In the Roadway/Sidewalk

Report different types of vehicle, trailer, RV issues in the public right-of-way (e.g., inoperable vehicle storage, extended trailer/RV parking on street, etc.) NOTE: Do not include personal info in the Description field.

Id 1020059. The city forces this report private. An address is required.

- Contact Name (3608, text, required, staff-only).
- Preferred Method of First Contact (3910, singleselect, required, staff-only). Options: Email (registered user email); Phone (please provide phone number).
- Phone Number (3611, text, optional, staff-only).
- Additional Location Description for Request (3656, text, required, staff-only).

### Missed Street Sweeping Route

To report that sweeping was not done on your scheduled day.

Id 15499. This report is public. An address is required.

- Intersection (5129, text, required, staff-only).

### Public Right of Way Obstructions/Encroachment

Report different types of Public Right of Way Encroachment issues (Overgrown Vegetation, debris, weeds, garbage, damaged news racks, etc on sidewalk/public right of way) NOTE: Do not include personal info in the Description field.

Id 1016994. The city forces this report private. An address is required.

- Contact Name (3608, text, required, staff-only).
- Preferred Method of First Contact (3910, singleselect, required, staff-only). Options: Email (registered user email); Phone (please provide phone number).
- Phone Number (3611, text, optional, staff-only).
- Additional Location Description for Request (3656, text, required, staff-only).

