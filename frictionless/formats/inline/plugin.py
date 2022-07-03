import typing
from ...plugin import Plugin
from .control import InlineControl
from .parser import InlineParser


class InlinePlugin(Plugin):
    """Plugin for Inline"""

    code = "inline"

    # Hooks

    def create_control(self, descriptor):
        if descriptor.get("code") == "inline":
            return InlineControl.from_descriptor(descriptor)

    def create_parser(self, resource):
        if resource.format == "inline":
            return InlineParser(resource)

    def detect_resource(self, resource):
        if resource.data:
            if not hasattr(resource.data, "read"):
                types = (list, typing.Iterator, typing.Generator)
                if callable(resource.data) or isinstance(resource.data, types):
                    resource.scheme = ""
                    resource.format = "inline"