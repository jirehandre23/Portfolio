PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS borrowers (
 id TEXT PRIMARY KEY, name TEXT NOT NULL, sector TEXT NOT NULL, principal REAL CHECK(principal>0)
);
CREATE TABLE IF NOT EXISTS scenarios (
 name TEXT PRIMARY KEY, revenue_change REAL, expense_change REAL, rate_shock REAL
);
CREATE TABLE IF NOT EXISTS results (
 borrower_id TEXT REFERENCES borrowers(id), scenario TEXT REFERENCES scenarios(name),
 cfads REAL, debt_service REAL, dscr REAL, covenant REAL, breach INTEGER CHECK(breach IN (0,1)),
 cash_days REAL, cash_after_year REAL,
 PRIMARY KEY(borrower_id,scenario)
);
CREATE VIEW IF NOT EXISTS sector_risk AS
SELECT r.scenario,b.sector,COUNT(*) AS borrower_count,SUM(b.principal) AS exposure,
 SUM(CASE WHEN r.breach=1 THEN b.principal ELSE 0 END) AS breached_exposure,
 SUM(r.cfads)/SUM(r.debt_service) AS aggregate_dscr
FROM results r JOIN borrowers b ON b.id=r.borrower_id GROUP BY r.scenario,b.sector;
