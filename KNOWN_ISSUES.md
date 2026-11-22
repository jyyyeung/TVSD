# Known Limitations

TVSD is a scraper for sites that have no API and change without notice. This file records what
is known to be imperfect today, so nobody has to rediscover it.

Last reviewed: 2026-11 (revival branch `revive/park-hardening`).

## Source health

| Source | State | Notes |
| --- | --- | --- |
| `xiao_bao` | active | now served from `ibaotv.com` (was `xiaoheimi.net`); the player already ships a WASM bundle on some pages, so the m3u8 extraction can break at any time |
| `olevod` | dead | the site became a Vue SPA that builds requests in WASM (`play.wasm`, `crypto-js`, `js-md5`); the old HTML selectors are gone. Reviving it means reverse-engineering that, not fixing a selector |
| `ssstv` | dead | `777tv.tw` answers 403 and `ssstv.com` times out |

`Source.__status__` is `"active"` or `"dead"`; `tvsd/search.py` skips dead sources and sources not
listed under `sources:` in `settings.yaml`. Run `make smoke` to re-check all of this.

## Naming

- **Show year for seasons > 1 is a guess.** The source only exposes the year of *this* season, so
  `Season.determine_show_begin_year()` computes `season_year - season_index + 1`. That is right for
  an annually released show and wrong otherwise (庆余年: season 2 aired 2024, but the show started
  2019, so the folder is `庆余年 (2023)`). Interactively the CLI asks; non-interactively (piped
  stdin, CI, `scripts/smoke.py`) it uses the computed value. Plex normally still matches on the
  title, but a wrong year can produce a mismatch for remakes — rename the folder if it does.
- **Special episodes** are detected by *exclusion*: an episode name that the number regex cannot
  parse ("特别篇", "预告片") becomes `S00`, while names like `20240101`, `第3期上` or `12` stay in
  the regular season. That matches how the sources label episodes, but a site that numbers its
  specials like regular episodes will file them in the wrong place.
- **Title cleanup is regex-based** (`_clean_season_title()` in `tvsd/sources/xiao_bao.py`) and
  strips the current site branding/noise tokens. A rebrand or a new marketing suffix will leak
  into folder names until the token list is updated.

## Interaction

- The CLI is interactive by design: `typer.prompt()` for show choice, download selection, season
  index and first-season year. The two *fix-up* prompts (season index, begin year) skip themselves
  when stdin is not a TTY or `NON_INTERACTIVE=true`, so smoke tests and scripts do not hang. The
  show-choice and episode-choice prompts still require a TTY.
- Prompts are hardcoded in Chinese; the rest of the output is English.

## Download engine

- `yt-dlp` + `ffmpeg` are external prerequisites (not vendored). `tvsd.downloader.check_engine()`
  reports what is missing before a download starts.
- Downloads resume (`continuedl`) and retry, but there is no queue, no concurrent episode
  download and no `--download-archive`-style ledger: re-running is how you get missing episodes.
- A failed download removes its temp directory; `tvsd clean-temp` clears leftovers from a crash.

## Dependencies

- `cloudscraper` comes from PyPI, whose newest release (1.2.71, 2023) predates the fork
  TVSD was written against. `tvsd/utils.py` uses it when the arguments it needs exist and
  otherwise falls back to a plain `requests.Session` with a desktop user agent, so a plain
  install survives sites that only need a browser user agent, not a solved challenge.
- `cloudscraper` debug output is off by default; set `SCRAPER_DEBUG=true` to see raw HTTP traffic.
- If a source starts serving a real Cloudflare challenge, upgrade the scraper with
  `make install-stealth` — it overlays `VeNoMouS/cloudscraper@9ea528a` (3.0.0) on top of the
  install. That overlay cannot live in package metadata (PyPI rejects git dependencies), so
  it is a deliberate, optional step rather than a default.

## Testing

- `tests/` covers episode numbering, Plex naming, title cleanup and source filtering — no network.
- `scripts/smoke.py` covers the live chain (search → details → m3u8 → naming) and is the fastest
  way to see which layer broke. It is not part of `pytest` because it needs the internet.

## Not implemented

- Episode tracking / new-episode notifications
- TMDB/IMDB metadata (show year, episode titles) — issue #1, would remove the year guessing above
- Web UI (removed; the unfinished Django app was deleted in this branch)
