# Validateurs locaux

English: [README.md](README.md)

Ce sont les vérifications qu'un contributeur peut lancer hors ligne, sans
plateforme et sans base de données, avant de soumettre du contenu. Elles ont
besoin de Python 3 et de PyYAML :

```bash
pip install pyyaml
```

Lance-les avec `-I` (mode isolé) pour qu'elles ne chargent que leur propre code
et la bibliothèque standard, jamais un module parasite du répertoire courant.

## Ce que chacun vérifie

### validate_static_meta.py

Valide le `meta.yml` d'un static challenge : qu'il est du YAML valide (la panne
numéro un dans la vraie vie est un `': '` dans un hint non protégé), que chaque
clé requise est présente et bien formée, que le flag correspond à la forme
`ESPILON{...}`, que `category` est en kebab-case minuscule, que `level` est une
des valeurs fermées de la grille CTF, et que `hints` est une échelle non vide.

```bash
python3 -I validators/validate_static_meta.py templates/static-challenge
```

Pointe-le vers ton propre répertoire de challenge. Un code de sortie 0 veut dire
réussi.

### check_fr_accents.py

Un scan négatif d'accents sur les champs français d'un `meta.yml` de static
challenge (`description_fr`, `technique_fr`, `hints_fr`, et tout autre champ
`*_fr`). Il retire les parties où l'ASCII plat est correct (spans de code, URL,
identifiants en capitales, accolades de flag), puis vérifie mot à mot ce qui
reste contre une liste de mots français dont la seule orthographe correcte porte
un accent, et affirme que chaque champ français porte au moins un accent. Lire le
français n'est pas une vérification ; ceci en est une.

```bash
python3 -I validators/check_fr_accents.py templates/static-challenge
```

Il dépend de `bilingual_doc.py` dans ce répertoire. Un code de sortie 0 veut dire
réussi.

### check_lab_yaml.py

Une vérification de champs pour un lab Model-B : que `lab.yaml` a les clés
requises et le préfixe de slug `lab-`, que `category` et `difficulty` sont dans
leurs enums, qu'exactement un parmi `flag` / `flag_generator` / `flags` est
déclaré et bien formé, que `success_criteria` a la bonne forme, et que
`compose.yaml` respecte le sous-ensemble strict (pas de `privileged`, pas de
`cap_add`, pas de bind mount vers un chemin hôte, pas de mode réseau hôte) avec
le `FLAG` injecté qui correspond à `lab.yaml` pour un lab à flag unique.

```bash
python3 -I validators/check_lab_yaml.py templates/model-b-lab
```

Pointe-le vers ton propre dossier de lab. Un code de sortie 0 veut dire que les
champs sont bien formés. C'est un linter de champs, pas un test d'exécution : il
ne peut pas dire si la cible émet réellement le flag par le protocole.

### bilingual_doc.py

Pas une vérification que tu lances directement. C'est la règle partagée qui
sépare un document bilingue en ses moitiés anglaise et française, importée par
`check_fr_accents.py`.

## Ce qui n'est PAS ici, et pourquoi

Certaines vérifications ne peuvent pas tourner sans la plateforme ou le corpus de
contenu complet, donc elles tournent côté mainteneur quand ta soumission est
ingérée. N'attends pas un feu vert de ce répertoire pour elles :

- La synchro des cours et ses gates structurelles (longueur du TLDR, la liste
  autorisée TYPE et ARCHETYPE_ROLE, la résolution des artefacts) ont besoin d'une
  base de données. `docs/course.md` liste ce qu'il faut vérifier à la main en
  attendant.
- Les gates d'accents français des cours et du wiki se calibrent sur l'ensemble
  du corpus publié, donc elles ne peuvent pas juger une soumission isolée.
- La vérification des références liées du wiki a besoin du catalogue vivant de
  matériel et de cours ; mets de vrais slugs de plateforme dans `related_gear` et
  `related_courses` et les mainteneurs les valident à l'ingestion.
- Le comportement à l'exécution d'un lab Model-B (la cible émet-elle réellement
  le flag par le protocole) ne peut être jugé qu'en l'exécutant ;
  `check_lab_yaml.py` couvre les règles statiques de champs et de compose, pas
  cela.

Les docs par type sous `docs/` disent, pour chaque type, exactement quelles
vérifications tu lances ici et lesquelles sont côté mainteneur.
