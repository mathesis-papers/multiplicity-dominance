# Exact support for Petrov–Scott §8.5, Conjecture 8.22 and Problem 8.23

## Mathematical contents

`note.pdf` and `note.tex` give exact support and dominance as an application and alternative proof of Philippe Flajolet's 1980 Stieltjes–Rogers coefficient formula (Proposition 3B, p. 132). The proof identifies composition multiplicities with ordered-tree depth profiles through a noncrossing-partition–Motzkin–Dyck bijection. This classical coefficient formula is credited to Flajolet, not presented as a new enumeration theorem.

Flajolet's Proposition 10(i), pp. 150–151, states the tree-profile form and attributes an independent derivation to the earlier work of R. C. Read (1979), *The chord intersection problem*, DOI 10.1111/j.1749-6632.1979.tb32822.x, in its footnote 2. The attribution to Read is made through Flajolet. The profile formula was also proved by Darij Grinberg on MathOverflow on 20 February 2015 (answer 198057); Ira Gessel's answer 198059 identifies Flajolet's coefficient formula. These earlier profile results are distinguished from the source-specific partition-fiber identification and matrix-support theorem.

The source questions are Conjecture 8.22 and Problem 8.23 of Leonid Petrov and Jeanne Scott, *Random Fibonacci Words via Clone Schur Functions*, arXiv:2412.21126v2, Section 8.5; the journal version is *Forum of Mathematics, Sigma* 14 (2026), e15, DOI 10.1017/fms.2025.10165. The note distinguishes the printed odd-length splitting from the weight-preserving correction and states the conclusions for both matrices.

The journal PDF updated on 5 February 2026 retains the odd-length bound. The 27 March 2026 corrigendum, DOI 10.1017/fms.2026.10186, records notation-rendering corrections and gives no replacement splitting formula.

Proved corollaries cover partition statistics and canonical lifts (Lemma 8.17, Proposition 8.18 and Remark 8.19), explicit moment coefficients (Corollary 8.20), both one-alphabet specialization counts (§8.5, opening paragraph), splitting injectivity and projection surjectivity (Lemma 8.14), positive diagonal entries, rational invertibility and support counts by hike. The source's already-proved statements are credited to Petrov–Scott (2025). The unasserted converse to dominance fails at `(221,212)`, whose entry is zero. Other questions listed in the source's Section 18 are outside the note's coverage.

## Files

- `note.tex`: self-contained LaTeX, including its bibliography.
- `note.pdf`: typeset note.
- `metadata.json`: authors, license, problem coverage and the pinned Lean declaration.
- `verify.py`: standard-library Python exact-integer checks.
- `checks.json`: deterministic output of the checker.
- `README.md`: these instructions.

## Build the note

Use Tectonic 0.17.0:

```sh
tectonic --untrusted --outdir . note.tex
```

Alternatively, use a standard LaTeX installation with the `geometry`, `amsmath`, `amssymb`, `amsthm`, `booktabs`, `array` and `hyperref` packages:

```sh
pdflatex -interaction=nonstopmode -halt-on-error note.tex
pdflatex -interaction=nonstopmode -halt-on-error note.tex
```

The bibliography is embedded; no BibTeX invocation or additional source files are needed. Tectonic may download standard TeX resources on its first invocation.

## Reproduce the finite checks

Use Python 3.9 or later, with no third-party packages:

```sh
python3 verify.py --output checks-rebuilt.json
cmp checks.json checks-rebuilt.json
```

The checker enumerates all 26,442 set partitions of sizes 1 through 9 and filters noncrossing partitions directly from consecutive-block arcs. It independently enumerates Dyck paths through semilength 9 and compares their height-profile counts with the composition multiplicities. It checks all 87,840 ordered pairs of Fibonacci words through weight 12, and all 65,535 positive compositions through weight 16. All 64 entries of Figure 8 agree with the weight-preserving matrix.

It also checks 65,535 canonical lifts through weight 16; statistics, moment-polynomial coefficients and one-alphabet specialization counts through weight 9; exact literal support, positive diagonal entries and refined support counts through weight 12; and the explicit converse counterexample. For common hike `p>=1`, the corrected support requires `a_i>=b_i` at every coordinate `2<=i<=p+1`; the literal matrix additionally requires `a_(p+1)=b_(p+1)` when `p>=2`. The corrected hike-`p` support count is `binomial(n,2p)`; for `n>=2` the literal total is `2^(n-2)+1+binomial(n-1,2)`.

The written proofs establish the results for every positive weight. Finite checks provide additional exact examples and consistency checks, not an all-weight proof.

## Lean coverage

The declaration `D5.S3.Combinatorics.YoungFibonacci.PetrovScottMultiplicityDominance.result` concerns the literal fixed-weight matrix, including the printed odd-length bound. Its conclusion is upper triangularity, prefix dominance on nonzero entries, and equal hike.

Pinned declaration source:

https://github.com/the-omega-institute/trureturing/blob/e277c80d045570daf43bd03b4e313f7ce457b4e2/D5/S3/Combinatorics/YoungFibonacci/PetrovScottMultiplicityDominance.lean

The product formula, corrected splitting, corrected-matrix theorem, and exact support criterion have written proofs in the note. The source's Figure 8 belongs to the corrected interpretation.

The word constructor `D5.S1.Words.UnaryGapWords.gap` concatenates prescribed unary runs separated by a given list; the dominance declaration uses it for reverse-word comparisons. It makes no assertion about the multiplicity formula:

https://github.com/the-omega-institute/trureturing/blob/e277c80d045570daf43bd03b4e313f7ce457b4e2/D5/S1/Words/UnaryGapWords.lean

## Attribution and license

Authors, in order: Haobo Ma (ChronoAI Pte Ltd, Singapore); Wenlin Zhang (National University of Singapore; ChronoAI Pte Ltd, Singapore).

License: Creative Commons Attribution 4.0 International, `cc-by-4.0`.
