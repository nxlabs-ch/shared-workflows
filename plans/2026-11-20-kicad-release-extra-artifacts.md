# KiCad release: variant, fabrication and ordering artifacts

Status: planned

## Problem

`kicad-release.yml` saves four artifacts: every KiBot output (`all`), the default BOM, the default
schematic PDF and the project archive. A project that needs more as separate release assets has to add
a job of its own that downloads the `all` artifact, picks files out of it and uploads them again. Three
needs are common enough to belong in the shared workflow:

- **Assembly variants.** One board built with different parts fitted. KiBot generates a BOM and a
  schematic PDF per variant, but only the default ones become artifacts.
- **Fabrication set.** The Gerber and drill files to order bare boards, packed the way a manufacturer
  expects them. KiBot ships templates for the common manufacturers, JLCPCB and PCBWay among them.
- **Ordering BOMs.** A short BOM with distributor and manufacturer part numbers and quantities, to
  import at a distributor such as Mouser or Digi-Key.

The approach below was proven as a caller-side job in a consuming project, with the KiCad 9 image
(KiBot 1.9.1).

## Decision

The workflow saves the extra artifacts itself, driven by where the caller's KiBot configuration writes
its files. Callers that change nothing get exactly today's four artifacts.

| Deliverable       | KiBot writes, below `output/`              | Artifact, after the `kb<kibot>-<name>-` prefix | Trigger                    |
| ----------------- | ------------------------------------------ | ---------------------------------------------- | -------------------------- |
| Variant BOM       | `BoM/<variant>/<name>-bom_<variant>.csv`   | `bom-<variant>-<version>`                      | Listed in `variants` input |
| Variant schematic | `Schematic/<name>-schematic_<variant>.pdf` | `schematic-<variant>-<version>`                | Listed in `variants` input |
| Fabrication set   | `Fabrication/*.zip`                        | `fabrication-<version>`                        | Files are present          |
| Ordering BOMs     | `Ordering/*.csv`                           | `ordering-<version>`                           | Files are present          |

Every file gets the version in its name inside the artifact, as the default BOM and schematic do today:
`<file>-<version>.<ext>`, and `_<variant>` becomes `-<variant>`.

Two triggers, on purpose:

- **Variants are named by the caller**, in a new optional input `variants`. A variant produces one
  artifact per file, and a missing file is then an error with a message that names the expected path.
  Discovering variants from file names instead would turn a typo in the KiBot configuration into a
  silently missing release asset.
- **Fabrication and ordering are taken when present.** Each is a whole folder saved as one artifact, so
  there is nothing to name. An absent or empty folder means no artifact and no error.

The variant path convention is what KiBot produces by default for a variant whose `file_id` is
`_<variant>`, with the BOM output placed in `BoM/<variant>`.

## Changes

### 1. `.github/workflows/kicad-release.yml`

**New input**

- `variants`: space-separated names of the KiBot variants whose BOM and schematic are saved as
  artifacts of their own. Optional, default empty.

**Job `build-artifacts`** keeps its name, because callers may require its status check. It gains:

- A step **List variants** (`id: variants`, `set -euo pipefail`, input through `env:`). It checks every
  name against `^[A-Za-z0-9][A-Za-z0-9._-]*$`, fails with an `::error::` naming the offending value, and
  writes the list as a JSON array to `$GITHUB_OUTPUT` with `jq`. The job exposes it as the output
  `variants`.
- In **Prepare artifacts with version in name**: with `nullglob` set, copy `output/Fabrication/*.zip`
  into `fabrication/` and `output/Ordering/*.csv` into `ordering/`, inserting `-<version>` before the
  extension. Log how many files each folder gave.
- Two upload steps, **Save artifact (Fabrication set)** and **Save artifact (Ordering BOMs)**, for the
  two folders, with `if-no-files-found: ignore`.

**New job `variant-artifacts`**

