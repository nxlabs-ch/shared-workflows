# KiCad Release

The **KiCad Release** workflow `kicad-release.yml` sets the version and date to a KiCad project and creates the artifacts from the project.

## Pre-requisites

1. The workflow expects a the `version` output of the `version.yml` workflow.
2. The workflow expects a KiCad schema file with `name`in the directory `dir` to set the version.
3. Optionally a kibot version (defaults to v8) to specify the version of kibot to use for the build.

## Operation

You need to run the `version.yml` workflow before this one, and provide the `version` output as input.

The workflow will:

- set the schema in `dir`/`name` version to the `version`
- create the artifacts from the schema as defined in a provided kibot config file
- upload the BOM and Schematic artifacts with version number
- upload all other artifacts in the output folder

Example:

```yaml
jobs:
  version:
    uses: nxlabs-ch/shared-workflows/.github/workflows/version.yml@main

  kicad-release:
    needs: version
    uses: nxlabs-ch/shared-workflows//.github/workflows/kicad-release.yml@main
    with: 
      version: ${{ needs.version.outputs.tag }}
      dir: my_project
      name: schema
      kibot-version: v9
```
