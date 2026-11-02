# Retour d'expérience : analyse forensic d'images

## Contexte et objectif

Cet exemple résume une démarche appliquée lors d'un exercice de formation : examiner plusieurs fichiers images afin d'y retrouver des fragments d'information et de vérifier une hypothèse. Il ne s'agit pas d'un incident réel. Les fichiers de l'exercice, les solutions, les identifiants et les captures ne sont pas reproduits.

## Démarche

1. **Préserver et identifier les fichiers.** Travailler sur des copies, conserver les originaux et noter la provenance des éléments reçus.
2. **Contrôler l'intégrité.** Comparer l'empreinte calculée à celle fournie avec le jeu de données. L'exercice initial utilisait MD5 ; pour une nouvelle collecte, conserver aussi une empreinte SHA-256 et documenter les limites de chaque algorithme.
3. **Rechercher des indices.** Examiner les chaînes lisibles contenues dans les fichiers, sans supposer que toutes les données ont un sens.
4. **Interpréter les formats.** Identifier des fragments encodés en Base32 ou Base64, puis vérifier leur décodage. Un encodage est réversible et ne constitue pas un chiffrement.
5. **Tester une hypothèse.** Réassembler les fragments selon les indices de l'exercice et comparer le résultat au contrôle fourni. Le travail comprenait aussi l'exploration d'empreintes MD4 avec Hashcat : une recherche de candidat ne « déchiffre » pas une fonction de hachage.
6. **Documenter.** Noter les outils, versions, commandes et observations reproductibles dans un espace adapté, en distinguant faits observés et interprétations.

## Compétences mobilisées

Contrôle d'intégrité, exploration de fichiers, encodages, raisonnement sur les empreintes et rédaction d'un compte rendu. Outils utilisés dans l'exercice : `md5sum`, `strings`, `base32`, `base64`, Hashcat et CyberChef.

Ce retour d'expérience est une synthèse anonymisée préparée avec l'assistance de Codex. Il ne fournit ni jeu de preuves ni procédure applicable à une enquête réelle sans adaptation.
