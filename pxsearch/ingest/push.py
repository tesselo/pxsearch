#!/usr/bin/env python
"""
CLI to push ingestion jobs to AWS Batch

This assumes that the built package with the indicated version tag was
deployed to S3.

Usage example:
./pxsearch/ingest/push.py \
    -g 015e03ab74d3c7589f073ce09848e64d64f35043 \
    -u "https://landsatlook.usgs.gov/stac-server" \
    -s 1973 \
    -e 1979
"""
import os

import boto3
import click


def push_batch_job(
    version,
    stac_url,
    start,
    end,
    already_done,
    depends_on=None,
):
    command = [
        f"pxsearch-{version}/pxsearch/ingest/run.py",
        "-u",
        str(stac_url),
        "-s",
        str(start),
        "-e",
        str(end),
    ]

    if already_done:
        command += ["-d", already_done]

    job = {
        "jobName": f"Ingest-{start}-to-{end}-from-STAC-API-{stac_url.split('://')[1].split('/')[0].replace('.', '-')}",  # noqa E501
        "jobQueue": "fetch-and-run-queue",
        "jobDefinition": "pxsearch-ingestion-production",
        "containerOverrides": {
            "command": command,
            "resourceRequirements": [
                {
                    "type": "MEMORY",
                    "value": "1024",
                },
                {
                    "type": "VCPU",
                    "value": "1",
                },
            ],
            "environment": [
                {
                    "name": "BATCH_FILE_S3_URL",
                    "value": f"s3://tesselo-pixels-scripts/pxsearch-{version}.zip",  # noqa E501
                },
                {"name": "BATCH_FILE_TYPE", "value": "zip"},
                {
                    "name": "POSTGRES_HOST",
                    "value": os.environ.get("DB_HOST_PXSEARCH"),
                },
                {
                    "name": "POSTGRES_USER",
                    "value": os.environ.get("DB_USER_PXSEARCH"),
                },
                {
                    "name": "POSTGRES_DBNAME",
                    "value": os.environ.get("DB_NAME_PXSEARCH"),
                },
                {
                    "name": "POSTGRES_PASS",
                    "value": os.environ.get("DB_PASS_PXSEARCH"),
                },
                {
                    "name": "AWS_SECRET_ACCESS_KEY",
                    "value": os.environ.get("AWS_SECRET_ACCESS_KEY"),
                },
                {
                    "name": "AWS_ACCESS_KEY_ID",
                    "value": os.environ.get("AWS_ACCESS_KEY_ID"),
                },
                {"name": "PYTHONPATH", "value": f"./pxsearch-{version}"},
                {
                    "name": "SENTRY_DSN",
                    "value": "https://d8c1399a37c44cd2ae228dfb13fa800a@o640190.ingest.sentry.io/6167701",  # noqa E501
                },
            ],
        },
        "retryStrategy": {
            "attempts": 5,
            "evaluateOnExit": [
                {"onStatusReason": "Host EC2*", "action": "RETRY"},
                {"onReason": "*", "action": "EXIT"},
            ],
        },
    }
    # Set job dependency.
    if depends_on is not None:
        job["dependsOn"] = [{"jobId": dep} for dep in depends_on]
    # Push job to batch.
    batch = boto3.client("batch", region_name="eu-central-1")
    return batch.submit_job(**job)


@click.command()
@click.option(
    "-g",
    "--git-hash",
    "version",
    help="Git hash of package version to run",
    type=click.STRING,
    required=True,
)
@click.option(
    "-u",
    "--stac-url",
    "url",
    help="STAC api base url.",
    type=click.STRING,
    required=True,
)
@click.option(
    "-s",
    "--year-start",
    "start",
    help="Start year for ingestion.",
    type=click.INT,
    required=True,
)
@click.option(
    "-e",
    "--year-end",
    "end",
    default=None,
    help="End year for ingestion.",
    type=click.INT,
    required=True,
)
@click.option(
    "-d",
    "--already-done",
    "already_done",
    default=None,
    help="Date up to which the ingestion already is done",
)
def push_batch_jobs_for_date_range(version, url, start, end, already_done):
    previous = None
    for year in range(start, end + 1):
        if previous is None:
            previous = push_batch_job(
                version=version,
                stac_url=url,
                start=year,
                end=year,
                already_done=already_done,
            )
        else:
            previous = push_batch_job(
                version=version,
                stac_url=url,
                start=year,
                end=year,
                already_done=already_done,
                depends_on=[previous["jobId"]],
            )
        print(year, previous["jobId"])


if __name__ == "__main__":
    push_batch_jobs_for_date_range()
