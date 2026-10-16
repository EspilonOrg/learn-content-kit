# <img src="assets/espilon-logo.png" alt="Espilon" width="48" align="top"> Kit de création de contenu Espilon Learn

English: [README.md](README.md)

Templates et documentation pour contribuer du contenu à Espilon Learn, la
plateforme d'apprentissage en cybersécurité à
[learn.espilon.net](https://learn.espilon.net), gérée par l'association Espilon.
Copie un template, remplis-le, lance les vérifications locales, et soumets via le
portail membre. Tu ne déploies jamais ; les mainteneurs ingèrent et publient les
soumissions acceptées.

## Sommaire

- [Ce que tu peux construire](#ce-que-tu-peux-construire)
- [Comment ça marche](#comment-ça-marche)
- [Lancer les vérifications locales](#lancer-les-vérifications-locales)
- [Règles de la maison](#règles-de-la-maison)
- [Licence](#licence)

## Ce que tu peux construire

| Type de contenu | Template à copier | Guide |
|---|---|---|
| Un static challenge | [`templates/static-challenge/`](templates/static-challenge) | [`templates/static-challenge/README.fr.md`](templates/static-challenge/README.fr.md) |
| Un lab Model-B | [`templates/model-b-lab/`](templates/model-b-lab) | [`templates/model-b-lab/README.fr.md`](templates/model-b-lab/README.fr.md) |
| Un cours | [`templates/course/`](templates/course) | [`templates/course/README.fr.md`](templates/course/README.fr.md) |
| Une entrée wiki | [`templates/wiki/`](templates/wiki) | [`templates/wiki/README.fr.md`](templates/wiki/README.fr.md) |

Chaque template est un exemple réel et fonctionnel, pas une esquisse, et s'ouvre
sur son propre guide (le `README.md` dans le dossier). Le template
static-challenge passe les validateurs livrés tel quel.

- Un **static challenge** est un casse-tête autonome : des fichiers
  téléchargeables et un flag que le joueur récupère à partir de ces seuls
  fichiers. Pas de serveur.
- Un **lab Model-B** est une cible vivante, par session, que le joueur attaque
  depuis sa propre machine. Le lab ne livre que la cible ; le flag transite par
  le protocole.
- Un **cours** est une séquence bilingue de leçons qui enseigne un sujet et se
  termine en l'appliquant à un challenge ou à un lab.
- Une **entrée wiki** est une page de référence bilingue sur une seule chose :
  une puce, un protocole, un bus, un concept.

## Comment ça marche

1. Copie le template de ton type de contenu dans un dossier de travail.
2. Remplis-le en suivant le `README.md` dans le dossier du template.
3. Lance les vérifications locales (voir
   [`validators/README.md`](validators/README.md) et ce guide).
4. Soumets via le portail membre d'Espilon Learn.

Chaque guide dit exactement quelles vérifications tu lances localement et
lesquelles les mainteneurs exécutent à l'ingestion.

## Lancer les vérifications locales

```bash
pip install pyyaml

# Static challenge : construis l'artefact, prouve qu'il se résout, valide, scanne le FR.
python3 -I templates/static-challenge/generate.py
python3 -I templates/static-challenge/solve.py
python3 -I validators/validate_static_meta.py templates/static-challenge
python3 -I validators/check_fr_accents.py templates/static-challenge

# Lab Model-B : vérification des champs et du compose.
python3 -I validators/check_lab_yaml.py templates/model-b-lab
```

Pointe les validateurs vers ton propre dossier plutôt que vers le template. Les
cours et les entrées wiki portent des vérifications qui ont besoin de la
plateforme ou du corpus de contenu complet ; celles-ci tournent côté mainteneur à
l'ingestion.

## Règles de la maison

Le contenu est bilingue (anglais et français), porte de vrais accents français,
et n'utilise aucun emoji ni aucun tiret cadratin ou demi-cadratin. Les règles
complètes et la façon de proposer du contenu sont dans
[`CONTRIBUTING.fr.md`](CONTRIBUTING.fr.md).

## Licence

MIT. Voir [`LICENSE`](LICENSE).

Le nom et le logo Espilon sont des marques de l'association Espilon et ne sont
pas couverts par la licence MIT. La licence MIT s'applique aux templates, aux
scripts et à la documentation de ce dépôt, pas aux marques Espilon.
