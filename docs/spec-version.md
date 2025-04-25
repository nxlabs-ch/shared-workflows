# SPEC Version

The **SPEC Version Check** workflow `spec-version.yml` checks that the SPEC version used in the project is the same as the one used for releases using the `version.yml` workflow.

## Pre-requisites

1. The workflow expects a `.spec` file in the provided `toml_file` variable (including path to) to check the SPEC version
2. The workflow expects a the `tag` output of the `version.yml` workflow.

## Operation

You need to run the `version.yml` workflow before this one, and provide the `tag` output as input.

The workflow will check the SPEC version against the `tag` and:

- succeed if the SPEC version is the same as the `tag`
- if the SPEC version is different from the `tag`:
  - fail if it's a release build
  - succeed with a warning if it's a development build

Example:

```yaml
jobs:
  version:
    uses: nxlabs-ch/shared-workflows/.github/workflows/version.yml@main

  check-spec-version:
    needs: version
    uses: nxlabs-ch/shared-workflows//.github/workflows/spec-version.yml@main
    with: 
      version: ${{ needs.version.outputs.tag }}
      toml_file: my_module/app.spec
```
