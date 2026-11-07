# Jurisdictions

Palo Alto, Redwood City, and Menlo Park are the places this repo files. A photo outside that city is refused. Another jurisdiction is a new folder under `skills/`, using the same photo, GPS, and preview-before-send flow. A row that is not Done is not built.

Palo Alto's request-type list and photo runs are `docs/palo-alto/catalog.md` and `docs/palo-alto/runs.md`. The next city gets the same pair, `docs/<city>/catalog.md` and `docs/<city>/runs.md`. This file stays the list of every jurisdiction.

Checked November 4, 2026. SeeClickFix results are from `GET /api/v2/issues/new` at a downtown point, and only count when the organization is that city or the city page names SeeClickFix. A SeeClickFix place page is not evidence. Palo Alto has one and uses PublicStuff.

Effort is the work to add a skill like Palo Alto. Photo GPS, JPEG conversion, and reverse geocoding already live in `file-311-common`. The client, catalog, account file, and boundary check do not carry over.

- **Done.** The skill exists.
- **Low.** A public create API answered for that jurisdiction.
- **Medium.** A public form or known portal accepts the report. No public create API was found.
- **High.** The channel is a closed CRM, an app whose vendor was not captured, or a phone line.
- **Not confirmed.** This check did not open a live submit form.

Ten cities are still Low, and they are all SeeClickFix. Menlo Park is the SeeClickFix skill that is filed. Palo Alto and Redwood City are both Accela PublicStuff. Palo Alto is client `406`. Redwood City is client `226`. The myRWC catalog was read on November 5, 2026.

Volunteer and ETA are open. A blank row is unclaimed. To take one, open a pull request that puts your GitHub name in Volunteer and a date in ETA, then send the skill in that pull request or a follow-up. Review the other open pull requests. Palo Alto, Redwood City, and Menlo Park are already filed, so leave those rows blank.

## Santa Clara County cities

