from ingestion.sources.api import APIClient
from utils.connectors import run_inserts
import logging
from datetime import datetime, timezone
import geopandas as gpd
from shapely.geometry import Point


def run(config):
    logger = logging.getLogger(__name__)

    logger.info(f"Pipeline {config['pipeline_name']} Started")

    current_timestamp = datetime.now(timezone.utc)

    apiClient = APIClient(config["source"]["base_url"])
    raw_data = apiClient.get(config["source"]["endpoint"])

    logger.info(
        f"Filtering {len(raw_data.get('features', []))} rows of data for Maia region polygon")

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

    logger.info(
        f"Filtered down to {len(gdf_filtered)} rows of data for Maia region polygon")

    data = []

    logger.info("Normalizing and transforming data")

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

    logger.info(f"Data normalized and transformed")

    run_inserts(config, data)
