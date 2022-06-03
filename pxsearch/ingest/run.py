#!/usr/bin/env python3.8
"""
CLI to ingest data by year from any stac api.
Example stac api are
Landsat: https://landsatlook.usgs.gov/stac-server
Sentinel-2: https://earth-search.aws.element84.com/v0
"""
import click
from dateutil import parser

from pxsearch.ingest.stac_api import ingest_stac_collections, ingest_stac_year
from pxsearch.utils import initialize_sentry_sdk


@click.command()
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
)
@click.option(
    "-e",
    "--year-end",
    "end",
    default=None,
    help="End year for ingestion.",
    type=click.INT,
)
@click.option(
    "-c",
    "--ingest-collections",
    "collections",
    is_flag=True,
    help="Only ingest collections.",
)
@click.option(
    "-d",
    "--already-done",
    "already_done",
    default=None,
    help="Date up to which the ingestion already is done",
)
@click.option(
    "-l",
    "--limit-to-collections",
    "limit_collections",
    help="Comma separated list of collection ids to use",
    default="",
)
def ingest_year_range(
    url, start, end, collections, already_done, limit_collections
):

    if collections:
        ingest_stac_collections(url)
    else:
        if limit_collections:
            limit_collections = limit_collections.split(",")
        if not url or not start:
            raise click.UsageError("To ingest items provide start year.")
        if end is None:
            end = start
        if already_done:
            already_done = parser.parse(already_done).date()
        for year in range(start, end + 1):
            ingest_stac_year(url, year, already_done, limit_collections)


if __name__ == "__main__":
    initialize_sentry_sdk()
    ingest_year_range()
