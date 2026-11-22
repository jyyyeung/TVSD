# TV Series Downloader [电视节目下载程序]

[![GitHub version](https://badge.fury.io/gh/jyyyeung%2FTVSD.svg)](https://badge.fury.io/gh/jyyyeung%2FTVSD) [![PyPI version](https://badge.fury.io/py/tvsd.svg)](https://badge.fury.io/py/tvsd)
[![PyPi Version](https://img.shields.io/pypi/v/tvsd.svg)](https://pypi.python.org/pypi/tvsd/)

[![PyPi Python Versions](https://img.shields.io/pypi/pyversions/tvsd.svg)](https://pypi.python.org/pypi/tvsd/)
[![PyPi Downloads](http://pepy.tech/badge/tvsd)](http://pepy.tech/project/tvsd)

> **Status: parked, still working (as of 2026-11).** This is a personal tool that is revived
> occasionally rather than actively developed. See [Current status](#current-status) for what
> works today and how to check it yourself in under a minute.

A small program to download TV and movies from websites, and saves files in a [Plex](https://www.plex.tv/)-readable format.

This program does not provide any of the media content, instead, it grabs content through sites from the internet. Keep
in mind that the copyright of all videos downloaded by this program belongs to the original creator.

谨记本程序下载的所有视频版权归原创者所有，本程序只提供下载服务，并不提供资源存储，也不参与录制、上传。
若本程序无意侵犯了贵司版权，请新增 Issue 提出 。

## Installation and Usage

### Setup and installation

```bash
pip install tvsd
tvsd --help # Show available commands
```

### Update

```bash
pip install tvsd -U
```

### Usage

```bash
tvsd search <your-search-query> # Search query for media from sources and downloads if available
tvsd clean-temp # Removes everything in temp downloading directory, useful after app crashed or aborted
```

Defaults are built in. Override them with a `settings.yaml` in the current directory, with
`~/.config/tvsd/settings.yaml`, with `TVSD_*` environment variables, or per run with flags. The
default media root is `/mnt/viewable`, and it has to exist before a command will validate the
config:

```bash
mkdir -p ~/Movies/TVSD
tvsd --media-root ~/Movies/TVSD search <your-search-query>
```

## Current status

TVSD scrapes sites that are not built to be scraped, so it decays when a site changes. Rather
than pretend otherwise, the repo ships a smoke test that says exactly which layer rotted:

```bash
make install-deps  # poetry install + yt-dlp/ffmpeg prerequisites
make test          # unit tests, no network
make smoke         # live check: search -> details -> m3u8 -> Plex naming
```

`make smoke` prints one PASS/FAIL line per layer and exits non-zero on failure, so "is this
still working?" is a 60-second question instead of an afternoon of debugging.

| Date | Layer | State |
| --- | --- | --- |
| 2026-11 | `xiao_bao` (ibaotv.com, formerly xiaoheimi.net) | working |
| 2026-11 | `olevod` | dead — the site is now a Vue SPA with a WASM/encrypted player |
| 2026-11 | `ssstv` | dead — 403 / timeouts |

Sources are marked `__status__ = "active"|"dead"` and only active ones are queried, so dead
sources cost nothing. Reviving one means rewriting its ~90-line scraper in `tvsd/sources/`, then
running `make smoke` against it.

### Prerequisites

- Python 3.10+
- `ffmpeg` on `PATH` (remuxing the downloaded segments)
- `yt-dlp` on `PATH` or installed in the same environment (the download engine)

```bash
brew install ffmpeg yt-dlp          # macOS
sudo apt install ffmpeg yt-dlp      # Debian/Ubuntu
pip install tvsd "yt-dlp>=2025.1.1" # or let pip provide yt-dlp
```

`tvsd` checks both tools before it starts a download and tells you what is missing.

If a source starts serving a real Cloudflare challenge (the search step fails while the
site still loads in a browser), `make install-stealth` swaps in the maintained
`cloudscraper` fork; see [KNOWN_ISSUES.md](KNOWN_ISSUES.md#dependencies).

## Contribution

Contributions are welcomed, contribution methods and accurate details will be included very soon.

```bash
git clone https://github.com/jyyyeung/TVSD.git
cd tvsd
make setup-dev-env # install pre-commit hooks
make install-deps   # poetry install + ffmpeg/yt-dlp check
cp .env.example .env # update .env according to your environment
make test           # unit tests
make smoke          # live check against the sources
```

### Versioning

This project uses [Commitizen](https://github.com/commitizen-tools/commitizen) to help release and versioning management.

- Fetch GitHub Version Tags: `make fetch-tags`
- Commit: `cz commit`
- Update Release Version: `make bump`
- Push GitHub Version Tag: `make push-tag`

### Publish

```bash
poetry config pypi-token.pypi <my-pypi-token>
poetry build
poetry publish
```


- [x] Search & Download Shows
- [x] Plex naming (season/episode detection, Season 00 for specials)
- [x] Resume, retries and progress via `yt-dlp`
- [ ] Track new episodes
- [ ] TMDB/IMDB metadata lookup (issue #1)
- [ ] Per-source maintenance (see [Current status](#current-status))

## Inspired By and Credits to

- <https://github.com/hectorqin/reader>
- Sonarr

## 免责声明（Disclaimer）

This program is only a tool for personal and mainly educational purposes, and also for those who would like to watch TV
shows in environments without quality internet access, e.g. on the plane.

### Responsibilities

By using this program to download any form of media ("content"), you are entirely responsible for the content of, and
any harm resulting from, that Content. That is the case regardless of whether the Content in question constitutes text,
graphics, an audio file, or computer software. By using this program, you represent and warrant that:

- the downloading, copying and use of the Content will not infringe the proprietary rights, including but not limited to
  the copyright, patent, trademark or trade secret rights, of any third party;
- you have fully complied with any third-party licenses relating to the Content, and have done all things necessary to
  successfully pass through to end users any required terms;
- the Content does not contain or install any viruses, worms, malware, Trojan horses or other harmful or destructive
  content;
- the Content does not contain unethical or unwanted commercial content designed to drive traffic to third party sites
  or boost the search engine rankings of third party sites, or to further unlawful acts (such as phishing) or mislead
  recipients as to the source of the material (such as spoofing);
- the Content is not pornographic, does not contain threats or incite violence, and does not violate the privacy or
  publicity rights of any third party;
- your content is not getting advertised via unwanted electronic messages such as spam links on newsgroups, email lists,
  blogs and websites, and similar unsolicited promotional methods;

### Disclaimer of Warranties

The program is provided “as is”. The program and its suppliers and licensors hereby disclaim all warranties of any kind,
express or implied, including, without limitation, the warranties of merchantability, fitness for a particular purpose
and non-infringement. Neither this program nor its suppliers and licensors, makes any warranty that the program will be
error free or that cess thereto will be continuous or uninterrupted. If you’re actually reading this, here’s a treat.
You understand that you download from, or otherwise obtain content or services through, this program at your own
discretion and risk.

This document is CC-BY-SA. It was last updated March 15, 2023.

Originally adapted from the [Sonarr Terms of Service](https://forums.sonarr.tv/tos).
