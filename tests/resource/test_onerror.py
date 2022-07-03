import pytest
from frictionless import Resource, FrictionlessException


# General


def test_resource_onerror():
    resource = Resource(path="data/invalid.csv")
    assert resource.onerror == "ignore"
    assert resource.read_rows()


@pytest.mark.skip
def test_resource_onerror_header_warn():
    data = [["name"], [1], [2], [3]]
    schema = {"fields": [{"name": "bad", "type": "integer"}]}
    resource = Resource(data=data, schema=schema, onerror="warn")
    assert resource.onerror == "warn"
    with pytest.warns(UserWarning):
        resource.read_rows()


@pytest.mark.skip
def test_resource_onerror_header_raise():
    data = [["name"], [1], [2], [3]]
    schema = {"fields": [{"name": "bad", "type": "integer"}]}
    resource = Resource(data=data, schema=schema, onerror="raise")
    assert resource.onerror == "raise"
    with pytest.raises(FrictionlessException):
        resource.read_rows()


@pytest.mark.skip
def test_resource_onerror_row_warn():
    data = [["name"], [1], [2], [3]]
    schema = {"fields": [{"name": "name", "type": "string"}]}
    resource = Resource(data=data, schema=schema, onerror="warn")
    assert resource.onerror == "warn"
    with pytest.warns(UserWarning):
        resource.read_rows()


@pytest.mark.skip
def test_resource_onerror_row_raise():
    data = [["name"], [1], [2], [3]]
    schema = {"fields": [{"name": "name", "type": "string"}]}
    resource = Resource(data=data, schema=schema, onerror="raise")
    assert resource.onerror == "raise"
    with pytest.raises(FrictionlessException):
        resource.read_rows()