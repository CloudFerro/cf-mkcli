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
