# Investment Memo Workbench

[Open the explanation and demo page](https://jirehandre23.github.io/Portfolio/projects/investment-memo/)

Fictional, deterministic template illustrating structured screening. It computes simplified cash available, DSCR and opening cash days and drafts a traceable memo. The thresholds are illustrative. This is separate from the employer workflow described in the professional background; no confidential employer data or code is reproduced. No LLM, PDF extraction or document verification is connected.

## Run locally

From the portfolio repository root, run `python -m http.server 9000`, then open
`http://localhost:9000/projects/investment-memo/`. The demonstration runs in the browser with
no account or backend connection.

## Source and verification

[Original project/source](https://github.com/jirehandre23/Portfolio/tree/main/projects/investment-memo). The shared interface is in
`projects/shared/`. Data checks run with `node scripts/test-project-data.mjs`;
memo calculations have `node projects/investment-memo/test.mjs`.
The responsive browser suite exercises filters and controls in Chromium and WebKit.

To rebuild data exports, clone the three source repositories alongside the portfolio
and run `python scripts/build-project-demos.py --source-root ..`. This regenerates
aggregate JSON only; it does not access the restricted GeoPackage or refresh Power BI.
