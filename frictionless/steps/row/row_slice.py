from typing import Optional
from dataclasses import dataclass
from ...pipeline import Step


# NOTE:
# We need to review simpleeval perfomance for using it with row_filter
# Currently, metadata profiles are not fully finished; will require improvements


@dataclass
class row_slice(Step):
    """Slice rows"""

    code = "row-slice"

    # Properties

    start: Optional[int] = None
    """TODO: add docs"""

    stop: Optional[int] = None
    """TODO: add docs"""

    step: Optional[int] = None
    """TODO: add docs"""

    head: Optional[int] = None
    """TODO: add docs"""

    tail: Optional[int] = None
    """TODO: add docs"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        if self.head:
            resource.data = table.head(self.head)  # type: ignore
        elif self.tail:
            resource.data = table.tail(self.tail)  # type: ignore
        else:
            resource.data = table.rowslice(self.start, self.stop, self.step)  # type: ignore

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": [],
        "properties": {
            "code": {},
            "start": {},
            "stop": {},
            "step": {},
            "head": {},
            "tail": {},
        },
    }