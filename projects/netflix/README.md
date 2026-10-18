# Netflix Catalog Explorer

[Open the explanation and demo page](https://jirehandre23.github.io/Portfolio/projects/netflix/)

Aggregates from all 8,807 rows in `jirehandre23/Netflix_SQL/netflix_titles.csv`. Filters use release year and content type. Country and genre memberships are nonexclusive. Browser calculations operate on exported aggregates; SQL source lives in the original repository. No viewing or revenue measurements are inferred.

## Run locally

From the portfolio repository root, run `python -m http.server 9000`, then open
`http://localhost:9000/projects/netflix/`. The demonstration runs in the browser with
no account or backend connection.

## Source and verification

[Original project/source](https://github.com/jirehandre23/Netflix_SQL). The shared interface is in
`projects/shared/`. Data checks run with `node scripts/test-project-data.mjs`;
memo calculations have `node projects/investment-memo/test.mjs`.
The responsive browser suite exercises filters and controls in Chromium and WebKit.

To rebuild data exports, clone the three source repositories alongside the portfolio
and run `python scripts/build-project-demos.py --source-root ..`. This regenerates
aggregate JSON only; it does not access the restricted GeoPackage or refresh Power BI.
