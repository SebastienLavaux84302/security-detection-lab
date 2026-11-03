# Security Detection Lab

**Explorer la collecte, l'analyse et la qualification d'événements dans un laboratoire personnel.**

Mes expérimentations de sécurité s'appuient sur des environnements Linux et Active Directory, notamment GOAD, ainsi que sur des outils comme Security Onion, Snort, Wazuh et Kibana. Ce dépôt présente une démarche de travail, des retours d'expérience anonymisés et un exemple autonome d'analyse sur des données fictives.

> Les schémas sont pédagogiques et ne décrivent pas une intégration précise entre les produits. Les événements et résultats fournis sont synthétiques : ce ne sont pas des journaux ni des incidents réels.

## Contenu

| Élément | Description |
| --- | --- |
| [Architecture fonctionnelle](docs/architecture.md) | Sources, collecte et analyse dans un lab de détection. |
| [Méthode d'investigation](docs/methodologie.md) | Du scénario de test à la qualification et à la documentation. |
| [Analyse forensic d'images](docs/forensic-analyse-images.md) | Synthèse anonymisée d'un exercice d'analyse et de contrôle d'intégrité. |
| [Sécurité web et Active Directory](docs/securite-web-et-active-directory.md) | Retours d'expérience issus de laboratoires contrôlés. |
| [Événements fictifs](examples/auth-events.jsonl) | Exemple JSONL avec adresses de documentation et comptes fictifs. |
| [Cas pratique : échecs rapprochés](docs/detection-authentification.md) | Jeu de données fictif et scénario reproductible avec fenêtre temporelle. |
| [Analyseur Python](tools/analyse_auth.py) | Comptage global ou recherche d'échecs rapprochés par source et utilisateur. |
| [Tests](tests/test_analyse_auth.py) | Vérifient le regroupement, les dates, la fenêtre et les données invalides. |

## Essayer l'exemple

Il suffit de disposer de Python 3.10 ou plus récent ; aucune bibliothèque externe n'est nécessaire.

```bash
python3 tools/analyse_auth.py examples/auth-events.jsonl --min-failures 3
python3 -m unittest discover -s tests
```

Résultat attendu sur le fichier fourni :

```text
Source          Utilisateur  Échecs  Succès
192.0.2.10      alice        3       1
```

Sans l'option `--window-minutes`, l'exemple regroupe tout le fichier : un succès et plusieurs échecs d'un même groupe ne prouvent pas à eux seuls un lien entre ces événements.

Pour examiner les échecs rapprochés dans une fenêtre glissante de 10 minutes :

```bash
python3 tools/analyse_auth.py examples/auth-events-fenetres.jsonl \
  --min-failures 3 --window-minutes 10
```

Le résultat signale le groupe fictif `192.0.2.10` / `alice` : ses trois échecs sont compris dans la fenêtre, bornes incluses. Le groupe `bob` compte aussi trois échecs au total, mais ils sont trop éloignés dans le temps. Le [cas pratique](docs/detection-authentification.md) précise le format, l'interprétation et les limites de cette détection pédagogique.

## Ressources liées

- [Homelab Infrastructure](https://github.com/SebastienLavaux84302/homelab-infrastructure) : virtualisation, services et automatisation dans le lab personnel.
- [Mon profil PentesterLab](https://pentesterlab.com/profile/SebastienLavaux84302) : exercices pratiques de sécurité.

## Périmètre et assistance

Projet personnel à vocation pédagogique. Les données brutes, configurations et résultats détaillés des labs ne sont pas inclus ; les retours d'expérience résument des exercices de formation. L'exemple Python, ses tests et cette documentation ont été préparés avec l'assistance de **Codex (OpenAI)** ; ils ne représentent pas une intégration existante des outils cités.
