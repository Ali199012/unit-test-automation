import pytest
from cachetools import keys
from cachetools.keys import hashkey, typedkey


# ------------------------------------------------------------------ hashkey

def test_hashkey_empty_args_gives_empty_tuple():
    assert hashkey() == ()


def test_hashkey_positional_args_match_plain_tuple():
    assert hashkey(1, 2) == (1, 2)


def test_hashkey_same_args_are_equal():
    assert hashkey("a", 5) == hashkey("a", 5)


def test_hashkey_argument_order_matters():
    assert hashkey(1, 2) != hashkey(2, 1)


def test_hashkey_keyword_order_is_ignored():
    assert hashkey(a=1, b=2) == hashkey(b=2, a=1)


def test_hashkey_positional_differs_from_keyword():
    assert hashkey(1) != hashkey(a=1)


def test_hashkey_int_and_float_are_equal():
    assert hashkey(1) == hashkey(1.0)


def test_hashkey_str_and_int_differ():
    assert hashkey("1") != hashkey(1)


def test_hashkey_unhashable_arg_raises_typeerror():
    with pytest.raises(TypeError):
        hash(hashkey([1, 2]))


# ----------------------------------------------------------------- typedkey

def test_typedkey_empty_args_gives_empty_tuple():
    assert typedkey() == ()


def test_typedkey_adds_the_argument_types():
    assert typedkey(1, "a") == (1, "a", int, str)


def test_typedkey_int_and_float_differ():
    assert typedkey(1) != typedkey(1.0)


def test_typedkey_bool_and_int_differ():
    assert typedkey(True) != typedkey(1)


def test_typedkey_same_args_are_equal():
    assert typedkey(1, "a") == typedkey(1, "a")


def test_typedkey_argument_order_matters():
    assert typedkey(1, "a") != typedkey("a", 1)


def test_typedkey_keyword_order_is_ignored():
    assert typedkey(a=1, b="x") == typedkey(b="x", a=1)


# ------------------------------------------------------------- module level

def test_keys_hash_is_an_int():
    assert isinstance(hash(hashkey(1, 2)), int)


def test_keys_equal_keys_have_equal_hashes():
    assert hash(hashkey(1, 2)) == hash(hashkey(1, 2))


def test_keys_hashkey_works_as_dict_key():
    assert {hashkey(1, 2): "x"}[hashkey(1, 2)] == "x"


def test_keys_hashkey_merges_int_and_float_in_a_dict():
    assert len({hashkey(1): "a", hashkey(1.0): "b"}) == 1


def test_keys_typedkey_separates_int_and_float_in_a_dict():
    assert len({typedkey(1): "a", typedkey(1.0): "b"}) == 2


@pytest.mark.parametrize("name", ["hashkey", "typedkey", "methodkey", "typedmethodkey"])
def test_keys_module_exports_function(name):
    assert hasattr(keys, name)