| City | System | How a resident files | Programmatic access | Effort | Volunteer | ETA |
| --- | --- | --- | --- | --- | --- | --- |
| Campbell | iWorQ Citizen Engagement | Web portal and the iWorQ Service Request app. Agency code `Campbell01`. Guest or account. Photos. | No public API found. | Medium | | |
| Cupertino | Granicus CitySourced, branded Cupertino 311 | City site and app. The app uses GPS and a photo. Anonymous, or logged in for status email. | No open create API confirmed. | Medium | | |
| Gilroy | SeeClickFix, branded GilroyConnect | City streetlight page and app `org.cityofgilroy.seeclickfix.com`. | API returned 61 types at `37.0058, -121.5683`, including Streetlights and Streets. Orgs are named Maintenance Requests and Customer Service Requests. | Low | | |
| Los Altos | CivicPlus Form Center | [Maintenance Service Request](https://www.losaltosca.gov/FormCenter/Public-Works-6/Maintenance-Service-Request-46). Photo under 6 MB. Name. After-hours street lights are a phone line, (650) 947-2770. | HTML form. | Medium | | |
| Los Altos Hills | Not confirmed | SeeClickFix returned no types. An older road list pointed at Los Altos Hills Connect. That page was not opened. | | Not confirmed | | |
| Los Gatos | GOGov, branded MyLosGatos311 | Web and app. Account, with anonymous submit still offered. Photo and address. The town said it chose GOGov. | No public API found. | Medium | | |
| Milpitas | SeeClickFix, City of Milpitas | API types include Street Lighting, Street Lights, Pothole/Roadway Repairs, and Sidewalk Repair. The city also links a Milpitas app. | API v2. 30 types at `37.4323, -121.8996`. | Low | | |
| Monte Sereno | Not confirmed | SeeClickFix returned no types. An older list pointed at a CivicPlus form. | | Not confirmed | | |
| Morgan Hill | SeeClickFix, City of Morgan Hill | The city announced SeeClickFix for street lights, sidewalks, potholes, graffiti, and dumping. | API v2. 59 types at `37.1305, -121.6544`. | Low | | |
| Mountain View | Comcate, branded Ask Mountain View. Government id `128`. | [Ask Mountain View](https://clients.comcate.com/newrequest.php?id=128) and the city app. New user, existing user, or anonymous. | No public API. The page embeds 43 topics and 283 subtopics. Custom fields come from `POST ajax_customfields.php`, which returned an empty body without a session. | Medium | | |
| Palo Alto | Accela PublicStuff. Client `406`. | PaloAlto311 site and app. | JSON API at `https://vc0.publicstuff.com`. Catalog is in `skills/palo-alto/catalog.json`. | Done | | |
| San José | Oracle Service Cloud, app by AST. Branded San José 311. | [San José 311](https://www.sanjoseca.gov/your-government/departments-offices/customer-service/san-jos-311) and app `com.astcorporation.three11`. Anonymous or account. Photos and a map. | No public citizen API found. | High | | |
| Santa Clara | MySantaClara | The city tells people to use the app for sidewalks, potholes, trees, and graffiti. Vendor was not on the page. | SeeClickFix returned no types. | High | | |
| Saratoga | CivicPlus Fix It Form and Citizen Request Tracker | [Fix It Form](https://www.saratoga.ca.us/FormCenter/Report-a-Concern-6/Fix-It-Form-45). Checkboxes include pothole, street lights, sidewalk, and signals. | HTML form. | Medium | | |
| Sunnyvale | MySunnyvale. Salesforce Public Sector Solutions. | Web portal and the MySunnyvale CA app. Replaced Access Sunnyvale on June 22, 2026. | No public citizen API. The city page returned HTTP 403, so the live form was not read. | High | | |

Mountain View street lights are subtopic `10878`. The page's location widget is on for potholes and sidewalks and off for street lights, so a street-light report may be a typed address. Those custom fields still need a logged-in session.

Sunnyvale's old Dynamics form, with pole number and pole type, is retired. Street lights and potholes can be called in at (408) 730-7415 until the new portal is readable.

## San Mateo County cities

| City | System | How a resident files | Programmatic access | Effort | Volunteer | ETA |
| --- | --- | --- | --- | --- | --- | --- |
| Atherton | SeeClickFix, Town of Atherton | Types include Street Light, Pothole, Sidewalk Damage, and Traffic Signal. | API v2. 29 types at `37.4613, -122.1977`. | Low | | |
| Belmont | Not confirmed | SeeClickFix returned no types. The lead is the Public Works page. | | Not confirmed | | |
| Brisbane | Not confirmed | SeeClickFix returned no types. The lead is the city contact page. | | Not confirmed | | |
| Burlingame | SeeClickFix, City of Burlingame | Types include Pothole, Sidewalk, Street Light, and Street Sweeping. | API v2. 34 types at `37.5841, -122.3661`. | Low | | |
| Colma | Not confirmed | SeeClickFix returned no types. An older list pointed at a CivicPlus embed for potholes and storm drains. | | Not confirmed | | |
| Daly City | SeeClickFix departments, and We Help Daly City | The city site now sends people to We Help Daly City, the rebrand of iHelp, using the website login. The API still returns Public Works, Code Enforcement, and other department types at `37.6879, -122.4702`, including Streetlight. | API v2 is the callable door. 32 types. | Low | | |
| East Palo Alto | Not confirmed | SeeClickFix returned no East Palo Alto organization. The place page lists Menlo Park nearby. | | Not confirmed | | |
| Foster City | SeeClickFix, City of Foster City | Types include Streets (Pothole), Streets (Street Lights), and Sidewalks. | API v2. 31 types at `37.5585, -122.2711`. | Low | | |
| Half Moon Bay | Not confirmed | SeeClickFix returned no types. The lead is the Public Works page. | | Not confirmed | | |
| Hillsborough | SeeClickFix, Town of Hillsborough | Graffiti, Litter / Dumping, Pothole, Traffic or Street Sign Issue, Tree Branch. No streetlight type in that list. | API v2. 9 types at `37.5741, -122.3794`. | Low | | |
| Menlo Park | SeeClickFix, branded ACT Menlo Park. | [ACT Menlo Park](https://www.menlopark.gov/Services/ACT-Menlo-Park). Account required. Guest and anonymous reporting are off. | JSON API at `https://seeclickfix.com/api/v2`. Catalog is in `skills/menlo-park/catalog.json`. Streetlight is `94217`. | Done | | |
| Millbrae | SeeClickFix, branded Millbrae Works | The city page names SeeClickFix. Types include Streetlight, Pothole, and a separate El Camino Real type. | API v2. 29 types at `37.5985, -122.3872`. | Low | | |
| Pacifica | QScend | [Request for Service](https://pacificaca.qscend.com/311/request/add). Address search, current location, or a map pin. | Vendor portal. No public API found. | Medium | | |
| Portola Valley | PV Connect | Web form for town roads, trails, trees, and dumping. The town said the phone app was dropped in October 2025. Code enforcement is email only, code@portolavalley.net. | Web form. | Medium | | |
| Redwood City | Accela PublicStuff, branded myRWC. Client `226`. Space `29066`. | City page and app. | JSON API at `https://vc0.publicstuff.com`. Catalog is in `skills/redwood-city/catalog.json`. | Done | | |
| San Bruno | Accela, branded San Bruno Responds | Web and app `com.accela.san_bruno_ca`. The city FAQ sends freeway issues to Caltrans and Caltrain property to (800) 660-4287. | Same publisher as Palo Alto. Client id not captured. SeeClickFix returned no types. | Medium | | |
| San Carlos | Not confirmed | SeeClickFix returned no types. | | Not confirmed | | |
| San Mateo | Catalis Request311, branded My San Mateo | Web portal and app, launched May 6, 2026. Street lights, graffiti, potholes. Account is optional. Email updates still go out without one. | No public API found. | High | | |
| South San Francisco | SeeClickFix, South San Francisco | Types include Streetlight, Pothole, Signals, and Sidewalk/Curb Gutter. | API v2. 22 types at `37.6547, -122.4077`. | Low | | |
| Woodside | Not confirmed | SeeClickFix returned no types. The lead is the town contact page. | | Not confirmed | | |

Menlo Park streetlight `94217` needs a title. Description and image are optional. Guest and anonymous reporting are off. Lights on electric poles are PG&E, 1-877-660-6789. Potholes on Willow Road, Bayshore Road, and El Camino Real are Caltrans.

## Counties

These take reports only on roads the county maintains, not on city streets.

| Jurisdiction | System | How a resident files | Programmatic access | Effort | Volunteer | ETA |
| --- | --- | --- | --- | --- | --- | --- |
| Santa Clara County | Roads and Airports service requests | [Service requests](https://roads.santaclaracounty.gov/services/service-requests). Mobile Citizen app, or a web form that requires registration. Signals, street lights, potholes, graffiti, and dumping on county roads and expressways. | Login wall. The page does not name the app vendor. | Medium | | |
| San Mateo County | Maintstar | Public Works citizen portal for unincorporated county roads. Register or log in. The county says it is not for emergencies and not for city streets. | Login wall. | Medium | | |

## State and regional

| Jurisdiction | System | How a resident files | Programmatic access | Effort | Volunteer | ETA |
| --- | --- | --- | --- | --- | --- | --- |
| Caltrans | Customer Service Request | [csr.dot.ca.gov](https://csr.dot.ca.gov/) and the CT Service app. The map pin has to turn green on a state highway. Weekdays, 8 a.m. to 4 p.m. Not for emergencies. A photo was not on the form text that was read. | No public API found. | Medium | | |
| Caltrain | Feedback form | [Contact](https://www.caltrain.com/about-caltrain/contact-us). This is not a lat/lng work order. Office line (650) 508-6200. San Bruno sends Caltrain-property graffiti to (800) 660-4287. | No work-order API found. | High | | |

## What to build

Menlo Park is filed in `skills/menlo-park/`. Atherton, Burlingame, Daly City, Foster City, Gilroy, Hillsborough, Millbrae, Milpitas, Morgan Hill, and South San Francisco still need their own SeeClickFix catalogs and a boundary so a photo from another city is refused.

PublicStuff is the second shared client, not the first. Palo Alto is client `406`. Redwood City is client `226`, space `29066`, in `skills/redwood-city/`. San Bruno's app is Accela and may be the same product. That is not established.

Nine cities still need a live form before they can be rated: Los Altos Hills, Monte Sereno, Belmont, Brisbane, Colma, East Palo Alto, Half Moon Bay, San Carlos, and Woodside.

A router that reads the photo's city and picks a skill is useful after the SeeClickFix client can submit. State highways inside a city still belong to Caltrans, which the Menlo Park pothole note already says.
