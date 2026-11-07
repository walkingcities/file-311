# Development

How to try out a skill you've written before it's merged to `master`.

## Option 1: Install from your branch (recommended)

This tests what users will get. The branch must be pushed to GitHub first.

```bash
git push -u origin <your-branch>

npx skills@latest add walkingcities/file-311#<your-branch> \
  --skill <your-skill> --skill file-311-common \
  -g -a cursor -a claude-code -a codex -y
```

Example, for the `menlo-park` branch:

```bash
npx skills@latest add walkingcities/file-311#menlo-park \
  --skill menlo-park --skill file-311-common \
  -g -a cursor -a claude-code -a codex -y
```

- Include `file-311-common`, because city skills depend on it.
- Leave out `--skill` to install every skill on the branch.
- If the shorthand doesn't parse, use the full URL:
  `https://github.com/walkingcities/file-311/tree/<your-branch>`

## Option 2: Install from your local checkout

Use this to iterate without pushing. Run it from the repo root:

```bash
npx skills@latest add . --skill <your-skill> --skill file-311-common -g -a cursor -a claude-code -a codex -y
```

## Picking up changes

After you edit a skill, re-run the `add` command to refresh the installed copy.
`npx skills update` may track the default branch rather than your branch, so
don't rely on it for branch testing.

## Verify

1. Restart or reload your agent so it rediscovers skills.
2. Drop a test photo and confirm the skill triggers.
3. Stop at the confirmation step. Nothing is submitted until you confirm, so
   don't confirm against a real city system.
4. Run the tests:

```bash
python -m unittest discover -s tests
```

## Clean up

Once your branch is merged, reinstall from `master` to go back to the released version:

```bash
npx skills@latest add walkingcities/file-311 -g -a cursor -a claude-code -a codex -y
```
