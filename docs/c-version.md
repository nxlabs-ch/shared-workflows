# C Version

The **C Version Check** workflow `c-version.yml` checks that the C version used in the project is the same as the one used for releases using the `version.yml` workflow.

## Pre-requisites

1. The workflow expects a `.h` file in the provided `header_file` variable (including path to) to check the C version
2. The workflow expects a `#define VERSION` in the provided `version_define` that contains the label after the `#define` to look for to extract the version string (default: `VERSION`)
3. The workflow expects a the `tag` output of the `version.yml` workflow.

## Operation

You need to run the `version.yml` workflow before this one, and provide the `tag` output as input.

The workflow will check the C version against the `tag` and:

- succeed if the C version is the same as the `tag`
- if the C version is different from the `tag`:
  - fail if it's a release build
  - succeed with a warning if it's a development build

Example:

```yaml
jobs:
  version:
    uses: nxlabs-ch/shared-workflows/.github/workflows/version.yml@main

  check-c-version:
    needs: version
    uses: nxlabs-ch/shared-workflows/.github/workflows/c-version.yml@main
    with: 
      version: ${{ needs.version.outputs.tag }}
      header_file: src/version.h
      version_define: VERSION
```
