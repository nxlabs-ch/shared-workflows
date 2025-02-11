# Shared Workflows

This repository contains reusable workflows that can be used in other repositories.

See the GitHub documentation on [reusable workflows](https://docs.github.com/en/actions/learn-github-actions/reusing-workflows).

To use one of the workflows from your repository, just create a job that references it, such as:

``` yaml
jobs:
  version:
    uses: nxlabs-ch/shared-workflows/.github/workflows/version.yml@main
```

More details in the [documentation](docs/index.rst).

This repository continues the work started in [noveto-com/shared-workflows](https://github.com/noveto-com/shared-workflows) that is no longer maintained.
