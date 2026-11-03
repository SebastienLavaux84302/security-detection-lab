import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from analyse_auth import analyse, detect_bursts, utc_text


def event(outcome, ip="192.0.2.10", name="alice", action="login", timestamp=None):
    return json.dumps({"@timestamp": timestamp,
                       "event": {"action": action, "outcome": outcome},
                       "source": {"ip": ip}, "user": {"name": name}})


class AnalyseAuthTests(unittest.TestCase):
    def test_groupes_et_seuil(self):
        lines = [event("failure"), event("failure"), event("success"),
                 event("failure", ip="198.51.100.7"), event("failure", action="logout")]
        self.assertEqual(analyse(lines, 2), [("192.0.2.10", "alice", 2, 1)])

    def test_json_invalide_avec_numero_de_ligne(self):
        with self.assertRaisesRegex(ValueError, "ligne 2 : JSON invalide"):
            analyse([event("failure"), "{invalid}"])

    def test_champ_requis_absent(self):
        with self.assertRaisesRegex(ValueError, "source.ip et user.name"):
            analyse(['{"event":{"action":"login","outcome":"failure"},'
                     '"source":{},"user":{"name":"alice"}}'])

    def test_seuil_invalide(self):
        with self.assertRaisesRegex(ValueError, "seuil"):
            analyse([], 0)


class FenetresTests(unittest.TestCase):
    def test_borne_incluse_et_tri_chronologique(self):
        lines = [event("failure", timestamp="2026-01-10T10:10:00Z"),
                 event("failure", timestamp="2026-01-10T10:00:00Z"),
                 event("failure", timestamp="2026-01-10T10:05:00Z")]
        burst, = detect_bursts(lines, 3, 10)
        self.assertEqual((burst.source, burst.user, burst.failures), ("192.0.2.10", "alice", 3))
        self.assertEqual(utc_text(burst.first), "2026-01-10T10:00:00Z")
        self.assertEqual(utc_text(burst.last), "2026-01-10T10:10:00Z")

    def test_echec_hors_fenetre_et_succes_ignores(self):
        lines = [event("failure", timestamp="2026-01-10T10:00:00Z"),
                 event("failure", timestamp="2026-01-10T10:05:00Z"),
                 event("success"),
                 event("failure", timestamp="2026-01-10T10:10:01Z")]
        self.assertEqual(detect_bursts(lines, 3, 10), [])

    def test_fuseaux_convertis_en_utc(self):
        lines = [event("failure", timestamp="2026-01-10T11:00:00+01:00"),
                 event("failure", timestamp="2026-01-10T10:02:00Z")]
        burst, = detect_bursts(lines, 2, 3)
        self.assertEqual(utc_text(burst.first), "2026-01-10T10:00:00Z")

    def test_un_seul_resultat_par_couple_source_utilisateur(self):
        lines = [event("failure", timestamp=f"2026-01-10T10:0{i}:00Z") for i in range(4)]
        lines += [event("failure", name="bob", timestamp=f"2026-01-10T10:0{i}:00Z")
                  for i in range(2)]
        rows = detect_bursts(lines, 2, 10)
        self.assertEqual([(row.user, row.failures) for row in rows], [("alice", 2), ("bob", 2)])
        self.assertEqual(utc_text(rows[0].last), "2026-01-10T10:01:00Z")

    def test_date_absente_invalide_ou_sans_fuseau(self):
        for timestamp in [None, "invalide", "2026-01-10T10:00:00"]:
            with self.subTest(timestamp=timestamp):
                with self.assertRaisesRegex(ValueError, "ligne 2 : @timestamp"):
                    detect_bursts(["", event("failure", timestamp=timestamp)])

    def test_fenetre_et_seuil_invalides(self):
        with self.assertRaisesRegex(ValueError, "fenêtre"):
            detect_bursts([], 3, 0)
        with self.assertRaisesRegex(ValueError, "fenêtre"):
            detect_bursts([], 3, 10**30)
        with self.assertRaisesRegex(ValueError, "seuil"):
            detect_bursts([], 0, 10)

    def test_precision_subseconde_conservee(self):
        rows = detect_bursts([event("failure", timestamp="2026-01-10T10:00:00.125Z")], 1, 1)
        self.assertEqual(utc_text(rows[0].first), "2026-01-10T10:00:00.125000Z")

    def test_commande_sur_jeu_fictif(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [sys.executable, str(root / "tools/analyse_auth.py"),
             str(root / "examples/auth-events-fenetres.jsonl"), "--window-minutes", "10"],
            capture_output=True, text=True, check=True,
        )
        self.assertIn("192.0.2.10", result.stdout)
        self.assertIn("2026-01-10T10:10:00Z", result.stdout)
        self.assertNotIn("198.51.100.7", result.stdout)


if __name__ == "__main__":
    unittest.main()
