import pytest
import datetime
from frictionless import Package, Resource, FrictionlessException
from frictionless.plugins.ckan import CkanStorage, CkanDialect


# General


@pytest.mark.vcr
def test_ckan_parser(options):
    url = options.pop("url")
    dialect = CkanDialect(resource="table", **options)
    source = Resource("data/table.csv")
    target = source.write(url, format="ckan", dialect=dialect)
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


@pytest.mark.vcr
def test_ckan_parser_timezone(options):
    url = options.pop("url")
    dialect = CkanDialect(resource="timezone", **options)
    source = Resource("data/timezone.csv")
    target = source.write(url, format="ckan", dialect=dialect)
    with target:
        assert target.read_rows() == [
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
            {"datetime": datetime.datetime(2020, 1, 1, 15), "time": datetime.time(15)},
        ]


# Storage


@pytest.mark.vcr
def test_ckan_storage_types(options):
    url = options.pop("url")
    dialect = CkanDialect(**options)
    source = Package("data/storage/types.json")
    storage = source.to_ckan(url, dialect=dialect)
    target = Package.from_ckan(url, dialect=dialect)

    # Assert metadata
    assert target.get_resource("types").schema == {
        "fields": [
            {"name": "any", "type": "string"},  # type fallback
            {"name": "array", "type": "array"},
            {"name": "boolean", "type": "boolean"},
            {"name": "date", "type": "string"},  # type fallback
            {"name": "date_year", "type": "string"},  # type fallback
            {"name": "datetime", "type": "datetime"},
            {"name": "duration", "type": "string"},  # type fallback
            {"name": "geojson", "type": "object"},  # type downgrade
            {"name": "geopoint", "type": "string"},  # type fallback
            {"name": "integer", "type": "integer"},
            {"name": "number", "type": "number"},
            {"name": "object", "type": "object"},
            {"name": "string", "type": "string"},
            {"name": "time", "type": "time"},
            {"name": "year", "type": "integer"},  # type downgrade
            {"name": "yearmonth", "type": "string"},  # type fallback
        ],
    }

    # Assert data
    assert target.get_resource("types").read_rows() == [
        {
            "any": "中国人",
            "array": ["Mike", "John"],
            "boolean": True,
            "date": "2015-01-01",
            "date_year": "2015",
            "datetime": datetime.datetime(2015, 1, 1, 3, 0),
            "duration": "P1Y1M",
            "geojson": {"type": "Point", "coordinates": [33, 33.33]},
            "geopoint": "30,70",
            "integer": 1,
            "number": 7,
            "object": {"chars": 560},
            "string": "english",
            "time": datetime.time(3, 0),
            "year": 2015,
            "yearmonth": "2015-01",
        },
    ]

    # Cleanup storage
    storage.delete_package(target.resource_names)


@pytest.mark.vcr
def test_ckan_storage_integrity(options):
    url = options.pop("url")
    dialect = CkanDialect(**options)
    source = Package("data/storage/integrity.json")
    storage = source.to_ckan(url, dialect=dialect)
    target = Package.from_ckan(url, dialect=dialect)

    # Assert metadata (main)
    assert target.get_resource("integrity_main").schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "parent", "type": "integer"},
            {"name": "description", "type": "string"},
        ],
        # primary key removal
        # foreign keys removal
    }

    # Assert metadata (link)
    assert target.get_resource("integrity_link").schema == {
        "fields": [
            {"name": "main_id", "type": "integer"},
            {"name": "some_id", "type": "integer"},  # constraint removal
            {"name": "description", "type": "string"},  # constraint removal
        ],
        # primary key removal
        # foreign keys removal
    }

    # Assert data (main)
    assert target.get_resource("integrity_main").read_rows() == [
        {"id": 1, "parent": None, "description": "english"},
        {"id": 2, "parent": 1, "description": "中国人"},
    ]

    # Assert data (link)
    assert target.get_resource("integrity_link").read_rows() == [
        {"main_id": 1, "some_id": 1, "description": "note1"},
        {"main_id": 2, "some_id": 2, "description": "note2"},
    ]

    # Cleanup storage
    storage.delete_package(target.resource_names)


@pytest.mark.vcr
def test_ckan_storage_constraints(options):
    url = options.pop("url")
    dialect = CkanDialect(**options)
    source = Package("data/storage/constraints.json")
    storage = source.to_ckan(url, dialect=dialect)
    target = Package.from_ckan(url, dialect=dialect)

    # Assert metadata
    assert target.get_resource("constraints").schema == {
        "fields": [
            {"name": "required", "type": "string"},  # constraint removal
            {"name": "minLength", "type": "string"},  # constraint removal
            {"name": "maxLength", "type": "string"},  # constraint removal
            {"name": "pattern", "type": "string"},  # constraint removal
            {"name": "enum", "type": "string"},  # constraint removal
            {"name": "minimum", "type": "integer"},  # constraint removal
            {"name": "maximum", "type": "integer"},  # constraint removal
        ],
    }

    # Assert data
    assert target.get_resource("constraints").read_rows() == [
        {
            "required": "passing",
            "minLength": "passing",
            "maxLength": "passing",
            "pattern": "passing",
            "enum": "passing",
            "minimum": 5,
            "maximum": 5,
        },
    ]

    # Cleanup storage
    storage.delete_package(target.resource_names)


@pytest.mark.vcr
def test_ckan_storage_not_existent_error(options):
    url = options.pop("url")
    dialect = CkanDialect(**options)
    storage = CkanStorage(url, dialect=dialect)
    with pytest.raises(FrictionlessException) as excinfo:
        storage.read_resource("bad")
    error = excinfo.value.error
    assert error.code == "storage-error"
    assert error.note.count("does not exist")


@pytest.mark.vcr
def test_ckan_storage_write_resource_existent_error(options):
    url = options.pop("url")
    dialect = CkanDialect(**options)
    storage = CkanStorage(url, dialect=dialect)
    resource = Resource(path="data/table.csv")
    storage.write_resource(resource, force=True)
    with pytest.raises(FrictionlessException) as excinfo:
        storage.write_resource(resource)
    error = excinfo.value.error
    assert error.code == "storage-error"
    assert error.note.count("already exists")
    # Cleanup storage
    storage.delete_package(list(storage))


@pytest.mark.vcr
def test_ckan_storage_delete_resource_not_existent_error(options):
    url = options.pop("url")
    dialect = CkanDialect(**options)
    storage = CkanStorage(url, dialect=dialect)
    with pytest.raises(FrictionlessException) as excinfo:
        storage.delete_resource("bad")
    error = excinfo.value.error
    assert error.code == "storage-error"
    assert error.note.count("does not exist")
