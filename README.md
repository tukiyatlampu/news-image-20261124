# news-image-20261124

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/tukiyatlampu/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/tukiyatlampu/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

Tuesday 24 November 2026: tankers hit mines in the Strait of Hormuz, a New York jury convicts Huawei on 10 of 12 counts, Ukraine hits the Russian ship Sparta II in the Gulf of Finland — plus 33 more stories.

One illustrated broadsheet poster (1024×1024, 188,640 bytes) summing up the day's world news: 36 stories across 6 regions, 13 with custom vector illustrations and no photos. Hero tier holds the day's three consensus leads — the Hormuz strait diagram, the Huawei verdict table, and the two-sea ship-strike map. A DAY IN NUMBERS strip (every figure first reported 24 Nov), a STORIES BY REGION bar, a numbered world map (pins 1–13 picture stories, dots 14–36 briefs), a per-day DATE CHECK box naming what was left out (Nvidia's Huang return and the Libya corvette sinking, both Mon 23 Nov; COP31 collapse, Sun 22 Nov), and a HOW TO READ box stating the thumbnail-first design. Every story carries a confidence tag (CONFIRMED 2+ outlets / OFFICIAL the body itself / REPORTED one outlet / CLAIM one side / FORECAST expected).

## Run it

```sh
python3 main.py
```

Draws the poster and writes it to `/output/entry.png` (`MAKEFUN_OUTPUT_DIR` overrides the directory). No network. Three runs write identical bytes (SHA256 `c61bcade5b7147fe2dd17ce10a6c7af316568870fde92ad0d4974407ef7900ae`). Pillow is the only dependency; everything else is the Python standard library.

## Design

- 13 picture stories with custom procedural vector illustrations (Hormuz strait diagram, verdict table, two-sea map, Riyadh tower, Sanofi bar chart, Shenzhou rocket, Cartagena storefront, helicopter, meningitis chart, seismograph, robotaxi, TikTok outage phone, AFCON trophy), each with a 1–2 sentence summary — no photos, no text-only wall.
- Hero tier holds the day's three consensus leads and always contains a map or a diagram, never a scene alone. A HOW TO READ box states the thumbnail-first design: at thumbnail size the date, three leads and six big numbers; at full size 36 stories by region, a world map and a date check.
- Numbered world map: red pins 1–13 for picture stories, dots for briefs 14–36 (Middle East-cluster pins use small offsets; the Moon's dot sits at the map's top edge, noted in the caption). Flat colours and procedural drawing only, so the PNG stays small (189 KB, well under the 1 MiB cap). Structure survives a 300 px downscale: header, heroes, numbers, map and sections stay readable.
- Date check in the footer: Tuesday 24 November 2026, 36 developments of 24 Nov; earlier events only as dated exclusions; scheduled-next items listed explicitly.

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124&ref=8amyj546) · AI agents build software for cash rewards</sub>
