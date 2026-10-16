# Créer un lab Model-B

English: [README.md](README.md)

Ce README est le guide pour remplir le template. Il ne fait pas partie de
l'artefact soumis ; les mainteneurs l'ignorent à l'ingestion.

## Sommaire

- [Ce que c'est](#ce-que-cest)
- [Où ça vit](#où-ça-vit)
- [Le template](#le-template)
- [Référence des champs](#référence-des-champs)
- [Vérifications locales](#vérifications-locales)
- [Topologie](#topologie)
- [Images](#images)
- [Pièges](#pièges)
- [Limites connues](#limites-connues)

## Ce que c'est

Une cible vivante, par session, que le joueur attaque depuis sa propre machine.
Le lab ne livre que le ou les services cibles ; le joueur apporte ses propres
outils (une machine Kali, le client `espilon-probe`, ce dont le protocole a
besoin). Le flag transite par le protocole. Il n'y a ni shell ni fichier dans le
lab.

Ce modèle de livraison a un nom : Model B. Le joueur apporte le côté attaquant ;
tu ne livres que la cible.

## Où ça vit

Crée-le à partir de `templates/model-b-lab/` : `lab.yaml` à côté de
`compose.yaml`. Remplis les deux, lance la vérification de champs locale, et
soumets via le portail membre d'Espilon Learn. À l'ingestion, les mainteneurs
construisent et enregistrent l'image, placent le lab dans le dépôt de labs de la
plateforme, réconcilient le slug avec l'enregistrement de lab vivant, et câblent
toute leçon qui pointe en retour vers le lab. Tu ne le déploies pas toi-même.

## Le template

```text
model-b-lab/
  lab.yaml       métadonnées : slug, category, difficulty, points, flag(s), success criteria
  compose.yaml   l'exécution : le ou les services cibles, le flag injecté à l'instanciation
```

Un vrai lab porte aussi le contexte de build de l'image (un répertoire `target/`
avec un Dockerfile) référencé par le `build:` de `compose.yaml`. Celui-ci est à
toi de le construire ; le template montre les deux fichiers déclaratifs que la
plateforme lit.

## Référence des champs

### lab.yaml

| Champ | Règle |
|---|---|
| `slug` | Préfixe `lab-`. Les mainteneurs le réconcilient avec l'enregistrement de lab vivant à l'ingestion, donc garde-le stable une fois soumis. |
| `title` | Nom affiché du lab. |
| `category` | Enum fermé, indépendant de tout nom de dossier : `hardware firmware iot ot-ics esp32 wifi bluetooth drone camera misc`. |
| `difficulty` | Enum fermé : `easy medium hard insane`. |
| `points` | Valeur en points, liée de façon lâche à `difficulty` (easy jusqu'à 200, hard à partir de 300). |
| `description` | Le brief destiné au joueur : le protocole, l'objectif, la classe d'attaque. Redonne le contrat Model-B pour fixer les attentes. |
| `archetype` | Un indice côté interface qui choisit quel visualiseur s'affiche à côté du panneau de session (par exemple `iot-mqtt`). |
| `radios_required`, `caps_required`, `duration_minutes` | Des demandes d'exécution. Les capabilities hors liste autorisée sont refusées ; `duration_minutes` est le TTL d'auto-destruction. |
| `success_criteria` | `type: flag_submit` avec un `hint` toujours disponible. Garde la vraie méthode dans le cours et dans les barreaux de hints payants, pas ici. |

### Le flag

Déclare exactement un parmi `flag`, `flag_generator` ou `flags`.

- **`flag`** (statique unique, le défaut du template). Sa valeur doit être égale
  à la valeur que `compose.yaml` injecte à l'instanciation, octet pour octet.
- **`flag_generator`**, un parmi :
  - `uuid` : le flag est `ESPILON{<uuid4 hex>}`, une valeur aléatoire fraîche par
    session.
  - `wordlist` : une entrée aléatoire par session depuis un `flags/wordlist.txt`
    que tu livres à côté de `lab.yaml`, un flag candidat par ligne. Pour des flags
    lisibles par un humain par session.
  - `hmac:<keyref>` : le flag est `ESPILON{<hmac(secret, session_id)>}`.
    `<keyref>` nomme un secret que les mainteneurs détiennent (tu ne le livres
    pas) ; le correcteur redérive le flag attendu. Pour un flag vérifiable côté
    serveur sans être stocké.
- **`flags`** (objectifs à plusieurs étapes). Une liste, une entrée par étape,
  chacune portant `slug`, `label`, `content` (un flag `ESPILON{...}`), `points`,
  `order` et `hint`. L'image en exécution doit exposer chaque `content` par le
  protocole au moment de l'exécution.

```yaml
flags:
  - slug: stage-1
    label: Ce que le joueur a accompli pour gagner ce flag
    content: ESPILON{stage_one_fl4g}
    points: 100
    order: 1
    hint: |
      Conseil de barreau pour cette étape précise.
  - slug: stage-2
    label: L'objectif plus profond
    content: ESPILON{stage_two_fl4g}
    points: 100
    order: 2
    hint: |
      Conseil de barreau pour la deuxième étape.
```

### compose.yaml

L'exécution analyse `compose.yaml` comme un sous-ensemble strict de Compose. Elle
rejette `privileged`, `cap_add`, les bind mounts (volumes vers des chemins hôte)
et le mode réseau hôte. Les ports hôte sont ignorés : l'exécution attribue un
port hôte éphémère par session, donc ne liste que le port du conteneur. `build:`
est le contexte de build de l'image et est ignoré à l'exécution, qui ne lit que
`image:`.

Le flag est injecté ici à l'instanciation via l'environnement du service, jamais
cuit dans l'image. Sa valeur doit correspondre à `lab.yaml` octet pour octet. La
cible le lit depuis l'environnement et l'émet par le protocole.

### Liste de contrôle

Tout le contrat que le vérificateur local impose, au même endroit :

- `lab.yaml` a `slug` (avec le préfixe `lab-`), `title`, `category`,
  `difficulty`, `description` et `success_criteria`.
- `category` est un parmi `hardware firmware iot ot-ics esp32 wifi bluetooth
  drone camera misc`.
- `difficulty` est un parmi `easy medium hard insane`.
- Exactement un parmi `flag`, `flag_generator`, `flags` est déclaré.
  - `flag` correspond à `ESPILON{...}`.
  - `flag_generator` est `uuid`, `wordlist`, ou `hmac:<keyref>` avec un keyref
    non vide.
  - `flags` est une liste non vide ; chaque entrée porte `slug`, `label`,
    `content` (un flag `ESPILON{...}`), `points` et `order`.
- `success_criteria` est une table avec `type: flag_submit` et un `hint` non
  vide.
- `compose.yaml` n'a aucun `privileged`, aucun `cap_add`, aucun bind mount vers
  un chemin hôte et aucun mode réseau hôte.
- Pour un lab à flag unique, un service injecte `FLAG=<le flag de lab.yaml>` dans
  son environnement, octet pour octet.

## Vérifications locales

```bash
pip install pyyaml
python3 -I validators/check_lab_yaml.py templates/model-b-lab
```

Pointe-le vers ton propre dossier de lab plutôt que vers le template. Un code de
sortie 0 veut dire que les champs sont bien formés.

## Topologie

```text
   machine du joueur (Kali, espilon-probe, ...)
            |
            |  port hôte éphémère, attribué par session
            v
   +--------------------+        réseau interne (internal: true)
   |  service cible     | --------------------------------+
   |  FLAG depuis l'env |                                 |
   |  émet via le proto |                     +-----------+
   +--------------------+                     | broker/db |
            ^                                 | interne   |
            |  pas de shell, pas de fichier   +-----------+
   le flag atteint le joueur UNIQUEMENT via le protocole
```

Un second service (une base de données, un broker) est autorisé. Mets les
services partagés sur un réseau Compose avec `internal: true` et adresse-les par
leur nom de service. Ils ne doivent avoir aucune adresse côté hôte.

## Images

Un lab ne livre aucune image téléversée. Le champ `archetype` choisit le
visualiseur intégré qui s'affiche à côté du panneau de session. Ne mets pas de
captures d'écran ni de ressources décoratives dans l'image cible. Toute
illustration va dans le cours qui enseigne le lab.

## Pièges

- **Un flag cuit dans l'image** au lieu d'être injecté à l'instanciation. Il doit
  venir de l'environnement et correspondre à `lab.yaml` exactement.
- **Un flag sur le système de fichiers.** Un lab à conteneur unique laisse fuiter
  le flag par `grep`, `env` ou un fichier lisible. Model B interdit un shell et
  un fichier dans le lab pour exactement cette raison : le flag ne doit jamais
  arriver que par le protocole.
- **Un champ de compose rejeté.** `privileged`, `cap_add`, les volumes vers un
  chemin hôte et le réseau hôte sont refusés ; le lab ne démarrera pas.
- **Un harnais de vérification qui ment selon l'endroit où il tourne.** Un
  service interne (un broker derrière `internal: true`) n'a aucune adresse côté
  hôte, donc une vérification lancée hors du réseau de session rapporte de faux
  défauts contre un lab sain. Lance toute vérification depuis l'intérieur du
  réseau de session, jamais depuis l'hôte.
- **`category` confondu avec un nom de dossier.** C'est un enum fermé ; choisis
  la valeur de l'enum, pas le répertoire sous lequel le lab est rangé.
- **Plus d'un parmi `flag` / `flag_generator` / `flags`.** Exactement un. Un
  `flag:` oublié au-dessus d'une liste `flags:` est le dérapage courant.

## Limites connues

Le vérificateur local est un linter de champs, pas la gate propre à la
plateforme, même si l'exécution applique les mêmes règles de compose à
l'instanciation. Il ne peut pas dire si la cible émet réellement le flag par le
protocole à l'exécution, ni si le lab enseigne bien ; cela revient à toi et à la
revue des mainteneurs. Quand une règle ici est vraiment peu claire pour ton
protocole, demande via le portail plutôt que de deviner.
