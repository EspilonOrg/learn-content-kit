# Créer un static challenge

English: [static-challenge.md](static-challenge.md)

Un static challenge est un casse-tête autonome : un ou plusieurs fichiers
téléchargeables et un flag que le joueur récupère à partir de ces seuls
fichiers. Pas de serveur, pas de session, pas de réseau. Si la réponse peut être
recalculée à partir de l'artefact sur la propre machine du joueur, c'est un
static challenge.

Template : `templates/static-challenge/`. Copie le dossier entier, garde-le
passant les vérifications locales, et remplace les valeurs d'exemple par les
tiennes.

## Les fichiers

```
static-challenge/
  meta.yml        la fiche du challenge : flag, category, level, hints, brief bilingue
  generate.py     construit files/ de façon déterministe ; l'artefact ENCODE la réponse
  solve.py        le solveur de référence : récupère le flag depuis files/ seul
  files/          exactement ce que le joueur télécharge (épinglé par meta.yml `files:`)
```

`generate.py` et `solve.py` ne sont jamais livrés au joueur. Seul le contenu de
`files/` l'est, et seulement les entrées nommées dans `meta.yml` sous `files:`.

## Remplir meta.yml, champ par champ

Requis (le validateur de meta rejette le fichier sans eux) : `slug`, `title`,
`category`, `level`, `flag`, `description`, `hints`. Attendus pour un challenge
bilingue et relié au wiki : `tags`, `files`, `technique`, `description_fr`,
`technique_fr`, `hints_fr`, `max_attempts`.

- `slug` : identifiant en kebab-case minuscule, unique.
- `category` : kebab-case minuscule uniquement. Une majuscule ou un underscore
  parasite scinde silencieusement le groupe dans l'interface. Ce n'est PAS l'axe
  de difficulté.
- `level` : la grille de difficulté CTF, un ensemble fermé. Exactement un parmi
  `very-easy`, `easy`, `medium`, `hard`, `insane`.
- `flag` : doit correspondre à la forme `ESPILON{...}` (le littéral `ESPILON`, un
  bloc `{...}`, au moins un caractère, pas d'accolades imbriquées). Rends-le
  concret, jamais un motif générique. Pour un static challenge le flag est dérivé
  de l'artefact ; `solve.py` prouve qu'il est récupérable à partir de `files/`
  seul.
- `tags` : pilotent la carte wiki associée. Mets entre guillemets tout tag qui a
  l'air numérique (un `802154` nu est interprété comme un entier).
- `files` : épingle les téléchargements exacts destinés au joueur. Sans cette
  clé, chaque fichier ordinaire sous `files/` est attaché, donc un fichier de
  brouillon parasite fuite.
- `description` : le brief destiné au joueur. Énonce la tâche et le format exact
  de la réponse. Utilise un bloc plié `>` pour éviter le piège YAML du `': '`. Il
  énonce ; il n'interprète pas.
- `technique` : la note de conception privée. Énonce le chemin de résolution
  prévu et pourquoi les raccourcis échouent, pour qu'un relecteur puisse juger la
  difficulté.
- `hints` : une liste non vide de chaînes non vides, une échelle de barreaux qui
  enseigne le comment sans donner la réponse. Le dernier barreau ne doit pas
  imprimer le flag ni l'exploit mot pour mot.
- `description_fr`, `technique_fr`, `hints_fr` : le jumeau français. Du français
  technique naturel avec de vrais accents ; garde les noms d'outils et de
  protocoles en anglais. Un champ FR manquant retombe sur l'EN, donc livre le FR
  quand le challenge est bilingue.

## Topologie

Comment les trois scripts et le flag sont reliés :

```
  TOKEN (constante dans generate.py)
         |
         |  generate.py  (build déterministe)
         v
  files/sample.bin  ---- ce que le joueur télécharge --------
         |                                                  |
         |  solve.py (référence)        analyse du joueur
         v                                                  |
  ESPILON{TOKEN}  <===== doit être égal octet pour octet ===+
         ^
  meta.yml `flag:`  (solve.py vérifie que sa sortie égale ceci)
```

L'invariant à tenir : l'artefact encode la réponse, la construction est
déterministe, et `solve.py` reproduit exactement le flag de `meta.yml`. Casse
l'un des trois et le challenge n'est pas prouvé.

## Règle des images et des ressources

Un static challenge n'a pas d'image de couverture. Les ressources destinées au
joueur sont les téléchargements dans `files/`, et elles lui sont proposées
exactement comme épinglées par `files:`. Ne dépose pas une image décorative dans
`files/` : elle serait servie comme un téléchargement. Les illustrations vont
dans l'entrée wiki associée ou dans le cours qui enseigne le challenge, pas dans
le dossier d'artefact.

## Lancer les vérifications locales

Depuis la racine du kit, hors ligne, sans plateforme et sans base de données :

```bash
# 1. Construis l'artefact (déterministe ; sans risque à relancer).
python3 -I templates/static-challenge/generate.py

# 2. Prouve que le challenge se résout depuis le seul artefact et que le flag correspond.
python3 -I templates/static-challenge/solve.py

# 3. Valide la fiche meta.
python3 -I validators/validate_static_meta.py templates/static-challenge

# 4. Scanne les champs français pour des accents retirés.
python3 -I validators/check_fr_accents.py templates/static-challenge
```

Pointe-les vers ton propre dossier de challenge plutôt que vers
`templates/static-challenge`. Les quatre doivent sortir avec 0.

## Comment cela atteint la plateforme

Tu ne seedes ni ne déploies. Soumets le dossier via le portail membre d'Espilon
Learn. Quand ta soumission est ingérée, les mainteneurs créent l'enregistrement
du challenge, attachent les fichiers que tu as épinglés, et câblent toute leçon
de cours qui nomme le challenge par son slug. Les octets d'artefact dont dépend
un cours sont épinglés par sha256 côté mainteneur, et c'est pourquoi
`generate.py` doit rester déterministe.

## Pièges qui coûtent du temps

- Le piège YAML du `': '`. Une `description` ou un hint multi-lignes en clair qui
  contient `': '` ou un `:` final casse l'analyse. Utilise un bloc plié `>` ou
  mets la chaîne entre guillemets. C'est la panne réelle la plus fréquente.
- Un flag qui est un motif générique, pas une valeur concrète. Le flag doit être
  la chaîne exacte que produit le solveur.
- Pas de solveur de référence exécutable. Un static challenge dont le `solve.py`
  ne tourne pas en bibliothèque standard seule (ou avec une dépendance épinglée)
  n'est pas prouvé. Ne le livre pas.
- `category` n'est pas `level`. `category` groupe le challenge ; `level` est la
  grille CTF fermée. Les mélanger scinde le groupe de l'interface ou fait échouer
  la validation.
- Un `files:` non épinglé. Chaque fichier sous `files/` est livré tant que tu
  n'épingles pas la liste.
- Du français affirmé par lecture. Le FR a déjà été livré accents retirés plus
  d'une fois. Lance la vérification d'accents FR ; ne te fie pas à l'oeil.
- Un artefact qui dérive. Si `generate.py` n'est pas déterministe, chaque
  épinglage au niveau de l'octet qu'un cours fait contre l'artefact devient
  périmé en silence.
