#


## SearchQuery
[source](https://github.com/sheepyy039/tv-series-download/blob/main/TVSD/search.py/#L14)
```python 
SearchQuery(
   query: str
)
```


---
Searches for a show based on query


**Methods:**


### .find_show
[source](https://github.com/sheepyy039/tv-series-download/blob/main/TVSD/search.py/#L23)
```python
.find_show(
   base_path: str
)
```

---
Finds show information locally or online


**Args**

* **base_path** (str) : Base path to local media directory


### .check_local_shows
[source](https://github.com/sheepyy039/tv-series-download/blob/main/TVSD/search.py/#L39)
```python
.check_local_shows(
   base_path: str
)
```

---
Checks if show exists locally in directory


**Args**

* **base_path** (str) : Base path to local media directory


### .find_shows_online
[source](https://github.com/sheepyy039/tv-series-download/blob/main/TVSD/search.py/#L65)
```python
.find_shows_online()
```

---
Searches for shows online and returns a list of shows

### .chosen_show
[source](https://github.com/sheepyy039/tv-series-download/blob/main/TVSD/search.py/#L91)
```python
.chosen_show()
```

---
Returns the chosen show


**Returns**

* Chosen show

