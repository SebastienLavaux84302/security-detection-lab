# Méthode de travail

## 1. Définir un scénario

Formuler une question observable, par exemple : « Plusieurs échecs d'authentification concernent-ils le même compte depuis une même source ? » Définir le périmètre de test, les machines autorisées et la période examinée.

## 2. Vérifier les données disponibles

Identifier la source des journaux, le fuseau horaire, l'état de la collecte et la signification des champs. Une recherche sans résultat peut traduire une absence d'événements, mais aussi une collecte incomplète ou un mauvais filtre.

## 3. Regrouper, puis qualifier

Comparer les échecs, les succès, les comptes concernés et le contexte : activité attendue, application, fenêtre de temps et fréquence habituelle. Éviter de conclure à une compromission sur un seul indicateur.

Le script du dépôt propose un regroupement global et une recherche d'échecs rapprochés sur des données **fictives**. Cette dernière utilise une fenêtre temporelle, mais ne corrèle pas les succès ultérieurs : c'est une base de discussion, pas une règle opérationnelle. Voir le [cas pratique d'authentification](detection-authentification.md).

## 4. Documenter les résultats réels

Pour un exercice effectivement réalisé, conserver dans un espace approprié le scénario, les sources et versions, les critères de recherche, les observations, les faux positifs possibles et les prochaines vérifications. Avant partage public, retirer les journaux, noms, adresses et autres données propres à l'environnement.
