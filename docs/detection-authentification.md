# Cas pratique : échecs d'authentification rapprochés

## Question et périmètre

Comment repérer, dans un fichier d'événements, plusieurs échecs de connexion visant **le même utilisateur depuis la même adresse source** en peu de temps ? Ce scénario illustre une première étape de triage. Les événements sont entièrement fictifs et les adresses appartiennent aux plages réservées à la documentation.

## Reproduire l'exemple

Prérequis : Python 3.10 ou plus récent, sans dépendance externe. Depuis la racine du dépôt :

```bash
python3 tools/analyse_auth.py examples/auth-events-fenetres.jsonl \
  --min-failures 3 --window-minutes 10
python3 -m unittest discover -s tests -v
```

Résultat attendu :

```text
Source          Utilisateur  Premier échec (UTC)  Seuil atteint (UTC)  Échecs
192.0.2.10      alice        2026-01-10T10:00:00Z 2026-01-10T10:10:00Z 3
```

Dans ce jeu de données, Alice cumule trois échecs en dix minutes exactement : la borne est incluse. Bob a lui aussi trois échecs au total, mais aucun groupe de trois ne tient dans la fenêtre. Les lignes sont volontairement désordonnées : le script trie les échecs avant de les analyser.

## Données attendues

Chaque ligne non vide est un objet JSON. Pour un échec `event.action=login` et `event.outcome=failure`, fournir `source.ip`, `user.name` et `@timestamp` au format ISO 8601 avec fuseau explicite, par exemple `2026-01-10T10:00:00Z` ou `2026-01-10T11:00:00+01:00`. Les dates sont normalisées en UTC. Une date absente ou invalide pour un échec provoque une erreur qui indique le numéro de ligne.

L'option `--window-minutes` examine les échecs compris entre l'instant courant moins la durée et cet instant, **bornes incluses**. Elle affiche le premier franchissement du seuil pour chaque couple source/utilisateur ; elle ne compte pas les succès. Sans cette option, le mode historique affiche les totaux du fichier, succès compris, sans utiliser les dates.

## Interprétation et limites

- Un seuil atteint n'est ni une preuve d'attaque ni une preuve de compromission : un mot de passe oublié, une application mal configurée ou une adresse partagée peuvent produire le même signal.
- Cette règle ne détecte pas correctement les tentatives réparties entre plusieurs adresses ou plusieurs comptes. Elle n'associe pas non plus un succès ultérieur à une séquence d'échecs.
- Le prototype ne lit que le format JSONL décrit ici ; il n'interroge aucun SIEM, ne vérifie pas que `source.ip` est une adresse IP valide et ne normalise pas directement les journaux SSH ou Windows. Il conserve et trie les échecs en mémoire et n'est pas conçu pour de gros volumes ou du temps réel.
- Il ne remonte que le premier franchissement par couple sur le fichier. Des pics ultérieurs pour ce même couple ne sont pas affichés.

Dans un exercice réel, il faudrait vérifier le contexte du compte et de la source, la couverture de collecte, l'horodatage, l'activité habituelle et les événements voisins avant de qualifier l'alerte. Ne pas publier de journaux ou d'identifiants réels.
