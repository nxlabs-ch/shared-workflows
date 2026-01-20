# Check Format

The **Check Format** workflow `check-format.yml` checks that the code formatting in the repository adheres to the
defined style guidelines using `clang-format`.

## Pre-requisites

1. The workflow expects a `clang-format` configuration file (e.g., `.clang-format`) to be present in the repository
   root or specified directory.
2. The workflows expects a file (e.g., `.clang-format-include`) that contains patterns of files to include in the
   formatting check.
3. The workflow requires the source code files to be formatted using `clang-format`.
4. The source code files need to be formatted with the specified `clang-format` version.

## Operation

The workflow runs `clang-format` on the source code files specified in the include file and checks if they are
formatted according to the defined style guidelines, using the specified `clang_format_version` of `clang-format`.

To find the files to check, it uses the `git ls-files` command with the include patterns provided in the file specified
in the `include_file` input to list all files matching the specified patterns that are tracked by Git.

The include file can also contain exclude patterns by prefixing the pattern with a `:(exclude)`. For example:

```txt
:(exclude)samples/C/excluded/*
*.h
*.c
```

Which will include all `.h` and `.c` files except those in the `samples/C/excluded/` directory.

If any files are not properly formatted, the workflow will fail and provide a list of files that need to be
reformatted, and the necessary formatting changes.

Example:

```yaml
jobs:
  check-format:
    uses: nxlabs-ch/shared-workflows/.github/workflows/clang-format.yml@main
    with:
      clang_format_version: "20"
      include_file: .clang-format-include
```
