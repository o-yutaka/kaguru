# Kaggriculture AB10 Plan

Baseline A = current Phase3 v1, frozen.
B variants change exactly one mechanism.

1. B01_OPP_SELL — public opponent farm -> sparse SELL ordering only.
2. B02_MARKET_TIMING — sell high-pressure products later; no production change.
3. B03_GEOMETRY_NEAREST — nearest feasible high-value work target.
4. B04_MOVE_BUDGET — cap nonproductive movement / penalize long detours.
5. B05_LAND_TIMING — alter land expansion timing only.
6. B06_HIRE_TIMING — alter hire timing only.
7. B07_FERTILIZER_LIQUIDATION — test fertilizer liquidation timing independently.
8. B08_DEMAND_AWARE_SELL — town demand + current price -> SELL order only.
9. B09_OPP_PLUS_MARKET — B01 + B08, no production change.
10. B10_OPP_PLUS_GEOMETRY — B01 + B03, no production change.

Protocol per B:
- same seeds: 42,1000,1050,1100,1200,1500,2026,300257
- both seats
- 720 turns
- record final_cash, winner, action count, runtime, contract errors
- compute paired delta vs A
- no promotion from one replay

Promotion gate:
1. contract/regression PASS
2. runtime non-regression
3. paired head-to-head improvement
4. only then public Kaggle submission

Do not modify Phase3 production/task/plant/terminal machinery during this screen.
