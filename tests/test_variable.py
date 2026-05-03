from app.variable import is_valid_identifier

def test_is_valid_identifier():
    assert is_valid_identifier("foo")
    assert is_valid_identifier("foo_bar")
    assert is_valid_identifier("_foo")
    assert not is_valid_identifier("1foo")
    assert not is_valid_identifier("foo-bar")
    assert not is_valid_identifier("pear-mango")
