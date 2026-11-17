"""Eigenständigkeit: kein Import aus anderen Demos, Zufall nur über den SplitMix64 der Demo, kein Python-`hash()` und kein `random`-Modul im Rechenkern."""

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOKAL = {p.stem for p in ROOT.glob("*.py")}


def _quellen():
    return sorted(ROOT.glob("*.py"))


def test_jedes_eigene_modul_hat_das_praefix_gdg_oder_ist_die_app():
    assert all(name == "app" or name.startswith("gdg_") for name in LOKAL), sorted(LOKAL)


def test_importe_sind_standardbibliothek_oder_laufzeitpakete_oder_eigene_module():
    erlaubt = {"numpy", "pandas", "plotly", "streamlit"}
    import sys
    fremd = []
    for path in _quellen():
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            namen = []
            if isinstance(node, ast.Import):
                namen = [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
                namen = [node.module.split(".")[0]]
            fremd += [(path.name, n) for n in namen if n not in sys.stdlib_module_names and n not in erlaubt and n not in LOKAL]
    assert not fremd, fremd


def test_kein_hash_und_kein_random_modul_im_rechenkern():
    for path in _quellen():
        text = path.read_text(encoding="utf-8")
        code = "\n".join(line for line in text.splitlines() if not line.strip().startswith("#"))
        assert not re.search(r"(?<![\w.])hash\(", code), path.name
        if path.name != "gdg_presets.py":                      # nur der Zufalls-Knopf der Seitenleiste zieht neue Zufalls-Seeds mit `random`
            assert not re.search(r"^\s*import random\s*$", code, re.M), path.name
