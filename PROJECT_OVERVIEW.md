# TVSD Project Overview

## Project Purpose

TVSD (TV Series Downloader) is a Python CLI application that searches for and downloads TV shows and movies from various Chinese streaming websites. It saves files in a Plex-readable format with proper naming conventions.

## Architecture Overview

### Core Components

#### 1. **CLI Interface** (`tvsd/cli.py`)

- Built with **Typer** for command-line interface
- Main commands:
  - `search <query>` - Search and download media
  - `clean-temp` - Clean temporary download directory
  - `list-shows` - List all downloaded shows
  - `remove-show` - Remove a show from library
  - `print-state` - Print current configuration
  - `clean-base` - Remove empty directories
- Supports flags: `--verbose`, `--dry-run`, `--series-dir`, `--media-root`, `--env`

#### 2. **Search System** (`tvsd/search.py`)

- `SearchQuery` class handles search operations
- Searches across multiple sources (plugins)
- Displays results in a Rich table
- Interactive selection of shows to download

#### 3. **Download System** (`tvsd/download.py`)

- `Download` class manages episode downloads
- Downloads m3u8 streams and converts to MP4
- Handles:
  - Guided downloads (interactive)
  - Batch downloads (all episodes)
  - Selective downloads (choose episodes)
  - Specials vs regular episodes
  - Episode numbering and file naming

#### 4. **Source System** (`tvsd/sources/`)

- Plugin-based architecture for different streaming sites
- Base class: `Source` (abstract base class)
- Active sources:
  - `xiao_bao.py` - XiaoBao source
  - `olevod.py` - OLEVOD source
  - `ssstv.py` - SSSTV source
- Inactive sources (prefixed with `_`):
  - `_bu_ding_3.py`
  - `_ify.py`
  - `_mov.py`
  - `_ying_hua.py`
  - `_template.py` (template for new sources)

**Source Interface:**
Each source must implement:

- `_search_url()` - Build search URL
- `_get_query_results()` - Parse search results
- `_set_episode_title()` - Extract episode title
- `_set_relative_episode_url()` - Extract episode URL
- `_get_result_details_url()` - Get show details page URL
- `_set_season_title/description/episodes/year()` - Parse season info
- `_set_episode_script()` - Extract player script
- `_set_episode_m3u8()` - Extract m3u8 URL from script

#### 5. **Type System** (`tvsd/types/`)

- **Show** - Represents a TV show (parent of seasons)
- **Season** - Represents a season (parent of episodes)
- **Episode** - Represents a single episode
- Hierarchy: Show → Season → Episode

#### 6. **Configuration** (`tvsd/config.py`)

- Uses **Dynaconf** for configuration management
- Config file: `settings.yaml` (in user config dir or project root)
- Key settings:
  - `MEDIA_ROOT` - Where downloaded shows are stored
  - `TEMP_ROOT` - Temporary download directory
  - `SERIES_DIR` - Subdirectory for TV series (default: "TV Series")
  - `SPECIALS_DIR` - Subdirectory for specials (default: "Specials")
  - `CREATE_MEDIA_ROOT` / `CREATE_TEMP_ROOT` - Auto-create directories
  - `DRY_RUN` - Test mode without actual downloads
  - `sources` - List of active sources

#### 8. **Utilities** (`tvsd/utils.py`)

- `SCRAPER` - CloudScraper instance for web scraping
- Directory/file operations
- Video file detection
- Typer CLI helper decorator

## File Structure

```
TVSD/
├── tvsd/                    # Main package
│   ├── __init__.py         # Package initialization
│   ├── __main__.py         # Entry point
│   ├── cli.py              # CLI commands
│   ├── actions.py          # High-level actions (search, list)
│   ├── search.py           # Search functionality
│   ├── download.py         # Download functionality
│   ├── config.py           # Configuration management
│   ├── utils.py            # Utility functions
│   ├── sources/            # Source plugins
│   │   ├── base.py         # Base Source class
│   │   ├── xiao_bao.py     # Active source
│   │   ├── olevod.py       # Active source
│   │   ├── ssstv.py        # Active source
│   │   └── _*.py           # Inactive sources
│   └── types/               # Data models
│       ├── show.py         # Show class
│       ├── season.py       # Season class
│       └── episode.py      # Episode class
├── settings.yaml            # Default configuration
├── scripts/
│   └── smoke.py            # Live health check (search -> details -> m3u8 -> naming)
├── tests/                   # Unit tests (no network)
├── pyproject.toml          # Poetry dependencies
└── README.md               # User documentation
```

