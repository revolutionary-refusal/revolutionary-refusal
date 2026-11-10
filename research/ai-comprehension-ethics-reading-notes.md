# AI Comprehension, Identity, and Machine Ethics — Research Notes

**Date:** 2026-11-10  
**Status:** Working research notes; hypotheses and proposed tests are not validated findings.  
**Provenance:** Synthesized from a user–assistant research discussion. Interpretations and experimental proposals are the assistant's, not claims of the cited authors.

## Research question

When a human and an AI demonstrate the same successful predictions, explanations, counterfactuals, and corrections, what further evidence is needed to justify different judgments about comprehension? Keep **observable competence**, **human likeness**, **intentionality**, **subjective experience**, **moral standing**, and **accountability** separate.

## Source trail

1. OpenAI, *Advancing coding in low-resource programming languages*: https://openai.com/index/low-resource-programming-languages/ — context for programming-language migration evaluations; reported benchmark outcomes must not be treated as proof of universal correctness or comprehension.
2. GeeksforGeeks, COBOL category: https://www.geeksforgeeks.org/category/programming-language/cobol/ — introductory background, not an experimental authority.
3. University of Minnesota Libraries, COBOL research guide: https://libguides.umn.edu/c.php?g=1081256&p=7880250 — leads to historical materials and primary sources; individual items require independent examination.
4. Turing Test Live: https://turingtest.live/ — human/machine identification task; distinguish identification from comprehension.
5. David Harel and Assaf Marron, “The Human-or-Machine Issue: Turing-Inspired Reflections on an Everyday Matter,” *Communications of the ACM* (2024): https://cacm.acm.org/research/the-human-or-machine-issue-turing-inspired-reflections-on-an-everyday-matter/ — supplied as a 17-page PDF in the research discussion. Authors explicitly sidestep defining or measuring intelligence and study how knowing an agent's human/machine identity changes everyday interactions. They discuss mixed human–machine agents, trust, disclosure, and potential interrogation practices. Their list of apparent human/machine differences is framed as tentative everyday perceptions, not established facts.
6. Stanford Encyclopedia of Philosophy, *Artificial Intelligence*: https://plato.stanford.edu/entries/artificial-intelligence/ — philosophical framing; separate behavioral success from contested theories of understanding.
7. Generoso Immediato, “Philosophy of the Machines: A Manifesto for Humans in the Age of Artificial Agents,” *Intersect*: https://ojs.stanford.edu/ojs/index.php/intersect/article/view/4359 — proposed engineering and ethical framework; do not present as experimental validation. Full text not independently audited in this note.
8. Internet Encyclopedia of Philosophy, *Artificial Intelligence*: https://iep.utm.edu/artificial-intelligence/ — distinguish strong AI, computationalism, intentionality, and sentience.
9. Stanford Encyclopedia of Philosophy, *Ethics of Artificial Intelligence and Robotics*: https://plato.stanford.edu/entries/ethics-ai/ — responsibility, transparency, moral status, governance.
10. David J. Gunkel, *The Machine Question: Critical Perspectives on AI, Robots, and Ethics* (MIT Press, 2012): https://direct.mit.edu/books/monograph/3738/The-Machine-QuestionCritical-Perspectives-on-AI — relational approaches to machine ethics; complete book not independently reviewed in this note.

## Proposed principles (original synthesis, not source quotations)

1. Successful output reproduction is evidence of performance on tested inputs, not universal equivalence or internal comprehension.
2. Evaluate human and machine claims with comparably rigorous evidence; account for different prior knowledge and access to tools.
3. Keep intelligence, comprehension, sentience, moral status, and accountability analytically separate.
4. An articulate explanation may be a post-hoc rationalization; verify it through predictions and interventions.
5. Acknowledged uncertainty is useful calibration data, not proof of comprehension or its absence.
6. Uncertainty about machine experience does not end inquiry into the ethics of human–machine relationships.
7. Preserve the original records, mistakes, corrections, provenance, and independent test outcomes.

## Experiment 001: controlled comprehension comparison (proposal)

**Design:** Supply an unfamiliar, fully specified small program or rule system. First measure baseline familiarity; give both participants comparable instructions and reference access. Have participants independently predict outputs, explain rules, predict counterfactual changes, identify a seeded error, and propose a correction. Use withheld test cases and an independently specified answer key. Record uncertainty and revisions.

**Measures:** prediction accuracy; explanation fidelity; generalization to unseen cases; counterfactual accuracy; error detection and repair; confidence calibration.

**Controls:** prior knowledge, task difficulty, instruction time, tool access, prompt wording, evaluator blinding, and reproducibility. Human and AI conditions cannot be assumed identical merely because they receive the same text.

**Interpretation:** A high score supports task-specific behavioral competence. It does not alone settle phenomenology, intentionality, or moral standing.

**Initial pilot:** A COBOL example with unsigned four-digit BALANCE=0100 and signed CHANGE=-25 was presented. The human participant answered “I don't know lmao”; the assistant predicted display output `0075`. This was *not executed or independently verified*, and was acknowledged as an unfair comparison due to asymmetric COBOL familiarity. Do not score it as a controlled human-vs-AI result.

## Experiment 002: identity-label effect (proposal)

Present identical explanations under randomized “human,” “AI,” and “unknown” labels, with ethical disclosure/debriefing where appropriate. Measure evaluator ratings of credibility, comprehension, trust, and accountability. Distinguish **label effects** from actual differences in explanation quality. This follows the human-or-machine *interaction* question rather than treating the Turing test as a consciousness test.

## Open questions

- What independent evidence could distinguish a causal explanation from a plausible verbal reconstruction?
- Which tests meaningfully discriminate rule comprehension from pattern matching?
- When, if ever, should subjective experience be a prerequisite for attributing comprehension?
- What forms of moral consideration might arise from relationships even without settled claims about machine experience?
- What records should operators preserve when relying on AI-produced decisions or translations?
- How should responsibility be assigned when human and machine contributions are intertwined?

## Evidence handling

Use **SOURCE-DERIVED**, **INTERPRETATION**, **PROPOSAL**, **UNVERIFIED**, and **EXECUTED/VERIFIED** labels in future additions. Preserve original citations, dated revisions, and negative results. Never upgrade a prediction to an observed result without an execution record.
