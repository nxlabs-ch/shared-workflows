# Google Cloud Workflows

## Google Cloud Run Execute Job

The **Google Cloud Run Execute Job** workflow `gcloud-run-jobs-execute.yml` wraps the equivalent `gcloud` command into a workflow.

### Pre-requisites

1. The job to execute must exist on Google Cloud Run Jobs.

### Operation

This workflow will create a job execution of the provided job.

Example:

```yaml
jobs:
  execute-job:
    uses: nxlabs-ch/shared-workflows/.github/workflows/gcloud-run-jobs-execute.yml@main
    with:
      job-name: build-project
      region: us-west1
    secrets:
      GCP_PROJECT: my-project-123456
      GCP_CREDENTIALS: ${{ secrets.GCP_CREDENTIALS }}
```

## Google Cloud Upload Artifact

The **Google Cloud Upload Artifact** workflow `gcloud-upload-artifact.yml` wraps the equivalent `gsutil` command into a workflow.

### Pre-requisites

1. The target bucket must exist on Google Cloud Storage. Default is `gs://artifacts.nxlabs.ch`.
2. There must be a service account with the necessary permissions to upload files to the bucket.
3. The service account key must be stored as a secret in the repository or organization.

### Operation

This workflow will upload the specified file to the target bucket.

inputs:

- `source`: The path to the file to upload.
- `destination`: The folder in the bucket where the file will be uploaded.
- `bucket`: The bucket where the file will be uploaded. Default is `artifacts.nxlabs.ch`.

So if the inputs are:

- `source`: `./dist/my-app.zip`
- `destination`: `my-project`
- `bucket`: `artifacts.nxlabs.ch`

The file `my-app.zip` will be uploaded to `gs://artifacts.nxlabs.ch/my-project/my-app.zip`.
Note that the source folder `.dist` is not included in the destination path.

Example:

```yaml
jobs:
  upload-artifact:
    uses: nxlabs-ch/shared-workflows/.github/workflows/gcloud-upload-artifact.yml@main
    with:
      source: ./dist/my-app.zip
      destination: my-project
      bucket: artifacts.nxlabs.ch
    secrets:
      GCP_PROJECT: my-project-123456
      GCP_CREDENTIALS: ${{ secrets.GCP_CREDENTIALS }}
```

## Google Cloud Deploy

The **Google Cloud Deploy** workflow `gcloud-deploy.yml` allows pushing previously generated artifacts to Google Cloud Storage.

### Pre-requisites

1. A previous job has generated artifacts.
2. There is an existing Google Cloud Storage bucket.

### Operation

You should run `gcloud-deploy` as the last job in your workflow.
It will do the following:

1. Download all previously created artifacts.
2. Upload them to the provided Google Cloud Storage bucket, in the provided project folder and the provided version as a subfolder.

Example:

```yaml
jobs:
  version:
    uses: nxlabs-ch/shared-workflows/.github/workflows/version.yml@main

  build:
    needs: version
    uses: nxlabs-ch/shared-workflows/.github/workflows/build.yml@main
    with:
      version: ${{ needs.version.outputs.version }}
      dependencies: "npm install"

  deploy:
    needs: [version, build]
    uses: nxlabs-ch/shared-workflows/.github/workflows/gcloud-deploy.yml@main
    with:
      version: ${{ needs.version.outputs.version }}
      project: my-project-123456
    secrets:
      GCP_PROJECT: my-project-123456
      GCP_CREDENTIALS: ${{ secrets.GCP_CREDENTIALS }}
```
