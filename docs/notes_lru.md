# Notes: LRUCache (cachetools)

Module under test: `cachetools.LRUCache` (Least Recently Used cache).
Behaviour below was confirmed by running the class by hand (probe script), not assumed.

## 1. `__setitem__` (`c[key] = value`)

**ECP (equivalence classes)**
- Valid hashable keys: str, int, tuple, float, None -> stored and readable
- Existing key -> value is overwritten, size does not grow
- Invalid key: unhashable type (list) -> `TypeError: unhashable type: 'list'`

**BVA (boundary values), with maxsize = 3**
- Insert into empty cache: size 0 -> 1
- Insert up to the limit: size 2 -> 3, nothing evicted
- Insert one past the limit (4th item): oldest item evicted, size stays 3
- maxsize = 0: any insert -> `ValueError: value too large`

**Other**
- Overwriting a key counts as "recently used"

## 2. `__getitem__` (`c[key]`)

**ECP**
- Existing key -> returns its value
- Missing key -> `KeyError: 'a'`
- Key that was evicted earlier -> `KeyError`

**BVA**
- Cache with exactly 1 item
- Oldest key and newest key of a full cache both readable

**Other**
- Reading a key marks it "recently used", so it is evicted last

## 3. `popitem()`

**ECP**
- Non-empty cache -> removes and returns the least recently used `(key, value)`
- Empty cache -> `KeyError: 'LRUCache is empty'`

**BVA**
- Cache with exactly 1 item: returns it, cache becomes empty
- Full cache (size = maxsize): returns the oldest item
- Calling popitem repeatedly until empty, then once more -> `KeyError`

## 4. Class level (`LRUCache` as a whole)

- maxsize boundaries: 1, 2, 5 (cache never holds more than maxsize items)
- Properties and operators: `maxsize`, `currsize`, `len(c)`, `key in c`
- Eviction order after a mix of reads and writes
- `clear()` empties the cache (currsize 0)
- `pop(key)` removes a specific key; `pop` of a missing key raises `KeyError`

## Observed results from the probe (evidence)

| Action | Result |
|---|---|
| get missing key | KeyError 'a' |
| popitem on empty cache | KeyError 'LRUCache is empty' |
| set with maxsize=0 | ValueError value too large |
| set unhashable key (list) | TypeError unhashable type: 'list' |
| 3 inserts into maxsize 2 | ['b', 'c'], currsize 2 |
| read b, then add d | ['b', 'd'] (c evicted, b kept) |
| popitem | ('b', 2) |
