"""Gemeinsame Fixtures und der Marker `slow` (nur mit GDG_SLOW=1; ein vollständiger Lauf aller langsamen Tests dauert einige Minuten)."""

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: langsame Orakel-Läufe (nur mit Umgebungsvariable GDG_SLOW=1)")


def pytest_collection_modifyitems(config, items):
    if os.environ.get("GDG_SLOW") == "1":
        return
    skip = pytest.mark.skip(reason="langsam: GDG_SLOW=1 setzen")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip)


@pytest.fixture
def handbeispiel():
    """Der Zug (2, 4, 6, 1, 3, 5) von Hand: steigende Folgen {1}, {2, 3}, {4, 5}, {6}, also R = 4; mit 2 Gleisen 2 Durchgänge, Radix ⌈log₂ 6⌉ = 3."""
    return (2, 4, 6, 1, 3, 5)
