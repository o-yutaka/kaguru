# v38 HANDS / ANIMAL MANAGEMENT SWEEP

Baseline: v38, unchanged mechanics except one variable per candidate. Reference A: v30_flat.

Goal: isolate whether v38 loses because hands are under-provisioned, over-provisioned, or poorly scheduled.

Candidates:
B11_HAND_RATIO_2 = 1 hand / 2 animals
B12_HAND_RATIO_3 = 1 / 3
B13_HAND_RATIO_4 = current v38 reference
B14_HAND_RATIO_5 = 1 / 5
B15_HAND_RATIO_6 = 1 / 6
B16_HAND_RATIO_8 = 1 / 8
B17_COW_ONLY = v38 scheduler + cow only, no sheep
B18_NO_EXPANSION = v38 animals/hands but one pasture only
B19_HANDS_ONLY = v30_flat mechanics + hands, no pasture expansion/sheep
B20_ANIMALS_ONLY = v30_flat mechanics + controlled pasture expansion, no hands

Protocol:
- paired head-to-head against v30_flat and v38
- seeds: 42,1000,1050,1100,1200,1500,2026,300257 plus 0..39 if cheap locally
- both seats
- 720 turns
- record final cash, winner, animals alive, pastures, hands, wheat consumed, fertilizer harvested, milk/wool sold, escapes, runtime, contract errors
- freeze production rules except the declared variable

Promotion:
1. no contract/runtime regression
2. beats v38 on mean cash AND head-to-head rate
3. any candidate beating v30_flat gets a separate verification run
4. only verified winner proceeds to Kaggle submission

Important: do not infer causality from v38 aggregate alone. The key comparison is B17/B18/B19/B20, which separates sheep, expansion, and hands.
