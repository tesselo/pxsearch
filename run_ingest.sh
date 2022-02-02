# Ensure collections exist.
python pxsearch/ingest/run.py --stac-url=https://landsatlook.usgs.gov/stac-server -c

for year in 1980 1981 1982
do
  python pxsearch/ingest/run.py --year-start=$year --stac-url=https://landsatlook.usgs.gov/stac-server > ~/Desktop/pxsearch_ingest_logs/lsl2_$year.log 2>&1 &
done
