---
title: "My agents shipped 1,134 changes in a week. weekship could prove 9% of them."
published: false
tags: devchallenge, hf26challenge, opensource, github
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 2: Side Hustle](https://dev.to/challenges/hacktoberfest-week2-2026-10-12)*

## What I built

I ran a tool over my 46 active public repos for seven days. It counted 1,134 changes and 25 releases. One account sat behind 97% of the work. Only 9% of it carried any sign that an AI agent wrote it.

The tool is weekship. Point it at one repo, a list of repos, or a whole GitHub user or org. It reads the merged PRs, direct commits and releases for the week. Then it writes release notes grouped by impact, an owner brief, and a post you can share. Every output has a hard number in it, the share of the work that agents authored.

Who would pay for this? Anyone who runs coding agents and has to answer "what shipped this week?" A manager with thirty repos and a few agents has a pile of browser tabs. weekship answers in one run.

It is free for one repo. Running it across a whole org, on a schedule, with history, is the paid product. I have not built that hosted plan yet. The CLI and the GitHub Action are MIT licensed and already read a whole org today.

## Demo

This is the top of the brief weekship wrote for my own account, from a real run.

```
1,134 changes across 46 repos: 97 agent-authored (9%), 20 bot, 1,017 with no agent marker.

- Agents: 97 changes, 54,256 lines in PRs (35% of PR lines)
- Humans (no agent marker): 1,017 changes, 102,638 lines in PRs
- Merged PRs: 97 of 302 agent-authored (32%). Direct commits: 0 of 832
- Bots: 20 changes (10% of all changes were agents or bots)
```

The first finding was a hole in my own setup. My agents commit under my git identity, so every direct commit looks like I typed it. None of the 832 carried a marker. All 97 agent changes were PRs, where branch names gave them away.

So 9% is a floor. The brief says that in a section called "Attribution gap" and points to a fix. The fix is a small commit hook that stamps agent commits, so next week's count sees them.

The full notes, brief and post from this run are in the repo under `docs/example`. The same run works as a scheduled GitHub Action, and the repo's own CI runs the Action on itself.

## Code

{% github joshuaswarren/weekship %}

## How I built it

weekship is Python 3.11 with the standard library only. There is nothing to install or audit beyond the tool itself.

It sorts each merged PR and direct commit into agent, bot or human. It looks at the author account, the branch prefix, the commit author identity, commit trailers and the PR body. Of my 97 agent changes, 85 matched on branch name alone. Nine matched on branch plus commit identity. Three matched on a trailer and the body. "Human" only means no marker was found.

Counting commits and PRs together is easy to get wrong. A squash merge, a rebase merge and a merge commit all leave different traces. An independent review of my first version caught that it counted a squash merge with a title-only subject twice, once as the PR and once as a commit. The collector now skips any commit whose hash belongs to a merged PR.

For the writing, weekship talks to any OpenAI-compatible endpoint. I pointed it at a 27B Qwen model on my own hardware, behind a LiteLLM proxy. The setup is three lines of config.

```toml
[llm]
base_url = "http://llm-proxy.internal:4000/v1"
model = "advisor"
api_key_env = "TEAM_LLM_KEY"
```

The first real run taught me more than the tests did. It wrote the report dates, and the number check rejected them. It repeated figures from PR titles. It numbered a bulleted list, which added numbers nobody computed. It wrapped every line at 40 columns. Once it looped on one bullet until it hit the token limit, and every number in that post was valid.

So the model never writes a number. The tool computes every figure. The lead line and the bullets of the post come from those figures. The model writes two sentences in between. weekship drops the model's text and writes plain text instead when the model adds a number the tool did not compute, runs long, or repeats a line. PR titles reach the model with their digits masked, so it cannot echo a figure it should not.

The tool also hides private work. A private repo's name and PR titles never reach the shareable post or the prompt. A flag removes them from the notes, the brief and the JSON export too.

There are 60 tests. Several pin the failures above, including the number check, the loop check, line joining and digit masking.

## Why does open innovation matter?

A weekly report on private repos is a list of private work. With a model running on my own hardware, I do not have to ask whether that list is safe to send to someone else's server. weekship also strips private titles before it builds the prompt, so the model sees less than the owner does.

The cost is power and nothing else. There is no per-token bill, so a team can run it every week on every repo without watching a meter.

I can swap the model with one environment variable. The checks do not care who wrote the text, so a new model gets the same guardrails on day one.

I did not run a closed model for comparison, so I cannot say whether it would loop less. What I can say is that I found every one of those failures because I could rerun the open model as often as I liked. Each fix went in with a test.

What would you want weekship to count that it cannot see yet?

## Prize categories

Best Use of GitHub Copilot, for automating the project with GitHub Actions.
