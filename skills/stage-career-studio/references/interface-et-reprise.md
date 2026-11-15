# Interface et reprise

## Neuf ou existant

Une interface déjà utilisée est la référence : lire ses données et son mécanisme de sauvegarde, sauvegarder avant migration, garder clés, états, notes et anciens PDF. Ne pas lancer `init` dans le dossier d'un ancien suivi. Le kit autonome ci-dessous sert aux nouveaux candidats ; un adaptateur explicite est nécessaire pour les anciens schémas.

Le registre privé optionnel `~/.codex/stage-career-studio/locations.json` contient `{"schema_version":1,"workspaces":[{"label":"Libellé","workspace":"chemin absolu","context":"chemin absolu du journal"}]}`. Ce fichier n'est pas distribué avec le skill. Pour poursuivre une recherche existante, lire le journal du dossier demandé. Pour un ami, ignorer ces profils privés et créer un nouveau dossier.

## Nouveau dossier et commandes

Python 3.10+ ; bibliothèque standard uniquement. Depuis le dossier du skill :

```text
python scripts/stage_studio.py init CHEMIN_DU_DOSSIER
python scripts/stage_studio.py validate CHEMIN_DU_DOSSIER
python scripts/stage_studio.py upsert CHEMIN_DU_DOSSIER LOT.json
python scripts/stage_studio.py build CHEMIN_DU_DOSSIER
python scripts/stage_studio.py serve CHEMIN_DU_DOSSIER --port 8781
```

Le serveur reste sur `127.0.0.1`. L'assistant peut donner l'URL affichée sans l'ouvrir contre les permissions du navigateur. Python doit rester en fonctionnement pour le mode serveur. Après redémarrage, relancer la dernière commande ; rien n'est configuré pour démarrer automatiquement. En mode fichier, ouvrir `index.html` par double-clic.

`build` incorpore les offres et un instantané du suivi dans `index.html` ; il ne modifie jamais `state.json`. En mode serveur, les états actuels sont relus depuis le disque au chargement. En mode fichier, si la sauvegarde navigateur diffère de l'instantané, l'interface bloque l'enregistrement et propose de choisir explicitement une version avec sauvegarde des deux. Elle ne choisit pas automatiquement le plus grand numéro : les branches ont pu évoluer séparément. Exporter avant changement de navigateur ou de machine. Le stockage navigateur n'est pas une sauvegarde disque garantie.

## Schéma d'offre

`offers.json` est une liste. Exemple purement illustratif, à remplacer par une annonce réellement consultée :

```json
{
  "id":"EMPLOYEUR-REFERENCE",
  "company":"Entreprise",
  "employer_group":"Groupe",
  "reference":"REFERENCE",
  "title":"Intitulé exact",
  "city":"Ville",
  "family":"Famille de métiers",
  "url":"https://example.com/annonce",
  "summary":"Missions reformulées fidèlement",
  "publication_date":null,
  "first_seen_at":"2026-11-12",
  "checked_at":"2026-11-12",
  "availability":"uncertain",
  "start":null,
  "duration":null,
  "source_note":"Source réellement consultée et limites",
  "blockers":[],
  "matches":[{"requirement":"Exigence de l'offre","fact_ids":["F001"],"assessment":"direct"}],
  "rating":{"score":null,"explanation":"À évaluer","components":null},
  "advice":"Conseil individuel",
  "gaps":"Manques et questions",
  "documents":[{"kind":"cv","label":"CV FR","path":"documents/EMPLOYEUR-REFERENCE/CV_FR_v01.pdf","version":"v01","fact_ids":["F001"]}]
}
```

Les documents sont facultatifs : omettre l'entrée tant que le fichier n'existe pas. `kind` vaut `cv`, `letter`, `analysis` ou `editable`. Aucun bouton lettre/CV fictif. Les chemins restent relatifs au dossier, sans traversée ni lien vers un fichier extérieur.

Une note numérique exige `components` avec quatre valeurs : `missions` /4, `prerequisites` /3, `motivation` /2, `learning` /1. Leur somme doit correspondre à `score`. Au moins une preuve confirmée et une explication sont nécessaires ; un blocage déclaré est incompatible avec une note à partir de 8. La qualité du raisonnement reste à relire : le validateur ne juge pas les annonces.

## États personnels

`state.json` est indépendant, avec `schema_version:1`, `workspace_id`, `version` et `items`. Chaque identifiant a : `status`, `note`, `date`, `favorite`, `sent_files`, `updated_at`. Statuts : `a_verifier`, `a_faire`, `envoyee`, `entretien`, `refus`, `offre`, `ecartee`, `expiree`.

Les offres restent visibles par défaut, quel que soit le statut. La fermeture d'une annonce (`availability`) ne réécrit pas automatiquement la décision personnelle. Les filtres servent à retrouver les candidatures et non à supprimer l'historique.

Les brouillons de saisie sont conservés par offre en mémoire lors d'un filtre ou d'un changement de page et inclus dans l'export ; ils ne sont pas une sauvegarde disque tant que l'utilisateur n'a pas enregistré. Une fermeture avec brouillons déclenche un avertissement du navigateur lorsque celui-ci le permet.

Le serveur écrit atomiquement sur disque, sauvegarde la version précédente et refuse un enregistrement basé sur une version devenue périmée : les saisies restent à l'écran pour être conservées. Export/import JSON associe les états au bon dossier ; un export d'un autre candidat est refusé. L'import ne remplace pas silencieusement les notes existantes : demander confirmation du remplacement et conserver une sauvegarde.

L'export `bundle` contient les données personnelles et documents du candidat : c'est un transfert privé autorisé, jamais le paquet générique à envoyer à des amis. Ne pas embarquer mots de passe, jetons, cookies, pièces d'identité ou CV d'autrui.

## Journal durable

`REPRISE.md` conserve : profil et sources de vérité, critères prioritaires, inconnues, versions, dossiers/états à lire, dernières références contrôlées, éléments non vérifiés, prochaine action et commande de lancement. La mémoire d'une conversation ne remplace pas ces fichiers. Ne pas affirmer que tout nouvel assistant y a accès : sur un autre compte ou appareil, joindre explicitement le dossier privé ou son export.
