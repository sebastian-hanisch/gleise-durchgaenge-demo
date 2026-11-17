"""Rechnet die vorgerechneten Tabellen neu (data/gdg_tables.json).

    python tools/gdg_make_tables.py            # schreibt data/gdg_tables.json (etwa 2 bis 4 Minuten)
    python tools/gdg_make_tables.py --check    # rechnet neu und vergleicht mit der Datei; Exit 1 bei Abweichung

Alle Zahlen sind Zähler aus ganzen Zahlen (SplitMix64, Aufzählung): auf jeder Plattform dieselben Werte."""

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import gdg_tables as T  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="neu rechnen und mit data/gdg_tables.json vergleichen")
    args = parser.parse_args()
    t0 = time.time()
    fresh = T.make_all()
    print(f"neu gerechnet in {time.time() - t0:.0f} s")
    if args.check:
        stored = T.load()
        # JSON kennt keine Tupel: durch einen Hin- und Rückweg vergleichbar machen
        same = json.loads(json.dumps(fresh)) == stored
        print("data/gdg_tables.json stimmt mit der Neuberechnung überein" if same else "ABWEICHUNG zwischen data/gdg_tables.json und der Neuberechnung")
        return 0 if same else 1
    T.DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(T.DATA_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(fresh, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    print(f"geschrieben: {T.DATA_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
