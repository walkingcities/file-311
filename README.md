# file-311

File a city 311 report from a photo.

This repo has one city today: Palo Alto. Install the skill once, drop a photo into Cursor, Claude Code, or Codex, and say what is wrong. The agent prepares the report. Nothing is sent until you agree.

This is an unofficial client of the city's PaloAlto311 site. It only files reports inside Palo Alto.

## Install

Global install is the default. Someone filing a street light is not inside a project repo.

You need Node 22.20 or newer. `npx` downloads and runs an npm package. `skills` is the [Vercel skills CLI](https://github.com/vercel-labs/skills), a separate tool from this repo. `@latest` means the newest published version of that CLI. The CLI then downloads `walkingcities/file-311` from GitHub and copies `skills/palo-alto/` into each agent's skills folder. This does not install an npm package named file-311.

```bash
npx skills@latest add walkingcities/file-311 --skill palo-alto -g -a cursor -a claude-code -a codex -y
```

One copy is installed, and the other agents symlink to it. Updates are `npx skills update`.

### Copy the folder yourself

Node is an extra requirement for a Python script. Copy `skills/palo-alto/` to one of these paths instead:

- Cursor: `~/.cursor/skills/palo-alto/`
- Claude Code: `~/.claude/skills/palo-alto/`
- Codex: `~/.agents/skills/palo-alto/`

## Use it

Drop the original photo into the chat. It must be the camera file, with location saved. On iPhone, Camera needs Precise Location. A screenshot or a re-saved image has no GPS, and the skill stops and asks for the original.

Say what is wrong, such as a street light that is out. The agent prepares a preview: request type, address, cross street, description, and the custom fields. It says which fields are public. For a street light, the photo and the location are public. Name and phone are staff-only.

Nothing is sent until you agree. The agent then prints the request id and the PaloAlto311 URL.

The city form means picking a category, typing the address, and filling the fields. Here that is a dropped photo and a confirmation. The city still asks for up to 5 business days on a street light. The street-light desk is (650) 496-6916 on workdays. A power outage is a different report, (650) 496-6914.

A photo outside Palo Alto is refused. Another city will be a new folder under `skills/`.

A JPEG location is read by the Python script. A HEIC photo needs Swift on the machine, which the Xcode command-line tools provide. The script runs `scripts/photo-gps.swift` for that file. The compiled binary is not part of this repo.

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
