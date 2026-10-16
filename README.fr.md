# <img src="assets/espilon-logo.png" alt="Espilon" width="48" align="top"> Kit de création de contenu Espilon Learn

English: [README.md](README.md)

Ce dépôt est l'ensemble canonique des templates et de la documentation pour
contribuer du contenu à Espilon Learn, la plateforme d'apprentissage en
cybersécurité à [learn.espilon.net](https://learn.espilon.net). Elle est gérée
par Espilon, une association à but non lucratif.

Si tu veux construire un lab, un challenge, un cours ou une page wiki et le
livrer à la plateforme, c'est ici que tu commences. Copie un template,
remplis-le, lance les vérifications locales, et soumets-le via le portail membre
d'Espilon Learn. Tu ne déploies rien toi-même ; les mainteneurs ingèrent et
publient les soumissions acceptées.

## Ce que tu peux construire

| Ce que tu construis | Copie ce template | Suis ce doc |
|---|---|---|
| Un static challenge | [`templates/static-challenge/`](templates/static-challenge) | [`docs/static-challenge.fr.md`](docs/static-challenge.fr.md) |
| Un lab Model-B | [`templates/model-b-lab/`](templates/model-b-lab) | [`docs/model-b-lab.fr.md`](docs/model-b-lab.fr.md) |
| Un cours | [`templates/course/`](templates/course) | [`docs/course.fr.md`](docs/course.fr.md) |
| Une entrée wiki | [`templates/wiki/`](templates/wiki) | [`docs/wiki-entry.fr.md`](docs/wiki-entry.fr.md) |

Chaque template est un exemple réel et fonctionnel, pas une esquisse. Le template
static-challenge passe les validateurs livrés tel quel, et chaque doc te dit
exactement quelles vérifications tu peux lancer localement et lesquelles les
mainteneurs exécutent à l'ingestion.

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

## Déroulé d'utilisation

1. Copie le template de ton type de contenu dans un dossier de travail.
2. Remplis-le en suivant le doc correspondant sous `docs/`.
3. Lance les vérifications locales (voir `validators/README.md` et le doc par
   type).
4. Soumets via le portail membre d'Espilon Learn.

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
l'ingestion, et chaque doc par type dit exactement quelles vérifications tu
lances localement et lesquelles sont côté mainteneur.

## Règles de la maison

Le contenu est bilingue (anglais et français), porte de vrais accents français,
et n'utilise aucun emoji ni aucun tiret cadratin ou demi-cadratin nulle part.
Voir `CONTRIBUTING.md` pour les règles complètes et comment proposer du contenu.

## Licence

MIT. Voir `LICENSE`.

Le nom et le logo Espilon sont des marques de l'association Espilon et ne sont
pas couverts par la licence MIT. La licence MIT s'applique aux templates, aux
scripts et à la documentation de ce dépôt, pas aux marques Espilon.
