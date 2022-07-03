from dataclasses import dataclass
from typing import Optional, List
from ...dialect import Control


@dataclass
class CkanControl(Control):
    """Ckan control representation"""

    code = "ckan"

    # State

    dataset: str
    """TODO: add docs"""

    resource: Optional[str] = None
    """TODO: add docs"""

    apikey: Optional[str] = None
    """TODO: add docs"""

    fields: Optional[List[str]] = None
    """TODO: add docs"""

    limit: Optional[int] = None
    """TODO: add docs"""

    sort: Optional[str] = None
    """TODO: add docs"""

    filters: Optional[dict] = None
    """TODO: add docs"""

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["dataset"],
        "additionalProperties": False,
        "properties": {
            "code": {},
            "resource": {"type": "string"},
            "dataset": {"type": "string"},
            "apikey": {"type": "string"},
            "fields": {"type": "array"},
            "limit": {"type": "integer"},
            "sort": {"type": "string"},
            "filters": {"type": "object"},
        },
    }