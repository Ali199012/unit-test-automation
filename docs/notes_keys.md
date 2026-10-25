# Notes: cachetools.keys (hashkey, typedkey)

Behaviour was checked by running the functions by hand first.

## hashkey(*args, **kwargs)
ECP:
- Valid input: no args, positional args, keyword args, mixed types
- Invalid input: an unhashable argument (list) -> TypeError when hashed
BVA / edge cases:
- Zero arguments -> empty tuple
- One argument vs two arguments
- Argument order matters: (1, 2) differs from (2, 1)
- Keyword order does not matter
- Positional 1 differs from keyword a=1
- 1 and 1.0 give equal keys (this is the weak point typedkey fixes)
- "1" and 1 give different keys

## typedkey(*args, **kwargs)
ECP:
- Same values and same types -> equal keys
- Same value, different type (1 vs 1.0, True vs 1) -> different keys
BVA / edge cases:
- Zero arguments -> empty tuple
- Result contains the values followed by their types: (1, "a", int, str)
- Argument order matters, keyword order does not

## Module level
- Keys are hashable and the hash is an int
- Equal keys have equal hashes, so they work as dict keys
- hashkey merges 1 and 1.0 in a dict (1 entry), typedkey keeps them apart (2 entries)
- The module exports hashkey, typedkey, methodkey, typedmethodkey
