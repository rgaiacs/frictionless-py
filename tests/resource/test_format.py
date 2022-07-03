import pytest
from frictionless import Resource, FrictionlessException


# General


def test_resource_format_csv():
    with Resource("data/table.csv") as resource:
        assert resource.format == "csv"


@pytest.mark.skip
def test_resource_format_ndjson():
    with Resource("data/table.ndjson") as resource:
        assert resource.format == "ndjson"


def test_resource_format_tsv():
    with Resource("data/table.tsv") as resource:
        assert resource.format == "tsv"


def test_resource_format_xls():
    with Resource("data/table.xls") as resource:
        assert resource.format == "xls"


def test_resource_format_xlsx():
    with Resource("data/table.xlsx") as resource:
        assert resource.format == "xlsx"


@pytest.mark.skip
def test_resource_format_error_non_matching_format():
    resource = Resource("data/table.csv", format="xlsx")
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.code == "format-error"
    assert error.note == 'invalid excel file "data/table.csv"'