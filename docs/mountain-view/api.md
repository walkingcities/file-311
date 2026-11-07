# Mountain View

Checked November 7, 2026. Mountain View has no public API for creating a 311 report.

The resident channel is still Ask Mountain View, Comcate government id `128`: [the request form](https://clients.comcate.com/newrequest.php?id=128). The city describes it on the [Ask Mountain View](https://www.mountainview.gov/our-city/departments/information-technology/ask-mountain-view) page. The form offers New User, Existing User, and Remain Anonymous. The composed letter is a public record. Emergencies are 911, not this form.

The mobile apps are the same product. iOS is Ask Mountain View Mobile, id `370409740`, version 6.0.2, updated June 11, 2018, copyright Comcate. Android is `comcate128.android`. Neither store listing publishes an API.

Street Lights is filed by `skills/mountain-view/`. That skill posts this HTML form. It is not a JSON client like Palo Alto, Redwood City, or Menlo Park. Other subtopics are not built.

## Checks for a create API

SeeClickFix does not cover the city. `GET /api/v2/issues/new` returned `{"request_types":[]}` at `37.3861, -122.0839` and at `37.3894, -122.0819`. The [place page](https://seeclickfix.com/mountain_view) says no organization there participates. `GET /open311/v2/mountainview.gov/services.json` on seeclickfix.com returned 404. Mountain View is not on the [Open311 GeoReport v2 server list](http://wiki.open311.org/GeoReport_v2/Servers/). `api.mountainview.gov` does not resolve. Scripted requests to `mountainview.gov` Open311 paths got the same HTTP 403 as the rest of that site, not a services document.

The [open data catalog](https://data-mountainview.opendata.arcgis.com/) is GIS. A search for 311, service request, streetlight, pothole, and Comcate matched nothing. The dataset collection is Zoning Districts and General Plan Land Use. The map collection is layers such as roads, parcels, trees, and the city boundary. That search API reads the catalog. It does not create a request. The weekly police call-for-service logs are a downloadable spreadsheet, not a work-order API.

Comcate's public [API Reference Information](https://comcate.elevio.help/en/articles/250-api-reference-information) is not a citizen 311 API. It documents a Code Enforcement `createCase` method so an external CRM can open a code case, and a webhook that sends case updates back. The article says to contact Comcate support for which APIs they support. The production base it names is `https://ext-api.comcate.com/api/v1/`. A GET of that host returns a JSON 404, not a spec. `https://api.comcate.com/` is a placeholder page, last modified May 9, 2017, and `/docs`, `/swagger`, and `/v1` are 404. The API Integrations articles are Data Ticket, Okta single sign-on, Cartegraph, and T2 parking. On Comcate's code-enforcement and animal-control price sheets, a web service API is an agency add-on. It is not a public key for Ask Mountain View.

`https://cmv-mvps.mountainview.gov/Help` is a separate ASP.NET help page for land, parcels, and projects. It does not describe Ask Mountain View or a service request.

## The form

The submit control is a multipart POST to `/newrequest.php`. The page script defines 43 topic names and 283 subtopic names. The visible accordion lists 39 topics. Four names are in the script and not in that menu: Bulk Case Import, IT Department, Mobile App, and Other. One subtopic blocks submit: Birth and Death Certificates / Marriage Licenses, `11309`.

Custom fields are `POST ajax_customfields.php` with `govtId=128` and `subtopic`. After the form page has set the agency cookie, Street Lights, Potholes, Sidewalk, Graffiti, and Traffic Signals each returned an empty table. No account was required. A call with no agency cookie is redirected and has an empty body, which is what the November 4 note recorded.

`jsTopicLocation` is `1` on 31 subtopics. Those show the map widget. The others ask for a typed address. The form also has a file field.

Street reports a skill would care about:

| Topic | Subtopic | Id | Map widget |
| --- | --- | --- | --- |
| Streets | Street Lights | `10878` | Off |
| Streets | Potholes & Pavement Issues | `11266` | On |
| Streets | Sidewalk | `18005` | On |
| Streets | Street condition/Sidewalk condition | `18054` | On |
| Streets | Street Signs | `10854` | Off |
| Streets | Traffic Signals | `10855` | Off |
| Streets | Power Outages | `10870` | Off |
| Streets | Street Sweeping | `10879` | Off |
| Graffiti | Graffiti | `10868` | On |
| Illegal Dumping | Streets/Sidewalks | `16487` | On |

The subtopic message call returned an empty body for each of those, so the form does not replace them with a phone-only notice.

## Phones the city publishes

Street light outages go to Public Services at (650) 903-6329. That is Ask Mountain View FAQ 6336. The [street maintenance page](https://www.mountainview.gov/our-city/departments/public-works/roads-and-transportation/street-maintenance) uses the same number for urgent street problems and sends non-urgent reports to Ask Mountain View.

Traffic signal outages go to Public Works at (650) 903-6311. Central Expressway is Santa Clara County, (408) 494-2700. El Camino Real and freeway ramps are Caltrans, (415) 330-6500, after hours (510) 286-6918.

Graffiti goes to (650) 903-6767. Freeway on-ramps and off-ramps go to Caltrans at (408) 436-0930. Shopping carts on public property use (650) 903-6767.
