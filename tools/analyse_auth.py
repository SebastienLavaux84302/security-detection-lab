#!/usr/bin/env python3
"""Regroupement pédagogique d'événements d'authentification JSONL."""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


def analyse(lines, min_failures=3):
    """Retourner (source, utilisateur, échecs, succès) pour chaque groupe retenu."""
    if min_failures < 1:
        raise ValueError("le seuil doit être supérieur ou égal à 1")

    counts = defaultdict(lambda: {"failure": 0, "success": 0})
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"ligne {number} : JSON invalide") from error
        if not isinstance(record, dict):
            raise ValueError(f"ligne {number} : objet JSON attendu")

        event = record.get("event", {})
        if not isinstance(event, dict):
            raise ValueError(f"ligne {number} : event doit être un objet")
        outcome = event.get("outcome")
        if event.get("action") != "login" or outcome not in ("failure", "success"):
            continue

        source, user = record.get("source"), record.get("user")
        if not isinstance(source, dict) or not isinstance(user, dict):
            raise ValueError(f"ligne {number} : source et user doivent être des objets")
        ip, name = source.get("ip"), user.get("name")
        if not isinstance(ip, str) or not ip or not isinstance(name, str) or not name:
            raise ValueError(f"ligne {number} : source.ip et user.name sont requis")
        counts[(ip, name)][outcome] += 1

    rows = [(ip, name, values["failure"], values["success"])
            for (ip, name), values in counts.items()
            if values["failure"] >= min_failures]
    return sorted(rows, key=lambda row: (-row[2], row[0], row[1]))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path, help="fichier JSONL à analyser")
    parser.add_argument("--min-failures", type=int, default=3,
                        help="seuil minimal d'échecs par groupe (défaut : 3)")
    args = parser.parse_args(argv)
    try:
        with args.file.open(encoding="utf-8") as stream:
            rows = analyse(stream, args.min_failures)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Erreur : {error}", file=sys.stderr)
        return 2

    if not rows:
        print("Aucun groupe n'atteint le seuil.")
        return 0
    print(f"{'Source':<15} {'Utilisateur':<12} {'Échecs':<7} Succès")
    for ip, name, failures, successes in rows:
        print(f"{ip:<15} {name:<12} {failures:<7} {successes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
