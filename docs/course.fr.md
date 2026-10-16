# Créer un cours

English: [course.md](course.md)

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

Une séquence bilingue de leçons, groupées en modules, qui enseigne un sujet et se
termine en l'appliquant à un artefact réel (un static challenge ou un lab). Un
cours n'est que du texte et de la structure ; la plateforme le rend.

## Où ça vit

Crée-le à partir de `templates/course/`. Copie le dossier entier et remplace les
valeurs d'exemple ; le template est un cours de trois leçons, deux modules, EN
plus FR, qui suit le format de la maison. Soumets le dossier via le portail
membre d'Espilon Learn. À l'ingestion, les mainteneurs créent l'enregistrement du
cours, synchronisent les leçons et les modules, et résolvent chaque `ARTIFACT`
vers le challenge ou le lab correspondant. Un artefact nommé qui n'existe pas
encore est un avertissement, pas un échec, donc une faute de frappe dans un slug
`ARTIFACT` laisse une leçon non câblée en silence. Les mainteneurs épinglent les
octets de tout artefact dont une leçon dépend, par sha256.

## Le template

```text
course/
  course.yaml                identité du cours : title, slug, difficulty, summary, track
  _modules.yaml              structure : slugs de module, ordre, icônes, archetype
  _artifacts.yaml            épingle les octets d'artefact du challenge par sha256
  lesson-en/
    lessons.md               leçons EN (les champs structurels sont lus ici)
    module-text.yaml         titres et descriptions de module EN
  lesson-fr/
    lessons.md               leçons FR (chacune écrit une ligne de traduction)
    module-text.yaml         titres et descriptions de module FR
```

Ajoute une locale avec un répertoire `lesson-<locale>/` contenant les deux mêmes
fichiers. Les champs structurels sont lus sur `lesson-en` seulement ; chaque
autre locale porte une traduction de la prose.

## Référence des champs

### course.yaml

L'identité du cours, lue par les mainteneurs pour créer l'enregistrement. Les
cinq champs sont requis.

| Champ | Règle |
|---|---|
| `title` | Nom affiché, en anglais. |
| `slug` | Identifiant unique en kebab-case minuscule. |
| `difficulty` | L'axe de difficulté du cours, un ensemble fermé : `beginner`, `intermediate`, `advanced`. Un vocabulaire différent du `level` d'un static challenge (la grille CTF) ; ne les mélange pas. |
| `summary` | Une ou deux phrases pour la carte du catalogue. Commence par le scénario concret que le cours enseigne. |
| `track` | Le slug de la piste de curriculum à laquelle ce cours appartient. Les mainteneurs le mappent à une piste vivante à l'ingestion ; si tu n'es pas sûr de la piste qui convient, dis-le au moment de soumettre plutôt que de deviner. |

### _modules.yaml

La spécification structurelle des modules : aucune chaîne d'affichage ici. Chaque
module a un `slug`, un `order` et une `icon`. L'`archetype` de premier niveau
pilote la forme du cours :

- `project` (archétype A, le défaut) : la théorie est motivée par un besoin
  pratique et livrée juste à temps.
- `reference` (archétype B) : un livre de recettes indépendantes.
- `fundamentals` (archétype C) : une construction de concepts de bas en haut.

### lessons.md

Un `lessons.md` par locale. Les leçons sont des blocs délimités par
`===== LESSON START =====` et `===== LESSON END =====`, chacun portant des
en-têtes à clés puis un corps markdown `CONTENT:`. Les clés sont `ORDER`,
`TITLE`, `TYPE`, `ARCHETYPE_ROLE`, `MODULE`, `TLDR`, `ESTIMATED_MINUTES`,
`LEARNING_OUTCOMES`, `FURTHER_READING`, `XP`, et le `ARTIFACT` optionnel.

| Clé | Règle |
|---|---|
| `TYPE` | Un parmi `theory`, `practical`, `challenge`, `quiz`, `lab`, `hands-on`. |
| `ARCHETYPE_ROLE` | Le rôle de la leçon dans la forme. Un parmi `hook`, `theory`, `setup`, `attempt`, `practice`, `deepdive`, `recipe`, `quiz`, `lab`. |
| `MODULE` | Le slug du module tiré de `_modules.yaml`. |
| `TLDR` | Une ligne, affichée dans le plan. Écrite dans une colonne `String(500)`, donc elle doit rester sous 500 caractères sinon l'ingestion avorte. |
| `LEARNING_OUTCOMES` | Une liste : ce que le lecteur sait faire après la leçon. |
| `FURTHER_READING` | Des références `wiki:<slug>` ou des entrées `{kind: url, title, url}` qui pointent vers une source primaire qu'un lecteur peut vérifier. |
| `ARTIFACT` | Câble la leçon à la chose qu'elle exerce. Syntaxe `<kind>:<slug>` où kind vaut `challenge` ou `lab`. |

Le corps `CONTENT:` est du markdown : les titres H2, les blocs de code et les
tableaux se rendent tous.

### Liste autorisée TYPE et ARCHETYPE_ROLE

Ce sont deux listes autorisées séparées jointes par un OU : une leçon est
acceptée si son `TYPE` est dans la liste TYPE OU si son `ARCHETYPE_ROLE` est dans
la liste ROLE. Elle n'est rejetée à l'ingestion que lorsque aucun des deux champs
n'est reconnu, parce qu'elle se rendrait sinon avec le mauvais badge dans le
plan.

