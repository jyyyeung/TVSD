## v1.1.2 (2023-07-24)

### Fix

- catch error during download and aport
- return None if error exists and ignore result

## v1.1.1 (2023-07-24)

### Fix

- 777TV year matching regex fix

### Perf

- catch exception upon connection error

## v1.1.0 (2023-07-24)

### Feat

- set source simplified or traditional search_query for automatic translation
- create general series directory if not exist in base
- **config**: created basic config setup

### Refactor

- Cleanup code

## v1.0.1 (2023-07-12)

### Refactor

- added all sources import in __init__.py and generalized ssstv urls into source_url and relative path

## v1.0.0 (2023-07-11)

### Feat

- **source**: Added new media source 777tv

### Fix

- websockets auto patch failed due to pyppeteer==1.0.2 dependencies

## v1.0.0a0 (2023-07-11)

### Fix

- update COMMIT_MSG_HOOK in makefile