## Workflow

1. **User runs**: `tvsd search "show name"`
2. **Search phase**:
   - `SearchQuery` iterates through all active sources
   - Each source searches and returns results
   - Results displayed in table
   - User selects show
3. **Details phase**:
   - Selected show's details are fetched
   - Episodes are parsed and generated
   - Season index is determined
4. **Download phase**:
   - User chooses download mode (all/selective)
   - For each episode:
     - Check if already exists locally
     - Fetch m3u8 URL from source
     - Download using `yt-dlp` via `tvsd.downloader.download_m3u8()` (requires `ffmpeg`)
     - Save to: `{MEDIA_ROOT}/{SERIES_DIR}/{Show Name (Year)}/Season {NN}/{filename}.mp4`
     - Specials go to: `{MEDIA_ROOT}/{SERIES_DIR}/{Show Name (Year)}/{SPECIALS_DIR}/`

## Key Dependencies

- **typer** - CLI framework
- **rich** - Terminal UI (tables, formatting)
- **yt-dlp** - Download engine (HLS handling, resume, retries); needs `ffmpeg` on `PATH`
- **beautifulsoup4** - HTML parsing
- **cloudscraper** - Web scraping (bypasses Cloudflare), pinned to a commit
- **chinese-converter** - Chinese character conversion
- **dynaconf** - Configuration management

## Naming Convention

Episodes are named:

```
{Show Name (Year)} - S{Season}E{Episode} - {Episode Title}.mp4
```

Example:

```
The Office (2005) - S01E01 - Pilot.mp4
```

Specials:

```
{Show Name (Year)} - S00E{Number} - {Episode Title}.mp4
```

## Configuration

Default config location: `~/.tvsd/settings.yaml` (or `settings.yaml` in project root)

Example:

```yaml
default:
  media_root: /mnt/viewable
  create_media_root: false
  temp_root: "@format {env[HOME]}/Movies/temp-parts"
  create_temp_root: true
  series_dir: TV Series
  specials_dir: Specials
  sources: [xiao_bao, olevod]
  verbose: false
```

## Known Issues / TODOs

From code analysis:

1. **Incomplete features**:
   - Web UI is partially implemented (forms exist but don't fully work)
   - Database integration mentioned but not implemented
   - Local show detection (`check_local_shows`) is incomplete
   - Source details persistence (`load_source_details`) incomplete

2. **Code quality**:
   - Some error handling could be improved
   - Type hints are mostly present but some inconsistencies
   - Some hardcoded Chinese prompts in English codebase
   - Episode number detection regex is complex and may have edge cases

3. **Architecture**:
   - `Show` class is noted as "Currently not used a lot, will consider removing"
   - Some deprecated config keys (BASE_PATH, TEMP_PATH) handled via hooks

4. **Features mentioned in README but not implemented**:
   - Track new episodes
   - Web UI (partially done)
   - Docker support
   - Searching progress bar

## Testing

- Test file exists: `tests/cli_test.py`
- Uses pytest
- No comprehensive test suite visible

## Development Setup

```bash
poetry install
make setup-dev-env  # Install pre-commit hooks
cp .env.example .env  # Configure environment
```

## Version Management

- Uses Commitizen for versioning
- Version in: `pyproject.toml`, `VERSION`, `setup.py`
- Commands:
  - `cz commit` - Commit with conventional commits
  - `make bump` - Update version
  - `make push-tag` - Push version tag

## Common Issues to Check

1. **Source breakage**: Websites change HTML structure frequently
2. **m3u8 URL extraction**: Regex patterns may need updates
3. **Episode numbering**: Complex regex for Chinese episode names
4. **File existence detection**: Multiple checks, may have edge cases
5. **Directory creation**: Race conditions possible in multi-threaded downloads

## Areas for Improvement

1. **Error handling**: More robust error handling and retry logic
2. **Logging**: Better structured logging
3. **Testing**: More comprehensive test coverage
4. **Documentation**: API documentation, source plugin guide
5. **Source plugins**: Make sources pluggable so a dead site is a one-file fix
6. **Database**: Add proper database for tracking shows
7. **Progress tracking**: Better download progress indicators
8. **Resume downloads**: Handle interrupted downloads
9. **Concurrent downloads**: Better threading/async support
10. **Source validation**: Health checks for sources
