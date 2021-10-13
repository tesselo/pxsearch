# PxSearch API
The PxSearch is an API for internal services created to allow search and requests of satellite image data. 

# Objectives
The restructuring of the project in this branch aims to:
- Add to our catalog new datasets, such as sentinel-1 and the landsat collection with level 2 of processing;
- Update our indexing processes using datasets from AWS S3 inventory;
- Restructure the database using STAC specifications(https://stacspec.org/) and SqlAlchemy ORM;

# Requirements

```bash
make install
```

# Upgrade unpinned dependencies

```bash
make upgrade_dependencies
```
```
pip install -r ./requirements.txt
```

# Migrations
Use alembic to have the migrations and latest version of the database.

```bash
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


Copyright 2021 Tesselo - Space Mosaic Lda. All rights reserved.
