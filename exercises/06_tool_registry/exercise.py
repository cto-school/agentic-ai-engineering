"""Implement the small registry at the centre of the course harness."""


class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, name, schema, handler, capability):
        """Register once; reject duplicate names."""
        raise NotImplementedError("TODO")

    def schemas_for(self, granted_capabilities):
        """Return schemas only for tools whose capability is granted."""
        raise NotImplementedError("TODO")

    def dispatch(self, name, arguments, granted_capabilities):
        """Reject unknown or ungranted tools, otherwise call the handler."""
        raise NotImplementedError("TODO")

