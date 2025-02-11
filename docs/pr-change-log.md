# Change log in PR

The **PR Change Log** workflow `pr-change-log.yml` allows handling automatic change log generation in a PR.

## Operation

By default the workflow will generate a change log for a PR to the branch `main`.
Optionally you can provide a `target-branch` input to generate the change log for a PR to a different branch.

Example:

```yaml

jobs:
  pr-change-log:
    uses: nxlabs-ch/shared-workflows/.github/workflows/pr-change-log.yml@main
    with:
      target-branch: develop
```
