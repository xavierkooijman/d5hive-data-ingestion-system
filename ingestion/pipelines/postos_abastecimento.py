from datetime import datetime, timezone
import geopandas as gpd
from shapely.geometry import Point
from ingestion.pipelines.base import BaseETLPipeline
from ingestion.models.postos_abastecimento import PostosAbastecimentoRawResponse


class PostosAbastecimentoPipeline(BaseETLPipeline):
    def validate_raw_schema(self, data):
        PostosAbastecimentoRawResponse.model_validate(data)
        return data

    def transform_data(self, data):
        self.logger.info(
            f"Filtering {len(data.get('features', []))} rows of data for Maia region polygon")

        maia_gdf = gpd.read_file("maia_polygon.geojson").to_crs(epsg=4326)
        maia_polygon = maia_gdf.geometry.iloc[0]
        minx, miny, maxx, maxy = maia_polygon.bounds

        gdf_points = gpd.GeoDataFrame([
            {
                "globalid": feature["properties"]["globalid"].strip("{}"),
                "marca": feature["properties"]["Marca"],
                "geometry": Point(feature["geometry"]["coordinates"])

            }
            for feature in data.get("features", [])
        ], geometry="geometry", crs="EPSG:4326")

        gdf_points = gdf_points.cx[minx:maxx, miny:maxy]
        gdf_filtered = gdf_points[gdf_points.geometry.within(maia_polygon)]

        self.logger.info(
            f"Filtered down to {len(gdf_filtered)} rows of data for Maia region polygon")

        current_timestamp = datetime.now(timezone.utc)
        transformed_data = []

        for idx, row in gdf_filtered.iterrows():
            transformed_data.append({
                "globalId": row["globalid"],
                "hostfeed": "hostfeed",
                "source": self.config["source"]["name"],
                "brand": row["marca"],
                "latitude": row.geometry.y,
                "longitude": row.geometry.x,
                "tstamp": current_timestamp
            })
        return transformed_data
