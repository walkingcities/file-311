# Redwood City 311 catalog

Every request type in [`skills/redwood-city/catalog.json`](../../skills/redwood-city/catalog.json). A checkmark in the Run column links to that photo run in [`runs.md`](runs.md). This file is Redwood City only. The list of other places is [`../jurisdictions.md`](../jurisdictions.md).

Street Light Outage is covered offline by [`tests/test_redwood_city_street_light.py`](../../tests/test_redwood_city_street_light.py). That test uses a stand-in photo and does not call the city. The camera-photo run is [Street light broken, November 8, 2026](runs.md#street-light-broken-november-8-2026).

## Source

`catalog.json` is a trimmed copy of Redwood City's request types from the myRWC PublicStuff API, client 226, read November 5, 2026:

```
https://vc0.publicstuff.com/api/2.0/requesttypes_list?client_id=226&device=iframe&return_type=json
```

The response lists `response.request_types[].request_type`. The file keeps `id`, `name`, `description`, `confirmation`, `require_address`, `force_private`, and each custom field's `id`, `name`, `type`, `required`, `staff_only` (`is_public` is 0), and option names. `confirmation` is the text myRWC shows after a report is accepted. The repair timeline for a street light is in that text. `list`, `show`, `prepare`, and `submit` read this file. They do not refetch this list.

## Request types

46 types, in catalog order.

| Run | Id | Request type |
| --- | --- | --- |
|  | 1001535 | [Water Quality](#water-quality) |
|  | 23862 | [Illegal Dumping on Public Property](#illegal-dumping-on-public-property) |
|  | 14085 | [Hydrant Problem](#hydrant-problem) |
|  | 27265 | [Illegal Construction](#illegal-construction) |
|  | 15459 | [Parking Meters](#parking-meters) |
|  | 1009139 | [Customer Leak Questions](#customer-leak-questions) |
|  | 1009144 | [Recycled Water Questions](#recycled-water-questions) |
|  | 28868 | [Residential Noise](#residential-noise) |
|  | 1009148 | [Construction Meter](#construction-meter) |
|  | 1010249 | [No Water Issue - Non Billing Related](#no-water-issue---non-billing-related) |
|  | 14086 | [Water Leak](#water-leak) |
|  | 27266 | [Overgrown Weeds](#overgrown-weeds) |
|  | 1001862 | [Report Water Waste](#report-water-waste) |
|  | 1009158 | [Water Meter Issues](#water-meter-issues) |
|  | 1001863 | [Conservation Assistance](#conservation-assistance) |
|  | 1013691 | [Smoking Violation](#smoking-violation) |
|  | 1019988 | [Homeless](#homeless) |
|  | 26420 | [Tree Branch Down](#tree-branch-down) |
|  | 23498 | [Other](#other) |
|  | 1009467 | [Downtown Decorative Tree Lighting](#downtown-decorative-tree-lighting) |
|  | 1007816 | [Tree Other](#tree-other) |
|  | 1009141 | [Backflow/Well Questions](#backflowwell-questions) |
|  | 27264 | [Construction Noise](#construction-noise) |
|  | 1009954 | [High/Low Pressure Issue](#highlow-pressure-issue) |
|  | 1009138 | [High Bill Questions](#high-bill-questions) |
|  | 1005036 | [Abandoned Shopping Cart](#abandoned-shopping-cart) |
|  | 1010483 | [Glass/Debris in Street](#glassdebris-in-street) |
|  | 18477 | [ROW - Graffiti Removal - Public Property](#row---graffiti-removal---public-property) |
|  | 2469 | [Pothole](#pothole) |
|  | 1008709 | [Tree Pruning](#tree-pruning) |
|  | 1010750 | [Right of Way - Repainting of Curb & Pavement](#right-of-way---repainting-of-curb-pavement) |
|  | 24363 | [Sidewalk](#sidewalk) |
|  | 32016 | [Sign Knockdown](#sign-knockdown) |
|  | 32017 | [Sign Repair](#sign-repair) |
|  | 27268 | [Dayburner](#dayburner) |
|  | 2499 | [Other Street Light Problem](#other-street-light-problem) |
| [✅](runs.md#street-light-broken-november-8-2026) | 27267 | [Street Light Outage](#street-light-outage) |
|  | 2498 | [Traffic Signal Problem](#traffic-signal-problem) |
|  | 1004760 | [Graffiti Removal - Private Property](#graffiti-removal---private-property) |
|  | 30400 | [Illegal Dumping on Private Property](#illegal-dumping-on-private-property) |
|  | 1009801 | [Parking in Red Zone](#parking-in-red-zone) |
|  | 1019310 | [Bicycle-related incidents](#bicycle-related-incidents) |
|  | 2496 | [Abandoned Vehicles](#abandoned-vehicles) |
|  | 32018 | [Sign Other](#sign-other) |
|  | 24364 | [Tree Down](#tree-down) |
|  | 14988 | [Manhole](#manhole) |

## Types

### Water Quality

Confirmation: Thank you for submitting this water quality issue. You will be notified with progress updates, if any email address we provided.

Id 1001535. The city forces this report private. An address is required.

- Water Quality Complaint (39065, multiselect, required, staff-only). Options: Taste; Odor; Color; Turbidity; Air; High Pressure; Low Pressure; Water Outage; Suspended Solids; Other.
- Water Quality Issue Description (39066, text, optional, staff-only).

### Illegal Dumping on Public Property

Items dumped illegally in the public right of way will be scheduled for pickup. Examples of acceptable items include: mattresses, furniture, etc. This includes city owned buildings, streets, sidewalks, parking facilities, etc...

Confirmation: Thank you for submitting your request.  Staff will be assigned to complete this.

Id 23862. The city forces this report private. An address is required.

- Please check off all debris that is present. (3371, multiselect, optional, staff-only). Options: Compressed Gas; Furniture; Green trimmings; Household appliances; Paint; Trash; Unknown liquid.
- Please estimate how much debris is present. (3372, multiselect, optional, staff-only). Options: Equal to a standard pick-up truck bed; Less than a standard pick-up truck bed; More than a standard pick-up truck bed.

### Hydrant Problem

Hydrant leaking water or requires other maintenance.

Confirmation: Thank you for submitting your request.  Staff will follow up with your hydrant request, and update you on progress through this system.

Id 14085. The city forces this report private. An address is required.

- Is water spewing into the air? (3289, checkbox, optional).
- Is there an electrical line above the spewing water? (3286, checkbox, optional).
- Is the hydrant leaking? (3287, checkbox, optional).
- If water is not spewing/hydrant leaking, pls describe request. (3288, text, optional).

### Illegal Construction

Confirmation: Thank you for notifying The City of this potential code violation. Your request will be entered into our code tracking software by one of The City's code enforcement employees, and you will be provided with a tracking number within the next 5 business days.

Id 27265. The city forces this report private. An address is required.

No custom fields.

### Parking Meters

Problem with a parking meter (pay station or coin operated).

Confirmation: Thank you for submitting your request. Staff will follow up with your parking meter request, and update you on progress through this system.

Id 15459. The city forces this report private. An address is required.

- Is the problem with a parking pay station? (3290, checkbox, optional).
- If so, please check all problems with pay station. (3291, multiselect, optional). Options: Meter has been vandalized; Out of receipt paper; Unit will not operate at all.
- Please describe "other" pay station problem. (3292, text, optional).
- Is the problem with a coin-only parking meter? (3294, checkbox, optional).
- If so, please check all problems with coin-only meter. (3293, multiselect, optional). Options: Meter has been vandalized; Meter jammed, can't insert coins; Meter seems to be broken.

### Customer Leak Questions

Questions about customer leak, receiving leak emails, receiving leak door hangers.

Confirmation: Thank you for contacting Redwood City Water Resources Program. Staff will review your request, and will be in touch with you soon.

Id 1009139. The city forces this report private. An address is required.

No custom fields.

### Recycled Water Questions

Question in relation to the City's Recycled Water Program

Confirmation: Thank you for contacting Redwood City Water Resources Program. Staff will review your request, and will be in touch with you soon.

Id 1009144. The city forces this report private. An address is required.

No custom fields.

### Residential Noise

Confirmation: Thank you for notifying The City of this noise complaint. Your request will be delivered to our Police Department for follow up. Responses to requests will take place during business days (Monday-Friday). The Police Department can only address a noise complaint while the noise is occurring. If you would like immediate assistance please call 780-7100.

Id 28868. The city forces this report private. An address is required.

No custom fields.

### Construction Meter

Questions in relation to Potable and Recycled Water construction meter

Confirmation: Thank you for contacting Redwood City Water Resources Program. Staff will review your request, and will be in touch with you soon.

Id 1009148. The city forces this report private. An address is required.

No custom fields.

### No Water Issue - Non Billing Related

Confirmation: Thank you for submitting the request. Staff will follow up with your high/low pressure request, and update you on progress through this system. (PLEASE CALL POLICE DISPATCH 650-780-7118 IF THIS IS HAPPENING OUTSIDE OF Mon. - Fri. 7:00am - 3:30pm)

Id 1010249. The city forces this report private. An address is required.

No custom fields.

### Water Leak

If water is spewing onto the street or sidewalk, please submit a request and Public Works will respond immediately.

Confirmation: Thank you for submitting the request. Staff will follow up with your water leak request, and update you on progress through this system. (PLEASE CALL POLICE DISPATCH 650-780-7118 IF THIS IS HAPPENING OUTSIDE OF Mon. - Fri. 7:00am - 3:30pm)

Id 14086. The city forces this report private. An address is not required.

- Location of leak (choose best option). (3322, singleselect, optional). Options: Inside a private property; On the street; On the street (near sewer manhole); Outside a private property.
- Other location of leak (Please Describe) (3319, text, optional).
- Does the water smell like sewage? (3321, checkbox, optional).
- Is the water causing a flood? (3320, checkbox, optional).
- Is traffic being affected? (3323, checkbox, optional).

### Overgrown Weeds

Confirmation: Thank you for notifying The City of this potential code violation. Your request will be entered into our code tracking software by one of The City's code enforcement employees, and you will be provided with a tracking number within the next 5 business days.

Id 27266. The city forces this report private. An address is required.

No custom fields.

### Report Water Waste

Confirmation: Thank you for helping Redwood City conserve water. Staff will follow up with your request, and update you on progress through this system.

Id 1001862. The city forces this report private. An address is required.

- Address Requirements (4749, display, optional, staff-only).
- Violation (4750, singleselect, required, staff-only). Options: Fountain using water and not recirculating; Hotel did not give guest option to not launder linens; Irrigating during rainfall; Irrigating within 48 hours after rainfall; Irrigation water runoff; Restaurant serves water without request; Washing car without shutoff nozzle; Washing driveway or sidewalk.

### Water Meter Issues

Questions about meter replacement and meter related issues

Confirmation: Thank you for contacting Redwood City Water Resources Program. Staff will review your request, and will be in touch with you soon.

Id 1009158. The city forces this report private. An address is required.

No custom fields.

### Conservation Assistance

Questions about the City's conservation program

Confirmation: Thank you for contacting Redwood City Water Resources Program. Staff will review your request, and will be in touch with you soon.

Id 1001863. The city forces this report private. An address is required.

- Help with MyWater (4752, checkbox, optional, staff-only).
- Help with a rebate (4753, checkbox, optional, staff-only).
- Recycled Water Fill Station Program (4754, checkbox, optional, staff-only).
- Other (4755, text, optional, staff-only).

### Smoking Violation

Id 1013691. The city forces this report private. An address is required.

No custom fields.

### Homeless

Use this request type to report any homeless encampments, vehicles, unhoused individuals sleeping on the ground, and/or other issues.

Confirmation: Thank you for submitting your request.  Staff will be assigned to review your request.

Id 1019988. The city forces this report private. An address is required.

No custom fields.

### Tree Branch Down

Confirmation: Thank you for submitting your request.  Staff will follow up with your branch down request, and update you on progress through this system. (if this is an emergency, and immediate response is required please call 650-780-7464)

Id 26420. The city forces this report private. An address is required.

No custom fields.

### Other

If you cannot locate a request category that matches your request, please use the "Other" category to submit your request.

Confirmation: Thank you for submitting your request.  We will look into assigning your request to the correct department. Please watch for updates about your request using the tracking number that has been assigned to this request.

Id 23498. The city forces this report private. An address is required.

No custom fields.

### Downtown Decorative Tree Lighting

Confirmation: Thank you for submitting your lighting request. Staff will be assigned soon to investigate the issue.

Id 1009467. The city forces this report private. An address is required.

No custom fields.

### Tree Other

Confirmation: Thank you for submitting your request. Staff will follow up with your tree request, and update you on progress through this system.  (if this is an emergency, and immediate response is required please call 650-780-7464)

Id 1007816. The city forces this report private. An address is required.

No custom fields.

### Backflow/Well Questions

Questions about the City's Cross Connection program (Backflow and Well).

Confirmation: Thank you for contacting Redwood City Water Resources Program. Staff will review your request, and will be in touch with you soon.

Id 1009141. The city forces this report private. An address is required.

No custom fields.

### Construction Noise

Confirmation: Thank you for notifying The City of this potential code violation. Your request will be entered into our code tracking software by one of The City's code enforcement employees, and you will be provided with a tracking number within the next 5 business days.

Id 27264. The city forces this report private. An address is required.

No custom fields.

### High/Low Pressure Issue

Confirmation: Thank you for submitting the request. Staff will follow up with your high/low pressure request, and update you on progress through this system. (PLEASE CALL POLICE DISPATCH 650-780-7118 IF THIS IS HAPPENING OUTSIDE OF Mon. - Fri. 7:00am - 3:30pm)

Id 1009954. The city forces this report private. An address is required.

No custom fields.

### High Bill Questions

Questions in regards to high water bill.

Confirmation: Thank you for contacting Redwood City Water Resources Program. Staff will review your request, and will be in touch with you soon.

Id 1009138. The city forces this report private. An address is required.

No custom fields.

### Abandoned Shopping Cart

Id 1005036. The city forces this report private. An address is required.

No custom fields.

### Glass/Debris in Street

Items such as broken glass, litter, etc. in the street or on the sidewalk.

Confirmation: Thank you for submitting your request.  Staff will be assigned to complete this.

Id 1010483. The city forces this report private. An address is required.

No custom fields.

### ROW - Graffiti Removal - Public Property

Confirmation: Thank you for bringing this to our attention. This case will be assigned to the Police Department and City Graffiti Team within the next 2 business days. Please be aware that it could take several days to remove the graffiti depending on the workload of City staff.

Id 18477. The city forces this report private. An address is required.

- What is the graffiti on? (3310, multiselect, optional). Options: A building; A fence or wall; A sidewalk or street; A street sign or pole.
- Where exactly is the graffiti located? (3312, text, optional).
- Please provide any known suspect information. (3314, text, optional).

### Pothole

Report potholes within Redwood City limits here. 

Potholes on Woodside Road or El Camino Real are repaired by Caltrans. To submit a Caltrans request, please call (916) 654-5266 or visit http://www.dot.ca.gov/hq/maint/msrsubmit

Confirmation: Thank you for submitting your request.  Staff will follow up with your pothole request, and update you on progress through this system.

Id 2469. The city forces this report private. An address is required.

- Is the pothole located in a lane of traffic? (3343, checkbox, optional).
- Please estimate the width of the pothole. (3344, singleselect, optional). Options: Less than 12 inches across.; More than 12 inches across.

### Tree Pruning

Confirmation: Thank you for submitting your request. Staff will follow up with your tree request, and update you on progress through this system.  (if this is an emergency, and immediate response is required please call 650-780-7464)

Id 1008709. The city forces this report private. An address is required.

No custom fields.

### Right of Way - Repainting of Curb & Pavement

Repainting only. New curb and pavement markings must go through CD/Traffic Eng. staff for review and approval

Id 1010750. The city forces this report private. An address is required.

No custom fields.

### Sidewalk

Id 24363. The city forces this report private. An address is not required.

No custom fields.

### Sign Knockdown

Confirmation: Thank you for submitting your request.  Staff will follow up with your sign request, and update you on progress through this system.

Id 32016. The city forces this report private. An address is required.

No custom fields.

### Sign Repair

Confirmation: Thank you for submitting your request.  Staff will follow up with your sign request, and update you on progress through this system.

Id 32017. The city forces this report private. An address is required.

- Is there an damage to the pole? (3402, checkbox, optional, staff-only).

### Dayburner

Street light is on during the day.

Confirmation: Thank you for submitting this request. This Dayburner will be referred to Public Works' street light maintenance contractor for repair. You will be updated on the progress within the next 3 business days.

Id 27268. The city forces this report private. An address is required.

- Please provide street name and Cross Street. (3345, text, required, staff-only).

### Other Street Light Problem

Confirmation: Thank you for submitting this request. Staff will follow up with your street light request, and update you on progress through this system.

Id 2499. The city forces this report private. An address is not required.

- Street light pole fell on the street. (3331, checkbox, optional).
- Electrical wires fell on the street. (3332, checkbox, optional).

### Street Light Outage

Example run recorded. See [Street light broken, November 8, 2026](runs.md#street-light-broken-november-8-2026).

Street light bulb out.

Confirmation: Thank you for submitting this request. The Outage will be referred to Public Works' street light maintenance contractor for repair. You will be updated on the progress within the next 3 business days.

Id 27267. The city forces this report private. An address is required.

- Please provide street name and Cross Street. (3346, text, required, staff-only).

### Traffic Signal Problem

Traffic signal light out, flashing, or if the pole has fallen on the street.

Confirmation: Thank you for submitting your request. Staff will follow up with your traffic signal request, and update you on progress through this system.

Id 2498. The city forces this report private. An address is not required.

- Traffic signal bulb is out. (3333, checkbox, optional).
- Red light is flashing. (3334, text, optional).
- Traffic signal pole has fallen on the street. (3335, checkbox, optional).

### Graffiti Removal - Private Property

Confirmation: Thank you for bringing this to our attention. This case will be assigned to the Police Department and City Graffiti Team within the next 2 business days. Please be aware that it could take several days to remove the graffiti depending on the workload of City staff.

Id 1004760. The city forces this report private. An address is required.

- What is the graffiti on? (3310, multiselect, optional). Options: A building; A fence or wall; A sidewalk or street; A street sign or pole.
- Where exactly is the graffiti located? (3312, text, optional).
- Please provide any known suspect information. (3314, text, optional).

### Illegal Dumping on Private Property

Redwood City is not allowed to remove belongings from private property. If this is a repeat offence the city's code enforcement team can potentially fine the owner if items are not properly disposed of in a timely manor.

Confirmation: Thank you for submitting your request.  Redwood City's code enforcement will investigate the situation, and update you on progress through myRWC.

Id 30400. The city forces this report private. An address is required.

- Please estimate how much debris is present. (3396, multiselect, optional, staff-only). Options: Equal to a standard pick-up truck bed; Less than a standard pick-up truck bed; More than a standard pick-up truck bed.

### Parking in Red Zone

Vehicles Parked Illegally in a Red Zone
(Please call 780-7100 for immediate response)

Confirmation: Thank you for bringing this to our attention. This case will be assessed by the Police Department Traffic Supervisor within the next 2 business days. Please be aware that if the vehicle has been moved before this request is received we will not be able to take action. If you need someone to come out right away, please call 650-780-7100. Thank You.

Id 1009801. The city forces this report private. An address is required.

No custom fields.

### Bicycle-related incidents

Id 1019310. The city forces this report private. An address is required.

No custom fields.

### Abandoned Vehicles

72 hours or greater.

Confirmation: Thank you for bringing this to our attention. This case will be assigned to the Abandoned Vehicle Program Manager within the next two business days. Please be aware that abandoned vehicles may not be removed by the City until at least 72 hours have elapsed from the time an officer inspects the vehicle.

Id 2496. The city forces this report private. An address is required.

- Cross streets/specific address where vehicle is located? (3357, text, required, staff-only).
- Please describe the vehicle (make, model, color)? (3358, text, required, staff-only).
- What is the license plate number? (3355, text, required, staff-only).
- Why do you think this vehicle is abandoned? (3356, multiselect, required, staff-only). Options: The vehicle is stripped.; Vehicle parked over 72 hours.

### Sign Other

Confirmation: Thank you for submitting your request.  Staff will follow up with your sign request, and update you on progress through this system.

Id 32018. The city forces this report private. An address is required.

No custom fields.

### Tree Down

Confirmation: Thank you for submitting your request. Staff will follow up with your tree down request, and update you on progress through this system.  (if this is an emergency, and immediate response is required please call 650-780-7464)

Id 24364. The city forces this report private. An address is required.

No custom fields.

### Manhole

Metal cover missing or not fitting properly.

Confirmation: Thank you for submitting your request.  Staff will follow up with your manhole request, and update you on progress through this system.

Id 14988. The city forces this report private. An address is not required.

- What shape is the missing/damage cover (choose best option). (3285, singleselect, optional). Options: Large circular cover (sewer manhole); Rectangle; Small circular cover (water main); Square; Triangle (recycled water).
- Is the cover or lid missing? (3283, checkbox, optional).
- Is the cover or lid not seated properly (not flush with street)? (3284, checkbox, optional).
- Location of backup (3330, multiselect, optional, staff-only). Options: Cleanout; Manhole out in street; In Building; In Yard.
