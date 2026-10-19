# The Measurability Trap: Evidence Requirements and the Allocation of Innovation: Scarcity, endogenous applications, and the optimal direction of evidence adjustment

**Dr. Jan-Hendrik Weinert** · Working paper · Editorial edition F1, 19 October 2026

[Read the paper](paper.pdf) · [LaTeX source](manuscript.tex) · [Editable Markdown](manuscript.md) · [Reproduction instructions](REPRODUCIBILITY.md)

## Abstract

Evidence requirements affect both which projects apply and which receive scarce funding. We derive optimal screening rules when privately informed teams obtain funding benefits and face heterogeneous application costs. In a two-class exponential-score model, the allocation reduces to a strictly convex resource frontier. A common standardized cutoff is optimal at one interior budget despite unequal verification precision. Above that budget, the optimum tightens the standard for the more informative class and relaxes it for the other; below it, the direction reverses. Stronger private funding benefits can improve funded quality while reducing net organizational value through application costs. Complete proofs and synthetic computations support this model-specific scarcity reversal; no firm-level evidence is reported.

## Contents

- `paper.pdf`: complete paper, including proofs, bibliography and appendices.
- `manuscript.tex`: authoritative mathematical typesetting source; `manuscript.md`: editable alternative.
- Calculation scripts, recorded synthetic outputs, and the paper-specific source ledgers and prospective research protocols.
- `reproduce.py`, `requirements.txt`: one entry point and dependencies for the supplied analysis.
- `build_paper.sh`: rebuilds the current PDF from the LaTeX source without replacing the supplied PDF.
- `CITATION.cff`: citation metadata; `SHA256SUMS.txt`: published payload checksums.

`code/replicate.R` is an optional base-R scalar replication. It was not executed in the publication preparation; the Python suite is the executed reference.

## Reproduce the calculations

Use Python 3.12. From the repository root, create a virtual environment and run:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 reproduce.py
```

The analysis uses synthetic inputs or exact model primitives supplied with the code. It requires no private organizational data, API credentials or data download. Installing dependencies may require access to a package index. Full analytical proofs remain in the paper; finite computations supplement those proofs.

## Rebuild the paper

With TeX Live and the packages declared in `manuscript.tex` installed:

```sh
bash build_paper.sh
```

The result is `build/manuscript.pdf`. Compile from the repository root so figure paths resolve. The supplied `paper.pdf` is the visually checked publication edition. PDF byte hashes can vary between rebuilds because of timestamps and toolchain metadata. Do not regenerate this edition's LaTeX through Pandoc when a matching layout is required.

## Research status

This is a theoretical working paper with synthetic computational illustrations. Any empirical or field protocol included here is prospective, and no reported synthetic output is an observed firm result. Publication of this repository does not imply journal acceptance or empirical validation. The paper states its model-specific assumptions and limitations.

## Citation

Weinert, Jan-Hendrik (2026). *The Measurability Trap: Evidence Requirements and the Allocation of Innovation: Scarcity, endogenous applications, and the optimal direction of evidence adjustment*. Working paper, editorial edition F1.
Use the repository's citation metadata when citing or reusing the work.
