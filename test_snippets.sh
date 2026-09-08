#!/bin/bash

# Test snippet 1: JSON endpoint backwards compatibility
curl -X POST "http://localhost:8000/api/v1/planner/generate_kmz" \
     -H "Content-Type: application/json" \
     -d '{
       "fov_h": 84.0,
       "fov_v": 60.0,
       "agl": 120.0,
       "speed": 10.0,
       "overlap_f": 0.8,
       "overlap_s": 0.7,
       "drone_enum": 95,
       "payload_enum": 52,
       "waypoint_mode": "sparse",
       "boundary_geojson": {
         "type": "Polygon",
         "coordinates": [
           [
             [113.931, 22.531],
             [113.932, 22.531],
             [113.932, 22.532],
             [113.931, 22.532],
             [113.931, 22.531]
           ]
         ]
       }
     }' --output flight_routes_json.kmz

# Test snippet 2: File upload endpoint (multipart/form-data)
# First create a dummy KML file for testing
cat << 'EOF' > test_boundary.kml
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>
              113.931,22.531,0
              113.932,22.531,0
              113.932,22.532,0
              113.931,22.532,0
              113.931,22.531,0
            </coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>
  </Document>
</kml>
EOF

curl -X POST "http://localhost:8000/api/v1/planner/generate_kmz_from_file" \
     -F "file=@test_boundary.kml" \
     -F "agl=150.0" \
     -F "speed=12.0" \
     -F "overlap_f=0.85" \
     -F "overlap_s=0.75" \
     -F "drone_enum=95" \
     -F "payload_enum=52" \
     --output flight_routes_file.kmz
