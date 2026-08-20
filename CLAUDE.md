# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A library of **reusable GitHub Actions workflows** (`workflow_call` only) plus one composite action, consumed by other `nxlabs-ch` repositories as
`uses: nxlabs-ch/shared-workflows/.github/workflows/<name>.yml@main`. There is no application code — the deliverable is the YAML itself, its documentation, and the tags/releases that consumers pin to.

Three coupled parts, all of which must be updated together:

| Part          | Location                                             | Note                                                                       |
| ------------- | ---------------------------------------------------- | -------------------------------------------------------------------------- |
| Workflows     | [.github/workflows/](.github/workflows/)             | Every file except `ci.yml` is a public API surface                         |
| Documentation | [docs/](docs/)                                       | One `.md` per workflow, listed in [docs/index.rst](docs/index.rst) toctree |
| Self-test     | [.github/workflows/ci.yml](.github/workflows/ci.yml) | Dogfoods every workflow against [samples/](samples/)                       |

## Commands

Documentation is the only thing buildable locally. It uses `uv` (not the `requirements.txt` at the root, which is legacy) and is driven from [docs/](docs/):

```bash
make -f uv-makefile -C docs install    # uv venv + uv sync
make -f uv-makefile -C docs html       # HTML into docs/_build/html
make -f uv-makefile -C docs latex      # xelatex-targeted .tex sources, for Tectonic (the default path)
make -f uv-makefile -C docs latexpdf   # pdflatex PDF, the uv-docs.yml path (needs texlive + latexmk)
make -f uv-makefile -C docs clean
```

To produce a PDF locally the same way CI does, compile the `latex` output with the same engine:

```bash
brew install tectonic
make -f uv-makefile -C docs latex
tectonic -X compile docs/_build/latex/shared-workflows.tex --outdir docs/_build/latex
```

`docs/Makefile` is the stock sphinx-quickstart one kept for the deprecated `docs.yml`; CI uses `uv-makefile` via the `makefile:` input.

There is no test runner. To validate a workflow change, add or adjust a job in `ci.yml` and push — CI is the test suite.

## Architecture

### Version checking is one composite action behind thin wrappers

[.github/actions/check-version/action.yml](.github/actions/check-version/action.yml) holds the whole implementation: strip the `v` prefix from the tag, run an `extract_cmd` shell pipeline with `$FILE` bound to the target file, compare, fail only when the expected version is non-empty (an empty expected version means a development build, which passes).

`c-version.yml`, `rust-version.yml`, `toml-version.yml`, `json-version.yml`, `yaml-version.yml`, `spec-version.yml`, `kicad-version.yml` and the generic `check-version.yml` each contain a checkout plus a call to that action with a format-specific `extract_cmd` and `label`. **Adding support for a new file format means adding a wrapper with a new `extract_cmd` — never reimplementing the comparison.**

Wrappers reference the action by absolute path `nxlabs-ch/shared-workflows/.github/actions/check-version@main`, not a relative path (relative `uses:` does not resolve when a reusable workflow is called from another repository). Consequence: **a change to the composite action is not exercised by PR CI — the PR run still uses `main`'s copy.** Action changes only take effect once merged. `docs/check-version.md` still describes the older relative-path approach; treat the YAML as authoritative.

### Release pipeline

`version.yml` is the head of every consumer pipeline and drives everything downstream:

- On a PR to `main`: computes the next version from commit-message types (dry run) and posts it as a PR comment.
- On a push to `main`: creates the annotated tag, creates the GitHub release with preface + changelog + postface, then force-updates `develop` to `main` via the GitHub API (fast-forward back-merge) using the `FF_MERGE_PAT` secret.
- Always outputs `version`, `tag`, `build`, `pep440`, the preface/postface content (raw and shell-escaped), and `changelog`.

Downstream jobs consume `needs.version.outputs.*`: version-check jobs take `tag`, build/deploy jobs take `version`. `deploy-gs.yml` and `deploy-release.yml` both download *all* artifacts produced in the run, re-zip each one, and publish — so any workflow that uploads an artifact automatically ends up in the release.

GitFlow is assumed: `develop` is the default branch, `main` is the release branch, and consumers need "Read and write permissions" under Settings → Actions → General (each section on that page has its own Save button).

### Commit messages control the version bump

`custom_release_rules` is duplicated verbatim in `version.yml` and `pr-change-log.yml` — keep them in sync. Types: `api`/`feature`/`revert` → minor, `breaking` → major, `build`/`ci`/`doc`/`docs`/`fix`/`perf`/`refactor`/`test` → patch. Commits outside this set do not bump anything (`default_bump: false`).

### The repo releases itself, so its own version must be bumped by hand

`ci.yml` runs `check-version` against `docs/pyproject.toml`. A release PR to `main` therefore needs a `build: update version to X.Y.Z for release` commit updating `version` in [docs/pyproject.toml](docs/pyproject.toml) to exactly what the tag will be, or CI fails on the mismatch. Confirm the computed version from the PR comment first.

### Documentation build

Three generations, all still present:

