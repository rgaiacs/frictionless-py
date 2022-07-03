import pytest
from frictionless import validate


# General


def test_validate_inquiry():
    report = validate({"tasks": [{"path": "data/table.csv"}]})
    assert report.valid


def test_validate_inquiry_multiple():
    report = validate(
        {
            "tasks": [
                {"path": "data/table.csv"},
                {"path": "data/matrix.csv"},
            ]
        },
    )
    assert report.valid


def test_validate_inquiry_multiple_invalid():
    report = validate(
        {
            "tasks": [
                {"path": "data/table.csv"},
                {"path": "data/invalid.csv"},
            ]
        },
    )
    assert report.flatten(["taskPosition", "rowPosition", "fieldPosition", "code"]) == [
        [2, None, 3, "blank-label"],
        [2, None, 4, "duplicate-label"],
        [2, 2, 3, "missing-cell"],
        [2, 2, 4, "missing-cell"],
        [2, 3, 3, "missing-cell"],
        [2, 3, 4, "missing-cell"],
        [2, 4, None, "blank-row"],
        [2, 5, 5, "extra-cell"],
    ]


def test_validate_inquiry_multiple_invalid_limit_errors():
    report = validate(
        {
            "tasks": [
                {"path": "data/table.csv"},
                {"path": "data/invalid.csv", "checklist": {"limitErrors": 1}},
            ]
        },
    )
    assert report.flatten(["taskPosition", "code", "note"]) == [
        [2, "blank-label", ""],
    ]
    assert report.tasks[0].flatten(["rowPosition", "fieldPosition", "code"]) == []
    assert report.tasks[1].flatten(["rowPosition", "fieldPosition", "code"]) == [
        [None, 3, "blank-label"],
    ]


def test_validate_inquiry_multiple_invalid_with_schema():
    report = validate(
        {
            "tasks": [
                {
                    "path": "data/table.csv",
                    "schema": {"fields": [{"name": "bad"}, {"name": "name"}]},
                },
                {"path": "data/invalid.csv"},
            ],
        },
    )
    assert report.flatten(["taskPosition", "rowPosition", "fieldPosition", "code"]) == [
        [1, None, 1, "incorrect-label"],
        [2, None, 3, "blank-label"],
        [2, None, 4, "duplicate-label"],
        [2, 2, 3, "missing-cell"],
        [2, 2, 4, "missing-cell"],
        [2, 3, 3, "missing-cell"],
        [2, 3, 4, "missing-cell"],
        [2, 4, None, "blank-row"],
        [2, 5, 5, "extra-cell"],
    ]


def test_validate_inquiry_with_one_resource_from_descriptor():
    report = validate(
        {
            "tasks": [
                {"descriptor": "data/resource.json"},
            ]
        },
    )
    assert report.valid


def test_validate_inquiry_with_one_package_from_descriptor():
    report = validate(
        {
            "tasks": [
                {"descriptor": "data/package/datapackage.json"},
            ]
        },
    )
    assert report.valid


def test_validate_inquiry_with_multiple_packages():
    report = validate(
        {
            "tasks": [
                {"descriptor": "data/package/datapackage.json"},
                {"descriptor": "data/invalid/datapackage.json"},
            ]
        },
    )
    assert report.flatten(["taskPosition", "rowPosition", "fieldPosition", "code"]) == [
        [3, 3, None, "blank-row"],
        [3, 3, None, "primary-key"],
        [4, 4, None, "blank-row"],
    ]


# Parallel


@pytest.mark.ci
def test_validate_inquiry_parallel_multiple():
    report = validate(
        {
            "tasks": [
                {"path": "data/table.csv"},
                {"path": "data/matrix.csv"},
            ]
        },
        parallel=True,
    )
    assert report.valid


@pytest.mark.ci
def test_validate_inquiry_parallel_multiple_invalid():
    report = validate(
        {
            "tasks": [
                {"path": "data/table.csv"},
                {"path": "data/invalid.csv"},
            ]
        },
        parallel=True,
    )
    assert report.flatten(["taskPosition", "rowPosition", "fieldPosition", "code"]) == [
        [2, None, 3, "blank-label"],
        [2, None, 4, "duplicate-label"],
        [2, 2, 3, "missing-cell"],
        [2, 2, 4, "missing-cell"],
        [2, 3, 3, "missing-cell"],
        [2, 3, 4, "missing-cell"],
        [2, 4, None, "blank-row"],
        [2, 5, 5, "extra-cell"],
    ]


@pytest.mark.ci
def test_validate_inquiry_with_multiple_packages_with_parallel():
    report = validate(
        {
            "tasks": [
                {"descriptor": "data/package/datapackage.json"},
                {"descriptor": "data/invalid/datapackage.json"},
            ]
        },
        parallel=True,
    )
    assert report.flatten(["taskPosition", "rowPosition", "fieldPosition", "code"]) == [
        [3, 3, None, "blank-row"],
        [3, 3, None, "primary-key"],
        [4, 4, None, "blank-row"],
    ]