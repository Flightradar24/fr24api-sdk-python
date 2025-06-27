# Contributing to fr24api-sdk-python

We welcome your contributions! Please follow these guidelines to get started.

## 1. Reporting Issues

* Search existing issues before opening a new one.
* Provide:

  * Clear title and description
  * Steps to reproduce
  * Version of `fr24sdk`, Python, and OS
  * Relevant logs or errors

## 2. Contributing Code

1. Fork and clone the repo
2. Create a feature branch: `git checkout -b feature/desc`
3. Install dev dependencies:

   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -e '.[dev]'
   ```
4. Implement changes and add tests in `tests/`
5. Run:

   ```bash
   pre-commit run --all-files
   pytest --cov
   ```
6. Commit using [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) and reference issues
7. Push branch and open a PR against `main`

## 3. CI & Testing

* CI runs lint, type-check, and tests on GitHub Actions
* Ensure all checks pass before merging

Thanks for helping improve the SDK!
