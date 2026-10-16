# Contribuer

English: [CONTRIBUTING.md](CONTRIBUTING.md)

Merci de vouloir ajouter du contenu à Espilon Learn. Ce fichier donne les règles
de la maison et la façon de proposer du contenu. Le pas à pas pour chaque type de
contenu est le `README.md` dans le dossier de template de ce type ; ceci est ce
qui s'applique à tous.

## Règles de la maison

Ce ne sont pas des préférences de style ; la plateforme et ses gates les
imposent.

- **Aucun tiret cadratin et aucun tiret demi-cadratin, nulle part.** Utilise un
  trait d'union simple. Cela vaut pour chaque fichier : la prose, les
  commentaires de code, le YAML, les messages de commit.
- **Aucun emoji, nulle part.**
- **Bilingue, anglais et français.** Le contenu est livré dans les deux langues.
  La vérité structurelle est l'anglais ; le français est une vraie traduction de
  la prose.
- **De vrais accents français, vérifiés mot à mot.** Du contenu français a déjà
  été livré accents retirés plus d'une fois, toujours parce que quelqu'un a tapé
  de l'ASCII plat puis a affirmé par lecture que les accents étaient là. Lire
  n'est pas une vérification. Là où un validateur existe, lance-le ; là où il
  n'y en a pas, vérifie chaque surface française mot à mot. Garde les noms
  d'outils et de protocoles en anglais dans les deux langues.
- **Aucune mention d'un fournisseur ou assistant d'IA** dans le contenu, les
  commits ou les docs.
- **Conventional Commits.** Par exemple `feat(course): add the LoRaWAN join
  course` ou `fix(wiki): restore the accent on the DNP3 summary`.

## Comment proposer du contenu

1. Choisis le type de contenu et lis le `README.md` dans son dossier de template.
2. Copie le template correspondant depuis `templates/` dans un dossier de travail
   et remplis-le. Garde la structure d'exemple ; remplace les valeurs d'exemple
   par les tiennes.
3. Lance chaque vérification locale que le doc liste pour ce type (voir
   `validators/README.md`). Une vérification qui n'a pas tourné n'est pas une
   vérification qui est passée ; une vérification au rouge n'est pas prête à être
   soumise.
4. Soumets via le portail membre d'Espilon Learn. Les mainteneurs examinent,
   ingèrent et publient les soumissions acceptées. Tu ne déploies rien toi-même.

## Quand quelque chose est ambigu

Si ce kit et un exemple publié se contredisent, ou si une convention n'a jamais
été écrite, demande via le portail avant de deviner. Choisir une option en
silence et la livrer est la façon dont une mauvaise convention se répand. Il est
toujours moins coûteux de demander.
