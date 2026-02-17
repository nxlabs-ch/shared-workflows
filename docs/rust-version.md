# Rust Version

The **Rust Version Check** workflow `rust-version.yml` checks that the Rust version used in the project is the same as the one used for releases using the `version.yml` workflow.

## Pre-requisites

1. The workflow expects a `Cargo.toml` file in the provided `cargo_toml_dir` directory to check the Rust version
2. The workflow expects a the `tag` output of the `version.yml` workflow.

## Operation

You need to run the `version.yml` workflow before this one, and provide the `tag` output as input.

The workflow will check the Rust version against the `tag` and:

- succeed if the Rust version is the same as the `tag`
- if the Rust version is different from the `tag`:
  - fail if it's a release build
  - succeed with a warning if it's a development build

Example:

```yaml
jobs:
  version:
    uses: nxlabs-ch/shared-workflows/.github/workflows/version.yml@main

  check-rust-version:
    needs: version
    uses: nxlabs-ch/shared-workflows/.github/workflows/rust-version.yml@main
    with: 
      version: ${{ needs.version.outputs.tag }}
      cargo_toml_dir: my_module
```
