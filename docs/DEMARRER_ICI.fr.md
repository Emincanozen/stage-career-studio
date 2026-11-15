# Stage Career Studio : démarrer ou partager

Ce paquet contient la méthode, le questionnaire, un modèle de profil vierge et un kit d’interface. Il ne contient ni les CV, ni la photo, ni les coordonnées, ni le suivi du créateur du projet.

## Le plus simple pour un ami ou un autre compte

1. Joindre ce ZIP et son propre CV à une nouvelle conversation.
2. Envoyer le texte de `PROMPT_CHATGPT.txt`.
3. L’assistant lit `skills/stage-career-studio/SKILL.md` dans le ZIP, puis pose les questions utiles avant de chercher. Dans le dossier source non zippé, le chemin commence directement par `stage-career-studio`.

Le compte doit pouvoir lire les fichiers et accéder au Web pour vérifier les annonces. Pour produire PDF et interface téléchargeable, il lui faut aussi un outil de création de fichiers. Si une fonction manque, l’assistant doit le dire et préparer le contenu possible ; joindre un skill ne donne pas de nouveaux outils.

## Codex sur son propre ordinateur

Extraire le paquet et copier le dossier `skills/stage-career-studio` sous `~/.agents/skills/stage-career-studio`. Dans une nouvelle conversation :

> Utilise $stage-career-studio pour m’aider à trouver un stage. Voici mon CV. Pose-moi les questions manquantes, crée mon suivi et prépare mes candidatures sans rien envoyer.

Si le skill ne s’affiche pas, relancer l’application. Il s’agit d’une installation locale, pas d’une activation sur tous les comptes et appareils. Le ZIP contient aussi un manifeste de plugin pour les environnements qui acceptent l’import de plugins ; l’import dépend du produit et des droits du compte.

## Ce que le parcours prépare

Profil confirmé et questions ciblées ; recherche diversifiée et sources datées ; dédoublonnage et analyse d’adéquation expliquée ; CV personnalisés et lettres utiles ; interface avec liens, réserves, notes et statuts ; historique et export pour reprendre le travail.

Aucune candidature n’est envoyée automatiquement. Une note /10 n’est ni une probabilité d’embauche ni une garantie de passer un ATS. Les données d’un autre candidat ne sont jamais reprises.

## Interface et sauvegarde

Le script Python 3.10+ du skill fonctionne sans bibliothèque supplémentaire. Lire `references/interface-et-reprise.md` avant initialisation. Les CV sont rédigés et vérifiés par l’assistant ; le kit organise les fichiers réellement créés, il n’invente pas de dossiers.

- Fichier `index.html` : ouverture directe ; sauvegarde dans ce navigateur, export conseillé.
- Serveur local du kit : sauvegarde sur disque ; relancer Python après un redémarrage.
- Téléphone à distance : ni le fichier local ni `localhost` ne suffisent. Ne pas publier les CV ou ouvrir un tunnel sans accord explicite.

Pour transférer sa propre recherche sur un autre appareil, utiliser l’export privé du dossier, distinct de ce paquet générique. Garder une copie avant import.

## Installation et compatibilité : source officielle

Documentation consultée le 12 novembre 2026 : https://learn.chatgpt.com/docs/build-skills . Les possibilités d’import ou d’installation peuvent varier ; ne pas supposer qu’un ZIP active un skill dans n’importe quelle interface ChatGPT.
