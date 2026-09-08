import json
from typing import Union
from shapely.geometry import shape, Polygon, MultiPolygon
from shapely.validation import make_valid
from shapely import force_2d
from app.core.parsers.base import BaseBoundaryParser

class GeoJsonParser(BaseBoundaryParser):
    def parse(self, data: Union[str, bytes, dict]) -> Polygon:
        if isinstance(data, (str, bytes)):
            data = json.loads(data)

        # 兼容FeatureCollection，Feature，或者Polygon
        if data.get("type") == "FeatureCollection":
            features = data.get("features", [])
            if not features:
                raise ValueError("GeoJSON FeatureCollection must contain at least one Feature")
            geom = features[0].get("geometry")
        elif data.get("type") == "Feature":
            geom = data.get("geometry")
        else:
            geom = data

        poly = shape(geom)

        # Strip Z values
        poly = force_2d(poly)

        if not poly.is_valid:
            poly = make_valid(poly) # 自动修复自相交等无效多边形

        if isinstance(poly, MultiPolygon):
            # Extract the largest polygon by area
            poly = max(poly.geoms, key=lambda p: p.area)

        return poly
