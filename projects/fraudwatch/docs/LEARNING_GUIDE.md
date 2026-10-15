# Explain this project in an interview

## A 60-second walkthrough

“FraudWatch is a synthetic-data reference application for transaction risk scoring.
I use XGBoost to rank transactions, compare it with logistic regression, and choose
a review threshold on validation data using explicit error costs. FastAPI supports
direct scoring and a Kafka/Flink streaming path. Predictions are stored in PostgreSQL
with tenant and transaction IDs so replay does not duplicate results. MLflow packages
and records the model. Streamlit shows feature drift and evaluates performance when
labels arrive. The demonstration does not establish production fraud performance.”

Read and run the code before describing it as work you can independently maintain.

## Follow one transaction

1. Open `features.py`: identify what is available at scoring time. Why is the fraud label excluded?
2. Open `train.py`: find the three splits. Why would tuning a threshold on the test set leak information?
3. Open `model.py`: the MLflow wrapper returns a probability, not an automatic accusation of fraud.
4. Open `api.py`: a tenant key identifies the shop; `asyncio.to_thread` keeps CPU inference off the event loop.
5. Open `flink/pipeline.sql`: match `LN(1 + amount)` to NumPy `log1p(amount)`.
6. Open `worker.py`: follow the offset commit. What if the worker crashes after DB insertion?
7. Open `sql/init.sql`: explain the composite primary key and why transaction IDs alone are insufficient.
8. Open `dashboard.py`: explain why labels are necessary to measure performance decay.

## Questions you should be able to answer

- Why isn't accuracy the headline metric for rare fraud? Predicting every transaction legitimate can look accurate.
- What changes when the threshold falls? Usually more fraud is caught and more legitimate transactions are reviewed.
- Why use precision-recall as well as ROC? False-positive rates can look small in a large negative class while review volume is costly.
- Why not claim exactly-once? Kafka processing and database persistence do not share one transaction.
- Is drift the same as decay? No. Inputs may shift without hurting performance; decay needs observed outcomes.
- Does `async` make XGBoost faster? No. It helps I/O concurrency; inference still needs CPU resources.
- Why both Kafka and Flink? Kafka buffers/replays events; Flink continuously transforms them. For this small demo a simpler worker would suffice.
- Is this a full SaaS? No. It demonstrates tenant-scoped scoring and monitoring, without billing or onboarding.

## Five useful extensions to make it your own

1. Change the assumed false-positive cost from 5 to 20; rerun and explain threshold movement.
2. Add a unit test for simultaneous identical transaction submissions against real PostgreSQL.
3. Add merchant-category features consistently to generator, schema, SQL and model.
4. Plot AP over fixed time windows with label counts and prevalence alongside it.
5. Replace synthetic data with a properly licensed dataset and document its limitations.
