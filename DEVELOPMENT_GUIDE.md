# TVSD Development Guide

## Quick Reference

### Running the Application

```bash
# Install dependencies
poetry install

# Run CLI
poetry run tvsd search "show name"
poetry run tvsd list-shows
poetry run tvsd clean-temp

# With flags
poetry run tvsd --dry-run search "show name"
poetry run tvsd --verbose search "show name"
```

### Adding a New Source

1. Copy `tvsd/sources/_template.py` to `tvsd/sources/new_source.py`
2. Implement all abstract methods from `Source` base class
3. Set `self.__status__ = "active"` in `__init__`
4. Add domain(s) to `self._domains` list
5. Set Chinese conversion if needed: `self._is_simplified = True/False`
6. Add source name to `sources` list in `settings.yaml`

**Required methods to implement:**

- `_search_url(query)` - Build search URL
- `_get_query_results(soup)` - Find result elements in search page
- `_get_result_details_url(result)` - Extract show details page URL
- `_get_result_note(result)` - Extract note/description from result
- `_set_season_title(soup)` - Extract season title from details page
- `_set_season_description(soup)` - Extract description
- `_set_season_episodes(soup)` - Extract list of episode elements
- `_set_season_year(soup)` - Extract year
- `_set_episode_title(soup)` - Extract episode title from episode list
- `_set_relative_episode_url(soup)` - Extract episode URL
- `_episode_url(relative_url)` - Build full episode URL
- `_set_episode_script(soup)` - Extract player script from episode page
- `_set_episode_m3u8(script)` - Extract m3u8 URL from script

### Debugging a Source

```python
# Enable verbose logging
tvsd --verbose search "test"

# Or in code:
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Testing Configuration

```bash
# Dry run (no actual downloads)
tvsd --dry-run search "show name"

# Print current config
tvsd print-state
```

### Common Code Patterns

#### Source Implementation Pattern

```python
class NewSource(Source):
    def __init__(self):
        super().__init__()
        self.__status__ = "active"
        self._domains = ["https://example.com"]
        self._is_simplified = True  # or False for traditional

    def _search_url(self, search_query: str) -> str:
        return f"{self._domain}/search?q={search_query}"

    def _get_query_results(self, soup: BeautifulSoup) -> ResultSet:
        return soup.find_all("div", class_="result-item")

    # ... implement other methods
```

#### Episode Number Detection

The regex pattern in `episode.py` handles:

- Chinese format: `20240101第1期` or `第1集`
- Numeric format: `1`, `01`, `001`
- Special formats with parts: `第1期上`, `第1期下`

#### File Naming

Files are named using:

```python
f"{show_prefix} - S{season_index}E{episode_number} - {episode_name}.mp4"
```

Where:

- `show_prefix` = `{Title} ({Year})`
- `season_index` = `00` for specials, `01`, `02`, etc. for seasons
- `episode_number` = Zero-padded 2 digits

### Configuration Management

**Dynaconf** handles config with:

- Environment variables (prefix: `TVSD_`)
- YAML files (`settings.yaml`)
- Environment-specific configs (`default`, `dev`, etc.)

**Access config:**

```python
from tvsd.config import settings

media_root = settings.MEDIA_ROOT
temp_root = settings.TEMP_ROOT
```

**Update config:**

```python
settings.set("MEDIA_ROOT", "/new/path")
settings.update({"KEY": "value"})
```

### Web Scraping

Uses **CloudScraper** to bypass Cloudflare:

```python
from tvsd.utils import SCRAPER

response = SCRAPER.get(url)
soup = BeautifulSoup(response.content, "html.parser")
```

### Download Process

1. Check if episode exists locally
2. Fetch episode page
3. Extract m3u8 URL from player script
4. Download using `tvsd.downloader.download_m3u8()` (wraps `yt-dlp`, which needs `ffmpeg`)
5. Save to destination directory
6. Clean up temp directory

### Common Issues & Fixes

#### Source Not Finding Results

- Check if website HTML structure changed
- Verify search URL format
- Check if domain is still active
- Enable verbose logging to see requests

#### Episode Number Detection Failing

- Check episode name format
- May need to update regex in `episode.py`
- Can manually set episode number during download

#### m3u8 URL Not Found

- Player script extraction may have changed
- Check if website uses different player
- Verify regex pattern in `_set_episode_m3u8()`

#### Download Fails

- Check temp directory permissions
- Verify media root exists and is writable
- Check network connectivity
- Update `yt-dlp` (`terminal: pip install -U yt-dlp`) - the sites it fetches change often
- Run `make smoke` to see which layer broke

### Code Style

- Uses **Black** for formatting
- Uses **isort** for import sorting
- Uses **pylint** for linting
- Follows PEP 8
- Type hints are used throughout

### Version Management

```bash
# Commit with conventional commits
cz commit

# Bump version
make bump

# Push version tag
make push-tag
```

### Building & Publishing

```bash
# Build package
poetry build

# Publish to PyPI
poetry config pypi-token.pypi <token>
poetry publish
```

### Smoke test

The Django web UI was removed; the CLI is the whole product now. To check that the
scrapers still match the live sites:

```bash
poetry run python scripts/smoke.py            # full live check
poetry run python scripts/smoke.py --offline  # engine + config only
```

### Testing

```bash
# Run tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=tvsd
```

### Project Structure Decisions

- **Sources as plugins**: Easy to add/remove sources
- **Type hierarchy**: Show → Season → Episode mirrors file structure
- **Dynaconf**: Flexible configuration with environment support
- **Typer**: Modern CLI with automatic help generation
- **Rich**: Better terminal output than plain print

### Future Improvements (from code analysis)

1. **Database integration**: Track shows, episodes, download status
2. **Resume downloads**: Handle interrupted downloads
3. **Progress bars**: Better download progress indication
4. **Concurrent downloads**: Download multiple episodes simultaneously
5. **Source health checks**: Validate sources before use
6. **Better error recovery**: Retry logic, fallback sources
7. **Per-source scraper refresh**: rewrite a dead source in `tvsd/sources/`
8. **API**: REST API for programmatic access
9. **Notifications**: Alert when new episodes available
10. **Auto-organization**: Better file organization options
