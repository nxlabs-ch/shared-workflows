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
    uses: noveto-com/shared-workflows/.github/workflows/gcloud-run-jobs-execute.yml@main
    with:
      job-name: build-project
      region: us-west1
    secrets:
      GCP_PROJECT: my-project-123456
      GCP_CREDENTIALS: ${{ secrets.GCP_CREDENTIALS }}
```
