# Notes: cachetools.func (lru_cache, ttl_cache)

Behaviour was checked by running the decorators by hand first.

## lru_cache(maxsize, typed)
ECP:
- Repeated call with the same argument -> hit, function not run again
- New argument -> miss
- typed=False: 1 and 1.0 share one entry; typed=True: separate entries
- Invalid: unhashable argument -> TypeError; negative maxsize -> ValueError
BVA (maxsize):
- maxsize = 0 -> nothing is stored, every call is a miss
- maxsize = 2 with 3 different arguments -> the oldest is evicted and recomputed
- maxsize = None -> unbounded, nothing is evicted
- cache_clear() resets hits, misses and currsize to 0

## ttl_cache(maxsize, ttl, timer)
A fake clock replaces the real timer, so no test has to wait.
BVA (ttl = 10):
- time 0 -> first call is a miss
- time 9 (just before ttl) -> hit
- time 10 (exactly ttl) -> expired, miss
- time 11 after a recompute at 10 -> hit again
- cache_clear() forces a recompute

## Module level
- Wrapped function keeps its __name__ and has __wrapped__
- lru_cache used without arguments defaults to maxsize 128
- cache_parameters() reports maxsize and typed
- The module exports lru_cache, ttl_cache, fifo_cache, lfu_cache, rr_cache
