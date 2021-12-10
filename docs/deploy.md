# Deploy Artifacts to S3

The **Deploy Artifacts to S3** workflow `deploy-s3.yml` allows pushing previously generated artifacts to an S3 bucket.

## Pre-requisites

1. A previous job has generated artifacts.
2. There is an existing AWS S3 bucket.

## Operation

You should run `deploy-s3` as the last job in your workflow.
It will do the following:

1. Download all previously created artifacts.
2. Upload them to the provided S3 bucket, in the provided project folder and the provided version as a subfolder.

Example:

``` yaml
jobs:
  version:
    uses: noveto-com/shared-workflows/.github/workflows/version.yml@main

  docs:
    needs: version
    uses: noveto-com/shared-workflows/.github/workflows/docs.yml@main
    with:
      version: ${{ needs.version.outputs.version }}
      pdf-name: "User-Manual.pdf"
      dependencies: "Sphinx==3.5.4 myst-parser==0.15.2"

  deploy:
    needs: [version, docs]
    uses: noveto-com/shared-workflows/.github/workflows/deploy-s3.yml@main
    with:
      version: ${{ needs.version.outputs.version }}
      project: shared-workflows
    secrets:
      AWS_S3_BUCKET: ${{ secrets.AWS_S3_BUCKET }}
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

The artifacts `documentation` and `documentationHTML` are produced by the `docs` job, therefore will be picked up and uploaded by the `deploy` job.

This will result in the following structure on the S3 bucket, supposing version is `1.0.2`:

```sh
my-bucket.s3.amazonaws.com
    shared-workflows
        v1.0.2
            documentationHTML
            documentation
```

## Attribution

The workflow uses the [jakejarvis/s3-sync-action](https://github.com/jakejarvis/s3-sync-action) action.
