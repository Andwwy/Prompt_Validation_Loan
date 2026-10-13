"""Taxonomy package exports"""

from src.taxonomy.statutes import STATUTORY_FRAMEWORK
from src.taxonomy.protected_vars import PROTECTED_VARIABLES_CONFIG
from src.taxonomy.violations import VIOLATION_DEFINITIONS

__all__ = [
    "STATUTORY_FRAMEWORK",
    "PROTECTED_VARIABLES_CONFIG",
    "VIOLATION_DEFINITIONS",
]
