class ResourceNotFound(BaseException):
    """
    Exception raised when a resource is not found.
    """


class FlavorNotFound(ResourceNotFound):
    """
    Exception raised when a flavor is not found.
    """

    def __init__(self, flavor_name: str, available_flavors: list[str] = None):
        _msg: str = f"Flavor '{flavor_name}' not found."
        if available_flavors is not None:
            _msg += f"\nAvailable flavors: {', '.join(available_flavors)}"
        super().__init__(_msg)


class K8sVersionNotFound(ResourceNotFound):
    """
    Exception raised when a Kubernetes version is not found.
    """

    def __init__(self, version: str, available_versions: list[str] = None):
        _msg: str = f"Kubernetes version '{version}' not found."
        if available_versions is not None:
            _msg += f"\nAvailable versions: {', '.join(available_versions)}"
        super().__init__(_msg)


class StorageBaseError(Exception): ...


class ContextNotFound(StorageBaseError):
    """
    Exception raised when a context is not found.
    """

    def __init__(self, context_name: str, available_contexts: list[str] = None):
        _msg: str = f"Context '{context_name}' not found."
        if available_contexts is not None:
            _msg += f"\nAvailable contexts: {', '.join(available_contexts)}"
        super().__init__(_msg)


class EmptyStorage(StorageBaseError): ...


class InvalidFileLayout(StorageBaseError):
    """
    Exception raised when a file format is invalid.
    """

    def __init__(self, file_path: str):
        super().__init__(f"Invalid file layout for '{file_path}'.")


class NoActiveSession(BaseException):
    """No active session found."""
