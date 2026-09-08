import tempfile
import os
from typing import Union
from osgeo import ogr, osr
from shapely import wkt
from shapely.geometry import Polygon, MultiPolygon
from shapely.validation import make_valid
from shapely import force_2d
from app.core.parsers.base import BaseBoundaryParser

class KmlParser(BaseBoundaryParser):
    def parse(self, data: Union[str, bytes, dict]) -> Polygon:
        if isinstance(data, str):
            content = data.encode('utf-8')
        elif isinstance(data, bytes):
            content = data
        else:
            raise TypeError("KML 解析器只接受字符串或者二进制文件流")

        # 使用内存临时文件交由GDAL/OGR 驱动解析
        with tempfile.NamedTemporaryFile(suffix=".kml", delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        ds = None
        layer = None

        try:
            # 开启OGR exceptions以便捕获解析错误
            ogr.UseExceptions()
            ds = ogr.Open(tmp_path)
            if not ds:
                raise ValueError("无法解析该kml文件，文件格式不符合OGR kml标准")
            layer = ds.GetLayer(0)

            # CRS 处理
            spatial_ref = layer.GetSpatialRef()
            target_sr = osr.SpatialReference()
            target_sr.ImportFromEPSG(4326)

            transform = None
            if spatial_ref and not spatial_ref.IsSame(target_sr):
                transform = osr.CoordinateTransformation(spatial_ref, target_sr)

            poly = None
            for feature in layer:
                geom = feature.GetGeometryRef()
                if geom.GetGeometryName() in ["POLYGON", "MULTIPOLYGON"]:
                    if transform:
                        geom.Transform(transform)
                    poly = wkt.loads(geom.ExportToWkt())
                    break

            if poly is None:
                raise ValueError("KML 中未找到合法的POLYGON边界要素")

            # 去除3D坐标
            poly = force_2d(poly)

            if not poly.is_valid:
                poly = make_valid(poly)

            if isinstance(poly, MultiPolygon):
                # 提取最大面积的Polygon
                poly = max(poly.geoms, key=lambda p: p.area)

            return poly

        except Exception as e:
            raise ValueError(f"解析KML失败: {str(e)}")
        finally:
            # 安全释放资源避免文件锁定
            layer = None
            ds = None
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
