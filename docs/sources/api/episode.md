#


## Episode
[source](https://github.com/sheepyy039/tv-series-download/blob/main/TVSD/episode.py/#L36)
```python 
Episode(
   episode_name: str, episode_url: str, season = None
)
```


---
Episode class


**Methods:**


### .identify_episode_number_from_name
[source](https://github.com/sheepyy039/tv-series-download/blob/main/TVSD/episode.py/#L63)
```python
.identify_episode_number_from_name()
```

---
Tries to identify the episode number from the episode name.


**Returns**

* **int**  : The identified episode number.


### .determine_if_specials
[source](https://github.com/sheepyy039/tv-series-download/blob/main/TVSD/episode.py/#L92)
```python
.determine_if_specials()
```

---
Determines if the episode is a special episode from episode title.


**Returns**

* **bool**  : True if the episode is a special episode, False otherwise.


### .is_specials
[source](https://github.com/sheepyy039/tv-series-download/blob/main/TVSD/episode.py/#L104)
```python
.is_specials()
```

---
Returns True if the episode is a special episode, False otherwise.


**Returns**

* **bool**  : True if the episode is a special episode, False otherwise.


### .is_regular
[source](https://github.com/sheepyy039/tv-series-download/blob/main/TVSD/episode.py/#L113)
```python
.is_regular()
```

---
Returns True if the episode is a regular episode, False otherwise.


**Returns**

* **bool**  : True if the episode is a regular episode, False otherwise.


### .episode_number
[source](https://github.com/sheepyy039/tv-series-download/blob/main/TVSD/episode.py/#L122)
```python
.episode_number()
```

---
Returns the episode number.


**Returns**

* **int**  : The episode number.


### .determine_episode_number
[source](https://github.com/sheepyy039/tv-series-download/blob/main/TVSD/episode.py/#L138)
```python
.determine_episode_number()
```

---
Determines the episode number.


**Returns**

* **int**  : The episode number.


### .name
[source](https://github.com/sheepyy039/tv-series-download/blob/main/TVSD/episode.py/#L153)
```python
.name()
```

---
Returns the episode name.


**Returns**

* **str**  : The episode name.


### .filename
[source](https://github.com/sheepyy039/tv-series-download/blob/main/TVSD/episode.py/#L162)
```python
.filename()
```

---
Returns the filename of the episode.


**Returns**

* **str**  : The filename of the episode.


### .get_episode_url
[source](https://github.com/sheepyy039/tv-series-download/blob/main/TVSD/episode.py/#L174)
```python
.get_episode_url()
```

---
Gets the episode url from the episode object.


**Args**

* **episode** (Episode) : The episode object.


**Returns**

* **str**  : The episode url.


### .relative_episode_file_path
[source](https://github.com/sheepyy039/tv-series-download/blob/main/TVSD/episode.py/#L191)
```python
.relative_episode_file_path()
```

---
Returns the relative path to the episode file.


**Returns**

* **str**  : The relative path to the episode file.


### .file_exists_locally
[source](https://github.com/sheepyy039/tv-series-download/blob/main/TVSD/episode.py/#L200)
```python
.file_exists_locally()
```

---
Returns True if the episode exists locally, False otherwise.


**Returns**

* **bool**  : True if the episode exists locally, False otherwise.


### .season
[source](https://github.com/sheepyy039/tv-series-download/blob/main/TVSD/episode.py/#L224)
```python
.season()
```

---
Returns the season object.


**Returns**

* **Season**  : The season object.


### .fetch_episode_m3u8_url
[source](https://github.com/sheepyy039/tv-series-download/blob/main/TVSD/episode.py/#L233)
```python
.fetch_episode_m3u8_url()
```

---
Fetches the m3u8 url of the episode.


**Returns**

* **str**  : The m3u8 url of the episode.


### .relative_destination_dir
[source](https://github.com/sheepyy039/tv-series-download/blob/main/TVSD/episode.py/#L242)
```python
.relative_destination_dir()
```

---
Returns the relative destination directory of the episode.


**Returns**

* **str**  : The relative destination directory of the episode.


----


### get_episode_name
[source](https://github.com/sheepyy039/tv-series-download/blob/main/TVSD/episode.py/#L12)
```python
.get_episode_name(
   episode: 'Episode'
)
```

---
Gets the episode name from the episode object.


**Args**

* **episode** (Episode) : The episode object.


**Returns**

* **str**  : The episode name.