- `needs: build-artifacts`, `if:` the `variants` output is not `[]`, `runs-on: ubuntu-24.04`.
- `strategy.matrix.variant` from `fromJSON` of that output, `fail-fast: false`.
- Steps: download the `all` artifact of this run into `output/`; copy the two variant files to their
  versioned names, failing with an `::error::` that names the missing path; upload the two artifacts
  with `if-no-files-found: error`. The matrix value reaches `run:` steps through `env:`.

A separate job is needed because the number of artifacts depends on the input and upload steps cannot
loop. A caller's `needs:` on the reusable workflow waits for both jobs, so a release job that follows
picks up every artifact without a change on the caller's side.

### 2. `samples/kicad`

**Provenance.** The sample is the `RaspberryPi-HAT` project template of KiCad 7, instantiated as project
`sample`. Compared with `Projects/RaspberryPi-HAT` in
[kicad-templates](https://gitlab.com/kicad/libraries/kicad-templates) at tag `7.0.11`, it differs only
in the project name, the `rev` line that the version check and the release workflow need, and a re-save
by a later KiCad 7. It stays in that form. The template shipped with KiCad 9 has the same six parts but
is in the KiCad 9 file format, which KiCad 8 does not open.

**Edit the schematic as text.** Saving `sample.kicad_sch` from KiCad 8 or later rewrites it in that
version's file format, and every older KiCad then refuses it. The fields below are added by hand, as
`property` entries of the symbol concerned.

- **Attribution.** Add `samples/kicad/sample/README.md`. It sits inside the project folder so that it
  is part of the project archive the workflow publishes. Content:
  - the source: the repository, path and tag above;
  - the credits from the template's `meta/info.html`: © 2021 Caleb Reister; adapted from the
    `raspberrypi-gpio-40pin` template, © 2016 Ashton Johnson and © 2016 KiCad Developers;
  - the licence: CC-BY-SA 4.0 with the KiCad libraries exception, with a link to the upstream
    `LICENSE.md`;
  - the changes made: the three differences listed under Provenance, and the fields added below.
- **Variant.** Give one part of the sample schematic a variant-specific value, a field named
  `<variant>:Value`.
- **KiBot configuration.** `config.kibot.yaml`: add a `kibom` variant with `pre_transform: _var_rename`
  and its BOM and schematic outputs; import the `JLCPCB` and `PCBWay` templates with their assembly
  files switched off and their ZIP files directed to `Fabrication/`; add an ordering BOM output in
  `Ordering/`.
- **Ordering fields.** Give J1 the fields the ordering BOM lists, under the field names the proven
  configuration uses:

  | Column                   | Value for J1     |
  | ------------------------ | ---------------- |
  | Manufacturer             | Würth Elektronik |
  | Manufacturer part number | 61304021821      |
  | Mouser part number       | 710-61304021821  |

  J1 is a 2×20 socket, footprint `Connector_PinSocket_2.54mm:PinSocket_2x20_P2.54mm_Vertical`. The
  part is a 2×20, 2.54 mm, straight through-hole socket of the WR-PHD series. It was matched on the
  distributor's description only; the datasheet was not compared with the footprint.

  J1 is the only part that gets these fields. C1, R1, R2, U1 and JP1 have no footprint in the template,
  so there is no orderable part to name, and they have no part numbers in the ordering BOM.

### 3. `.github/workflows/ci.yml`

- Pass the sample variant in `variants` to `kicad-release-v9`. No `needs:` change: `deploy` and
  `release` already wait for that job, which now includes the matrix job.

Consequence: each release of this repository ships four more KiCad sample artifacts.

### 4. `docs/kicad-release.md`

- Pre-requisites: the `variants` input and the path conventions of the table above.
- Operation: the three new kinds of artifact and when each is saved.
- A KiBot configuration example for each: a variant, the two manufacturer templates, an ordering BOM
  with distributor part number, manufacturer, manufacturer part number and quantity columns.
- Two notes. The release workflows zip every artifact again, so the fabrication asset is a ZIP holding
  the manufacturer ZIPs. An ordering BOM can be imported by distributor part number where the design
  has one, and by manufacturer part number anywhere else.

### 5. Spelling

Run `cspell` on the changed files. A flagged term that is correct goes into the dictionary of the
directory that contains the file.

## Compatibility

- No input is required and the four existing artifacts keep their names and content.
- A caller whose KiBot configuration already writes to `output/Fabrication/` or `output/Ordering/` for
  another purpose gets a new artifact. Check the consumer repositories for those folder names before
  the release.
- A caller that already uploads artifacts under the new names from a job of its own must remove that
  job in the same change that moves its pin: two uploads under one name fail the run.

## Verification

`ci.yml` references `kicad-release.yml` by relative path, so the pull request run exercises the change.

1. `kicad-release-v9 / build-artifacts` succeeds and still uploads its four artifacts, unchanged.
2. The run has the four new artifacts: `bom-<variant>`, `schematic-<variant>`, `fabrication` and
   `ordering`, each with the version in its file names.
3. The fabrication artifact holds one ZIP per imported manufacturer template; each ZIP contains the
   copper, silkscreen, solder mask and outline Gerbers and the drill files.
4. The variant BOM differs from the default BOM in the row of the part that has the variant field.
5. The ordering BOM has a row for J1 with the manufacturer, manufacturer part number and Mouser part
   number of section 2.
6. The project archive in the `project` artifact contains the sample's `README.md`.
7. `sample.kicad_sch` still starts with `(kicad_sch (version 20230121)`.
8. Negative checks, once each, on throwaway commits removed before merging:
   - a name in `variants` that KiBot does not produce fails `variant-artifacts` with the path error;
   - a name with a character outside the allowed set fails **List variants** with the validation error;
   - with the variant, the templates and the ordering output taken out of the sample configuration and
     `variants` left empty, the run has exactly the four original artifacts and `variant-artifacts` is
     skipped.

## Relation to the multi-version plan

[2026-11-20-kicad-release-multi-version.md](2026-11-20-kicad-release-multi-version.md) edits the same
three files. The two changes do not depend on each other; the second to land rebases onto the first.
Once both are in:

- pass `variants` to each `kicad-release-v*` job in `ci.yml`;
- confirm on each KiCad version that the image's KiBot has the two manufacturer templates and the
  `_var_rename` filter. This plan was only proven with the KiCad 9 image;
- confirm that `kicad-release-v8` still opens the sample after the edits of section 2. That job is the
  reason the sample keeps its KiCad 7 file format.

## Out of scope

- Assembly files for a manufacturer: placement files and BOMs in the manufacturer's own format.
- Solder paste stencils.
- Prices and stock from distributor APIs.
- Changing the release workflows so that a single-file artifact is not zipped again.
- A fabrication set per variant. The bare board is the same for every assembly variant.
- Replacing the sample with a newer version of the `RaspberryPi-HAT` template.
- Footprints and orderable parts for C1, R1, R2, U1 and JP1 of the sample.

## Rejected alternatives

- **One artifact holding the files of all variants.** No second job is needed, but a release then has
  one asset for all variants while the default BOM and schematic stay separate assets.
- **Discover variants from file names.** No input is needed, but a misnamed KiBot output silently drops
  an asset instead of failing the run.
- **Upload from a script step with the artifact client library.** Keeps a single job, but installs a
  package at run time and replaces the pinned upload action with custom code.
- **Flags to switch the fabrication set and the ordering BOMs on.** The KiBot configuration already
  states whether they exist; a flag would be a second place to keep in step.

## Release

Commit type `feature:` (minor bump). Consumers pin release tags, so nothing changes for them until they
move their pin. The release PR needs the usual `build: update version to X.Y.Z for release` commit in
`docs/pyproject.toml`.
