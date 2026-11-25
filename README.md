# The World in One Day — Tuesday 24 November 2026

![Competition](https://make.fun/badge/news-image-20261124.svg)
![Rank](https://make.fun/badge/news-image-20261124/kyamano/news-image-20261124/rank.svg)
![Reward](https://make.fun/badge/news-image-20261124/kyamano/news-image-20261124/reward.svg)

An entry for the make.fun competition
[news-image-20261124](https://make.fun/c/news-image-20261124) —
"Sum up 24 November's world news in one image".

## What it does

`main.py` is a self-contained Python 3 program (standard library only, no
network) that draws a one-page newspaper summing up the world news of
Tuesday 24 November 2026 and writes it as a 1024 x 1024 PNG to
`/output/entry.png` (or to `$MAKEFUN_OUTPUT_DIR/entry.png` when that
environment variable is set).

The page carries ten detailed panels and twenty brief items, thirty stories
in all, each of which happened, or was first reported, on 24 November 2026
and was cross-checked in at least two independent outlets (Reuters, AP,
BBC, Al Jazeera, CNN and others) before it was included:

- Huawei convicted on 10 of 12 counts in its US criminal trial
- Iran says four tankers hit mines in the Strait of Hormuz
- Ukraine strikes Russian ships off Libya and in the Gulf of Finland
- Nvidia shares fall as the Jensen Huang comeback rally fizzles
- China's Politburo member Chen Jining under investigation
- Senegal regain the Africa Cup of Nations title on appeal
- Riyadh's PIF tower hit in a suspected drone attack, 11 wounded
- Shenzhou-24 crew unveiled, with Pakistan's first astronaut
- Britain launches an inquiry into nuclear tests and veterans
- Solomon Islands to end its China security pact for an Australia treaty

## How it works

There is no image file baked into the program and no imaging library.
The program contains:

- a small RGB framebuffer rasteriser (filled rectangles and rules),
- a hand-drawn 5 x 7 bitmap font covering A-Z, digits and punctuation,
- a word-wrap and panel layout engine for the newspaper page, and
- a minimal PNG encoder built on `zlib` and `struct` (IHDR / IDAT / IEND
  chunks with CRCs).

The output is deterministic: two runs write byte-identical files.

## Run it

```sh
mkdir -p out
MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png (1024 x 1024, well under 1 MiB)
```

## License

MIT — see `LICENSE` (SPDX-License-Identifier: MIT).
