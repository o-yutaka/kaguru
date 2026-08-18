# Kaggriculture Upper-Ladder Strategy Audit

Date: 2026-08-18

## Observed leaderboard snapshot
User-observed live snapshot (provenance, not independently re-fetched here):
- 1: カワシギ 3185.2
- 2: Thomas Tschinkel 3155.2
- 3: tetsuya 3037.7
- 20: boatlee 2880.8
- Phase3 v1: 895.6
- Prior V17: 900.4 / 910.6

Leaderboard is skill-rating based; do not compare rating μ directly with final cash.

## Official contract
Kaggriculture is a 2-player, 720-turn simulation. `farms` exposes both players' public farm state, while private shed/inventory is not public. Market order capacity defaults to 10. Official docs also expose episode/replay/log download commands for submitted agents.
Source: https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/AGENTS.md

## Public implementation signals
### GzmCR/Kaggriculture
Observed design signals:
- dynamic market-aware decisions
- current price / demand / inventory / cash / season timing
- deterministic rule policy
- baseline/history kept for reproducible rollback
- CPU-friendly, no GPU required
Source: https://github.com/GzmCR/Kaggriculture

### deepeshumrao/kaggriculture-agent
Observed design signals:
- market processed first
- nearest high-value target selection
- movement treated as a scarce turn resource
- move-or-act policy
- local simulator + 66 tests
Source: https://github.com/deepeshumrao/kaggriculture-agent

### Beiciccc/Kaggriculture
Observed public experiment notes emphasize:
- leaderboard is head-to-head / rating oriented, not final coin margin
- submitted versions must be evaluated on live ladder behavior
- experiment history and fresh-gate comparisons are used to avoid single-run conclusions
Source: https://github.com/Beiciccc/Kaggriculture

## Common-factor matrix
| Factor | Public evidence | BLACK treatment |
|---|---|---|
| Market state awareness | GzmCR | KEEP / measure |
| Season timing | GzmCR | KEEP / measure |
| Inventory-aware selling | GzmCR | KEEP / measure |
| Movement economy | Deepesh | CANDIDATE |
| Nearest high-value target | Deepesh | CANDIDATE |
| History + rollback | GzmCR / Beiciccc | REQUIRED |
| Head-to-head evaluation | Beiciccc + official scoring | PRIMARY |
| Opponent public farm | Official obs contract | CANDIDATE |
| Opponent private inventory | Not public | FORBIDDEN input |

## Current BLACK hypotheses
1. Opponent divergence should affect SELL ordering first, not production/planting.
2. Fertilizer gap is more plausibly liquidation/timing than raw production capacity because observed replay collect counts were similar while sell counts diverged sharply.
3. Geometry should be treated as action economy: every extra move consumes a turn that could have created or liquidated value.
4. Market and opponent signals should be orthogonalized: town demand vs rival supply before changing SELL priority.
5. Ladder promotion must use paired head-to-head results, not local final cash alone.

## Candidate ladder
A = Phase3 baseline
B = sparse opponent-aware SELL ordering
C = geometry/action-economy adapter
D = market timing adapter
E = B + D
F = B + C + D

## Promotion gate
- same seeds
- both seats
- fixed 720 steps
- identical baseline package
- no contract errors
- no runtime regression
- report final cash separately
- report head-to-head win/loss separately
- submit only after paired evidence improves

## Next highest-value measurement
Recover fresh official episodes/replays for the top ladder cohort and compute winner-loser deltas over:
- land-buy timing
- hire timing
- production mix
- SELL timing by product
- movement distance / move-share
- market-order count
- terminal liquidation
- opponent public-farm divergence
