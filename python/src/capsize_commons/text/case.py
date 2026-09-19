"""Case conversion for repository, file and symbol naming (§3.1).

Repos and files are ``kebab-case``, Python symbols ``snake_case`` and classes
``PascalCase``. Every project was writing a slightly different ``slugify``;
this is the one they share.
"""

from __future__ import annotations

import re
import unicodedata

__all__ = ["slugify", "to_kebab_case", "to_pascal_case", "to_snake_case"]

#: Split on any run of characters that are not alphanumerics.
_SEPARATORS = re.compile(r"[^0-9A-Za-z]+")
#: Split camelCase / PascalCase / HTTPServer at the correct boundaries.
_CAMEL_BOUNDARY = re.compile(
    r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])"
)


def _to_ascii(text: str) -> str:
    """Fold accents to their closest ASCII spelling."""
    decomposed = unicodedata.normalize("NFKD", text)
    return decomposed.encode("ascii", "ignore").decode("ascii")


def _words(value: str) -> list[str]:
    """Split ``value`` into its alphanumeric words, accents folded."""
    spaced = _CAMEL_BOUNDARY.sub(" ", _to_ascii(value).strip())
    return [word for word in _SEPARATORS.split(spaced) if word]


def slugify(
    value: str, *, separator: str = "-", lowercase: bool = True
) -> str:
    """Join the words of ``value`` with ``separator``.

    >>> slugify("Capsize Persona!")\
    # doctest: +SKIP
    'capsize-persona'
    """
    words = _words(value)
    if lowercase:
        words = [word.lower() for word in words]
    return separator.join(words)


def to_kebab_case(value: str) -> str:
    """Return ``value`` as ``kebab-case`` (the repo/file convention)."""
    return slugify(value, separator="-")


def to_snake_case(value: str) -> str:
    """Return ``value`` as ``snake_case`` (the Python symbol convention)."""
    return slugify(value, separator="_")


def to_pascal_case(value: str) -> str:
    """Return ``value`` as ``PascalCase`` (the class convention)."""
    return "".join(word.capitalize() for word in _words(value))
