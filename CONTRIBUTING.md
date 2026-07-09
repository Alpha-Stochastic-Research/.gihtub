# Contributing to Alpha Stochastic Research

Thank you for your interest in contributing to **Alpha Stochastic Research (ASR)**.

ASR is an independent quantitative finance research laboratory focused on rigorous, transparent, and reproducible research at the intersection of financial markets, mathematics, statistics, stochastic modelling, scientific computing, and artificial intelligence.

We welcome contributions that improve the scientific quality, technical reliability, documentation, reproducibility, and educational value of ASR projects.

---

## Contribution Philosophy

ASR values contributions that are:

- Scientifically rigorous
- Clearly documented
- Reproducible
- Transparent about assumptions and limitations
- Useful for students, researchers, and practitioners
- Aligned with open science principles

We encourage thoughtful contributions over large, unstructured changes.

---

## Ways to Contribute

You can contribute by:

- Fixing bugs
- Improving documentation
- Correcting mathematical notation
- Adding references or literature notes
- Improving Python implementations
- Adding numerical experiments
- Creating educational notebooks
- Improving figures and visualizations
- Reproducing research papers
- Adding tests
- Improving GitHub Actions workflows
- Suggesting new research directions

---

## Before You Start

Before opening an issue or pull request:

1. Search existing issues and discussions.
2. Check whether a similar contribution already exists.
3. Make sure the contribution fits the scientific scope of the repository.
4. Keep the contribution focused and easy to review.

For major research contributions, please open a **Research Proposal** issue first.

---

## Development Workflow

We recommend the following workflow.

```bash
git clone https://github.com/Alpha-Stochastic-Research/<repository-name>.git
cd <repository-name>
```

Create a new branch:

```bash
git checkout -b feature/short-description
```

Make your changes, then commit:

```bash
git add .
git commit -m "feat: add short description"
```

Push your branch:

```bash
git push origin feature/short-description
```

Then open a Pull Request on GitHub.

---

## Branch Naming

Use clear branch names.

Examples:

```text
feature/bachelier-option-pricing
fix/brownian-motion-simulation
docs/update-readme
paper/fix-latex-notation
research/black-scholes-reproduction
ci/update-python-workflow
```

---

## Commit Message Style

Use concise and meaningful commit messages.

Recommended prefixes:

```text
feat:     new feature or implementation
fix:      bug fix
docs:     documentation update
paper:    LaTeX or manuscript update
fig:      figure or visualization update
test:     tests
ci:       GitHub Actions or automation
refactor: code restructuring
research: research-related contribution
```

Examples:

```text
feat: implement Bachelier call pricing formula
docs: improve installation instructions
paper: correct notation in option pricing derivation
ci: add Python workflow
research: add historical notes on Bachelier 1900
```

---

## Python Code Guidelines

When contributing Python code:

- Prefer clear and readable code over overly compact code.
- Use descriptive function and variable names.
- Add docstrings for public functions.
- Keep numerical assumptions explicit.
- Fix random seeds when reproducibility matters.
- Avoid hidden dependencies.
- Save generated figures in the appropriate folder.
- Document parameters, units, and conventions.

Example:

```python
def bachelier_call_price(p0: float, strike: float, sigma: float, maturity: float) -> float:
    """
    Compute the European call price under the Bachelier model.

    Parameters
    ----------
    p0 : float
        Initial price.
    strike : float
        Option strike.
    sigma : float
        Absolute volatility parameter.
    maturity : float
        Time to maturity.

    Returns
    -------
    float
        Bachelier call option price.
    """
```

---

## Mathematical and Scientific Standards

For mathematical or research contributions:

- Define all variables clearly.
- State assumptions explicitly.
- Include references when appropriate.
- Distinguish exact results from numerical approximations.
- Report numerical tolerances when relevant.
- Explain limitations of models.
- Avoid overstating empirical results.
- Prefer reproducible derivations and simulations.

When reproducing a paper, include:

- Full citation
- Original model assumptions
- Implemented equations
- Numerical setup
- Validation method
- Known limitations

---

## LaTeX and Paper Contributions

For LaTeX files:

- Ensure the document compiles without errors.
- Keep notation consistent.
- Avoid unnecessary packages.
- Use clear mathematical formatting.
- Include references where needed.
- Do not commit temporary build files.

Do not commit files such as:

```text
*.aux
*.log
*.out
*.toc
*.synctex.gz
```

These should be excluded through `.gitignore`.

---

## Documentation Guidelines

Good documentation should help readers understand:

- What the project does
- Why it matters
- How to install it
- How to reproduce results
- What assumptions are used
- Where the relevant references are
- How to interpret figures and outputs

Documentation should be written in clear, professional English.

---

## Reproducibility Requirements

Whenever possible, contributions should include:

- Clear installation instructions
- Required dependencies
- Fixed random seeds
- Reproducible scripts or notebooks
- Documented parameters
- Saved figures or outputs
- References to original sources
- Explanation of numerical results

A contribution is stronger when another person can reproduce it from a clean environment.

---

## Pull Request Checklist

Before submitting a Pull Request, verify that:

- [ ] The contribution is focused and clearly described.
- [ ] Code runs without errors.
- [ ] Documentation has been updated where necessary.
- [ ] Mathematical notation is clear and consistent.
- [ ] Assumptions and limitations are documented.
- [ ] Numerical results are reproducible.
- [ ] References are provided when relevant.
- [ ] The Pull Request template has been completed.

---

## Issue Guidelines

Use the appropriate issue template:

- **Bug Report** — for errors, unexpected results, or broken functionality.
- **Feature Request** — for software, documentation, or workflow improvements.
- **Research Proposal** — for new scientific directions or paper reproductions.
- **Question** — for general questions about implementation, theory, or usage.

Please provide enough context for maintainers and contributors to respond effectively.

---

## Review Process

Pull Requests are reviewed for:

- Scientific correctness
- Code clarity
- Reproducibility
- Documentation quality
- Alignment with ASR research goals
- Maintainability
- References and validation

Review comments are part of the collaborative scientific process. Please treat them as constructive feedback.

---

## Community Standards

All contributors are expected to follow the ASR Code of Conduct.

We aim to maintain a professional, respectful, and intellectually rigorous environment for students, researchers, developers, and practitioners.

---

## Contact

For research-related questions, contact:

**research@asr-lab.online**

Website:

**https://asr-lab.online**

---

## Final Note

Alpha Stochastic Research is committed to building a transparent and reproducible open-source research ecosystem in quantitative finance.

Thank you for helping us improve the quality, accessibility, and scientific value of our work.
