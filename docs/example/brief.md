# Owner brief: joshuaswarren, Oct 5 - Oct 12, 2026

**1,134 changes across 46 repos: 97 agent-authored (9%), 20 bot, 1,017 with no agent marker.**

The team shipped 25 releases with 1,134 changes across 46 repos, including agent-authored work on MatMul and SDPA kernels in omarchy-mlx. Other changes included fixes to the remnic core and offline modes, and a Metal host API layer in metal2vk.

## Who wrote it

- Agents: 97 changes, 54,256 lines in PRs (35% of PR lines)
- Humans (no agent marker): 1,017 changes, 102,638 lines in PRs
- Merged PRs: 97 of 302 agent-authored (32%). Direct commits: 0 of 832
- Bots: 20 changes (10% of all changes were agents or bots)

## What moved the most

- fix(core): stop harmonic recall from scanning the corpus ([joshuaswarren/remnic#3187](https://github.com/joshuaswarren/remnic/pull/3187))
- fix(offline): finish digest-cache writes before returning ([joshuaswarren/remnic#3181](https://github.com/joshuaswarren/remnic/pull/3181))
- fix(core): resolve inferred MCP namespaces on flat daemons ([joshuaswarren/remnic#3171](https://github.com/joshuaswarren/remnic/pull/3171))
- matmul: direct-kernel route rows for the M2 Max and lower m floors on the M1 ([joshuaswarren/omarchy-mlx#38](https://github.com/joshuaswarren/omarchy-mlx/pull/38)) (agent)
- matmul: remove the G13G f32 a @ b route row (loses 8 to 42 % at k 2560 and n 9728) ([joshuaswarren/omarchy-mlx#39](https://github.com/joshuaswarren/omarchy-mlx/pull/39)) (agent)

## Where the work happened

- joshuaswarren/omarchy-mlx: 524 changes
- joshuaswarren/omarchy-apple-dev: 187 changes
- joshuaswarren/omarchy-cluster: 100 changes
- joshuaswarren/metal2vk: 88 changes
- joshuaswarren/coreglass: 41 changes

## Worth a look

- sweep: mlx-batch, all four families in one tree (top, vlmA, vlmb, others) ([joshuaswarren/metal2vk#74](https://github.com/joshuaswarren/metal2vk/pull/74)): 23,049 lines
- sweep/mlx-core: MLX library kernel corpus (1 067 / 17 301 compile-valid on clang-19) ([joshuaswarren/metal2vk#82](https://github.com/joshuaswarren/metal2vk/pull/82)) (agent): 17,996 lines
- host: Metal host API layer on Vulkan (Rust core, C ABI, compat crates for uzu) ([joshuaswarren/metal2vk#6](https://github.com/joshuaswarren/metal2vk/pull/6)): 12,106 lines
- custom kernel: metal2vk route for the verified kernel set (env opt-in) ([joshuaswarren/omarchy-mlx#70](https://github.com/joshuaswarren/omarchy-mlx/pull/70)): 8,757 lines
- Pin QMD to the 2.8.3 build and cancel abandoned daemon searches ([joshuaswarren/remnic#3174](https://github.com/joshuaswarren/remnic/pull/3174)) (agent): 4,018 lines

## Attribution gap

One account (joshuaswarren) authored 97% of changes, but only 9% carry an agent marker. If agents commit under that account, the agent count is a floor, not the real share. Have agents add a trailer so the next week counts them: see docs/attribution.md. None of the 832 direct commits carries a marker.

## How agent work was counted

Signals behind the agent count: branch x94, identity x9, trailer x3, body x3. An item is agent-authored when its author account, branch name, commit trailer or body marks an AI coding agent.
