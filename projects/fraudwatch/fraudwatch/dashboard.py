import json
import os
from pathlib import Path
import httpx
import pandas as pd
import streamlit as st
from fraudwatch.metrics import evaluate, psi

st.set_page_config(page_title="FraudWatch | Model health", page_icon="◈", layout="wide")
st.title("FraudWatch")
st.caption("Streaming fraud intelligence · synthetic demonstration · no real payment data")
key = st.sidebar.text_input("Tenant API key", type="password")
st.sidebar.button("Refresh")
st.sidebar.info("Data drift is a change in inputs. Model decay requires observed labels and comparable cohorts.")
if not key:
    st.info("Enter the demo tenant key from your .env file to inspect its predictions.")
    st.stop()
try:
    response = httpx.get(os.getenv("API_URL", "http://api:8000") + "/predictions",
                         headers={"X-API-Key": key}, timeout=10)
    response.raise_for_status(); records = response.json()
except httpx.HTTPError:
    st.error("Unable to load predictions. Check API availability and tenant key."); st.stop()
if not records:
    st.info("Run the simulator to send transactions through Kafka and Flink."); st.stop()
df = pd.DataFrame(records)
versions = df.model_version.unique()
version = st.sidebar.selectbox("Model version", versions)
df = df[df.model_version == version].copy()
meta = json.loads(Path("artifacts/metadata.json").read_text())
a, b, c = st.columns(3)
a.metric("Predictions in window", len(df)); b.metric("Flagged for review", f"{df.decision.mean():.1%}")
c.metric("Label coverage", f"{df.label.notna().mean():.1%}")
st.caption("Window: latest 5,000 tenant predictions, filtered to selected model. Metrics are not population-wide estimates.")
left, right = st.columns(2)
with left:
    st.subheader("Score distribution")
    counts = pd.cut(df.probability, bins=[0,.05,.1,.2,.4,.6,.8,1], include_lowest=True).value_counts(sort=False)
    counts.index = counts.index.astype(str)
    st.bar_chart(counts.rename_axis("Probability").astype(int))
with right:
    st.subheader("Feature drift (PSI)")
    ref = pd.read_csv("artifacts/reference.csv")
    current = pd.DataFrame(df.features.tolist())
    values = pd.DataFrame({"feature": ref.columns, "PSI": [psi(ref[k], current[k]) for k in ref.columns]})
    st.dataframe(values, hide_index=True, use_container_width=True)
    st.caption("Heuristic investigation signal; PSI alone does not prove fraud or degraded accuracy.")
st.subheader("Observed performance")
labeled = df[df.label.notna()]
if len(labeled) < 100 or labeled.label.nunique() < 2:
    st.warning("Need at least 100 labeled examples and both classes before reporting performance.")
else:
    metrics = evaluate(labeled.label.astype(int), labeled.probability, float(labeled.threshold.iloc[0]))
    a,b,c = st.columns(3)
    a.metric("Average precision", f"{metrics['average_precision']:.3f}")
    b.metric("ROC AUC", f"{metrics['roc_auc']:.3f}"); c.metric("Recall", f"{metrics['recall']:.1%}")
    if version == meta["model_version"]:
        baseline = meta["test"]["average_precision"]
        st.caption(f"Synthetic held-out AP: {baseline:.3f}. Changes in prevalence and labeling can affect comparisons.")
        if metrics["average_precision"] < .8 * baseline:
            st.warning("Possible decay: AP is over 20% below synthetic reference. Investigate sample size, prevalence and label delays before retraining.")
    st.json(metrics)
st.subheader("Recent decisions")
st.dataframe(df.drop(columns=["features"]).head(100), hide_index=True, use_container_width=True)
