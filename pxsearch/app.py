from flask import Flask, jsonify, request
from pxsearch.search import search_data
from pxsearch.utils import compute_wgs84_bbox,generate_polygon


app = Flask(__name__)
app.config["DEBUG"] = True


# 1 Define the API route with
@app.route(
    "/", methods=["GET"]
)  # The @ is used for defining the API route. We’re passing /, which means this is our base route.
def home():
    return "A prototype API for search imagery in eo_catalog db!"


# 2 Request and filter data from DB.
@app.route("/pxsearch", methods=["GET"])
def api_filter():
    # Define the query parameters.
    query_parameters = request.args
    # Chains the supported queries to the appropriate variable.
    start = query_parameters.get("start")
    end = query_parameters.get("end")
    platforms = query_parameters.get("platforms")
    maxcloud = query_parameters.get("maxcloud")
    limit = query_parameters.get("limit")
    scene = query_parameters.get("scene")
    sensor = query_parameters.get("sensor")
    level = query_parameters.get("level")
    sort = query_parameters.get("sort")
    xmin = query_parameters.get("xmin")
    ymin = query_parameters.get("ymin")
    xmax = query_parameters.get("xmax")
    ymax = query_parameters.get("ymax")

    # Compute bbox and transform to geojson.
    bbox = [float(xmin), float(ymin), float(xmax), float(ymax)]
    geojson = generate_polygon(bbox)

    # Execute search and return query.
    results = search_data(
        geojson,
        start=start,
        end=end,
        maxcloud=maxcloud,
        limit=limit,
        platforms=platforms,
        level=level,
        scene=scene,
        sensor=sensor,
        sort=sort
    )

    return jsonify(results)

# endpoint
#http://127.0.0.1:5000/pxsearch?maxcloud=20&platforms=SENTINEL_2&start=2021-03-01&end=2021-04-19&limit=1&xmin=-9.0425146546764&xmax=-8.851644885678159&ymin=39.7087369057418&ymax=39.925313329583915
