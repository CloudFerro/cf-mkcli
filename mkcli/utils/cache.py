import shelve
from typing import Any
from functools import wraps
from pathlib import Path
from mkcli.settings import APP_SETTINGS
from loguru import logger


CACHE_STORAGE_PATH = Path(f"{APP_SETTINGS.cache_dir}/shelve")


def ensure_path_exists(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def save(key: str, _object: Any) -> None:
    """Save data to a shelve file."""
    logger.info(f"Saving object with key '{key}' to cache.")
    ensure_path_exists(CACHE_STORAGE_PATH.parent)
    with shelve.open(str(CACHE_STORAGE_PATH), writeback=True) as _dict:
        _dict[key] = _object


def load(key: str) -> Any:
    """Load data from a shelve file."""
    logger.info(f"Loading object with key '{key}' to cache.")
    with shelve.open(str(CACHE_STORAGE_PATH)) as _dict:
        return _dict[key] if key in _dict else None


def cache(enabled: bool = APP_SETTINGS.resource_mappings_cache) -> callable:
    """Decorator to cache the result of a function for a specified time."""
    # TODO(EA): Implement a time-based cache invalidation mechanism

    def decorator(func):
        if not enabled:
            return func

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Implement caching logic here
            args_str = ",".join(map(str, args))
            cache_key = f"{func.__name__}_{args_str}_{kwargs}"
            cached = load(cache_key)

            if cached is not None:
                logger.info(f"Using cached result for key '{cache_key}'.")
                return cached
            result = func(*args, **kwargs)
            save(cache_key, result)
            return result

        return wrapper

    return decorator
