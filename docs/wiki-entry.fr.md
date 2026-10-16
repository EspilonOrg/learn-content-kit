# Créer une entrée wiki

English: [wiki-entry.md](wiki-entry.md)

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

Une page de référence sur une seule chose : une puce, un protocole, un bus, un
concept. Elle est bilingue, elle relie aux cours et au matériel qui l'utilisent,
et elle peut porter un diagramme structuré dans la page. C'est une lecture
autonome, pas une leçon.

## Où ça vit

Crée-la à partir de `templates/wiki/` : `example-entry.md` et son jumeau
`example-entry.fr.md`. Copie les deux, renomme-les avec ton slug, remplis-les, et
soumets les deux via le portail membre d'Espilon Learn. À l'ingestion, les
mainteneurs font un upsert de l'entrée, lancent la gate d'accents français sur
l'ensemble du corpus contre chaque surface FR, vérifient les références liées
contre le catalogue vivant, et la publient sous sa catégorie.

## Le template

```text
wiki/
  <slug>.md      EN : frontmatter + corps markdown + bloc diagram optionnel
  <slug>.fr.md   FR : traduit title et summary ; le corps est le markdown français
```

Le fichier d'appoint `.fr.md` ne traduit que le `title` et le `summary` du
frontmatter ; son corps est la prose française complète. Un corps FR manquant
retombe sur le corps anglais, donc une entrée à moitié traduite se rend quand
même, silencieusement en anglais.

## Référence des champs

### Frontmatter

```text
title, category, slug, order, summary, tags, terms, icon, published,
image, related_gear, related_courses, diagram
```

| Champ | Règle |
|---|---|
| `title`, `slug` | Le nom affiché et l'identifiant unique. |
| `category` | Groupe l'entrée sur l'index de catégorie. Porteur de sens. |
| `summary` | Une ou deux lignes sous le titre et sur l'index. |
| `tags` | Des mots-clés en texte libre. Mets entre guillemets tout ce qui a l'air numérique (un `802154` nu est interprété comme un entier). |
| `terms` | Les expressions qui s'auto-relient à cette entrée depuis la prose des leçons. |
| `icon` | Un court glyphe ou code. |
| `published` | `true` pour afficher l'entrée. |
| `image` | Image de couverture optionnelle (voir [Images](#images)). |
| `related_gear`, `related_courses` | Les slugs du matériel et des cours qui utilisent cette chose ; ils apparaissent comme des cartes. Mets un vrai slug de plateforme. Tu n'as pas le catalogue complet, donc les mainteneurs les valident à l'ingestion et retirent tout slug qui ne résout pas plutôt que de le livrer cassé. |
| `diagram` | Diagramme structuré dans la page, optionnel (voir [Images](#images)). |

Tout dans le frontmatter se dégrade proprement, donc une entrée à moitié remplie
se rend quand même. `slug` et `category` sont les deux qui doivent être justes.

### Le corps

Ouvre sur une définition d'un paragraphe introduite en gras, puis adapte le
squelette de sections que le template livre : ce que c'est, pourquoi c'est
important, comment ça marche, surface d'attaque et comment en évaluer une,
pièges, pour aller plus loin. Préfère une vraie commande exécutable à la prose
quand une commande est plus claire. Garde le jargon matériel et sécurité en
anglais dans les deux langues. N'invente pas de faits ; tire-les des entrées qui
existent déjà.

## Vérifications locales

La gate d'accents français du wiki est couplée au corpus, et la vérification des
références liées a besoin du catalogue complet de matériel et de cours, donc les
deux tournent côté mainteneur à l'ingestion et ne sont pas livrables ici. Avant
de soumettre, vérifie à la main :

- le fichier d'appoint FR porte de vrais accents sur le `title`, le `summary`, le
  corps, et les feuilles `fr:` de tout bloc `diagram:`, vérifiés mot à mot ;
- les `tags` qui ont l'air numériques sont entre guillemets ;
- le bloc `diagram:`, s'il est présent, est d'un type connu ;
- `related_gear` et `related_courses` portent de vrais slugs de plateforme.

## Topologie

```text
  entrée wiki
   |
   +-- <slug>.md       frontmatter EN + corps EN + bloc diagram: (optionnel)
   |                                             |
   |                                     les feuilles fr: dans diagram
   |                                     sont les libellés FR du diagramme
   +-- <slug>.fr.md    title FR + summary FR + corps FR
                          |
                   retombe sur le corps EN si absent
```

## Images

Deux choses distinctes :

- **`image`** : une image de couverture optionnelle. Référence-la comme
  `img/wiki/<slug>.webp` dans le frontmatter, et soumets le vrai webp à côté des
  deux fichiers markdown via le portail membre (un webp en 16:9, nommé d'après
  ton slug). Les mainteneurs le placent à ce chemin à l'ingestion ; tu ne commits
  pas un binaire dans une soumission de contenu. Au plus une par entrée. Sans
  image, retire la ligne `image:` et l'entrée se rend quand même.
- **`diagram`** : un diagramme structuré optionnel déclaré dans le frontmatter
  EN. Le schéma n'en accepte qu'un seul, et il est typé : choisis le type qui
  convient au sujet (`timing`, `wire`, `bus`, `tree` ou `partition`). Ses
  feuilles de texte portent des libellés `en` et `fr`. Préfère le diagramme
  structuré à une image matricielle là où le sujet est spatial ; supprime le bloc
  si un diagramme n'aide pas.

## Pièges

- **Un corps FR manquant ou vide.** L'entrée retombe sur l'anglais sans un mot
  d'avertissement, donc "on l'a traduit" et "le fichier FR est une ébauche" ont
  l'air identiques sur la page. Écris le corps français.
- **Des accents manquants hors du corps.** Ils ont déjà disparu dans le `summary`
  du frontmatter, dans les feuilles `fr:` du bloc `diagram:`, et dans la prose
  française portée par des commentaires de blocs de code. Vérifie chaque surface
  FR, pas seulement le corps.
- **Un `tag` numérique laissé sans guillemets.** `802154` devient un entier et le
  tag casse.
- **Plus d'un diagramme, ou un type de diagramme inconnu.** Le schéma tient un
  seul diagramme typé ; un second est retiré.
- **Un placeholder laissé dans `related_courses` ou `related_gear`.** Remplace-le
  par un vrai slug de plateforme ; les mainteneurs les valident à l'ingestion et
  retirent tout slug qui ne résout pas, donc un placeholder oublié perd la carte
  en silence.

## Limites connues

La gate d'accents français et la vérification des références liées sont couplées
au corpus et au catalogue, donc elles tournent côté mainteneur à l'ingestion et
ne peuvent pas être livrées ici. Lire le français n'est pas une vérification ;
vérifie-le mot à mot avant de soumettre.
