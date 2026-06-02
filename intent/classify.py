"""Working reference intent classifier (shipped for the stretch baseline).

This file is the WORKING reference implementation. The base pipeline you
are extending in this stretch uses this classifier as-is. You may inspect
it freely; modifying it will likely break the baseline regression test.
"""

import re
from enum import Enum


class Intent(Enum):
    """Fixed set of intents the pipeline routes between."""

    FIND_RECIPE = "find_recipe"
    RECIPES_BY_CUISINE = "recipes_by_cuisine"
    RECIPES_BY_INGREDIENT = "recipes_by_ingredient"
    RECIPES_BY_AUTHOR = "recipes_by_author"
    UNKNOWN = "unknown"


_PATTERNS = {
    Intent.RECIPES_BY_AUTHOR: [
        r"\bby\s+(anna|sarah|marco|yuki|raj)\b",
        r"\bauthored\s+by\b",
    ],
    Intent.RECIPES_BY_CUISINE: [
        r"\b(italian|french|thai|mexican|greek|japanese|european|asian|turkish)\b",
        r"\bcuisine\b",
    ],
    Intent.RECIPES_BY_INGREDIENT: [
        r"\bwith\s+\w+\b",
        r"\busing\s+\w+\b",
        r"\b(contain|containing|contains)\b",
    ],
    Intent.FIND_RECIPE: [
        r"\b(find|show|list)\s+recipes?\b",
        r"\brecipes?\b",
    ],
}


def classify(query: str) -> Intent:
    """Return the Intent for ``query``, defaulting to ``Intent.UNKNOWN``."""
    q = query.lower()
    for intent in (
        Intent.RECIPES_BY_AUTHOR,
        Intent.RECIPES_BY_CUISINE,
        Intent.RECIPES_BY_INGREDIENT,
        Intent.FIND_RECIPE,
    ):
        if any(re.search(p, q) for p in _PATTERNS[intent]):
            return intent
    return Intent.UNKNOWN
