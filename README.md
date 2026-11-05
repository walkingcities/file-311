# file-311

File a city 311 report from a photo.

This repo files two cities today: Palo Alto and Redwood City. Install it once, drop a photo into Cursor or Claude Code, and say what is wrong. The agent prepares the report. Nothing is sent until you agree.

This is an unofficial client of PaloAlto311 and of Redwood City's myRWC. A photo is filed only in the city it was taken.

Other places are listed in [docs/jurisdictions.md](docs/jurisdictions.md), with the system each one uses and how hard it is to add. We are looking for volunteers to help add skills for different cities/jursidictions. Claim a row by putting your GitHub name and an ETA in that file, then open a pull request for the skill. 

Fig 1 shows an example of a Palo Alto 311 submission using the palo-alto skill for a street light out at 125 University Ave, November 4, 2026. Cursor asked me to confirm and then submitted the PaloAlto311 request [18868128](https://iframe.publicstuff.com/#?client_id=406&request_id=18868128) (Fig 2). The run is written up in [docs/palo-alto/runs.md](docs/palo-alto/runs.md#street-light-out-november-4-2026).

![Chat: the preview, the confirmation, and request 18868128](docs/palo-alto/street-light-out-2026-11-04-chat.jpg)
Fig 1. Cursor chat history where I attached the camera photo, read the preview, then confirmed.

![PaloAlto311 request 18868128, submitted at 125 University Ave](docs/palo-alto/street-light-out-2026-11-04-request.jpg)
Fig 2. Palo Alto 311 submission.

## Install

Install the `file-311` plugin from the marketplace. That is the preferred install in Cursor and Claude Code. The plugin installs Palo Alto, Redwood City, and `file-311-common` together. The city script imports that library from the folder beside it.

Neither listing is available to install yet. Until one is approved, [install the skills directly](#install-the-skills-directly).

### Cursor

Submitted to the Cursor Marketplace on November 5, 2026. It is awaiting approval. Once it is listed:

1. Open Customize in the sidebar.
2. Search the Marketplace for `file-311`.
3. Choose Install, and install it for your user. A street-light report is not tied to one project.

### Claude Code

Not submitted yet. Someone with a Claude Pro plan needs to submit the repo at [claude.ai/directory/manage](https://claude.ai/directory/manage). Once it is listed:

1. Start Claude Code and run `/plugin`.
2. On the Discover tab, search for `file-311`.
3. Choose Install for you.

### Codex

Not submitted yet. OpenAI says: "We are not accepting more skills-only submissions at this time." See the [plugin guidelines](https://developers.openai.com/plugins/plugin-guidelines). The upload package is `dist/file-311-1.0.1.zip`, built with `python3 scripts/package_openai_zip.py`.

### Install the skills directly

Use this until a marketplace listing is approved. Global install is the default. Someone filing a street light is not inside a project repo.

You need Node 22.20 or newer. `npx` downloads and runs an npm package. `skills` is the [Vercel skills CLI](https://github.com/vercel-labs/skills), a separate tool from this repo. `@latest` means the newest published version of that CLI. The CLI then downloads `walkingcities/file-311` from GitHub and installs every skill in the repo: the shared library and each city. This does not install an npm package named file-311.

```bash
npx skills@latest add walkingcities/file-311 -g -a cursor -a claude-code -a codex -y
```

One copy of each skill is installed, and the other agents symlink to it. Updates are `npx skills update`.

To install only Palo Alto, name both the city skill and the library it imports:

```bash
npx skills@latest add walkingcities/file-311 --skill palo-alto --skill file-311-common -g -a cursor -a claude-code -a codex -y
```

Copy the folders yourself when Node is an extra requirement for a Python script. Copy `skills/file-311-common/`, `skills/palo-alto/`, and `skills/redwood-city/` into the same skills directory:

- Cursor: `~/.cursor/skills/`
- Claude Code: `~/.claude/skills/`
- Codex: `~/.agents/skills/`

## Use it

Drop the original photo into the chat. It must be the camera file, with location saved. On iPhone, Camera needs Precise Location. A screenshot or a re-saved image has no GPS, and the skill stops and asks for the original.

Say what is wrong, such as a street light that is out. The agent prepares a preview: request type, address, cross street, description, and the custom fields. It says which fields are public. For a Palo Alto street light, the photo and the location are public, and name and phone are staff-only. A Redwood City street light is private in the myRWC catalog. The photo and the location are still sent to the city.

Nothing is sent until you agree. The agent then prints the request id and the request URL.

The city form means picking a category, typing the address, and filling the fields. Here that is a dropped photo and a confirmation. Palo Alto asks for up to 5 business days on a street light. The street-light desk is (650) 496-6916 on workdays. A power outage is a different report, (650) 496-6914. myRWC's street-light confirmation says Public Works' contractor will send an update within 3 business days. Redwood City publishes (650) 780-7464 for street problems.

A photo outside the chosen city is refused. Another city will be a new folder under `skills/`.

[docs/palo-alto/catalog.md](docs/palo-alto/catalog.md) lists every Palo Alto request type. A checkmark in its Run column links to the matching photo run in [docs/palo-alto/runs.md](docs/palo-alto/runs.md). Redwood City has the same pair in [docs/redwood-city/catalog.md](docs/redwood-city/catalog.md) and [docs/redwood-city/runs.md](docs/redwood-city/runs.md). No Redwood City camera run is recorded yet.

A JPEG works on any computer. The Python script reads its location. A HEIC photo needs a Mac: Swift reads the location, and `sips` converts it for upload. The Swift file is `skills/file-311-common/photo-gps.swift`. The compiled binary is not part of this repo. On Linux or Windows, export the photo as a JPEG.

## One-time setup

The first report asks for the email, password, name, and phone on that city's 311 site. Palo Alto uses [Report an Issue](https://www.paloalto.gov/Residents/Services/Report-an-Issue). Redwood City uses [myRWC](https://www.redwoodcity.org/i-want-to/report/myrwc-report-problem-request-service). The password is passed only as an environment variable and is not saved. Email, name, phone, and the API key are stored with mode `600` in `~/.config/paloalto311/account.json` or `~/.config/myrwc/account.json`. The two accounts are separate. Deleting the file signs you out of that city. Later reports reuse it.

## Run the script

From a clone of this repo:

```bash
python3 skills/palo-alto/scripts/paloalto311.py list street
python3 skills/palo-alto/scripts/paloalto311.py show "Street Light Out"
python3 skills/palo-alto/scripts/paloalto311.py prepare --photo "/path/to/photo.jpg"
PALOALTO311_EMAIL="..." PALOALTO311_PASSWORD="..." PALOALTO311_NAME="..." PALOALTO311_PHONE="..." \
  python3 skills/palo-alto/scripts/paloalto311.py login
python3 skills/palo-alto/scripts/paloalto311.py submit --confirm
python3 skills/redwood-city/scripts/myrwc.py show "Street Light Outage"
python3 skills/redwood-city/scripts/myrwc.py prepare --photo "/path/to/photo.jpg"
```

`prepare` writes a preview and does not send it. `submit` sends only when `--confirm` is present.
