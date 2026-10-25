import pytest

# Execution order of the groups (files). Tests inside a file keep their written order.
ORDER = ["test_lru_mine", "test_keys_mine", "test_func_mine", "test_csv_mine"]

# Every test file belongs to one group (marker).
GROUPS = {
    "test_lru_mine": "lru",
    "test_keys_mine": "keys",
    "test_func_mine": "func",
    "test_csv_mine": "datadriven",
}

# Tests whose name has one of these words are also put in the "boundary" group.
BOUNDARY_WORDS = ("maxsize", "empty", "single", "zero", "limit", "exactly", "clear", "expire", "ttl")


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items):
    for item in items:
        stem = item.path.stem
        if stem in GROUPS:
            item.add_marker(getattr(pytest.mark, GROUPS[stem]))
        name = item.name.lower()
        if any(word in name for word in BOUNDARY_WORDS):
            item.add_marker(pytest.mark.boundary)
        if "raises" in name:
            item.add_marker(pytest.mark.negative)
    items.sort(key=lambda i: ORDER.index(i.path.stem) if i.path.stem in ORDER else len(ORDER))
