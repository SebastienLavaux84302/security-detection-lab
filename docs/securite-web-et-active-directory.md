# Retours d'expérience : sécurité web et Active Directory

Ces notes présentent des apprentissages issus d'exercices contrôlés. Elles ne reproduisent ni cibles réelles, ni identifiants, ni solutions ou captures de plateformes tierces.

## Applications web

Des exercices de formation, notamment sur des applications volontairement vulnérables, m'ont permis d'explorer les injections SQL classiques et aveugles, ainsi que l'analyse de petites applications Python et PHP.

La démarche consiste à identifier l'entrée concernée, comprendre le cheminement des données, observer l'effet sur l'application de test, puis proposer et vérifier un correctif. Parmi les mesures étudiées : requêtes paramétrées, réduction des privilèges du compte de base de données et traitement prudent des entrées. Une validation d'entrée seule ne remplace pas la paramétrisation.

## Laboratoire Active Directory

Dans un lab TryHackMe autorisé, j'ai travaillé sur la reconnaissance de services, l'analyse de partages SMB et l'étude de mécanismes d'authentification Windows et Kerberos. L'objectif du retour d'expérience est de comprendre les erreurs de configuration et les traces utiles à une investigation ; les commandes, secrets de lab et résultats de challenges ne sont pas publiés ici.

## Ce que je retiens

- Délimiter les tests et utiliser uniquement des environnements autorisés.
- Relier chaque constat à une preuve adaptée, puis vérifier le correctif ou l'hypothèse.
- Documenter les limites et nettoyer les noms de machines, adresses, secrets et données tierces avant publication.

Synthèse rédigée à partir de notes personnelles avec l'assistance de Codex ; elle ne prétend pas décrire un audit en production.
