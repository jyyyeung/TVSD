# Known Issues & Potential Bugs

## Critical Issues

### 1. Episode Number Parsing Bug (High Priority)

**Location**: `tvsd/download.py:198`

```python
number = int(existing_file.split(" - ")[1].split("E")[1])
```

**Issue**: This assumes the filename format is exactly `Show - S01E01 - Title.mp4`. If the format differs or contains "E" in the title, this will fail or parse incorrectly.

**Fix**: Use regex to extract episode number:

```python
import re
match = re.search(r'S\d+E(\d+)', existing_file)
if match:
    number = int(match.group(1))
```

### 2. Error Handling in Download

**Location**: `tvsd/download.py:232-236`
**Issue**: Exception is caught but temp directory cleanup happens regardless. If download fails, temp files may remain.

**Current code**:

```python
except Exception as error:
    print("Error downloading episode: " + str(error))
    print("Removing temp dir...")
if not settings.DRY_RUN:
    shutil.rmtree(temp_dir, ignore_errors=True)
```

**Issue**: The `shutil.rmtree` is outside the except block, so it always runs. Should be inside the except block.

### 3. Type Inconsistency in Episode Number

**Location**: `tvsd/types/episode.py:146`
**Issue**: `self._number` is declared as `int` but initialized as `None` in `__init__`. The property getter checks for `None`, but type hints don't reflect this.

**Fix**: Use `Optional[int]` or initialize with a default value.

### 4. Potential IndexError in Search

**Location**: `tvsd/search.py:123-125`

```python
self._chosen_show = query_results[
    typer.prompt(text="请选择你下载的节目", type=int)
]
```

**Issue**: No validation that the user input is within the valid range. If user enters an invalid index, this will raise `IndexError`.

**Fix**: Add validation:

```python
while True:
    choice = typer.prompt(text="请选择你下载的节目", type=int)
    if 0 <= choice < len(query_results):
        break
    typer.echo("Invalid choice, please try again")
self._chosen_show = query_results[choice]
```

## Medium Priority Issues

### 5. Incomplete Local Show Detection

**Location**: `tvsd/search.py:59-84`
**Issue**: `check_local_shows()` method is defined but never called (commented out). The functionality is incomplete.

**Status**: TODO - Feature not implemented

### 6. Database Integration Missing

**Location**: Multiple files

- `tvsd/search.py:54` - TODO comment about database
- `tvsd/search.py:92` - TODO about searching in database first
- `tvsd/sources/base.py:18-44` - `load_source_details()` incomplete

**Issue**: Database features are mentioned but not implemented. No database models or queries exist.

### 7. Hardcoded Chinese Text

**Location**: Multiple files

- `tvsd/search.py:124` - "请选择你下载的节目"
- `tvsd/types/season.py:55` - "这个节目是否续季？"
- `tvsd/types/season.py:56` - "这个节目是第几季？"
- `tvsd/types/season.py:247` - "第一季在那一年？"

**Issue**: Mixed Chinese/English in codebase. Should use i18n or at least constants.

### 8. Episode Number Detection Regex Complexity

**Location**: `tvsd/types/episode.py:80`
**Issue**: Complex regex pattern that may have edge cases:

```python
episode_number_identifying_regex = r"^[0-9]{8}[（(]*第(\d+)[期集][(（上中下)）]*[)）]?$|^(\d{1,3})$|^第(\d+)[期集][上中下]*$"
```

**Issue**: Hard to maintain and debug. Consider breaking into multiple patterns or using a parser.

### 9. Race Condition in Temp Directory Check

**Location**: `tvsd/download.py:219-221`

```python
if not os.path.isdir(temp_dir):
    mkdir_if_no(temp_dir)
```

**Issue**: Between the check and creation, another process could create the directory, causing issues.

**Fix**: Use `os.makedirs(exist_ok=True)` or handle `FileExistsError`.

