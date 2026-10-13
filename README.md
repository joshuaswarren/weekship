# weekship

Write what shipped. weekship reads a week of merged pull requests, direct commits and releases from one repository, a list of repositories, or every active repository of a GitHub user or organization. It writes three things:

- **Release notes**, grouped by impact: highlights first, then features, fixes, performance and the rest.
- **An owner brief** for the person who needs to know what happened, with a hard count of agent-authored vs human-authored work.
- **A shareable post** that leads with that number. It never names a private repo or a private change.

Your agents ship more than you know. weekship counts it.

```
$ weekship --owner acme --since 7d
===== brief.md =====
# Owner brief: acme, Oct 5 - Oct 12, 2026

**412 changes across 18 repos: 137 agent-authored (33%), 9 bot, 266 with no agent marker.**
...
```

It runs as a command line tool and as a GitHub Action. Python 3.11 or newer, standard library only.

## Install

```sh
pip install git+https://github.com/joshuaswarren/weekship
```

weekship reads GitHub with `GITHUB_TOKEN`, `GH_TOKEN`, or the token from `gh auth token`.

## Use

```sh
weekship --repo acme/api                    # one repo, last 7 days
weekship --repo acme/api --repo acme/web    # several repos
weekship --owner acme                       # every active repo of a user or org
weekship --owner acme --since 2w --tz America/Chicago --out ./week
weekship --owner acme --public-only --exclude 'acme/archive-*'
```

`--out DIR` writes `notes.md`, `brief.md`, `post.md` and `week.json`. `--format notes|brief|post|json|all` chooses what prints. `--redact-private` hides private repo names and private change titles in the notes, the brief and `week.json`. The post and the text sent to the language model never include them.

## How agent work is counted

Each merged PR and each direct commit lands in one bucket:

| Bucket | Evidence |
|---|---|
| agent | an agent account, an agent branch prefix, an agent commit identity, a `Co-authored-by`, `Generated-by` or `Assisted-by` trailer, or a "Generated with ..." line |
| bot | dependency and CI automation |
| human | no agent marker |

"Human" means no agent marker was found. If your agents commit under your own identity, every commit looks human, and the brief says so in an **Attribution gap** section. [docs/attribution.md](docs/attribution.md) covers the fix: a commit hook that stamps agent commits, and `.weekship.toml` rules for your own conventions.

Squash, rebase and merge-commit workflows are all handled: a commit that arrived through a merged PR counts once, as the PR.

## Language model

weekship works with no model: it writes plain text from the numbers. With a model it writes the summary paragraph and the post. Any OpenAI-compatible endpoint works: OpenAI, a LiteLLM proxy, vLLM, Ollama, llama.cpp.

```sh
export WEEKSHIP_LLM_BASE_URL=https://llm.example.com/v1
export WEEKSHIP_LLM_API_KEY=...
export WEEKSHIP_MODEL=my-model     # omitted: the first model the endpoint lists
```

Settings resolve in this order: flag, environment, `.weekship.toml` or `~/.config/weekship/config.toml`, then the default `http://localhost:4000/v1` (a LiteLLM proxy on its default port). Keep a team default in the config file:

```toml
[llm]
base_url = "http://llm-proxy.internal:4000/v1"
model = "advisor"
api_key_env = "TEAM_LLM_KEY"     # the name of the variable, never the key
```

The model sees only counts and titles of public changes. Its output is thrown away, and plain text is written instead, when it contains a number the tool did not compute or leaves out the real agent percentage. `--no-llm` skips the model.

## GitHub Action

```yaml
name: Weekly ship report
on:
  schedule: [{ cron: "0 14 * * 1" }]
  workflow_dispatch:
permissions:
  contents: read
  pull-requests: read
jobs:
  weekship:
    runs-on: ubuntu-latest
    steps:
      - id: ship
        uses: joshuaswarren/weekship@main
        with:
          since: 7d
          # owner: acme              # whole org; needs a token that can read it
          # github-token: ${{ secrets.ORG_READ_TOKEN }}
          # llm-base-url: https://llm.example.com/v1
          # llm-api-key: ${{ secrets.LLM_API_KEY }}
      - uses: actions/upload-artifact@v4
        with:
          name: weekship
          path: weekship-out
      - run: echo "${{ steps.ship.outputs.agent-pct }}% of ${{ steps.ship.outputs.changes }} changes were agent-authored"
```

The brief also appears in the job summary. Outputs: `changes`, `agent-count`, `agent-pct`, `out-dir`.

## Free for one repo, paid for the whole org

weekship is MIT licensed and nothing in the code is gated. Running it on one repository is free. The hosted team plan for a whole organization, with scheduled runs, history and delivery to the owner, is the paid product. It is not built yet. See [docs/pricing.md](docs/pricing.md).

## Develop

```sh
python -m pip install -e ".[dev]"
python -m pytest
```

## License

MIT
