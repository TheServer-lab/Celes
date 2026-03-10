"""
Celes 0.1 — A tag-based markup language.
"""

from .parser import parse_celes
from .validator import validate_celes, CelesError
from .md_to_celes import convert_md_to_celes
from .celes_to_md import convert_celes_to_md

__version__ = "0.1.1"
__all__ = [
    "parse_celes",
    "validate_celes",
    "CelesError",
    "convert_md_to_celes",
    "convert_celes_to_md",
]
