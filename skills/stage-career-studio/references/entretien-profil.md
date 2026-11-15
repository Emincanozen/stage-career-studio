# Entretien de cadrage

Le CV est une source, pas une preuve de toute compétence ajoutée dans un ancien brouillon. Recouper les corrections du candidat et distinguer le diplôme officiel de l'objectif professionnel.

## Premier échange : trois questions groupées au maximum

1. Quel diplôme prépares-tu, dans quelle spécialité officielle et à quel niveau ? Joins ton CV si tu en as un. Quelle disponibilité, durée et fin de cursus prévues ? Une date de jury inconnue reste inconnue.
2. Où peux-tu travailler, par ordre de préférence ? Quelles mobilités, contraintes de transport et langues de travail ?
3. Qu'aimerais-tu faire concrètement dans une journée, quels problèmes résoudre et quelles missions éviter ? Quels secteurs ou types d'entreprises privilégier ?

Ne pas redemander ce que les documents et messages établissent déjà. Commencer les recherches indépendantes pendant l'attente lorsqu'elles restent utiles.

## Deuxième passage selon les réponses

- Intérêt technique/client/projet/gestion, variété, accompagnement, apprentissage, perspective après stage.
- Grandes entreprises, PME ou indifférent ; secteurs désirés et exclus. Une marque connue ne garantit pas le contenu ou le salaire.
- Rémunération minimale et avantages importants, sans les transformer en montants acquis.
- Candidatures déjà envoyées, entretiens, expirations et refus. Préserver cet historique.
- Présentation : photo facultative, langues, longueur adaptée au parcours, modèle et fichiers éditables.

## Développer les expériences prometteuses

Demander : contexte, date, problème, contribution personnelle, outils effectivement utilisés, autonomie et accompagnement, livrable, résultat observable, public/client et élément montrable. Un résultat qualitatif est recevable ; noter « non mesuré » en préparation si aucune mesure n'existe, sans alourdir automatiquement le CV.

Si le candidat cite « A ou B », demander l'outil réellement utilisé. S'il ne se rappelle pas une loi de commande ou une version, employer une description exacte plus générale. Éviter les listes de technologies non pratiquées.

Pour un projet aidé par IA : préciser ce que le candidat a conçu, configuré, intégré, vérifié et vendu. Ne pas assimiler génération de code assistée et expertise de développeur ; ne pas dévaloriser non plus un vrai livrable testé et utilisé.

Pour les langues : niveau déclaré, usages, certification éventuelle ; un C1 autoévalué n'est pas une certification officielle. Pour le cloud : distinguer cours commencé, TP réalisé, architecture déployée et certification obtenue.

## Faits et cadrage

Créer `facts.json` :

```json
{"schema_version":1,"facts":[{"id":"F001","text":"Description validée par le candidat","status":"confirmed","source":"CV fourni ou réponse du candidat","confirmed_at":null,"tools":[],"metrics":[]}],"open_questions":[]}
```

`status` : `confirmed`, `ambiguous`, `planned`. Les deux derniers ne servent pas de preuve acquise. Ne pas créer de dates, chiffres, certifications, outils, nationalité ou clients absents des sources.

Reformuler brièvement le projet compris, les points forts et les inconnues. Laisser le candidat corriger sans imposer une validation supplémentaire aux opérations déjà autorisées. Construire un premier lot de qualité plutôt que promettre un volume arbitraire.
