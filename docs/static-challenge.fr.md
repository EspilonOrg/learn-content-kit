# Créer un static challenge

English: [static-challenge.md](static-challenge.md)

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

Un casse-tête autonome : un ou plusieurs fichiers téléchargeables et un flag que
le joueur récupère à partir de ces seuls fichiers. Pas de serveur, pas de
session, pas de réseau. Si la réponse peut être recalculée à partir de l'artefact
sur la propre machine du joueur, c'est un static challenge.

## Où ça vit

Crée-le à partir de `templates/static-challenge/`. Copie le dossier entier,
remplace les valeurs d'exemple, garde-le passant les vérifications locales, et
soumets-le via le portail membre d'Espilon Learn. À l'ingestion, les mainteneurs
créent l'enregistrement du challenge, attachent les fichiers que tu as épinglés,
et câblent toute leçon de cours qui nomme le challenge par son slug. Ils
épinglent les octets de l'artefact par sha256, donc `generate.py` doit rester
déterministe. Tu ne seedes ni ne déploies jamais.

## Le template

```text
static-challenge/
  meta.yml        la fiche du challenge : flag, category, level, hints, brief bilingue
  generate.py     construit files/ de façon déterministe ; l'artefact ENCODE la réponse
  solve.py        le solveur de référence : récupère le flag depuis files/ seul
  files/          exactement ce que le joueur télécharge (épinglé par meta.yml `files:`)
```

`generate.py` et `solve.py` ne sont jamais livrés au joueur. Seul le contenu de
`files/` l'est, et seulement les entrées listées dans `meta.yml` sous `files:`.

## Référence des champs

Requis (le validateur rejette le fichier sans eux) : `slug`, `title`,
`category`, `level`, `flag`, `description`, `hints`. Attendus pour un challenge
bilingue et relié au wiki : `tags`, `files`, `technique`, `description_fr`,
`technique_fr`, `hints_fr`, `max_attempts`.

| Champ | Règle |
|---|---|
| `slug` | Kebab-case minuscule, unique. |
| `category` | Kebab-case minuscule uniquement. Une majuscule ou un underscore parasite scinde le groupe dans l'interface. Ce n'est pas l'axe de difficulté. |
| `level` | La grille de difficulté CTF, un ensemble fermé : `very-easy`, `easy`, `medium`, `hard`, `insane`. |
| `flag` | Doit correspondre à `ESPILON{...}` (le littéral `ESPILON`, un bloc `{...}`, au moins un caractère, pas d'accolades imbriquées). Concret, jamais un motif générique. Dérivé de l'artefact ; `solve.py` prouve qu'il est récupérable depuis `files/` seul. |
| `tags` | Pilotent la carte wiki associée. Mets entre guillemets tout ce qui a l'air numérique (un `802154` nu est interprété comme un entier). |
| `files` | Épingle les téléchargements exacts destinés au joueur. Sans cette clé, chaque fichier ordinaire sous `files/` est attaché, donc un fichier de brouillon parasite fuite. |
| `description` | Le brief destiné au joueur. Énonce la tâche et le format exact de la réponse. Utilise un bloc plié `>` pour éviter le piège YAML du `': '`. Énonce ; n'interprète pas. |
| `technique` | La note de conception privée. Énonce le chemin de résolution prévu et pourquoi les raccourcis échouent, pour qu'un relecteur puisse juger la difficulté. |
| `hints` | Une liste non vide de chaînes non vides, une échelle de barreaux qui enseigne la méthode sans donner la réponse. Le dernier barreau ne doit pas imprimer le flag ni l'exploit mot pour mot. |
| `description_fr`, `technique_fr`, `hints_fr` | Le jumeau français. Du français technique naturel avec de vrais accents ; garde les noms d'outils et de protocoles en anglais. Un champ FR manquant retombe sur l'EN. |

## Vérifications locales

Lance-les depuis la racine du kit, hors ligne, sans plateforme et sans base de
données.

```bash
# 1. Construis l'artefact (déterministe ; sans risque à relancer).
python3 -I templates/static-challenge/generate.py

# 2. Prouve qu'il se résout depuis le seul artefact et que le flag correspond.
python3 -I templates/static-challenge/solve.py

# 3. Valide la fiche meta.
python3 -I validators/validate_static_meta.py templates/static-challenge

# 4. Scanne les champs français pour des accents retirés.
python3 -I validators/check_fr_accents.py templates/static-challenge
```

Pointe-les vers ton propre dossier de challenge plutôt que vers
`templates/static-challenge`. Les quatre doivent sortir avec 0.

## Topologie

```text
  TOKEN (constante dans generate.py)
         |
         |  generate.py  (build déterministe)
         v
  files/sample.bin  ---- ce que le joueur télécharge ----------
         |                                                    |
         |  solve.py (référence)        analyse du joueur
         v                                                    |
  ESPILON{TOKEN}  <===== doit être égal octet pour octet =====+
         ^
  meta.yml `flag:`  (solve.py vérifie que sa sortie égale ceci)
```

L'artefact encode la réponse, la construction est déterministe, et `solve.py`
reproduit exactement le flag de `meta.yml`. Casse l'un des trois et le challenge
n'est pas prouvé.

## Images

Un static challenge n'a pas d'image de couverture. Les ressources destinées au
joueur sont les téléchargements dans `files/`, servies exactement comme épinglées
par `files:`. Ne dépose pas une image décorative dans `files/` : elle serait
servie comme un téléchargement. Les illustrations vont dans l'entrée wiki
associée ou dans le cours qui enseigne le challenge.

## Pièges

- **Le piège YAML du `': '`.** Une `description` ou un hint multi-lignes en clair
  qui contient `': '` ou un `:` final casse l'analyse. Utilise un bloc plié `>`
  ou mets la chaîne entre guillemets. C'est la panne réelle la plus fréquente.
- **Un flag générique.** Le flag doit être la chaîne exacte que produit le
  solveur, pas un motif.
- **Pas de solveur exécutable.** Un `solve.py` qui ne tourne pas en bibliothèque
  standard seule (ou avec une dépendance épinglée) laisse le challenge non
  prouvé. Ne le livre pas.
- **`category` pris pour `level`.** `category` groupe le challenge ; `level` est
  la grille CTF fermée. Les mélanger scinde le groupe ou fait échouer la
  validation.
- **Un `files:` non épinglé.** Chaque fichier sous `files/` est livré tant que tu
  n'épingles pas la liste.
- **Du français affirmé par lecture.** Lance la vérification d'accents FR ; ne te
  fie pas à l'oeil.
- **Un artefact qui dérive.** Si `generate.py` n'est pas déterministe, chaque
  épinglage sha256 qu'un cours fait contre l'artefact devient périmé en silence.

## Limites connues

Les validateurs vérifient le format et la résolvabilité. Savoir si le challenge
est intéressant et bien noté est un jugement humain à la revue. L'épinglage par
sha256 et le câblage des leçons se font côté mainteneur à l'ingestion.
