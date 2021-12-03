# Introduction

This repository contains reusable workflows that can be used in other repositories.

See the GitHub documentation on [reusable workflows](https://docs.github.com/en/actions/learn-github-actions/reusing-workflows).

To use one of the workflows from your repository, just create a job that references it, such as:

``` yaml
jobs:
  version:
    uses: noveto-com/shared-workflows/.github/workflows/version.yml@main
```

Below is the documentation for each workflow.