### 10. Missing Error Handling for BeautifulSoup Parsing

**Location**: `tvsd/sources/base.py` and source implementations
**Issue**: Many BeautifulSoup operations don't check if elements exist before calling `.get_text()` or accessing attributes, which can raise `AttributeError`.

**Example**: `tvsd/sources/xiao_bao.py:31`

```python
return soup.find("a").get_text()  # Could be None
```

**Fix**: Add null checks:

```python
link = soup.find("a")
if link:
    return link.get_text()
return ""
```

## Low Priority / Code Quality Issues

### 11. Unused Show Class

**Location**: `tvsd/types/show.py:3`
**Comment**: "Currently not used a lot, will consider removing"

**Issue**: The Show class exists but may not be fully utilized. Consider refactoring.

### 12. Debug Mode Always On in Django

**Location**: `config/settings.py:105`

```python
DEBUG = True  # Hardcoded
```

**Issue**: Should use environment variable or config setting.

### 13. Incomplete Web UI

**Location**: `pages/views.py`
**Issue**: Forms are created but don't actually perform actions (commented out `search_media_and_download` call).

### 14. Episode Name Parsing TODO

**Location**: `tvsd/types/episode.py:186-190`
**Issue**: Comment mentions handling "中" (middle/part) but not implemented.

### 15. Missing Validation in Config

**Location**: `tvsd/config.py:44-45`
**Issue**: `MEDIA_ROOT` and `TEMP_ROOT` use `must_exist=True`, but if `CREATE_MEDIA_ROOT` or `CREATE_TEMP_ROOT` is True, this validation will fail before creation.

**Fix**: Validation should check creation flags.

### 16. Source Status Check

**Location**: `tvsd/search.py:109`

```python
if issubclass(cls_obj, Source) and cls_obj().__status__ == "active":
```

**Issue**: Creates an instance just to check status. Could be inefficient if sources have expensive initialization.

**Fix**: Use class attribute or check differently.

### 17. Episode Index Calculation Bug

**Location**: `tvsd/download.py:198-202`
**Issue**: When skipping existing episodes, the index is calculated from filename, but if episodes are out of order or missing, this could cause numbering issues.

### 18. No Retry Logic for Network Requests

**Location**: `tvsd/utils.py:17-28` (SCRAPER)
**Issue**: Network requests can fail due to temporary issues, but there's no retry logic.

**Fix**: Add retry decorator or wrapper.

### 19. File Existence Check Performance

**Location**: `tvsd/types/episode.py:233-273`
**Issue**: `file_exists_locally` does multiple directory listings which could be slow for large directories.

### 20. Season Index Prompt Always Shows

**Location**: `tvsd/types/season.py:197-199`
**Issue**: Even if season index can be determined automatically, user is always prompted to fix it.

## Recommendations

### Immediate Fixes (Before Next Release)

1. Fix episode number parsing bug (#1)
2. Fix error handling in download (#2)
3. Add index validation in search (#4)
4. Fix type hints for episode number (#3)

### Short Term Improvements

5. Add null checks for BeautifulSoup operations (#10)
6. Fix race condition in temp directory (#9)
7. Add retry logic for network requests (#18)
8. Fix config validation logic (#15)

### Long Term Refactoring

9. Implement database integration (#6)
10. Complete local show detection (#5)
11. Internationalize hardcoded strings (#7)
12. Simplify episode number detection (#8)
13. Complete web UI (#13)

## Testing Recommendations

1. **Unit Tests Needed**:
   - Episode number parsing (various formats)
   - File existence detection
   - Season index detection
   - Source parsing methods

2. **Integration Tests Needed**:
   - Full download workflow
   - Error recovery
   - Concurrent downloads
   - Config validation

3. **Edge Cases to Test**:
   - Episodes with special characters in names
   - Missing episodes in sequence
   - Network failures during download
   - Invalid user input in prompts
   - Corrupted temp directories
