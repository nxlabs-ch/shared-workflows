# KiCad Version

The **KiCad Version Check** workflow `kicad-version.yml` checks that the version used in the KiCad project is the same as the one used for releases using the `version.yml` workflow.

## Pre-requisites

1. The workflow expects a KiCad schema file in the provided `kicad_sch_path` file path to check the version
2. The workflow expects a the `tag` output of the `version.yml` workflow.

## Operation

You need to run the `version.yml` workflow before this one, and provide the `tag` output as input.

The workflow will check the schema version against the `tag` and:

- succeed if the schema version is the same as the `tag`
- if the schema version is different from the `tag`:
  - fail if it's a release build
  - succeed with a warning if it's a development build

Example:

```yaml
jobs:
  version:
    uses: noveto-com/shared-workflows/.github/workflows/version.yml@main

  check-kicad-version:
    needs: version
    uses: noveto-com/shared-workflows//.github/workflows/kicad-version.yml@main
    with: 
      version: ${{ needs.version.outputs.tag }}
      kicad_sch_path: my_schema/my_schema.kicad_sch
```