- `TYPE` acceptés : `theory`, `practical`, `challenge`, `quiz`, `lab`,
  `hands-on`.
- `ARCHETYPE_ROLE` acceptés : `hook`, `theory`, `setup`, `attempt`, `practice`,
  `deepdive`, `recipe`, `quiz`, `lab`.

Une contrainte d'appariement au-delà de la règle OU : une leçon dont
l'`ARCHETYPE_ROLE` est `lab` devrait câbler vers un artefact `lab:`, et une leçon
dont le rôle est `challenge` ne devrait pas câbler vers un artefact `lab:`. Un
désaccord est averti à l'ingestion, pas rejeté.

### module-text.yaml

Les chaînes d'affichage des modules par locale, clées par le slug de
`_modules.yaml` : un `title` et une `description` pour chaque module, dans la
langue de cette locale.

### _artifacts.yaml

Épingle les octets exacts de chaque artefact de challenge dont les leçons
dépendent, par sha256, pour qu'un artefact régénéré ou qui a dérivé soit attrapé
avant qu'un lecteur n'atteigne une leçon dont les faits cuits (offsets,
longueurs, nombres de trames) ne correspondent plus.

```yaml
artifacts:
  - slug: <challenge-slug>        # correspond à une ligne ARTIFACT: challenge:<slug>
    path: <emplacement du challenge dans ta soumission>
    files:
      <filename>: sha256:<hex>    # une ligne par fichier joueur épinglé
```

Le `templates/course/_artifacts.yaml` livré épingle le `sample.bin` du template
static-challenge compagnon. Son hash est le vrai sha256 de ce fichier tel que
`generate.py` le produit, donc tu peux le vérifier :

```bash
python3 -c "import hashlib;print(hashlib.sha256(open('templates/static-challenge/files/sample.bin','rb').read()).hexdigest())"
```

Un cours qui n'exerce aucun artefact téléchargeable (purement théorique, ou qui
ne pilote qu'un lab vivant) n'a pas besoin de `_artifacts.yaml` ; supprime le
fichier.

## Vérifications locales

Le format de cours est ingéré par un outillage de plateforme qui a besoin d'une
base de données, donc il n'y a pas de validateur de cours autonome dans ce kit.
Avant de soumettre, vérifie à la main :

- chaque `TLDR` est sous 500 caractères ;
- le `TYPE` ou l'`ARCHETYPE_ROLE` de chaque leçon est sur la liste autorisée
  ci-dessus ;
- chaque slug `ARTIFACT` correspond à un challenge ou un lab que tu soumets
  aussi, et chaque fichier dont il dépend est épinglé dans `_artifacts.yaml` ;
- la locale FR porte de vrais accents sur chaque surface, vérifiés mot à mot.

## Topologie

```text
  _modules.yaml  (archetype, slugs de module + ordre)
        |
        +--> lesson-en/lessons.md     (vérité structurelle + prose EN)
        +--> lesson-fr/lessons.md     (lignes de traduction FR)
        +--> lesson-*/module-text.yaml (titres de module par locale)
        |
   bloc de leçon  --- ARTIFACT: challenge:<slug> --->  static challenge
                  --- ARTIFACT: lab:<slug>       --->  lab Model-B
```

Les champs structurels vivent une seule fois, dans `lesson-en`. Chaque autre
locale porte les mêmes blocs de leçon avec `TITLE`, `TLDR`, résultats et corps
traduits, stockés comme des lignes de traduction rattachées à la leçon anglaise.

## Images

Un cours ne porte aucun téléversement matriciel. Là où le modèle est spatial (un
bus, une topologie, une disposition de paquet), inclus un `<svg>` écrit à la main
directement dans le markdown de la leçon : il se rend nativement. Ne référence
pas un fichier image téléversé. Garde le SVG simple et lisible ; il fait partie
de la source de la leçon.

## Pièges

- **Un `TLDR` au-dessus de 500 caractères.** C'est une colonne `String(500)` ; un
  seul TLDR trop long avorte toute la synchro du cours. Compte les caractères.
- **Une dérive structurelle entre locales.** Les champs structurels sont lus sur
  `lesson-en` seulement. Un `TYPE` ou un `MODULE` différent dans le fichier FR ne
  fait rien et cache le désaccord.
- **Une leçon où ni le `TYPE` ni l'`ARCHETYPE_ROLE` n'est sur la liste
  autorisée.** C'est le seul cas rejeté à l'ingestion (la règle est un OU, pas un
  appariement de paire), et le rejet est ce qui empêche une leçon de se rendre
  avec le mauvais badge.
- **Une faute de frappe dans un slug `ARTIFACT`.** L'ingestion avertit plutôt
  qu'échouer, donc la leçon est livrée non câblée. Lis les avertissements.
- **Une capture d'écran matricielle là où un SVG en ligne a sa place.** Les
  images téléversées ne font pas partie de la source de la leçon et ne sont pas
  prises en charge ici.
- **Du français affirmé par lecture.** Livre un FR vraiment accentué ; un corps
  FR manquant ou vide retombe en silence sur l'anglais.

## Limites connues

Les gates d'accents français et de structure de cours sont couplées au corpus et
tournent côté mainteneur à l'ingestion, donc aucun validateur autonome de ce kit
ne peut juger un cours isolé. Lire le français n'est pas une vérification ;
vérifie-le mot à mot. Si tu n'es pas sûr de la piste à laquelle un cours
appartient, demande plutôt que de deviner.
