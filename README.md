# PxSearch API
The PxSearch is an API for internal services created to allow search and requests of satellite image data.

# Objectives
The restructuring of the project in this branch aims to:
- Add to our catalog new datasets, such as sentinel-1 and the landsat collection with level 2 of processing;
- Update our indexing processes using datasets from AWS S3 inventory;
- Restructure the database using STAC specifications(https://stacspec.org/) and SqlAlchemy ORM;

## Install runtime dependencies

```
make install
```


## Install development dependencies

```
# This will also install the runtime dependencies
make dev_install
```

## Upgrade unpinned dependencies

```
make upgrade_dependencies
```

## Pre-commit hooks

We are using <https://pre-commit.com/> hooks, they are specified in the file `.pre-commit-config.yaml` and installed when you run `make dev_install`.
If the pre-commit configuration file is changed, remember to run `make dev_install` or `pre-commit install` again.

To manually force run the pre-commit tasks, you can type:

```bash
make pre-commit
```

## Make targets

The `Makefile` is a good resource to see how things are done.
Some of these targets include:

### Common checks before opening a PR

Includes the pre-commit hooks and running the tests with
code coverage reports.

```bash
make check
```


### Extended checks to know more about the code

Includes security checks and other code smells.

```bash
make check-advanced
```

### Picky checks to be a code snob

Includes code complexity and documentation style checks.
```bash
make check-picky
```

# Migrations
Use alembic to have the migrations and latest version of the database.

To create a new migration use
```bash
alembic migration
```

To update the database use
```bash
alembic upgrade head
```

# Deploy staging

```bash
zappa update staging
```

# Invoke staging

```bash
zappa invoke staging "pxsearch.app.main"
```

```
alembic migration
```

# Deploy staging

```bash
zappa update staging
```

# Invoke staging

```bash
zappa invoke staging "pxsearch.app.main"
```

# DB Setup
Create a DB install the postgis extension.

Create the LS Collections
```python
from pxsearch.lsl2 import create_collections
create_collections()
```

# Ingest

## LSL2 Ingestor
There is a cli to ingest data from any STAC api server.

Example for ingesting landsat data:
```bash
url=https://landsatlook.usgs.gov/stac-server
# Ingest all collections from a service.
python pxsearch/ingest/run.py --stac-url=$url -c
# Ingest items across all collections for a list of years.
for year in 1980 1981 1982
do
  python pxsearch/ingest/run.py --year-start=$year --stac-url=$url
done
```

Copyright 2021 Tesselo - Space Mosaic Lda. All rights reserved.
