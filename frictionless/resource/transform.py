import types
from typing import TYPE_CHECKING
from ..step import Step
from ..system import system
from ..helpers import get_name
from ..exception import FrictionlessException
from .. import errors

if TYPE_CHECKING:
    from .resource import Resource


def transform(resource: "Resource", *, steps):
    """Transform resource

    Parameters:
        steps (Step[]): transform steps

    Returns:
        Resource: the transform result
    """

    # Prepare resource
    resource.infer()

    # Prepare steps
    for index, step in enumerate(steps):
        if not isinstance(step, Step):
            steps[index] = (
                Step(function=step)
                if isinstance(step, types.FunctionType)
                else system.create_step(step)
            )

    # Validate steps
    for step in steps:
        if step.metadata_errors:
            raise FrictionlessException(step.metadata_errors[0])

    # Run transforms
    for step in steps:
        data = resource.data

        # Transform
        try:
            step.transform_resource(resource)
        except Exception as exception:
            error = errors.StepError(note=f'"{get_name(step)}" raises "{exception}"')
            raise FrictionlessException(error) from exception

        # Postprocess
        if resource.data is not data:
            resource.data = DataWithErrorHandling(resource.data, step=step)
            # NOTE:
            # We need rework resource.data or move to resource.__setattr__
            # https://github.com/frictionlessdata/frictionless-py/issues/722
            resource.scheme = ""
            resource.format = "inline"
            dict.pop(resource, "path", None)
            dict.pop(resource, "hashing", None)
            dict.pop(resource, "encoding", None)
            dict.pop(resource, "innerpath", None)
            dict.pop(resource, "compression", None)
            dict.pop(resource, "control", None)
            dict.pop(resource, "dialect", None)
            dict.pop(resource, "layout", None)

    return resource


# Internal


class DataWithErrorHandling:
    def __init__(self, data, *, step):
        self.data = data
        self.step = step

    def __repr__(self):
        return "<transformed-data>"

    def __iter__(self):
        try:
            yield from self.data() if callable(self.data) else self.data
        except Exception as exception:
            if isinstance(exception, FrictionlessException):
                if exception.error.code == "step-error":
                    raise
            error = errors.StepError(note=f'"{get_name(self.step)}" raises "{exception}"')
            raise FrictionlessException(error) from exception
