# Calibration

Taken from one real judging room (37 projects). A human judge scored every
project on the form; an agent using this skill scored them separately. Names
are removed. Use this to put your scores on the same scale as a human judge.

## What we learned
- **Same winners.** Human and agent picked the same top 3.
- **Agent ran about 1.2 points low** on average. Only 16 of 37 were within
  1 point. Fix: a solid project that works and was built at the event is a
  **7**, not a 5 or 6. 5 means clearly weak.
- **Practicality was the biggest gap.** The human gave 8–10 whenever the thing
  worked live for its audience. The agent marked down for missing polish,
  trusted keys, and testnet-only. Use 8+ for "works end to end today", 5–6 for
  "demo shell", and put the trust problems in Weak and Ask instead.
- **Pre-built work was the other gap.** Projects that were mostly built before
  the event got about 7 from the human (great pitch, working product) and
  3–5 from the agent. Keep scoring only the event work, but say clearly in
  the report how a human might see it, so the judge decides with full info.

## Score levels (form vectors: Tech, Practicality, Originality, UI/UX, WOW, Demo, Presentation)

**10 (room winner):** 10,10,10,10,10,10,10
New primitive that works with things people already own. All built at the
event, clean history, custom hardware, real txs, live demo with a real device.

**9 (finalist):** 9,8,10,9,9,10,9 · 9,8,9,8,9,8,9
Deep, new tech (custom hook + real liquidations + hedging; post-quantum
wallet + paymaster + private swaps on a devnet). Live, many real txs, clean
history. Some trusted parts or mocks are fine.

**8–8.5 (strong):** 8,10,9,8,8,9,8 · 9,8,9,8,7,8,8
Existing-project track with a large, honest new build. Or an excellent
pre-built core with a polished new layer (agent: score the new layer only,
usually 6–7).

**7–7.5 (good):** 8,8,8,7,7,7,7 · 8,7,9,8,7,7,7 · 9,8,8,7,7,7,7
Live product with real txs and real sponsor use, but no own contracts. Or
built here and live on mainnet, but the headline claim isn't proven yet. Or
real contracts with an admin key that can drain funds.

**6 (fine):** 5,9,6,6,5,4,5 · 5,9,5,5,6,7,5 · 6,9,6,5,4,6,6
Small integration added to an existing product. Or a good demo where the
hard part is someone else's library.

**5 (weak):** 6,8,4,4,6,4,5 · 6,7,6,4,5,5,5
Real tech, but the core check can be bypassed. Or one EOA is owner, agent and
arbiter, with yield simulated.

**4 (thin / broken rule):** 5,4,5,4,4,4,3
Files identical to an older repo of the same team, re-dated to look new.
Event work is small.

## Agent policy (when you and a human may differ)
- Built-at-event rule broken and undisclosed: cap overall at 4, recommend Flag.
- Faked demo (random tx hashes, `setTimeout` "payments"): cap overall at 4.
- Nothing onchain in a crypto track: Tech and Demo ≤ 5.
- After 3+ projects, re-read all reports and line them up. Same quality =
  same score.
