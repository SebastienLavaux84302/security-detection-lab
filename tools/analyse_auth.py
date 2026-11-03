#!/usr/bin/env python3
"""Analyse pédagogique d'événements d'authentification JSONL fictifs."""

import argparse
import json
import sys
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path


def iter_events(lines):
    """Lire les événements login pris en charge en conservant leur ligne."""
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
        yield number, ip, name, outcome, record.get("@timestamp")


def analyse(lines, min_failures=3):
    """Retourner les totaux par source et utilisateur sur tout le fichier."""
    if min_failures < 1:
        raise ValueError("le seuil doit être supérieur ou égal à 1")

    counts = defaultdict(lambda: {"failure": 0, "success": 0})
    for _, ip, name, outcome, _ in iter_events(lines):
        counts[(ip, name)][outcome] += 1

    rows = [(ip, name, values["failure"], values["success"])
            for (ip, name), values in counts.items()
            if values["failure"] >= min_failures]
    return sorted(rows, key=lambda row: (-row[2], row[0], row[1]))


def parse_timestamp(value, number):
    """Accepter une date ISO 8601 avec fuseau explicite et la convertir en UTC."""
    if not isinstance(value, str) or not value:
        raise ValueError(f"ligne {number} : @timestamp avec fuseau requis")
    try:
        # Le suffixe Z est aussi accepté sur Python 3.10.
        timestamp = datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
        if timestamp.utcoffset() is None:
            raise ValueError("fuseau absent")
        return timestamp.astimezone(timezone.utc)
    except (ValueError, OverflowError) as error:
        raise ValueError(f"ligne {number} : @timestamp invalide ou sans fuseau") from error


@dataclass(frozen=True)
class Burst:
    source: str
    user: str
    first: datetime
    last: datetime
    failures: int


def detect_bursts(lines, min_failures=3, window_minutes=10):
    """Premier franchissement du seuil par groupe dans une fenêtre glissante.

    La borne gauche est incluse. Tous les échecs sont triés par date avant
    analyse : ce prototype conserve donc le fichier en mémoire.
    """
    if min_failures < 1:
        raise ValueError("le seuil doit être supérieur ou égal à 1")
    if window_minutes < 1:
        raise ValueError("la fenêtre doit être d'au moins une minute")

    events = []
    for number, ip, name, outcome, timestamp in iter_events(lines):
        if outcome == "failure":
            events.append((parse_timestamp(timestamp, number), ip, name))
    events.sort()

    try:
        window = timedelta(minutes=window_minutes)
    except OverflowError as error:
        raise ValueError("la fenêtre est trop grande") from error
    pending = defaultdict(deque)
    alerted = set()
    bursts = []
    for timestamp, ip, name in events:
        group = (ip, name)
        if group in alerted:
            continue
        recent = pending[group]
        while recent and timestamp - recent[0] > window:
            recent.popleft()
        recent.append(timestamp)
        if len(recent) >= min_failures:
            bursts.append(Burst(ip, name, recent[0], timestamp, len(recent)))
            alerted.add(group)
    return bursts


def utc_text(timestamp):
    return timestamp.isoformat().replace("+00:00", "Z")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path, help="fichier JSONL à analyser")
    parser.add_argument("--min-failures", type=int, default=3,
                        help="seuil minimal d'échecs par groupe (défaut : 3)")
    parser.add_argument("--window-minutes", type=int,
                        help="fenêtre glissante en minutes ; sans option : totaux du fichier")
    args = parser.parse_args(argv)
    try:
        with args.file.open(encoding="utf-8") as stream:
            if args.window_minutes is None:
                rows = analyse(stream, args.min_failures)
            else:
                rows = detect_bursts(stream, args.min_failures, args.window_minutes)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Erreur : {error}", file=sys.stderr)
        return 2

    if not rows:
        print("Aucun groupe n'atteint le seuil.")
        return 0
    if args.window_minutes is None:
        print(f"{'Source':<15} {'Utilisateur':<12} {'Échecs':<7} Succès")
        for ip, name, failures, successes in rows:
            print(f"{ip:<15} {name:<12} {failures:<7} {successes}")
    else:
        print("Source          Utilisateur  Premier échec (UTC)  Seuil atteint (UTC)  Échecs")
        for burst in rows:
            print(f"{burst.source:<15} {burst.user:<12} {utc_text(burst.first)} "
                  f"{utc_text(burst.last)} {burst.failures}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
