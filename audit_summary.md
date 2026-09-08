# Audit Summary for `app/core/parsers/`

1. **`app/core/parsers/base.py`:**
   - **Fixes**: Fixed `@abstractclassmethod` which has been deprecated/removed since Python 3.3. Replaced it with `@abstractmethod`. Added `bytes` and `dict` typing support.
   - **Impact**: Code meets modern Python standard for abstract methods and will correctly raise errors when methods are not implemented, avoiding deprecation warnings/errors.

2. **`app/core/parsers/geojson_parser.py`:**
   - **Fixes**:
     - Fixed incorrect import path (`app.sore` -> `app.core`).
     - Added `shapely.force_2d(poly)` to strip any Z/3D coordinates that could break 2D routing algorithms.
     - Replaced `poly.buffer(0)` with `shapely.validation.make_valid(poly)` which is the standard, safer method for fixing self-intersections without inadvertently dropping valid geometry edges.
     - Explicitly handled `MultiPolygon` by extracting the polygon with the maximum area so that singular routing works.
   - **Impact**: Prevents runtime errors from typos, ensures compatibility with 2D planners by cleaning up Z values, and intelligently uses robust repairing routines for messy GeoJSON inputs.

3. **`app/core/parsers/kml_parser.py`:**
   - **Fixes**:
     - Corrected variable typos like `temp.write()` to `tmp.write()` and `ogs.Open()` to `ogr.Open()`.
     - Placed the OGR `layer` and `ds` references explicitly in a `finally` block to `None` them and release the file handles. This resolves issues specifically on Windows where deleting an open file raises `PermissionError` (GDAL/OGR leaks).
     - Applied `ogr.UseExceptions()` to explicitly catch C++ GDAL failures in Python try/except and re-raise them gracefully as `ValueError`.
     - Implemented dynamic CRS projection. Checks if the layer is in EPSG:4326. If not, sets up an `osgeo.osr.CoordinateTransformation` and transforms features on the fly.
     - Stripped 3D coordinates using `force_2d`.
     - Ensured topological validity using `make_valid` and handled `MultiPolygon` inputs by picking the largest area component.
   - **Impact**: Fixes syntax typos that crash the script. Closes file handles properly avoiding O/S level file locking issues and temporary file leaks. Guarantees that spatial data going to the route planner is always EPSG:4326 and strictly 2D Polygon compliant.

4. **`app/core/parsers/factory.py`:**
   - **Fixes**:
     - Fixed casing typos in the import path to match actual class names (`GeoJsonParser`, `KmlParser`).
     - Enabled extensions prefixed with `.` (e.g., `.kml`, `.geojson`) to strip the dot before resolving the appropriate parser.
   - **Impact**: Makes the boundary parser fully plug-and-play allowing endpoint handlers to safely resolve parsed bounds by format string/extension.
