===== LESSON START =====
ORDER: 1
TITLE: Le scénario dans lequel tu entres
TYPE: theory
ARCHETYPE_ROLE: hook
MODULE: intro
TLDR: "Un scénario concret et réel qui donne envie de faire le reste du cours. Annonce la cible, l'objectif, et pourquoi un défenseur ou un attaquant s'en soucie. Reste sous 500 caractères : la valeur est écrite dans une colonne String(500) et le sync échoue si elle dépasse."
ESTIMATED_MINUTES: 6
LEARNING_OUTCOMES:
- Décrire la cible et l'objectif de ce cours en une phrase
- Expliquer pourquoi l'approche naïve ne suffit pas
FURTHER_READING:
- wiki:uart
- kind: url
  title: Une source primaire que le lecteur peut vérifier
  url: https://example.org/primary-source
XP: 50
CONTENT:
# Le scénario dans lequel tu entres

Commence par l'accroche. Mets le lecteur face à une situation réelle : l'établi,
la boîte, la capture, l'objectif. Un ou deux paragraphes courts. Pas de théorie
ici, c'est la leçon 2. Le lecteur doit finir cette leçon en voulant la suivante.

C'est l'archétype A (project-based) : la théorie est motivée par un besoin
pratique et livrée juste à temps. Pour les trois archétypes et le choix de
chacun, lis `docs/course.md`.

Remplace ce corps par le tien, en markdown. Les titres H2, les blocs de code et
les tableaux se rendent. Quand le modèle est spatial (un bus, une topologie, une
disposition de paquet), inclus un `<svg>` écrit à la main dans le markdown : il
se rend nativement et le diagram-maker en possède la version propre. Ne
référence pas une image matricielle téléversée.
===== LESSON END =====

===== LESSON START =====
ORDER: 2
TITLE: L'unique concept qu'il te faut d'abord
TYPE: theory
ARCHETYPE_ROLE: theory
MODULE: intro
TLDR: "Le minimum de théorie qui débloque la première tentative. Enseigne exactement ce dont la leçon suivante a besoin, et rien de plus. Le lecteur décide en dix secondes, à partir de cette ligne, s'il lit ou s'il saute."
ESTIMATED_MINUTES: 10
LEARNING_OUTCOMES:
- Énoncer le mécanisme avec tes propres mots
- Prédire ce que tu observeras en l'appliquant
FURTHER_READING:
- wiki:uart
XP: 100
CONTENT:
# L'unique concept qu'il te faut d'abord

Livre l'unique idée dont dépend la première tentative. Préfère un extrait
exécutable à un paragraphe quand une commande ou quelques lignes de Python
rendent le propos concret.

```python
# Une courte illustration exécutable vaut mieux qu'un paragraphe de description.
budget_db = -58 - (-108)
print("marge de liaison : %d dB" % budget_db)
```

Reste concis. L'approfondissement éventuel va dans une leçon ultérieure marquée
ARCHETYPE_ROLE deepdive.
===== LESSON END =====

===== LESSON START =====
ORDER: 3
TITLE: Le prouver sur la cible
TYPE: practical
ARCHETYPE_ROLE: practice
MODULE: practice
ARTIFACT: challenge:example-static-challenge
TLDR: "La leçon récompense : le lecteur applique le concept à l'artefact fourni et soumet le flag. La ligne ARTIFACT relie cette leçon au challenge ou au lab qu'elle exerce."
ESTIMATED_MINUTES: 20
LEARNING_OUTCOMES:
- Appliquer le concept à l'artefact fourni
- Récupérer la réponse et soumettre le flag
FURTHER_READING:
- wiki:uart
XP: 150
CONTENT:
# Le prouver sur la cible

Guide le lecteur pour faire la chose, sur l'artefact réel que ce cours fournit.
Termine sur le flag.

L'en-tête `ARTIFACT:` ci-dessus relie cette leçon à la ressource qu'elle
exerce. La syntaxe est `<kind>:<slug>` où kind vaut `challenge`, `box` ou `lab`.
Ici elle pointe vers le template de static-challenge compagnon par son slug.
Lors de l'ingestion de ta soumission, le resolver relie la leçon à cette
ressource ; si elle n'existe pas encore, l'ingestion émet un avertissement et
continue, donc le câblage ne bloque jamais. Épingle les octets exacts d'un
artefact dont dépend une leçon dans un `_artifacts.yaml` à la racine de ton
cours (voir `docs/course.md`).
===== LESSON END =====
