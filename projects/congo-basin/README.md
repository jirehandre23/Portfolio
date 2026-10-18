# Congo Basin Mining Explorer

[Open the explanation and demo page](https://jirehandre23.github.io/Portfolio/projects/congo-basin/)

Historical country summaries extracted from saved output in public notebook commit `53c66592d7e8e5057f8c073c0d3fd9c5f5644f0a` of `jirehandre23/Spatial_Python-QGIS_Project`. Maps are resized WebP copies of the existing QGIS outputs. The source GeoPackage is not included. Summed concessions can overlap and are not active-mine or deforestation footprint. Map selection and country filters are independent.

## Run locally

From the portfolio repository root, run `python -m http.server 9000`, then open
`http://localhost:9000/projects/congo-basin/`. The demonstration runs in the browser with
no account or backend connection.

## Source and verification

[Original project/source](https://github.com/jirehandre23/Spatial_Python-QGIS_Project). The shared interface is in
`projects/shared/`. Data checks run with `node scripts/test-project-data.mjs`;
memo calculations have `node projects/investment-memo/test.mjs`.
The responsive browser suite exercises filters and controls in Chromium and WebKit.

To rebuild data exports, clone the three source repositories alongside the portfolio
and run `python scripts/build-project-demos.py --source-root ..`. This regenerates
aggregate JSON only; it does not access the restricted GeoPackage or refresh Power BI.
