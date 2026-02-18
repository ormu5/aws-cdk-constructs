import functools
import re
from typing import Type, TypeVar, Any

T = TypeVar("T")

def pascal_to_kebab(pascal_case: str) -> str:
    """Convert PascalCase to kebab-case, supports canonical resource naming."""
    # Use regular expression to find words in PascalCase
    words = re.findall(r"[A-Z]+(?=[A-Z][a-z0-9])|[A-Z][a-z0-9]*", pascal_case)

    return "-".join(words).lower()

def inject_canonical_id(cls: Type[T]) -> Type[T]:
    """
    Class decorator that injects a default `id_` kwarg into __init__
    if the caller didn't supply one.

    Canonical value is derived from the class name.
    """
    original_init = cls.__init__

    @functools.wraps(original_init)
    def __init__(self, scope, *args: Any, **kwargs: Any) -> None:
        # If caller already provided an id (positional), leave it alone.
        if args:
            return original_init(self, scope, *args, **kwargs)

        canonical_id = pascal_to_kebab(cls.__name__)
        return original_init(self, scope, canonical_id, *args, **kwargs)

    cls.__init__ = __init__
    return cls