| Workflow              | Status                               | PDF toolchain                                |
| --------------------- | ------------------------------------ | -------------------------------------------- |
| `tectonic-docs.yml`   | **Default** — use it for new callers | Tectonic static binary, `latex` target       |
| `uv-docs.yml`         | Maintained sibling, not deprecated   | apt `texlive-*` + latexmk, `latexpdf` target |
| `docs.yml`            | Deprecated, `if: false` in `ci.yml`  | apt texlive, slower than 10 minutes          |

In `ci.yml` both `tectonic-docs` and `uv-docs` run (the latter with `artifact-suffix: "uv"` so their artifacts do not collide), and both are dependencies of the `deploy` and `release` jobs. `tectonic-docs` is the primary build — its PDF is the canonical one — but `uv-docs` gates the release too, deliberately: it is maintained for backward compatibility, so making every release wait on it proves the path still works. Both artifact sets therefore ship in each release, told apart by the `-uv` suffix. This dependency is load-bearing for a second reason: `deploy-gs.yml` and `deploy-release.yml` call `actions/download-artifact` with no `name:` or `pattern:`, so they publish whatever artifacts happen to exist in the run when their download step executes. Dropping either docs job from `needs:` does not remove its artifacts from the release, it just makes their presence a race. Keep both working when touching either.

All three share the same scaffolding: write the version into a `.version` file at the repo root, which [docs/conf.py](docs/conf.py) reads for `release` (falling back to `$GIT_VERSION_NUMBER`, then `development`); scrape the Sphinx `project` name out of `conf.py` by regex to name artifacts `documentation-<project>[-<suffix>]-{html,pdf}-<version>`; rename the PDF to `<base>[-<suffix>]-<version>.pdf`.

Where `tectonic-docs.yml` differs, and what a caller must satisfy:

- It calls the Makefile's **`latex`** target, not `latexpdf`, and runs `tectonic -X compile` on the generated sources itself. A custom Makefile must therefore expose `html` and `latex`.
- Tectonic is a XeTeX engine. pdflatex-targeted sources compile "successfully" but silently drop every non-ASCII glyph, so the workflow guards against it: it scans the generated `.tex` **preamble only** (`sed -n '/\begin{document}/q;p'`) for `\usepackage{fontspec}`, which Sphinx loads only under xelatex, and fails the build if absent. Body text may mention the package, hence the preamble-only scan.
- **Where `latex_engine` lives depends on the caller.** This repository builds its PDF both ways, so `conf.py` leaves the engine at its pdflatex default and the `latex` target in [docs/uv-makefile](docs/uv-makefile) passes `-D latex_engine=xelatex` for the Tectonic build only — setting it in `conf.py` here would break `uv-docs.yml`, whose apt list has no XeTeX binary. A project that uses only `tectonic-docs.yml` should do the opposite: set `latex_engine = "xelatex"` in its `conf.py` and drop the `-D` override.
- `latex_elements["sphinxsetup"] = "iconpackage=none"` in `conf.py` is load-bearing: Sphinx ≥ 7.4 decorates admonitions with FontAwesome, and Tectonic's bundle ships `fontawesome5.sty` without the `expl3.sty` it needs, which is a hard error.
- The Tectonic bundle is cached with `actions/cache` keyed on `conf.py`'s hash, with a `restore-keys` prefix so a `conf.py` edit refreshes the bundle rather than fetching it again. `TECTONIC_CACHE_DIR` is pinned explicitly because Tectonic's default location is platform dependent.
- The two PDFs are not visually identical — Tectonic/xelatex uses FreeSerif, pdflatex uses TeX Gyre. For customer-facing documents that matters; set `fontpkg` explicitly to keep a typeface.

`conf.py`'s `setup()` registers a `TaskListLaTeXTranslator` subclass via `app.set_translator("latex", ..., override=True)` — it used to monkey-patch `LaTeXTranslator`'s methods; do not regress to that. It overrides the bullet-list and list-item visitors so MyST task lists become an `itemize` whose labels are the `\emptybox`/`\checkedbox` macros defined in the `latex_elements` preamble. Without it the checkboxes vanish from the PDF silently, with no build warning: MyST emits them as raw HTML and Sphinx's LaTeX writer drops raw nodes that are not `latex` format. [docs/task-lists.md](docs/task-lists.md) exists to exercise this in every build — do not delete it.

## Conventions

- Pin `runs-on: ubuntu-24.04` on every job; pin third-party actions to a major tag.
- Every `workflow_call` input needs a `description`, and every optional one a `default`; these descriptions are the API contract users read.
- In `run:` steps, pass caller-supplied inputs through `env:` rather than `${{ }}` interpolation — an interpolated input is shell injection. `tectonic-docs.yml` is the reference for this, along with `set -euo pipefail`, retried/timeout-bounded `apt-get`, and a `timeout-minutes` on any step that touches the network.
- When adding a workflow: create `.github/workflows/<name>.yml`, add `docs/<name>.md` (Pre-requisites / Operation / Example sections, matching the existing pages), add the page to the `docs/index.rst` toctree, and wire a job into `ci.yml`.
- New sample fixtures go under [samples/](samples/) and get referenced from `ci.yml`.
- cspell dictionaries are scoped per directory: [.cspell.json](.cspell.json) at the root holds the shared terms, and [docs/.cspell.json](docs/.cspell.json) and [.github/.cspell.json](.github/.cspell.json) each `import` it and add only what their own tree needs. Put a new word in the narrowest file that covers it, and add jargon rather than rewording around it.
