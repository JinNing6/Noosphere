# Noosphere SDK
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from noosphere.client import Noosphere

__all__ = ["Noosphere"]
__version__ = "0.10.0"


def __getattr__(name: str):
    """Load the HTTP client only when the public SDK export is requested."""
    if name != "Noosphere":
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    from noosphere.client import Noosphere

    globals()[name] = Noosphere
    return Noosphere


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
