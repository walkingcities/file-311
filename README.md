# file-311

File a city 311 report from a photo.

This repo has one city today: Palo Alto. Install it once, drop a photo into Cursor or Claude Code, and say what is wrong. The agent prepares the report. Nothing is sent until you agree.

This is an unofficial client of the city's PaloAlto311 site. It only files reports inside Palo Alto.

Other places are listed in [docs/jurisdictions.md](docs/jurisdictions.md), with the system each one uses and how hard it is to add. Eleven cities already have a public SeeClickFix API. Claim a row by putting your GitHub name and an ETA in that file, then open a pull request for the skill. Review the other pull requests. A photo is never sent until the person filing it agrees.

## Install

Install the `file-311` plugin from the marketplace. That is the preferred install in Cursor and Claude Code. The plugin installs Palo Alto and `file-311-common` together. The city script imports that library from the folder beside it.

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

Not submitted yet. Build the upload package with `python3 scripts/package_openai_zip.py`, then upload `dist/file-311-1.0.1.zip` from the OpenAI plugin dashboard.

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

Copy the folders yourself when Node is an extra requirement for a Python script. Copy `skills/file-311-common/` and `skills/palo-alto/` into the same skills directory:

- Cursor: `~/.cursor/skills/`
- Claude Code: `~/.claude/skills/`
- Codex: `~/.agents/skills/`

## Use it

Drop the original photo into the chat. It must be the camera file, with location saved. On iPhone, Camera needs Precise Location. A screenshot or a re-saved image has no GPS, and the skill stops and asks for the original.

Say what is wrong, such as a street light that is out. The agent prepares a preview: request type, address, cross street, description, and the custom fields. It says which fields are public. For a street light, the photo and the location are public. Name and phone are staff-only.

Nothing is sent until you agree. The agent then prints the request id and the PaloAlto311 URL.

The city form means picking a category, typing the address, and filling the fields. Here that is a dropped photo and a confirmation. The city still asks for up to 5 business days on a street light. The street-light desk is (650) 496-6916 on workdays. A power outage is a different report, (650) 496-6914.

A photo outside Palo Alto is refused. Another city will be a new folder under `skills/`.

[docs/palo-alto/catalog.md](docs/palo-alto/catalog.md) lists every Palo Alto request type. A checkmark in its Run column links to the matching photo run in [docs/palo-alto/runs.md](docs/palo-alto/runs.md). Those two files are Palo Alto only. Another city gets the same pair under `docs/<city>/`.

A JPEG works on any computer. The Python script reads its location. A HEIC photo needs a Mac: Swift reads the location, and `sips` converts it for upload. The Swift file is `skills/file-311-common/photo-gps.swift`. The compiled binary is not part of this repo. On Linux or Windows, export the photo as a JPEG.

## One-time setup

The first report asks for the PaloAlto311 email, password, name, and phone. You need an account on the city's 311 site, [Report an Issue](https://www.paloalto.gov/Residents/Services/Report-an-Issue). The password is passed only as an environment variable and is not saved. Email, name, phone, and the API key are stored in `~/.config/paloalto311/account.json` with mode `600`. Deleting that file signs you out. Later reports reuse it.

## Run the script

From a clone of this repo:

```bash
python3 skills/palo-alto/scripts/paloalto311.py list street
python3 skills/palo-alto/scripts/paloalto311.py show "Street Light Out"
python3 skills/palo-alto/scripts/paloalto311.py prepare --photo "/path/to/photo.jpg"
PALOALTO311_EMAIL="..." PALOALTO311_PASSWORD="..." PALOALTO311_NAME="..." PALOALTO311_PHONE="..." \
  python3 skills/palo-alto/scripts/paloalto311.py login
python3 skills/palo-alto/scripts/paloalto311.py submit --confirm
```

`prepare` writes a preview and does not send it. `submit` sends only when `--confirm` is present.
