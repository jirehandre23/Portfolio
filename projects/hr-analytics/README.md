# HR Workforce Explorer

[Open the explanation and demo page](https://jirehandre23.github.io/Portfolio/projects/hr-analytics/)

Aggregate audit output from `jirehandre23/HR_SQL-PowerBi_Project/reports/audit.json`, snapshot 2023-12-31. No individual employee names or records are included in the browser data. The historical Power BI image is not refreshed to the corrected metric definitions. Department filters apply to the department summaries; the annual flow table remains all-department.

## Run locally

From the portfolio repository root, run `python -m http.server 9000`, then open
`http://localhost:9000/projects/hr-analytics/`. The demonstration runs in the browser with
no account or backend connection.

## Source and verification

[Original project/source](https://github.com/jirehandre23/HR_SQL-PowerBi_Project). The shared interface is in
`projects/shared/`. Data checks run with `node scripts/test-project-data.mjs`;
memo calculations have `node projects/investment-memo/test.mjs`.
The responsive browser suite exercises filters and controls in Chromium and WebKit.

To rebuild data exports, clone the three source repositories alongside the portfolio
and run `python scripts/build-project-demos.py --source-root ..`. This regenerates
aggregate JSON only; it does not access the restricted GeoPackage or refresh Power BI.
