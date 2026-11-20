# KiCad release: support KiCad 8, 9 and 10 with one image pull

Status: planned

## Problem

`kicad-release.yml` selects the KiBot build with one `uses: INTI-CMNB/KiBot@v2_k<N>` step per KiCad
version, each guarded by `if:`. `uses:` cannot take an expression, and the runner builds every Docker
action referenced in a job during "Set up job", before any `if:` is evaluated. Each extra version
therefore adds an image build to every run, whether it is used or not. That is why v8 was dropped in
0.23.0, and it blocks adding KiCad 10.

Baseline from the last successful CI run (`kicad-release-v9`): 42 s to build the action image, 5 s to
run KiBot, about 1 minute for the whole job.

## Decision

Stop using the `INTI-CMNB/KiBot` action. Pull the upstream image for the requested version and run
`kibot` in it with `docker run` from a `run:` step. Only the selected image is ever pulled.

The action adds nothing this workflow needs:

- Its `Dockerfile` at `v2_k8`, `v2_k9` and `v2_k10` is `FROM ghcr.io/inti-cmnb/kicad<N>_auto_full:latest`
  plus an `entrypoint.sh`.
- The entrypoint is identical across the three tags. With the inputs this workflow passes it reduces
  to `kibot -c <config> -e <schema> -d output`.
- The three images exist on ghcr.io with a `latest` tag, define no entrypoint and run as root
  (KiCad 10 image: about 1.35 GB compressed).

## Changes

### 1. `.github/workflows/kicad-release.yml`

Replace the `Run KiBot v9` step with two steps.

**Pull KiBot image** (`id: kibot-image`, `timeout-minutes: 10`, `set -euo pipefail`, input passed
through `env:`):

- Validate `kibot-version` against `^v[0-9]+$`. On mismatch, emit an `::error::` naming the received
  value and exit 1.
- Derive `ghcr.io/inti-cmnb/kicad${KIBOT_VERSION#v}_auto_full:latest`.
- `docker pull` it with three attempts and a growing back-off, the same loop shape
  `tectonic-docs.yml` uses for `apt-get`.
- Write the image reference to `$GITHUB_OUTPUT` as `image`.

**Run KiBot** (`set -euo pipefail`, all inputs through `env:`):

```bash
docker run --rm \
  --volume "$GITHUB_WORKSPACE:/workdir" \
  --workdir /workdir \
  "$IMAGE" \
  kibot -c "$DIR/config.kibot.yaml" -e "$DIR/$NAME/$NAME.kicad_sch" -d output
```

Update the `kibot-version` input description: it is the KiCad major version of the KiBot image, in
the form `v<major>`; `v8`, `v9` and `v10` are tested. The name and the `v9` default stay, so no
caller breaks.

The validation is a pattern, not an allow-list, on purpose: a future KiCad 11 works without a
workflow change as long as upstream keeps the image naming. An unknown major fails at `docker pull`
with a message that names the missing image.

No other step changes. Artifact names already carry the `kb<version>` prefix.

### 2. `.github/workflows/ci.yml`

- Keep the job `kicad-release-v9` under its current name. The `branch-protections` ruleset requires
  the status check `kicad-release-v9 / build-artifacts`; renaming the job or folding it into a matrix
  would change the check name and block every PR.
- Add `kicad-release-v8` and `kicad-release-v10`, identical except for `kibot-version`.
- Add both new jobs to the `needs:` of `deploy` and `release`. The deploy workflows download every
  artifact in the run with no name filter, so a job left out of `needs:` would have its artifacts
  published nondeterministically.

The sample project needs no change: `samples/kicad/sample` is in KiCad 7 file format, which all
three versions open.

Consequence: each release of this repository ships twelve KiCad sample artifacts instead of four.

### 3. `docs/kicad-release.md`

- Pre-requisite 3: accepted values `v8`, `v9`, `v10`, default `v9`.
- Replace the closing note ("v8 is no longer supported") with: v8 is supported again and v10 is new
  as of the release that contains this change; state that version once the PR comment confirms it.
- Add one sentence in Operation: KiBot runs in the upstream `kicad<N>_auto_full` image.

### 4. Spelling

Run `cspell` on the changed files. `kibot` and `CMNB` are already in `.github/.cspell.json` and
`docs/.cspell.json`; any other flagged term that is correct goes into the dictionary of the
directory that contains the file.

## Behaviour differences from the Docker action

| Aspect               | Docker action                          | `docker run`                 | Impact                                                       |
| -------------------- | -------------------------------------- | ---------------------------- | ------------------------------------------------------------ |
| Runner variables     | `GITHUB_*` and `CI` injected           | Not forwarded                | None today: no consumer `config.kibot.yaml` references them  |
| `HOME`               | `/github/home`                         | `/root`                      | None: nothing is read back from it                           |
| KiCad git filters    | `kicad-git-filters.py` run if `.git`   | Not run                      | None: only affects `git diff` of KiCad files                 |
| Workspace mount path | `/github/workspace`                    | `/workdir`                   | None: all paths passed to `kibot` are relative               |
| Output ownership     | root                                   | root                         | Unchanged                                                    |
| Image version        | `latest` at action build time          | `latest` at pull time        | Unchanged                                                    |

Checked against the eight consumer repositories in `nxlabs-ch`: none uses environment variables or
git-derived values in its KiBot configuration.

## Verification

`ci.yml` references `kicad-release.yml` by relative path, so the PR run exercises the change (unlike
changes to the `check-version` composite action).

1. All three `kicad-release-v*` jobs succeed on the PR.
2. No `Build INTI-CMNB/KiBot@…` step appears in any of them, and each pulls exactly one image.
3. Each job uploads its four artifacts (`kbv<N>-sample-{all,bom,schematic,project}-<version>`).
4. The v9 `output` artifact contains the same file set as the one from the last `main` run.
5. Job duration stays in the range of the baseline above.
6. Negative check, once, on a throwaway commit: `kibot-version: '9'` fails in the pull step with the
   validation error. Remove the commit before merging.

## Out of scope

- An input to pin the image tag (for example `1.9.1`) instead of `latest`.
- Renaming `kibot-version` to reflect that it selects the KiCad version.
- Switching to the smaller non-`full` images.
- Changing the default from `v9` to `v10`; that is a breaking change for callers that omit the input.

## Rejected alternatives

- **Job-level `container:` with an expression image.** Pulls one image too, but every step then runs
  inside the KiBot image: `actions/checkout` with `lfs: true` would depend on git-lfs being present
  there, mapping `v9` to `9` needs a `fromJSON` lookup, and an invalid value produces an obscure
  error.
- **One job per version, each with a job-level `if:`.** Skipped jobs set up nothing, so it works, but
  the job body is triplicated, every KiCad release needs a workflow edit, and every caller sees two
  skipped jobs per run.

## Release

Commit type `feature:` (minor bump). Consumers pin release tags, so nothing changes for them until
they move their pin. The release PR needs the usual
`build: update version to X.Y.Z for release` commit in `docs/pyproject.toml`.
