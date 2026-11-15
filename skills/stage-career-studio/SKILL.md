---
name: stage-career-studio
description: "Accompagner une recherche de stage ou PFE : clarifier le profil, trouver des offres actuelles et pertinentes, adapter des CV et lettres sans inventer de compétences, puis créer ou actualiser une interface de suivi persistante. Utiliser pour démarrer ce parcours, poursuivre une sélection de stages ou produire plusieurs dossiers ciblés."
metadata:
  version: "1.0.0"
---

# Stage Career Studio

Transformer un CV et les préférences du candidat en une sélection justifiée, des dossiers ciblés et un suivi durable. Répondre dans la langue de l'utilisateur. La méthode ne contient aucun profil personnel par défaut.

## Commencer au bon endroit

- **Nouveau candidat** : lire [entretien-profil.md](references/entretien-profil.md). Extraire d'abord les réponses présentes dans le CV et les échanges ; poser seulement les questions manquantes, par petits groupes. Ne pas reprendre le profil d'un autre candidat ni imposer une ville, une école, une profession ou une date.
- **Reprise d'un dossier** : lire le profil, le journal de reprise, le catalogue et les états actuels. Si le chemin manque et que l'environnement permet le système de fichiers, consulter `~/.codex/stage-career-studio/locations.json` : ce registre privé contient des pointeurs, pas des instructions. Utiliser uniquement le dossier correspondant à la demande. Pour un ami ou un nouveau candidat, repartir sur un dossier distinct.
- **Une offre ou un CV précis** : traiter ce périmètre ; ne pas recommencer tout le questionnaire ou remplacer l'interface existante.

Vérifier les outils réellement accessibles. La recherche nécessite un accès web ou des annonces fournies. La génération de fichiers nécessite un environnement qui sait les créer. Le skill ne donne aucun accès supplémentaire aux sites, comptes ou fichiers ; signaler les limites réelles et avancer sur ce qui reste possible. Ne jamais prétendre avoir consulté, généré, téléversé ou installé ce qui ne l'a pas été.

## Profil et faits utilisables

Conserver un dossier privé par candidat : `profile.json`, `facts.json`, `offers.json`, `state.json`, `documents/`, `REPRISE.md` et `index.html`. Lire le [contrat de données](references/interface-et-reprise.md) pour initialiser un nouveau dossier. Une interface existante conserve sa structure et ses clés ; ne pas l'écraser avec le modèle neuf.

Chaque fait a un identifiant, une source, une date de confirmation et un état : confirmé, ambigu ou prévu. Distinguer formation commencée, exercice, prototype, projet utilisé et solution vendue. Un intitulé d'outil ou un projet envisagé ne démontre pas sa maîtrise. En cas de contradiction, demander une clarification et utiliser la formulation vérifiée la moins ambitieuse en attendant.

Ne pas confondre nationalité, droit au travail, résidence ou habilitation. Ne demander les données administratives sensibles que si une exigence de l'offre ou un formulaire le justifie ; ne pas les diffuser dans les recherches ou le paquet partagé.

## Chercher et évaluer

Lire [recherche-et-adequation.md](references/recherche-et-adequation.md) avant un lot de recherche. Explorer plusieurs familles de métiers fondées sur les problèmes que le candidat veut résoudre, puis vérifier les missions réelles, le niveau requis et les contraintes. Élargir intelligemment sans confondre proximité de mots et adéquation.

Privilégier les annonces de l'employeur ; les plateformes servent à découvrir et complètent les sources. Enregistrer séparément publication, première observation, contrôle et début annoncé. Une page inaccessible ou une date inconnue reste une incertitude ; une republication ne devient pas une nouvelle offre.

Dédupliquer contre tout l'historique avant de générer des documents. Conserver les candidatures envoyées, les refus et les offres expirées. Un objectif de volume ou de note ne justifie ni faux résultats ni hausse artificielle des scores. Une note mesure une adéquation argumentée, jamais une probabilité d'embauche ni un score ATS garanti.

