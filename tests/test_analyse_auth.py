import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from analyse_auth import analyse


def event(outcome, ip="192.0.2.10", name="alice", action="login"):
    return json.dumps({"event": {"action": action, "outcome": outcome},
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


if __name__ == "__main__":
    unittest.main()
