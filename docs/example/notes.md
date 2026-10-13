# What shipped: Oct 5 - Oct 12, 2026

1,134 changes across 46 repos: 97 agent-authored (9%), 20 bot, 1,017 with no agent marker.

The team shipped 25 releases with 1,134 changes across 46 repos, including agent-authored work on MatMul and SDPA kernels in omarchy-mlx. Other changes included fixes to the remnic core and offline modes, and a Metal host API layer in metal2vk.

## Releases

- joshuaswarren/remnic: 14 releases, v9.69.95 to v10.0.2
- omarchy-cluster 0.1.0 ([joshuaswarren/omarchy-cluster v0.1.0](https://github.com/joshuaswarren/omarchy-cluster/releases/tag/v0.1.0))
- v0.7.31 — batched bf16 coopmat QMM fix, kv-maskless series gate, batched GDN decode, routing default ON ([joshuaswarren/omarchy-mlx v0.7.31](https://github.com/joshuaswarren/omarchy-mlx/releases/tag/v0.7.31))
- Wheel for the H3 video guide (dev build 95e7b6f) ([joshuaswarren/omarchy-mlx tensorfold-video-wheel-95e7b6f](https://github.com/joshuaswarren/omarchy-mlx/releases/tag/tensorfold-video-wheel-95e7b6f))
- v0.7.32: int8 matmul exactness and speed, large-shape correctness fixes, GDN and SDPA serve routes, translator fixes ([joshuaswarren/omarchy-mlx v0.7.32](https://github.com/joshuaswarren/omarchy-mlx/releases/tag/v0.7.32))
- v0.1.0 ([joshuaswarren/omarchy-apple-dev v0.1.0](https://github.com/joshuaswarren/omarchy-apple-dev/releases/tag/v0.1.0))
- v0.2.0 ([joshuaswarren/omarchy-apple-dev v0.2.0](https://github.com/joshuaswarren/omarchy-apple-dev/releases/tag/v0.2.0))
- v0.3.0 ([joshuaswarren/omarchy-apple-dev v0.3.0](https://github.com/joshuaswarren/omarchy-apple-dev/releases/tag/v0.3.0))
- metal2vk v0.2.0 ([joshuaswarren/metal2vk v0.2.0](https://github.com/joshuaswarren/metal2vk/releases/tag/v0.2.0))
- metal2vk v0.2.1 ([joshuaswarren/metal2vk v0.2.1](https://github.com/joshuaswarren/metal2vk/releases/tag/v0.2.1))
- metal2vk v0.3.0 ([joshuaswarren/metal2vk v0.3.0](https://github.com/joshuaswarren/metal2vk/releases/tag/v0.3.0))
- v0.1.0 ([joshuaswarren/ane-linux-experiments v0.1.0](https://github.com/joshuaswarren/ane-linux-experiments/releases/tag/v0.1.0))

## Fixes

- fix(core): stop harmonic recall from scanning the corpus ([joshuaswarren/remnic#3187](https://github.com/joshuaswarren/remnic/pull/3187))
- fix(offline): finish digest-cache writes before returning ([joshuaswarren/remnic#3181](https://github.com/joshuaswarren/remnic/pull/3181))
- fix(core): resolve inferred MCP namespaces on flat daemons ([joshuaswarren/remnic#3171](https://github.com/joshuaswarren/remnic/pull/3171))
- fix: preserve requested associated domains when signing ([joshuaswarren/omarchy-apple-dev#47](https://github.com/joshuaswarren/omarchy-apple-dev/pull/47))
- patch(1) handling: explicit 'not installed' error instead of a misleading version-mismatch (the M2 gate failure); installer prerequisite check + PKGBUILD makedepends note; regression tests ([joshuaswarren/omarchy-mlx@3f477c4](https://github.com/joshuaswarren/omarchy-mlx/commit/3f477c49de40a0569bebc0fe40708354ec9ad986))
- g-hold stub harness: run the MLX_PIN heredoc for real against a namespace-package fixture (mlx has no __init__.py, __file__ None) - the harness now catches the pathlib.Path(mlx.__file__) bug class; gates README: g7c parakeet-reference cache stage + tmpfs vendor-dir note ([joshuaswarren/omarchy-mlx@4b48602](https://github.com/joshuaswarren/omarchy-mlx/commit/4b4860211dc489b5848f13256cf98d8714af96e6))
- release notes: known issue - batched prefill of GDN/linear-attention models diverges rows 1-3 at B>1 (present in v0.7.28 and v0.7.29, not a regression; cause under investigation; oMLX completion_batch_size flag with workaround being confirmed) ([joshuaswarren/omarchy-mlx@11e0ad0](https://github.com/joshuaswarren/omarchy-mlx/commit/11e0ad0d7914956e20ddedf59c8cb1515f5ba476))
- release notes: final known-issue wording for the batched-prefill bug (Main's exact line; no cause claim; oMLX completion_batch_size note) ([joshuaswarren/omarchy-mlx@af34a80](https://github.com/joshuaswarren/omarchy-mlx/commit/af34a80431dd0e1aabdc7ae9b7916ed6c04205a7))
- g14 dead-leg regression harness: dead server -> liveness fail-fast (rc=1, 9s, no leg B) on the hardened staged gate ([joshuaswarren/omarchy-mlx@11b13a3](https://github.com/joshuaswarren/omarchy-mlx/commit/11b13a342f6d18d21f003f186d7160c10a59d53d))
- release gates: g7a fixture uses the packaged honeykrisp ICD (the stock-[redacted] default cannot pass on Omarchy M+ images); g10 primer budget 60s->90s (measured 22.6s pass / 61.6s fail on the same idle host - gate-defect limit tightness, not a perf regression). Gates-only commit for the v0.7.30 cut. ([joshuaswarren/omarchy-mlx@5aaad7e](https://github.com/joshuaswarren/omarchy-mlx/commit/5aaad7e89654d108c8fab2f7cca1ef62b63b2869))
- g10 primer budget 60s->90s: measured 22.6 s (window-1 pass) / 61.6 s (window-2 fail) on the same idle host - limit tightness, not a perf regression ([joshuaswarren/omarchy-mlx@cf71ea2](https://github.com/joshuaswarren/omarchy-mlx/commit/cf71ea276eb87fd2a1289be4c60cfce0dd85536b))
- g17-patch-series: pristine mlx-lm 0.31.3 and 0.32.0 venvs, apply-mlx-lm-patches rc=0 + idempotent rerun, CPU-only, both lines (the M2 g1 blocker regression gate) ([joshuaswarren/omarchy-mlx@3db5cc1](https://github.com/joshuaswarren/omarchy-mlx/commit/3db5cc1ba5b7a6be82680f5d73345c4215b6694d))

## Performance

- sdpa causal flash: launch the heaviest causal q tiles first (bit identical, 1 to 5 percent faster) ([joshuaswarren/omarchy-mlx#49](https://github.com/joshuaswarren/omarchy-mlx/pull/49)) (agent)
- Correction to the governor docs: no gain from the performance governor with ANE work running ([joshuaswarren/omarchy-mlx#137](https://github.com/joshuaswarren/omarchy-mlx/pull/137))
- omarchy: hold a PM-QoS CPU latency request while GPU work is in flight on G13 (non-C) parts (CPU PD lever: TTFT -3..-9 %, decode +0.6-0.8 %) ([joshuaswarren/omarchy-mlx@7847040](https://github.com/joshuaswarren/omarchy-mlx/commit/78470402f088250bd077aad86570c2b3f8a13ccd))
- README: iPhone RPC node section (capacity node, not a speedup) ([joshuaswarren/omarchy-cluster@ee50f86](https://github.com/joshuaswarren/omarchy-cluster/commit/ee50f861b1b80ada05a14c010ed0533170a91cef))
- llamacpp engine: default llama-server threads to the performance cores (one efficiency core in the team cost 36% of decode on an M1 Max) ([joshuaswarren/omarchy-cluster@67dd2f2](https://github.com/joshuaswarren/omarchy-cluster/commit/67dd2f2e908f4f75fe1ca8a97e31990e2ee3ff45))
- receipt: llama-server on performance cores only (decode +10%, prefill +34% on an M1 Max) ([joshuaswarren/omarchy-cluster@8185199](https://github.com/joshuaswarren/omarchy-cluster/commit/8185199684c04f7ab42c07ef671277e340b6b4fb))
- agent: rpc-server CPU threads default to the performance cores (its own default is half of all CPUs, efficiency cores included) ([joshuaswarren/omarchy-cluster@e41eff4](https://github.com/joshuaswarren/omarchy-cluster/commit/e41eff4fdeae9232677d9c7f8e53cbc0d1123fee))
- receipt: rpc-server at 8 threads prefills 51% faster than its 5-thread default (decode unchanged) ([joshuaswarren/omarchy-cluster@3951c7b](https://github.com/joshuaswarren/omarchy-cluster/commit/3951c7b8d5765a18f8dcc195678b92479aeab368))
- receipt: M2 Max rpc-server at 8 threads prefills 35% faster than its 6-thread default; 12 threads trade 6% decode for 8% prefill ([joshuaswarren/omarchy-cluster@4608f0f](https://github.com/joshuaswarren/omarchy-cluster/commit/4608f0f539bc9c3555e7bf11a29a627588bafe5a))

## Refactoring

- custom-kernel: drop threadgroup-pointer params from helper call sites; rename GLSL-reserved identifiers; header rsqrt map ([joshuaswarren/omarchy-mlx@ec5886b](https://github.com/joshuaswarren/omarchy-mlx/commit/ec5886ba4012dea3c518b8e84d74b16b665b14b6))

## Docs

- docs: shrink AGENTS.md under the advisor 49152 context cap ([joshuaswarren/remnic#3168](https://github.com/joshuaswarren/remnic/pull/3168)) (agent)
- docs: reduced repro for the clspv OpPhi predecessor mismatch (GatedActMul_v1) ([joshuaswarren/metal2vk#13](https://github.com/joshuaswarren/metal2vk/pull/13))
- Keep entity retrieval warm across score and lifecycle rewrites ([joshuaswarren/remnic#3178](https://github.com/joshuaswarren/remnic/pull/3178)) (agent)
- Revalidate warm embedding caches after peer index writes ([joshuaswarren/remnic#3176](https://github.com/joshuaswarren/remnic/pull/3176))
- docs: rewrite five guides to pass voice lint ([joshuaswarren/omarchy-mlx#87](https://github.com/joshuaswarren/omarchy-mlx/pull/87))
- Pin QMD to the 2.8.3 build and cancel abandoned daemon searches ([joshuaswarren/remnic#3174](https://github.com/joshuaswarren/remnic/pull/3174)) (agent)
- README: split into a front door and nine docs (move only) ([joshuaswarren/omarchy-mlx#113](https://github.com/joshuaswarren/omarchy-mlx/pull/113))
- Docs: M2 Max bench table, gemm-gap title, sourced 4x/30x figures ([joshuaswarren/metal2vk#71](https://github.com/joshuaswarren/metal2vk/pull/71))
- README: a plain first screen, quick start, limits and roadmap; dev notes move to docs/ ([joshuaswarren/metal2vk#62](https://github.com/joshuaswarren/metal2vk/pull/62))
- Cover offline upload staging with real filesystem checks ([joshuaswarren/remnic#3177](https://github.com/joshuaswarren/remnic/pull/3177))
- docs: oMLX intro says v0.7.1.dev1; raw serve-run receipts ([joshuaswarren/omarchy-mlx#73](https://github.com/joshuaswarren/omarchy-mlx/pull/73))
- docs: pass the voice gates in README and docs prose ([joshuaswarren/coreglass#3](https://github.com/joshuaswarren/coreglass/pull/3))
- and 135 more

## Tests

- simview M3 follow-up: state pooling fixes and mutation coverage rows ([joshuaswarren/omarchy-apple-dev#27](https://github.com/joshuaswarren/omarchy-apple-dev/pull/27))
- coverage: 553 of 609 with the private OpPtrAccessChain case and the lossless implicit-cast merge (+3 over the 550 floor, 0 lost) ([joshuaswarren/metal2vk#35](https://github.com/joshuaswarren/metal2vk/pull/35))
- coverage: front end closes, 598 of 610 (+13 over the 585 floor, 0 lost) ([joshuaswarren/metal2vk#39](https://github.com/joshuaswarren/metal2vk/pull/39))
- tests: detect the SimplifyPointerBitcast tail drift breaking the gate_up shared-gate scalar ([joshuaswarren/metal2vk#47](https://github.com/joshuaswarren/metal2vk/pull/47))
- TESTED-HARDWARE: add apple,t6031 row and a chip coverage check ([joshuaswarren/omarchy-mlx#162](https://github.com/joshuaswarren/omarchy-mlx/pull/162)) (agent)
- tests: fix four F2 battery reds that are test defects ([joshuaswarren/omarchy-mlx#72](https://github.com/joshuaswarren/omarchy-mlx/pull/72)) (agent)
- tests: pin NaN-frequency behavior of the rope host read against the nested gate ([joshuaswarren/omarchy-mlx#77](https://github.com/joshuaswarren/omarchy-mlx/pull/77)) (agent)
- test: independent-streams timing floor reports on NVIDIA, asserts elsewhere (PR #111) ([joshuaswarren/omarchy-mlx#128](https://github.com/joshuaswarren/omarchy-mlx/pull/128))
- tests: name machines, not lab hosts, in comments and two failure-message labels ([joshuaswarren/omarchy-mlx#145](https://github.com/joshuaswarren/omarchy-mlx/pull/145)) (agent)
- tests: M5 skip exits 0 on hosts without Swift; run tests/run.sh in CI ([joshuaswarren/omarchy-apple-dev#38](https://github.com/joshuaswarren/omarchy-apple-dev/pull/38))
- test: reverse-scan expected values match the suffix; uint32 max error uses Cannot max reduce ([joshuaswarren/omarchy-mlx@0311459](https://github.com/joshuaswarren/omarchy-mlx/commit/0311459224ef7aeb648b9428acf0e7b92473a66b))
- test: reverse inclusive scans output the suffix logaddexp ([joshuaswarren/omarchy-mlx@4b50167](https://github.com/joshuaswarren/omarchy-mlx/commit/4b501676126cdc8a82d0cd817975391a8c539233))
- and 15 more

## Build and CI

- sweep: every uzu and TensorFold Zig kernel through the pipeline, with a ranked table of what blocks the rest ([joshuaswarren/metal2vk#3](https://github.com/joshuaswarren/metal2vk/pull/3))
- host: uzu kernel pipeline on Linux (vulkan-host): build script emits the kernel bindings, 23 of 761 kernels translate ([joshuaswarren/metal2vk#26](https://github.com/joshuaswarren/metal2vk/pull/26))
- cli: m2v-compile, a cached one-file front door over the pipeline ([joshuaswarren/metal2vk#32](https://github.com/joshuaswarren/metal2vk/pull/32))
- build(deps): bump @modelcontextprotocol/sdk from 1.30.0 to 1.31.0 ([joshuaswarren/remnic#3170](https://github.com/joshuaswarren/remnic/pull/3170)) (bot)
- Add the GitHub Action ([joshuaswarren/weekship#2](https://github.com/joshuaswarren/weekship/pull/2))
- ci: build gate on the reference cases, one clspv build job, cancel superseded runs ([joshuaswarren/metal2vk#24](https://github.com/joshuaswarren/metal2vk/pull/24))
- ci: host header check so the C header cannot regress ([joshuaswarren/metal2vk#17](https://github.com/joshuaswarren/metal2vk/pull/17))
- CI: bonsai tests skip without mlx; restore assistant --yes flag ([joshuaswarren/omarchy-mlx#51](https://github.com/joshuaswarren/omarchy-mlx/pull/51))
- build(deps): bump datasets from 3.6.0 to 5.0.1 in /model-lab ([joshuaswarren/remnic#3169](https://github.com/joshuaswarren/remnic/pull/3169)) (bot)
- ci: run the test suite on Linux and macOS, Python 3.9 and 3.13 ([joshuaswarren/omarchy-cluster@76f7e26](https://github.com/joshuaswarren/omarchy-cluster/commit/76f7e2676c16274eb0265a4e3c54bc2853fa70e8))
- ci: allow manual runs ([joshuaswarren/omarchy-cluster@baab396](https://github.com/joshuaswarren/omarchy-cluster/commit/baab39640a61d5968dfb4201bdf07104bcbee553))
- ci: collectors job runs tests/ cleanly on runners without mlx ([joshuaswarren/omarchy-mlx@8b07fbe](https://github.com/joshuaswarren/omarchy-mlx/commit/8b07fbe4ed1c4f4a059a884034b9baa77d2afdbc))
- and 5 more

## Maintenance

- chore: remove scratch files and document exclude globs ([joshuaswarren/remnic#3172](https://github.com/joshuaswarren/remnic/pull/3172))
- chore(release): clarify promotion and native publish contracts ([joshuaswarren/remnic#3173](https://github.com/joshuaswarren/remnic/pull/3173))
- allocator: release the newest quarantined generation before the OOM retry ([joshuaswarren/omarchy-mlx#132](https://github.com/joshuaswarren/omarchy-mlx/pull/132))
- release-gates: neutral names for the ANE gate host variables (old names accepted for one release) ([joshuaswarren/omarchy-mlx#153](https://github.com/joshuaswarren/omarchy-mlx/pull/153)) (agent)
- Add v0.2.0 release notes ([joshuaswarren/omarchy-apple-dev#34](https://github.com/joshuaswarren/omarchy-apple-dev/pull/34))
- ledger: 2026-10-05 baseline, M2 Max release ([joshuaswarren/coreglass@13d61d3](https://github.com/joshuaswarren/coreglass/commit/13d61d32d14562a408a7e829e5fb701ac63b4c68))
- ledger correctness gate: greedy token digests per check, must match release on the same Mac ([joshuaswarren/coreglass@af4f173](https://github.com/joshuaswarren/coreglass/commit/af4f173d7b49ca25d181ccf82e0cf7c36e0017c7))
- chore(release): v9.69.95 [skip ci] ([joshuaswarren/remnic@0a4afdc](https://github.com/joshuaswarren/remnic/commit/0a4afdc830c13c0da1c5c9c095fb7691d24ccd4f)) (bot)
- omarchy: the idle tick honors the one-generation release rule ([joshuaswarren/omarchy-mlx@00bf9fa](https://github.com/joshuaswarren/omarchy-mlx/commit/00bf9facbc90a6707abc9d604e6203a2d7a4d0b1))
- chore(release): v9.69.96 [skip ci] ([joshuaswarren/remnic@f076082](https://github.com/joshuaswarren/remnic/commit/f0760820c759b895473c2adc0a268b02cd5a8773)) (bot)
- gate runbook v2 per w7K review: chip assertion + receipt tee + gpu-turn tickets + 2s release check + timeouts (g-g13c); vendored mlx-lm + token-id digests from generate_step + strict Ran-2/OK + 4-digest rule (g-hold); explicit B1 pass rule + SHA256SUMS precheck (M2 battery); [redacted]-gates.sh window plan (g7c/g7d/g13/g15 with CPU build stages); gates-run/ receipt contract; 02:10Z g-g13c PASS retracted ([joshuaswarren/omarchy-mlx@3704004](https://github.com/joshuaswarren/omarchy-mlx/commit/37040046ae9fb33c14802b1b06d27f5055a872c2))
- gate runbook v3 per w7K re-review: g-g13c device-line assignment no longer piped (set -u DEVLINE fix, full info output teed separately); g-hold live tests under the same ticket/lock; vendor-tar no-upstream-mlx assert + MLX_PIN version/libmlx-RECORD check; assets existence asserted before SHA256SUMS -c; stub harness per gate (g-g13c 3 cases, g-hold 3 cases, battery 3 cases) all passing under set -euo pipefail ([joshuaswarren/omarchy-mlx@8b1a6f1](https://github.com/joshuaswarren/omarchy-mlx/commit/8b1a6f1d07d514833c410dcab36cc1637c00cb70))
- and 27 more

## Other changes

- matmul: direct-kernel route rows for the M2 Max and lower m floors on the M1 ([joshuaswarren/omarchy-mlx#38](https://github.com/joshuaswarren/omarchy-mlx/pull/38)) (agent)
- matmul: remove the G13G f32 a @ b route row (loses 8 to 42 % at k 2560 and n 9728) ([joshuaswarren/omarchy-mlx#39](https://github.com/joshuaswarren/omarchy-mlx/pull/39)) (agent)
- gather_qmm: fp16 decode takes the subgroup kernel (M1 64.1 -> 4.13 ms per layer) ([joshuaswarren/omarchy-mlx#42](https://github.com/joshuaswarren/omarchy-mlx/pull/42)) (agent)
- sdpa: opt-in cooperative-matrix flash prefill for causal bf16 head_dim 128 (default off) ([joshuaswarren/omarchy-mlx#41](https://github.com/joshuaswarren/omarchy-mlx/pull/41)) (agent)
- host: Metal host API layer on Vulkan (Rust core, C ABI, compat crates for uzu) ([joshuaswarren/metal2vk#6](https://github.com/joshuaswarren/metal2vk/pull/6))
- sweep: parity harness for the 32 TensorFold sibling kernels ([joshuaswarren/metal2vk#22](https://github.com/joshuaswarren/metal2vk/pull/22))
- clspv pointer passes: undef pointer cache, convergence fixes, two IR pre-passes (441 to 486 of 609 valid) ([joshuaswarren/metal2vk#28](https://github.com/joshuaswarren/metal2vk/pull/28))
- parity: references for every refused kernel, compare-only mode ([joshuaswarren/metal2vk#37](https://github.com/joshuaswarren/metal2vk/pull/37))
- clspv SimplifyPointerBitcast: stop the +256 tail fold and the phi-incoming flip, make every give-up loud (598 of 610 unchanged) ([joshuaswarren/metal2vk#51](https://github.com/joshuaswarren/metal2vk/pull/51))
- custom kernel: metal2vk route for the verified kernel set (env opt-in) ([joshuaswarren/omarchy-mlx#70](https://github.com/joshuaswarren/omarchy-mlx/pull/70))
- omarchy: EXL3 trellis decode primitive (fast::exl3_decode) and composed fast::exl3_moe ([joshuaswarren/omarchy-mlx#97](https://github.com/joshuaswarren/omarchy-mlx/pull/97)) (agent)
- sweep: mlx-batch, all four families in one tree (top, vlmA, vlmb, others) ([joshuaswarren/metal2vk#74](https://github.com/joshuaswarren/metal2vk/pull/74))
- and 870 more
