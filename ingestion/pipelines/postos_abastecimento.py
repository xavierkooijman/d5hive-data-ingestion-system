from ingestion.sources.api import APIClient
from utils.connectors import run_inserts
import logging
from datetime import datetime, timezone
import geopandas as gpd
from shapely.geometry import Point


def run(config):
    logger = logging.getLogger(__name__)

    logger.info("Pipeline Started")

    current_timestamp = datetime.now(timezone.utc)
    logger.info(
        f"Fetching data from API URL: {config['source']['base_url']}{config['source']['endpoint']}")

    apiClient = APIClient(config["source"]["base_url"])
    raw_data = apiClient.get(config["source"]["endpoint"])

    maia_gdf = gpd.read_file("maia_polygon.geojson").to_crs(epsg=4326)
    maia_polygon = maia_gdf.geometry.iloc[0]
    minx, miny, maxx, maxy = maia_polygon.bounds

    gdf_points = gpd.GeoDataFrame([
        {
            "globalid": feature["properties"]["globalid"].strip("{}"),
            "marca": feature["properties"]["Marca"],
            "geometry": Point(feature["geometry"]["coordinates"])

        }
        for feature in raw_data["features"]
    ], geometry="geometry", crs="EPSG:4326")

    gdf_points = gdf_points.cx[minx:maxx, miny:maxy]

    gdf_filtered = gdf_points[gdf_points.geometry.within(maia_polygon)]

    data = []

    for idx, row in gdf_filtered.iterrows():
        data.append({
            "globalId": row["globalid"],
            "hostfeed": "hostfeed",
            "source": config["source"]["name"],
            "brand": row["marca"],
            "latitude": row.geometry.y,
            "longitude": row.geometry.x,
            "tstamp": current_timestamp
        })

    run_inserts(config, data)