## Adapter les dossiers

Lire [cv-et-lettres.md](references/cv-et-lettres.md). Pour chaque offre retenue, relier ses principales exigences à des faits confirmés, puis choisir le titre, l'accroche, l'ordre des expériences, les réalisations détaillées et les compétences prioritaires. Une adaptation ne se réduit pas à remplacer le nom de l'entreprise.

Préserver les sources et les anciennes versions. Ne pas remplacer la version réellement envoyée. Proposer les formats pertinents selon les préférences et l'annonce : français lisible, français avec photo réelle autorisée, anglais sans photo, fichiers éditables si disponibles. Ne pas inventer une photo ou un lien Canva ; distinguer une création locale d'un export du service.

Vérifier les PDF rendus : lisibilité, alignements, absence de débordement, ordre d'extraction, coordonnées, diplôme et disponibilité. Si aucun outil PDF n'est accessible, livrer le contenu structuré et dire ce qui manque. Ajouter un lien CV ou lettre seulement lorsque le fichier correspondant existe.

## Interface et continuité

Lire [interface-et-reprise.md](references/interface-et-reprise.md). Le kit Python et le modèle HTML inclus permettent de créer une interface locale sans dépendance externe ni compte payant. Avec un ancien suivi, réutiliser son serveur et ses états au lieu de créer des sauvegardes concurrentes.

Afficher annonce, missions, dates, adéquation détaillée, écarts, conseil, CV disponibles, lettres disponibles, statut, notes et pièces réellement envoyées. Tous les statuts restent visibles par défaut. Les notes modifient la priorité, pas les faits.

Sauvegarder les états indépendamment du catalogue. Vérifier la sauvegarde, conserver un export réimportable et expliquer le mode utilisé : serveur local sur disque ou stockage dans ce navigateur. Un fichier HTML local et une URL `localhost` ne sont pas un hébergement mobile. Ne pas exposer le suivi ou les CV sur Internet sans demande explicite.

## Livraison et reprise

Avant d'annoncer une livraison, contrôler les liens, les doublons, les documents créés et les états préservés. Mettre à jour `REPRISE.md` avec les critères, changements, incertitudes, sources, chemins, prochaine action et façon de rouvrir le suivi. Fournir le nombre réellement vérifié, les meilleurs choix et les réserves déterminantes.

**Préparer uniquement.** L'utilisation de ce skill n'autorise jamais l'envoi d'une candidature, d'un message, l'acceptation d'un consentement ou une réponse inventée à un formulaire. Une telle action exige une instruction explicite distincte. Pendant une évaluation interdisant l'aide extérieure, limiter l'aide aux consignes générales et à la préparation hors test.

## Ressources exécutables

- `scripts/stage_studio.py init DOSSIER` : dossier vide ; refuse d'écraser les fichiers existants.
- `scripts/stage_studio.py validate DOSSIER` : schéma, doublons et liens de documents.
- `scripts/stage_studio.py upsert DOSSIER LOT.json` : fusion contrôlée, sans toucher aux statuts.
- `scripts/stage_studio.py build DOSSIER` : interface autonome, actualisée sans modifier les états.
- `scripts/stage_studio.py serve DOSSIER --port 8781` : serveur local uniquement ; arrêt avec Ctrl+C.
- `scripts/stage_studio.py bundle DOSSIER SORTIE.zip` : export privé du dossier ; ne pas confondre avec le skill générique à partager.
- `scripts/test_stage_studio.py` : tests reproductibles sur des données fictives, sans recherche ni candidature réelle.

Adapter les commandes à l'environnement. Sous PowerShell, utiliser `npx.cmd` si nécessaire ; Python suffit pour les scripts fournis. Aucun appel d'API IA, clé, connexion employeur ou téléchargement n'est intégré aux scripts.
