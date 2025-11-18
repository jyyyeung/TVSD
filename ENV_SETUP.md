# Environment Variables Setup Guide

## Overview

TVSD uses **Dynaconf** for configuration, which supports multiple ways to set environment variables:

1. **Environment variables** with `TVSD_` prefix
2. **`.env` file** in project root (auto-loaded)
3. **`settings.yaml`** with environment-specific configs
4. **CLI flags** (`--env`, `--media-root`, etc.)

## Method 1: Using `.env` File (Recommended for Development)

Create a `.env` file in the project root:

```bash
# .env
TVSD_MEDIA_ROOT=/path/to/your/media
TVSD_TEMP_ROOT=/path/to/your/temp
TVSD_CREATE_MEDIA_ROOT=true
TVSD_CREATE_TEMP_ROOT=true
TVSD_SERIES_DIR="TV Series"
TVSD_SPECIALS_DIR="Specials"
TVSD_VERBOSE=true
TVSD_DEBUG=true
TVSD_DRY_RUN=false
```

**Note**: All environment variables must be prefixed with `TVSD_` (uppercase).

## Method 2: Using Environment Variables Directly

### Bash/Zsh

```bash
export TVSD_MEDIA_ROOT="/path/to/your/media"
export TVSD_TEMP_ROOT="/path/to/your/temp"
export TVSD_CREATE_MEDIA_ROOT=true
export TVSD_VERBOSE=true
```

### Fish Shell

```fish
set -x TVSD_MEDIA_ROOT "/path/to/your/media"
set -x TVSD_TEMP_ROOT "/path/to/your/temp"
set -x TVSD_CREATE_MEDIA_ROOT true
set -x TVSD_VERBOSE true
```

### Using direnv (if you have `.envrc`)

Add to `.envrc`:

```bash
export TVSD_MEDIA_ROOT="$PWD/temp/media"
export TVSD_TEMP_ROOT="$PWD/temp/downloads"
export TVSD_CREATE_MEDIA_ROOT=true
export TVSD_CREATE_TEMP_ROOT=true
export TVSD_VERBOSE=true
export TVSD_DEBUG=true
```

Then run: `direnv allow`

## Method 3: Using the `dev` Environment

The project already has a `dev` environment configured in `settings.yaml`:

```yaml
dev:
  media_root: "@format {env[PWD]}/temp/media"
  create_media_root: true
  temp_root: "@format {env[PWD]}/temp/downloads"
  create_temp_root: true
  series_dir: TV Series
  specials_dir: Specials
  verbose: true
  debug: true
```

Use it with the `--env` flag:

```bash
tvsd --env dev search "show name"
```

Or set it permanently:

```bash
export TVSD_ENV=dev
tvsd search "show name"
```

## Method 4: Using CLI Flags (Temporary Override)

Override settings for a single command:

```bash
tvsd --env dev --media-root /custom/path --verbose search "show name"
```

## Available Environment Variables

All variables use the `TVSD_` prefix:

| Variable                 | Type | Description                               | Default                   |
| ------------------------ | ---- | ----------------------------------------- | ------------------------- |
| `TVSD_MEDIA_ROOT`        | Path | Where downloaded shows are stored         | `/mnt/viewable`           |
| `TVSD_TEMP_ROOT`         | Path | Temporary download directory              | `$HOME/Movies/temp-parts` |
| `TVSD_CREATE_MEDIA_ROOT` | bool | Auto-create media root if missing         | `false`                   |
| `TVSD_CREATE_TEMP_ROOT`  | bool | Auto-create temp root if missing          | `true`                    |
| `TVSD_SERIES_DIR`        | str  | Subdirectory for TV series                | `"TV Series"`             |
| `TVSD_SPECIALS_DIR`      | str  | Subdirectory for specials                 | `"Specials"`              |
| `TVSD_VERBOSE`           | bool | Enable verbose logging                    | `false`                   |
| `TVSD_DEBUG`             | bool | Enable debug mode                         | `false`                   |
| `TVSD_DRY_RUN`           | bool | Test mode (no actual downloads)           | `false`                   |
| `TVSD_ENV`               | str  | Environment name (`default`, `dev`, etc.) | `"default"`               |

## Priority Order

Dynaconf loads settings in this order (later overrides earlier):

1. Default values in code
2. `settings.yaml` (project root or `~/.tvsd/settings.yaml`)
3. Environment variables (`TVSD_*`)
4. `.env` file
5. CLI flags (`--env`, `--media-root`, etc.)

## Quick Development Setup

### Option A: Create `.env` file

```bash
cat > .env << 'EOF'
TVSD_MEDIA_ROOT=$PWD/temp/media
TVSD_TEMP_ROOT=$PWD/temp/downloads
TVSD_CREATE_MEDIA_ROOT=true
TVSD_CREATE_TEMP_ROOT=true
TVSD_VERBOSE=true
TVSD_DEBUG=true
EOF
```

### Option B: Use dev environment

```bash
# Just use the --env flag
tvsd --env dev search "show name"

# Or set it once
export TVSD_ENV=dev
```

### Option C: Update `.envrc` (if using direnv)

```bash
cat >> .envrc << 'EOF'
export TVSD_ENV=dev
export TVSD_VERBOSE=true
export TVSD_DEBUG=true
EOF
direnv allow
```

## Verification

Check your current configuration:

```bash
tvsd print-state
```

Or with verbose output:

```bash
tvsd --verbose print-state
```

## Example Development Workflow

1. **Create `.env` file**:

   ```bash
   echo "TVSD_ENV=dev" > .env
   echo "TVSD_VERBOSE=true" >> .env
   ```

2. **Run with dry-run first**:

   ```bash
   tvsd --dry-run search "test show"
   ```

3. **Check configuration**:

   ```bash
   tvsd print-state
   ```

4. **Run actual download**:

   ```bash
   tvsd search "show name"
   ```

## Troubleshooting

### Environment variables not being picked up

- Make sure they're prefixed with `TVSD_` (uppercase)
- Check that `.env` file is in project root
- Verify with `tvsd print-state`

### Settings not applying

- Check priority order (CLI flags override everything)
- Use `--verbose` to see what's being used
- Check `~/.tvsd/settings.yaml` for user config

### Dev environment not working

- Make sure `dev:` section exists in `settings.yaml`
- Use `tvsd --env dev print-state` to verify
- Check that paths use `@format {env[PWD]}` syntax correctly

## Notes

- The `.env` file is **gitignored** by default (should be in `.gitignore`)
- Environment variables in `settings.yaml` use `@format {env[VAR_NAME]}` syntax
- Boolean values can be: `true`/`false`, `True`/`False`, `1`/`0`, `yes`/`no`
- Paths can be absolute or relative (relative to project root)
