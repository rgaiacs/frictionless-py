from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Protocol, BinaryIO, TextIO, Iterable, List, Dict, Any, Union, Literal

if TYPE_CHECKING:
    from .table import Row
    from .error import Error
    from .package import Package
    from .resource import Resource


# General


IDescriptor = Dict[str, Any]
IDescriptorSource = Union[str, dict]
IByteStream = BinaryIO
ITextStream = TextIO
IListStream = Iterable[List[Any]]
IBuffer = bytes
ISample = List[List[Any]]
IOnerror = Literal["ignore", "warn", "raise"]


# Functions


class ICheckFunction(Protocol):
    def __call__(self, row: Row) -> Iterable[Error]:
        ...


class IEncodingFunction(Protocol):
    def __call__(self, buffer: IBuffer) -> str:
        ...


class IFilterFunction(Protocol):
    def __call__(self, row: Row) -> bool:
        ...


class IProcessFunction(Protocol):
    def __call__(self, row: Row) -> Iterable[Any]:
        ...


class IStepFunction(Protocol):
    def __call__(self, source: Union[Resource, Package]) -> None:
        ...