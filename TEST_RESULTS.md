# TEST_RESULTS.md — news-image-20261124

Run date: Tue 25 Nov 2026 (WIB). All commands run by the build coordinator in
this session; results below are the real outputs, not estimates.

## 1. Kit verification

- Kit downloaded from `https://make.fun/c/news-image-20261124/kit`
  (8,476,062 bytes), unpacked to `work/kit/`.
- `RULES.txt` SHA256 `58cbe276c094a36f5fcb876b869b766506c7d1b708368e14f24af066a62217b9`
  — matches the `get_kit` manifest.
- `competition.yaml` SHA256 `b97f5bc59314a7b7bcec20a294efdf1e552cf43f2cf50aaae607c9bbe871f8f0`
  — matches the manifest.
- Checklist extracted: program `main.py` (Python 3.13, stdlib only), writes
  `/output/entry.png`; PNG or JPEG, at most 1 MiB and 1024x1024; two runs must
  write identical bytes; public GitHub repo + OSI license + transcripts;
  bundle/transcript required; deadline 2026-11-26T00:00:00Z.

## 2. Local execution (build machine)

```
$ MAKEFUN_OUTPUT_DIR=/tmp/n24a python3 main.py
wrote /tmp/n24a/entry.png (188640 bytes) sha256=c61bcade5b7147fe2dd17ce10a6c7af316568870fde92ad0d4974407ef7900ae
```

- Exit code 0. Output: 1024x1024 PNG, RGB, 188,640 bytes (well under the
  1 MiB cap).
- Python 3.12.3 here (harness: Python 3.13); code uses only `hashlib`, `os`,
  `sys` from the standard library plus Pillow 10.2.0, the same dependency the
  20261120/20261121/20261123 entries shipped and ran under.

## 3. Determinism

Three independent runs, two in place and one from a clean directory
containing only `main.py`:

```
c61bcade5b7147fe2dd17ce10a6c7af316568870fde92ad0d4974407ef7900ae  /tmp/n24a/entry.png
c61bcade5b7147fe2dd17ce10a6c7af316568870fde92ad0d4974407ef7900ae  /tmp/n24b/entry.png
c61bcade5b7147fe2dd17ce10a6c7af316568870fde92ad0d4974407ef7900ae  /tmp/n24c/out/entry.png
```

Byte-identical across all three runs. PASS.

## 4. Zero-fail QA (clean room)

- Fresh directory `/tmp/n24qa` with only the six files to be pushed
  (`main.py`, `entry.png`, `README.md`, `LICENSE`, `.makefun/owner.json`).
- `python3 -c "import ast; ast.parse(...)"` — syntax OK.
- `MAKEFUN_OUTPUT_DIR=/tmp/n24qa/out python3 main.py` — exit 0, output
  byte-identical to the build machine (SHA256 `c61bcade...`, see §3).
- Hardcoded-path / secret scan over the pushed files: no matches (the only
  `secret` hits are the words "trade-secret" in the Huawei story text —
  false positives, not credentials).
- Imports: `hashlib`, `os`, `sys` (stdlib) + `PIL.Image/ImageDraw/ImageFont`.
- `.makefun/owner.json` is exactly 58 bytes:
  `{"wallet": "G9dDsodYieJBpsE5wBZS2drwBBRrRCF6ait6z7fhdod"}` + newline.
- QA gate: PASS.

## 5. Visual checks

- Full-size render inspected: masthead, DAY IN NUMBERS, STORIES BY REGION
  bar, 3 hero cards, 10 picture cards, world map, 23 briefs, DATE CHECK +
  HOW SURE + HOW TO READ footer — all legible, no overlapping text.
  Two defects found and fixed in revision: hero Hormuz/hero ships caption
  lines overlapping their diagrams (captions removed, card text carries it),
  and hero 3's summary wrapping to 3 lines and colliding with its tag
  (summary shortened to 2 lines).
- 300 px downscale inspected: date, three leads, six big numbers and the
  region bar read at thumbnail size.
- Automated width check: none of the 23 brief headlines exceeds its column
  (no ellipsis truncation in the final render).

## 6. Judge 2-pass (SolAPI gpt-6.1-sol, Mode MAX)

- `list-models` HTTP 200, model `gpt-6.1-sol`. Judge call via
  `solapi.py chat --message-file work/judge_prompt.txt` returned HTTP 200
  (usage: 5,375 input / 10,899 output tokens; full reply in
  `work/judge_reply.json`).
- HONEST RESULT: **no 95/100 score is claimed.** The judge scored **40/100
  provisionally** because it believed the current date was 3 July 2026 and
  therefore treated 24 Nov 2026 as "in the future" and refused to verify the
  reporting — a model knowledge artifact, not a finding about the poster.
  The actual date is 25 Nov 2026 and every story was verified against
  24 Nov timestamps by three research passes (see `work/research.md`).
- The judge's specific editorial fixes were applied anyway: Huawei diagram
  now reads "US v HUAWEI — NEW YORK · 10 OF 12 COUNTS"; hero 3 headline
  names the vessel (Sparta II) and the second drone arc was removed;
  Hormuz tanker icons are unnumbered; Sanofi wording changed to "agrees to
  buy"; TikTok wording changed to "outage reports"; Senegal wording changed
  to the operative CAS ruling; brief 25 swapped from the weakly-sourced
  Hegseth/Patriots item to Nvidia's $240bn give-back (which also fixes the
  judge's "Nvidia unindexed" finding); all 23 briefs shortened so none
  truncates mid-outcome.
- NOT applied, deliberately: the judge's advice to cut to 10–12 events and
  delete the DATE CHECK / HOW TO READ / map — that contradicts the
  skill's postmortem evidence from three straight winning posters (35–38
  stories, per-day DATE CHECK, HOW TO READ, numbered map), which is the
  stronger evidence for this bounty.

## 7. Story-count audit

- 36 stories total: 3 heroes + 10 picture stories + 23 briefs.
- Regions: Middle East 5, Europe 6, Asia 8, Americas 10, Africa 4,
  Global 3 (= 36).
- Every story first reported Tue 24 Nov 2026 (UTC); exclusions listed
  per-day in the poster's DATE CHECK box and in `work/research.md`.

## 8. Package contents

| File | Size | SHA256 (first 16) |
| --- | --- | --- |
| main.py | 34,499 (835 lines) | fa5adb28af2d91b8… |
| entry.png | 188,640 | c61bcade5b7147fe… |
| README.md | ~3,400 | — |
| TEST_RESULTS.md | this file | — |
| LICENSE | 1,099 | MIT, SPDX line 1 |
| .makefun/owner.json | 58 | exact wallet file |

## 9. Not done by this build (parent's scope)

- No `git init`, no clone, no push, no submit, no bundle/record — the parent
  handles push + submit.
- No claim, no payment, no wallet creation.
