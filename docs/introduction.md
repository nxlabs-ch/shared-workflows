# Introduction

This repository contains reusable workflows that can be used in other repositories.

See the GitHub documentation on [reusable workflows](https://docs.github.com/en/actions/learn-github-actions/reusing-workflows).

To use one of the workflows from your repository, just create a job that references it, such as:

``` yaml
jobs:
  version:
    uses: nxlabs-ch/shared-workflows/.github/workflows/version.yml@main
```

## Versioning

Every merge to `main` produces an annotated tag and a GitHub release, numbered `vX.Y.Z` according to
the types of the commits it contains. Both refs below are supported, and the choice is a trade-off:

``` yaml
uses: nxlabs-ch/shared-workflows/.github/workflows/version.yml@v1.13.1   # pinned
uses: nxlabs-ch/shared-workflows/.github/workflows/version.yml@main      # tracks head
```

**Pin to a release tag when you need your builds to stay reproducible.** A pinned caller is
unaffected by anything merged afterwards, and you adopt changes deliberately by bumping the tag and
reading the release notes. There is no floating major alias such as `@v1`, so a pin is an exact
version and updating it is a manual step.

**Use `@main` when you would rather have fixes and improvements immediately.** That is the faster
and generally more reliable path — you get build speed-ups, hardening and bug fixes the day they
land, without a dependency bump. The cost is that a workflow's internals can change between
releases: a toolchain swap, a different set of system packages, a stricter input validation. Such a
change is announced in the release notes, but it reaches an `@main` caller before those notes are
read. Examples in this repository install their own dependencies with the `dependencies` and
`latex-packages` inputs precisely so a caller can restore anything a default set stops providing.

One caveat applies to both: the version-check wrappers reference the shared composite action as
`nxlabs-ch/shared-workflows/.github/actions/check-version@main`, because a relative `uses:` does not
resolve when a reusable workflow is called from another repository. Pinning the workflow therefore
pins the job definition, but the composite action it calls is always the one on `main`.

Below is the documentation for each workflow.
