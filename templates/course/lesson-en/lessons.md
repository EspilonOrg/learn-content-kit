===== LESSON START =====
ORDER: 1
TITLE: The scenario you are walking into
TYPE: theory
ARCHETYPE_ROLE: hook
MODULE: intro
TLDR: "A concrete, real-world scenario that makes the rest of the course worth doing. State the target, the goal, and why a defender or attacker cares. Keep this under 500 characters: it is written to a String(500) column and the sync aborts if it is longer."
ESTIMATED_MINUTES: 6
LEARNING_OUTCOMES:
- Describe the target and the goal of this course in one sentence
- Explain why the naive approach is not enough
FURTHER_READING:
- wiki:uart
- kind: url
  title: A primary source the reader can verify
  url: https://example.org/primary-source
XP: 50
CONTENT:
# The scenario you are walking into

Open with the hook. Put the reader in front of a real situation: the bench, the
box, the capture, the goal. One or two short paragraphs. No theory yet, that is
lesson 2. The reader should finish this lesson wanting the next one.

This is archetype A (project-based): theory is motivated by a practical need and
delivered just in time. For the three archetypes and when to pick each, read
`docs/course.md`.

Replace this body with your own markdown. H2 headings, fenced code blocks and
tables all render. Where the model is spatial (a bus, a topology, a packet
layout), inline a hand-written `<svg>` in the markdown: it renders natively and
the diagram-maker owns the clean version. Do not reference a raster upload.
===== LESSON END =====

===== LESSON START =====
ORDER: 2
TITLE: The one concept you need first
TYPE: theory
ARCHETYPE_ROLE: theory
MODULE: intro
TLDR: "The minimum theory that unlocks the first attempt. Teach exactly what the next lesson needs and no more. A reader decides in ten seconds from this line whether to read or skip."
ESTIMATED_MINUTES: 10
LEARNING_OUTCOMES:
- State the mechanism in your own words
- Predict what you will observe when you apply it
FURTHER_READING:
- wiki:uart
XP: 100
CONTENT:
# The one concept you need first

Deliver the single idea the first attempt depends on. Prefer a runnable snippet
over prose when a command or a few lines of Python make the point concretely.

```python
# A short, runnable illustration beats a paragraph of description.
budget_db = -58 - (-108)
print("link margin: %d dB" % budget_db)
```

Keep it tight. The deep dive, if any, belongs in a later lesson tagged with
ARCHETYPE_ROLE deepdive.
===== LESSON END =====

===== LESSON START =====
ORDER: 3
TITLE: Prove it on the target
TYPE: practical
ARCHETYPE_ROLE: practice
MODULE: practice
ARTIFACT: challenge:example-static-challenge
TLDR: "The payoff lesson: the reader applies the concept to the shipped artifact and submits the flag. The ARTIFACT line wires this lesson to the challenge or lab it exercises."
ESTIMATED_MINUTES: 20
LEARNING_OUTCOMES:
- Apply the concept to the provided artifact
- Recover the answer and submit the flag
FURTHER_READING:
- wiki:uart
XP: 150
CONTENT:
# Prove it on the target

Walk the reader through doing the thing, on the real artifact this course ships.
End on the flag.

The `ARTIFACT:` header above wires this lesson to the resource it exercises.
Syntax is `<kind>:<slug>` where kind is `challenge`, `box` or `lab`. Here it
points at the companion static-challenge template by slug. When your submission
is ingested the resolver links the lesson to that resource; if it does not exist
yet the ingestion warns and continues, so wiring never blocks. Pin the exact
artifact bytes a lesson depends on in a top-level `_artifacts.yaml` in your
course folder (see `docs/course.md`).
===== LESSON END =====
