#!/usr/bin/env python
"""
CLI to ingest data by year from any stac api.
Example stac api are
Landsat: https://landsatlook.usgs.gov/stac-server
Sentinel-2: https://earth-search.aws.element84.com/v0
"""
import click

from pxsearch.ingest.stac_api import ingest_stac_collections, ingest_stac_year


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
def ingest_year_range(url, start, end, collections):
    if collections:
        ingest_stac_collections(url)
    else:
        if not url or not start:
            raise click.UsageError("To ingest items provide start year.")
        if end is None:
            end = start + 1
        for year in range(start, end):
            ingest_stac_year(url, year)


if __name__ == "__main__":
    ingest_year_range()
