#


## Download
[source](https://github.com/sheepyy039/tv-series-download/blob/main/TVSD/download.py/#L16)
```python 
Download(
   target: (Literal['Show']|Literal['Season']|Literal['Episode']), base_path: str,
   temp_path: str = None
)
```


---
Download class


**Methods:**


### .guided_download
[source](https://github.com/sheepyy039/tv-series-download/blob/main/TVSD/download.py/#L32)
```python
.guided_download()
```

---
Guided download of show

### .choose_download
[source](https://github.com/sheepyy039/tv-series-download/blob/main/TVSD/download.py/#L52)
```python
.choose_download(
   season: 'Season'
)
```

---
Choose download of show

### .set_special_ep_index
[source](https://github.com/sheepyy039/tv-series-download/blob/main/TVSD/download.py/#L86)
```python
.set_special_ep_index(
   episode: 'Episode'
)
```

---
Set index for special episode


**Args**

* **episode** (Episode) : Episode to set index for


### .set_regular_ep_index
[source](https://github.com/sheepyy039/tv-series-download/blob/main/TVSD/download.py/#L95)
```python
.set_regular_ep_index(
   episode: 'Episode'
)
```

---
Set index for regular episode


**Args**

* **episode** (Episode) : Episode to set index for


### .set_ep_index
[source](https://github.com/sheepyy039/tv-series-download/blob/main/TVSD/download.py/#L104)
```python
.set_ep_index(
   episode: 'Episode'
)
```

---
Set index for episode


**Args**

* **episode** (Episode) : Episode to set index for
* **index** (int) : Index to set


### .download_episode
[source](https://github.com/sheepyy039/tv-series-download/blob/main/TVSD/download.py/#L122)
```python
.download_episode(
   episode: 'Episode'
)
```

---
Download an episode


**Args**

* **episode** (Episode) : Episode to download

